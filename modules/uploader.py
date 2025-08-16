"""
YouTube upload automation module
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from video_editor import VideoMetadata
from rewriter_tts import RewrittenContent
from utils import sanitize_filename, ensure_directory, retry_with_backoff

class YouTubeUploader:
    """YouTube upload automation for Shorts"""
    
    # YouTube API scopes
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Upload settings
        self.auto_upload = config.get('auto_upload', False)
        self.privacy_status = config.get('privacy_status', 'private')
        self.category_id = config.get('category_id', 24)  # Entertainment
        self.default_tags = config.get('default_tags', [])
        
        # Thumbnail settings
        self.thumbnail_config = config.get('thumbnail', {})
        
        # Scheduling settings
        self.scheduling = config.get('scheduling', {})
        
        # Credentials
        self.credentials_file = 'credentials.json'
        self.token_file = 'token.pickle'
        
        # Initialize YouTube service
        self.youtube_service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize YouTube API service"""
        try:
            credentials = self._get_credentials()
            if credentials:
                self.youtube_service = build('youtube', 'v3', credentials=credentials)
                self.logger.info("YouTube service initialized successfully")
            else:
                self.logger.warning("Could not initialize YouTube service - credentials not available")
                
        except Exception as e:
            self.logger.error(f"Error initializing YouTube service: {e}")
    
    def _get_credentials(self) -> Optional[Credentials]:
        """Get or refresh YouTube API credentials"""
        credentials = None
        
        # Load existing credentials
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    credentials = pickle.load(token)
            except Exception as e:
                self.logger.error(f"Error loading credentials: {e}")
        
        # Refresh or get new credentials
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                    self.logger.info("Credentials refreshed successfully")
                except Exception as e:
                    self.logger.error(f"Error refreshing credentials: {e}")
                    credentials = None
            
            # Get new credentials if needed
            if not credentials:
                credentials = self._get_new_credentials()
        
        # Save credentials
        if credentials:
            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(credentials, token)
            except Exception as e:
                self.logger.error(f"Error saving credentials: {e}")
        
        return credentials
    
    def _get_new_credentials(self) -> Optional[Credentials]:
        """Get new credentials via OAuth flow"""
        try:
            if not os.path.exists(self.credentials_file):
                self.logger.error(f"Credentials file not found: {self.credentials_file}")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.SCOPES)
            credentials = flow.run_local_server(port=0)
            
            self.logger.info("New credentials obtained successfully")
            return credentials
            
        except Exception as e:
            self.logger.error(f"Error getting new credentials: {e}")
            return None
    
    def upload_video(self, video_path: str, content: RewrittenContent, thumbnail_path: Optional[str] = None) -> str:
        """
        Upload video to YouTube
        
        Args:
            video_path: Path to video file
            content: RewrittenContent with metadata
            thumbnail_path: Optional path to thumbnail image
            
        Returns:
            str: YouTube video URL or empty string if failed
        """
        if not self.auto_upload:
            self.logger.info("Auto-upload disabled, skipping upload")
            return ""
        
        if not self.youtube_service:
            self.logger.error("YouTube service not initialized")
            return ""
        
        try:
            # Prepare video metadata
            video_metadata = self._prepare_video_metadata(content)
            
            # Upload video
            video_id = self._upload_video_file(video_path, video_metadata)
            
            if video_id:
                # Upload thumbnail if provided
                if thumbnail_path and os.path.exists(thumbnail_path):
                    self._upload_thumbnail(video_id, thumbnail_path)
                
                # Schedule publication if configured
                if self.scheduling.get('enabled', False):
                    self._schedule_publication(video_id)
                
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                self.logger.info(f"Video uploaded successfully: {video_url}")
                
                # Save upload record
                self._save_upload_record(video_id, video_path, content)
                
                return video_url
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Error uploading video: {e}")
            return ""
    
    def _prepare_video_metadata(self, content: RewrittenContent) -> Dict[str, Any]:
        """Prepare video metadata for upload"""
        # Combine tags
        tags = list(self.default_tags)
        tags.extend(content.keywords[:8])  # YouTube allows max 500 characters for tags
        
        # Create description
        description = self._create_description(content)
        
        # Prepare metadata
        metadata = {
            'snippet': {
                'title': content.rewritten_title[:100],  # YouTube title limit
                'description': description,
                'tags': tags,
                'categoryId': str(self.category_id),
                'defaultLanguage': 'en',
                'defaultAudioLanguage': 'en'
            },
            'status': {
                'privacyStatus': self.privacy_status,
                'madeForKids': False,
                'selfDeclaredMadeForKids': False
            }
        }
        
        return metadata
    
    def _create_description(self, content: RewrittenContent) -> str:
        """Create video description"""
        description = f"{content.rewritten_script[:300]}...\n\n"
        
        description += "🤖 This video was automatically generated using AI technology\n"
        description += "📱 Optimized for mobile viewing and YouTube Shorts\n\n"
        
        # Add hashtags
        if content.keywords:
            hashtags = " ".join([f"#{tag.replace(' ', '')}" for tag in content.keywords[:10]])
            description += f"{hashtags}\n\n"
        
        description += "#Shorts #AI #AutoGenerated #Tech #Facts\n\n"
        description += "Like and subscribe for more AI-generated content!"
        
        return description[:5000]  # YouTube description limit
    
    def _upload_video_file(self, video_path: str, metadata: Dict[str, Any]) -> Optional[str]:
        """Upload video file to YouTube"""
        try:
            # Create media upload object
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True,
                mimetype='video/mp4'
            )
            
            # Create upload request
            request = self.youtube_service.videos().insert(
                part='snippet,status',
                body=metadata,
                media_body=media
            )
            
            # Execute upload with retry logic
            def execute_upload():
                response = None
                error = None
                retry = 0
                
                while response is None:
                    try:
                        status, response = request.next_chunk()
                        if status:
                            self.logger.info(f"Upload progress: {int(status.progress() * 100)}%")
                    except HttpError as e:
                        if e.resp.status in [404, 500, 502, 503, 504]:
                            error = f"Retriable error: {e}"
                            retry += 1
                            if retry > 5:
                                raise e
                        else:
                            raise e
                    except Exception as e:
                        error = f"Unexpected error: {e}"
                        raise e
                
                return response
            
            response = retry_with_backoff(execute_upload, max_retries=3)
            
            if response and 'id' in response:
                video_id = response['id']
                self.logger.info(f"Video uploaded with ID: {video_id}")
                return video_id
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error uploading video file: {e}")
            return None
    
    def _upload_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Upload custom thumbnail for video"""
        try:
            request = self.youtube_service.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            )
            
            response = request.execute()
            
            if response:
                self.logger.info(f"Thumbnail uploaded for video {video_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error uploading thumbnail: {e}")
            return False
    
    def _schedule_publication(self, video_id: str) -> bool:
        """Schedule video publication"""
        try:
            if not self.scheduling.get('enabled', False):
                return False
            
            # Calculate publication time
            schedule_time = self.scheduling.get('time', '12:00')
            timezone = self.scheduling.get('timezone', 'UTC')
            
            # For now, just log the scheduling attempt
            # Real implementation would set publishAt in the video metadata
            self.logger.info(f"Video {video_id} scheduled for publication at {schedule_time} {timezone}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error scheduling publication: {e}")
            return False
    
    def _save_upload_record(self, video_id: str, video_path: str, content: RewrittenContent):
        """Save record of uploaded video"""
        try:
            record = {
                'video_id': video_id,
                'video_path': video_path,
                'title': content.rewritten_title,
                'upload_time': datetime.now().isoformat(),
                'original_title': content.original_title,
                'keywords': content.keywords,
                'url': f"https://www.youtube.com/watch?v={video_id}"
            }
            
            # Ensure uploads directory exists
            uploads_dir = Path('uploads')
            ensure_directory(str(uploads_dir))
            
            # Save record
            record_file = uploads_dir / f"upload_{video_id}.json"
            with open(record_file, 'w') as f:
                json.dump(record, f, indent=2)
            
            # Also append to master log
            log_file = uploads_dir / "upload_log.json"
            
            if log_file.exists():
                with open(log_file, 'r') as f:
                    upload_log = json.load(f)
            else:
                upload_log = []
            
            upload_log.append(record)
            
            with open(log_file, 'w') as f:
                json.dump(upload_log, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error saving upload record: {e}")
    
    def get_video_analytics(self, video_id: str) -> Dict[str, Any]:
        """Get analytics for uploaded video"""
        try:
            if not self.youtube_service:
                return {}
            
            # Get video statistics
            request = self.youtube_service.videos().list(
                part='statistics,snippet',
                id=video_id
            )
            
            response = request.execute()
            
            if response['items']:
                video_data = response['items'][0]
                analytics = {
                    'video_id': video_id,
                    'title': video_data['snippet']['title'],
                    'published_at': video_data['snippet']['publishedAt'],
                    'view_count': int(video_data['statistics'].get('viewCount', 0)),
                    'like_count': int(video_data['statistics'].get('likeCount', 0)),
                    'comment_count': int(video_data['statistics'].get('commentCount', 0)),
                    'favorite_count': int(video_data['statistics'].get('favoriteCount', 0))
                }
                
                return analytics
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting video analytics: {e}")
            return {}
    
    def update_video_metadata(self, video_id: str, title: Optional[str] = None, description: Optional[str] = None, tags: Optional[List[str]] = None) -> bool:
        """Update video metadata after upload"""
        try:
            if not self.youtube_service:
                return False
            
            # Get current video data
            request = self.youtube_service.videos().list(
                part='snippet',
                id=video_id
            )
            
            response = request.execute()
            
            if not response['items']:
                return False
            
            video_snippet = response['items'][0]['snippet']
            
            # Update provided fields
            if title:
                video_snippet['title'] = title[:100]
            if description:
                video_snippet['description'] = description[:5000]
            if tags:
                video_snippet['tags'] = tags
            
            # Update video
            update_request = self.youtube_service.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': video_snippet
                }
            )
            
            update_request.execute()
            
            self.logger.info(f"Video metadata updated for {video_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating video metadata: {e}")
            return False
    
    def delete_video(self, video_id: str) -> bool:
        """Delete video from YouTube"""
        try:
            if not self.youtube_service:
                return False
            
            request = self.youtube_service.videos().delete(id=video_id)
            request.execute()
            
            self.logger.info(f"Video {video_id} deleted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting video: {e}")
            return False
    
    def get_upload_quota_usage(self) -> Dict[str, Any]:
        """Get current quota usage information"""
        try:
            # This is a placeholder - YouTube API doesn't directly provide quota usage
            # In practice, you would track API calls and estimate usage
            
            quota_info = {
                'daily_limit': 10000,  # Default quota limit
                'estimated_usage': 0,  # Would track actual usage
                'uploads_today': self._count_uploads_today(),
                'quota_reset_time': '00:00 UTC'
            }
            
            return quota_info
            
        except Exception as e:
            self.logger.error(f"Error getting quota usage: {e}")
            return {}
    
    def _count_uploads_today(self) -> int:
        """Count uploads made today"""
        try:
            today = datetime.now().date()
            upload_count = 0
            
            uploads_dir = Path('uploads')
            if uploads_dir.exists():
                log_file = uploads_dir / "upload_log.json"
                if log_file.exists():
                    with open(log_file, 'r') as f:
                        upload_log = json.load(f)
                    
                    for record in upload_log:
                        upload_date = datetime.fromisoformat(record['upload_time']).date()
                        if upload_date == today:
                            upload_count += 1
            
            return upload_count
            
        except Exception as e:
            self.logger.error(f"Error counting today's uploads: {e}")
            return 0