"""YouTube upload functionality for uploading generated videos."""

import os
from typing import Dict, Optional, List
from dataclasses import dataclass


class YouTubeUploadError(Exception):
    """Custom exception for YouTube upload errors."""
    pass


@dataclass
class VideoMetadata:
    """Metadata for YouTube video upload."""
    title: str
    description: str = ""
    tags: List[str] = None
    category_id: str = "22"  # People & Blogs
    privacy_status: str = "private"  # private, public, unlisted
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class YouTubeUploader:
    """Main class for uploading videos to YouTube."""
    
    def __init__(self, api_key: str, client_id: str, client_secret: str):
        """
        Initialize the YouTube uploader.
        
        Args:
            api_key: YouTube Data API key
            client_id: OAuth 2.0 client ID
            client_secret: OAuth 2.0 client secret
        """
        if not api_key:
            raise YouTubeUploadError("API key is required")
        if not client_id:
            raise YouTubeUploadError("Client ID is required")
        if not client_secret:
            raise YouTubeUploadError("Client secret is required")
        
        self.api_key = api_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.authenticated = False
    
    def authenticate(self) -> bool:
        """
        Authenticate with YouTube API.
        
        Returns:
            bool: True if authentication successful
            
        Raises:
            YouTubeUploadError: If authentication fails
        """
        # Simulate authentication process
        if not self.api_key or not self.client_id or not self.client_secret:
            raise YouTubeUploadError("Missing authentication credentials")
        
        # In a real implementation, this would handle OAuth2 flow
        self.authenticated = True
        return True
    
    def upload_video(self, video_path: str, metadata: VideoMetadata) -> Dict[str, str]:
        """
        Upload a video to YouTube.
        
        Args:
            video_path: Path to the video file
            metadata: Video metadata for upload
            
        Returns:
            Dict containing upload response with video ID and status
            
        Raises:
            YouTubeUploadError: If upload fails
        """
        if not self.authenticated:
            raise YouTubeUploadError("Must authenticate before uploading")
        
        if not os.path.exists(video_path):
            raise YouTubeUploadError(f"Video file not found: {video_path}")
        
        if not metadata.title.strip():
            raise YouTubeUploadError("Video title is required")
        
        # Validate privacy status
        valid_privacy = ["private", "public", "unlisted"]
        if metadata.privacy_status not in valid_privacy:
            raise YouTubeUploadError(f"Invalid privacy status. Must be one of: {valid_privacy}")
        
        # Simulate upload process
        file_size = os.path.getsize(video_path)
        if file_size == 0:
            raise YouTubeUploadError("Video file is empty")
        
        # Simulate API call response
        video_id = f"mock_video_id_{hash(video_path) % 10000}"
        
        return {
            "video_id": video_id,
            "status": "uploaded",
            "title": metadata.title,
            "privacy_status": metadata.privacy_status,
            "upload_status": "processed"
        }
    
    def update_video_metadata(self, video_id: str, metadata: VideoMetadata) -> bool:
        """
        Update metadata for an existing video.
        
        Args:
            video_id: YouTube video ID
            metadata: Updated metadata
            
        Returns:
            bool: True if update successful
            
        Raises:
            YouTubeUploadError: If update fails
        """
        if not self.authenticated:
            raise YouTubeUploadError("Must authenticate before updating")
        
        if not video_id:
            raise YouTubeUploadError("Video ID is required")
        
        if not metadata.title.strip():
            raise YouTubeUploadError("Video title is required")
        
        # Simulate update process
        return True
    
    def get_video_status(self, video_id: str) -> Dict[str, str]:
        """
        Get the status of an uploaded video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dict containing video status information
            
        Raises:
            YouTubeUploadError: If status check fails
        """
        if not self.authenticated:
            raise YouTubeUploadError("Must authenticate before checking status")
        
        if not video_id:
            raise YouTubeUploadError("Video ID is required")
        
        # Simulate status check
        return {
            "video_id": video_id,
            "upload_status": "processed",
            "privacy_status": "private",
            "processing_status": "succeeded"
        }
    
    def delete_video(self, video_id: str) -> bool:
        """
        Delete a video from YouTube.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            YouTubeUploadError: If deletion fails
        """
        if not self.authenticated:
            raise YouTubeUploadError("Must authenticate before deleting")
        
        if not video_id:
            raise YouTubeUploadError("Video ID is required")
        
        # Simulate deletion process
        return True


def create_uploader_from_config(config) -> YouTubeUploader:
    """
    Factory function to create a YouTube uploader from configuration.
    
    Args:
        config: Configuration object with YouTube credentials
        
    Returns:
        YouTubeUploader instance
    """
    return YouTubeUploader(
        api_key=config.youtube_api_key,
        client_id=config.youtube_client_id,
        client_secret=config.youtube_client_secret
    )