#!/usr/bin/env python3
"""
YouTube Video Upload Module

This module provides functionality to upload videos to YouTube using the YouTube Data API v3.
It handles authentication, video upload, and metadata configuration.
"""

import os
import sys
import logging
from typing import Optional, Dict, List
import pickle
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class YouTubeUploader:
    """Class to handle YouTube video uploads."""
    
    def __init__(self):
        """Initialize the YouTube uploader with authentication."""
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with YouTube API using OAuth2 or service account."""
        creds = None
        
        # Check for existing token
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Try to get credentials from environment variables
                client_config = self._get_client_config_from_env()
                if client_config:
                    flow = InstalledAppFlow.from_client_config(
                        client_config, SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    # Fallback to client secrets file
                    if os.path.exists('client_secrets.json'):
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'client_secrets.json', SCOPES)
                        creds = flow.run_local_server(port=0)
                    else:
                        raise FileNotFoundError(
                            "No authentication method available. "
                            "Please provide either client_secrets.json file or "
                            "set YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET environment variables."
                        )
            
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('youtube', 'v3', credentials=creds)
        logger.info("Successfully authenticated with YouTube API")
    
    def _get_client_config_from_env(self) -> Optional[Dict]:
        """Get OAuth client configuration from environment variables."""
        client_id = os.getenv('YOUTUBE_CLIENT_ID')
        client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
        
        if client_id and client_secret:
            return {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": ["http://localhost"]
                }
            }
        return None
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str],
        category_id: str = "22",  # People & Blogs
        privacy_status: str = "private"
    ) -> Optional[str]:
        """
        Upload a video to YouTube.
        
        Args:
            video_path: Path to the video file
            title: Video title
            description: Video description
            tags: List of tags for the video
            category_id: YouTube category ID (default: 22 for People & Blogs)
            privacy_status: Privacy status (private, public, unlisted)
        
        Returns:
            Video ID if successful, None otherwise
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return None
        
        # Prepare video metadata
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Create media upload object
        media = MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True,
            mimetype='video/*'
        )
        
        try:
            logger.info(f"Starting upload of video: {title}")
            
            # Call the API's videos.insert method to create and upload the video
            insert_request = self.service.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            video_id = self._resumable_upload(insert_request)
            
            if video_id:
                logger.info(f"Video uploaded successfully. Video ID: {video_id}")
                logger.info(f"Video URL: https://www.youtube.com/watch?v={video_id}")
                return video_id
            else:
                logger.error("Failed to upload video")
                return None
                
        except HttpError as e:
            logger.error(f"An HTTP error occurred: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return None
    
    def _resumable_upload(self, insert_request):
        """Execute the resumable upload and handle retries."""
        response = None
        error = None
        retry = 0
        
        while response is None:
            try:
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        return response['id']
                    else:
                        logger.error(f"The upload failed with an unexpected response: {response}")
                        return None
            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    error = f"A retriable HTTP error {e.resp.status} occurred: {e.content}"
                else:
                    raise
            except Exception as e:
                error = f"A retriable error occurred: {e}"
            
            if error is not None:
                logger.warning(error)
                retry += 1
                if retry > 3:
                    logger.error("Maximum retry attempts exceeded")
                    return None
                
                logger.info(f"Retrying upload (attempt {retry}/3)...")
                error = None


def upload_video_to_youtube(
    video_path: str,
    title: str,
    description: str,
    tags: List[str],
    privacy_status: str = "private"
) -> Optional[str]:
    """
    Convenience function to upload a video to YouTube.
    
    Args:
        video_path: Path to the video file
        title: Video title
        description: Video description
        tags: List of tags for the video
        privacy_status: Privacy status (private, public, unlisted)
    
    Returns:
        Video ID if successful, None otherwise
    """
    uploader = YouTubeUploader()
    return uploader.upload_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        privacy_status=privacy_status
    )


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 5:
        print("Usage: python upload_to_youtube.py <video_path> <title> <description> <tags>")
        print("Example: python upload_to_youtube.py video.mp4 'My Video' 'Description' 'tag1,tag2,tag3'")
        sys.exit(1)
    
    video_path = sys.argv[1]
    title = sys.argv[2]
    description = sys.argv[3]
    tags = sys.argv[4].split(',') if sys.argv[4] else []
    
    video_id = upload_video_to_youtube(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        privacy_status="private"  # Default to private for safety
    )
    
    if video_id:
        print(f"Upload successful! Video ID: {video_id}")
        print(f"Video URL: https://www.youtube.com/watch?v={video_id}")
    else:
        print("Upload failed!")
        sys.exit(1)