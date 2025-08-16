"""Tests for the YouTube uploader module."""

import os
import pytest
from unittest.mock import patch, Mock
from youtube_uploader import (
    YouTubeUploader, 
    VideoMetadata, 
    YouTubeUploadError, 
    create_uploader_from_config
)


class TestVideoMetadata:
    """Test cases for the VideoMetadata dataclass."""
    
    def test_default_values(self):
        """Test that VideoMetadata has correct default values."""
        metadata = VideoMetadata(title="Test Video")
        
        assert metadata.title == "Test Video"
        assert metadata.description == ""
        assert metadata.tags == []
        assert metadata.category_id == "22"
        assert metadata.privacy_status == "private"
    
    def test_custom_values(self):
        """Test that VideoMetadata accepts custom values."""
        metadata = VideoMetadata(
            title="Custom Video",
            description="Custom description",
            tags=["tag1", "tag2"],
            category_id="10",
            privacy_status="public"
        )
        
        assert metadata.title == "Custom Video"
        assert metadata.description == "Custom description"
        assert metadata.tags == ["tag1", "tag2"]
        assert metadata.category_id == "10"
        assert metadata.privacy_status == "public"


class TestYouTubeUploader:
    """Test cases for the YouTubeUploader class."""
    
    def test_valid_credentials_initialization(self):
        """Test that YouTubeUploader initializes with valid credentials."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        
        assert uploader.api_key == "api_key"
        assert uploader.client_id == "client_id"
        assert uploader.client_secret == "client_secret"
        assert uploader.authenticated is False
    
    def test_empty_api_key_raises_error(self):
        """Test that empty API key raises YouTubeUploadError."""
        with pytest.raises(YouTubeUploadError, match="API key is required"):
            YouTubeUploader("", "client_id", "client_secret")
    
    def test_empty_client_id_raises_error(self):
        """Test that empty client ID raises YouTubeUploadError."""
        with pytest.raises(YouTubeUploadError, match="Client ID is required"):
            YouTubeUploader("api_key", "", "client_secret")
    
    def test_empty_client_secret_raises_error(self):
        """Test that empty client secret raises YouTubeUploadError."""
        with pytest.raises(YouTubeUploadError, match="Client secret is required"):
            YouTubeUploader("api_key", "client_id", "")
    
    def test_authenticate_success(self):
        """Test successful authentication."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        
        result = uploader.authenticate()
        
        assert result is True
        assert uploader.authenticated is True
    
    def test_authenticate_missing_credentials_raises_error(self):
        """Test that authentication with missing credentials raises error."""
        # This test covers the internal validation in authenticate method
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        uploader.api_key = ""  # Simulate corrupted state
        
        with pytest.raises(YouTubeUploadError, match="Missing authentication credentials"):
            uploader.authenticate()
    
    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize', return_value=1000)
    def test_upload_video_success(self, mock_getsize, mock_exists):
        """Test successful video upload."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        uploader.authenticate()
        metadata = VideoMetadata(title="Test Video")
        
        result = uploader.upload_video("test_video.mp4", metadata)
        
        assert "video_id" in result
        assert result["status"] == "uploaded"
        assert result["title"] == "Test Video"
        assert result["privacy_status"] == "private"
        assert result["upload_status"] == "processed"
        mock_exists.assert_called_once_with("test_video.mp4")
        mock_getsize.assert_called_once_with("test_video.mp4")
    
    def test_upload_video_not_authenticated_raises_error(self):
        """Test that upload without authentication raises error."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        metadata = VideoMetadata(title="Test Video")
        
        with pytest.raises(YouTubeUploadError, match="Must authenticate before uploading"):
            uploader.upload_video("test_video.mp4", metadata)
    
    @patch('os.path.exists', return_value=False)
    def test_upload_video_file_not_found_raises_error(self, mock_exists):
        """Test that upload with non-existent file raises error."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        uploader.authenticate()
        metadata = VideoMetadata(title="Test Video")
        
        with pytest.raises(YouTubeUploadError, match="Video file not found"):
            uploader.upload_video("nonexistent.mp4", metadata)
    
    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize', return_value=1000)
    def test_upload_video_empty_title_raises_error(self, mock_getsize, mock_exists):
        """Test that upload with empty title raises error."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        uploader.authenticate()
        metadata = VideoMetadata(title="")
        
        with pytest.raises(YouTubeUploadError, match="Video title is required"):
            uploader.upload_video("test_video.mp4", metadata)
    
    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize', return_value=1000)
    def test_upload_video_invalid_privacy_status_raises_error(self, mock_getsize, mock_exists):
        """Test that upload with invalid privacy status raises error."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        uploader.authenticate()
        metadata = VideoMetadata(title="Test Video", privacy_status="invalid")
        
        with pytest.raises(YouTubeUploadError, match="Invalid privacy status"):
            uploader.upload_video("test_video.mp4", metadata)
    
    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize', return_value=0)
    def test_upload_video_empty_file_raises_error(self, mock_getsize, mock_exists):
        """Test that upload with empty file raises error."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        uploader.authenticate()
        metadata = VideoMetadata(title="Test Video")
        
        with pytest.raises(YouTubeUploadError, match="Video file is empty"):
            uploader.upload_video("test_video.mp4", metadata)
    
    def test_update_video_metadata_success(self):
        """Test successful video metadata update."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        uploader.authenticate()
        metadata = VideoMetadata(title="Updated Title")
        
        result = uploader.update_video_metadata("video_123", metadata)
        
        assert result is True
    
    def test_update_video_metadata_not_authenticated_raises_error(self):
        """Test that update without authentication raises error."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        metadata = VideoMetadata(title="Updated Title")
        
        with pytest.raises(YouTubeUploadError, match="Must authenticate before updating"):
            uploader.update_video_metadata("video_123", metadata)
    
    def test_update_video_metadata_empty_video_id_raises_error(self):
        """Test that update with empty video ID raises error."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        uploader.authenticate()
        metadata = VideoMetadata(title="Updated Title")
        
        with pytest.raises(YouTubeUploadError, match="Video ID is required"):
            uploader.update_video_metadata("", metadata)
    
    def test_update_video_metadata_empty_title_raises_error(self):
        """Test that update with empty title raises error."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        uploader.authenticate()
        metadata = VideoMetadata(title="")
        
        with pytest.raises(YouTubeUploadError, match="Video title is required"):
            uploader.update_video_metadata("video_123", metadata)
    
    def test_get_video_status_success(self):
        """Test successful video status retrieval."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        uploader.authenticate()
        
        result = uploader.get_video_status("video_123")
        
        assert result["video_id"] == "video_123"
        assert result["upload_status"] == "processed"
        assert result["privacy_status"] == "private"
        assert result["processing_status"] == "succeeded"
    
    def test_get_video_status_not_authenticated_raises_error(self):
        """Test that status check without authentication raises error."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        
        with pytest.raises(YouTubeUploadError, match="Must authenticate before checking status"):
            uploader.get_video_status("video_123")
    
    def test_get_video_status_empty_video_id_raises_error(self):
        """Test that status check with empty video ID raises error."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        uploader.authenticate()
        
        with pytest.raises(YouTubeUploadError, match="Video ID is required"):
            uploader.get_video_status("")
    
    def test_delete_video_success(self):
        """Test successful video deletion."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        uploader.authenticate()
        
        result = uploader.delete_video("video_123")
        
        assert result is True
    
    def test_delete_video_not_authenticated_raises_error(self):
        """Test that deletion without authentication raises error."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        
        with pytest.raises(YouTubeUploadError, match="Must authenticate before deleting"):
            uploader.delete_video("video_123")
    
    def test_delete_video_empty_video_id_raises_error(self):
        """Test that deletion with empty video ID raises error."""
        uploader = YouTubeUploader("api_key", "client_id", "client_secret")
        uploader.authenticate()
        
        with pytest.raises(YouTubeUploadError, match="Video ID is required"):
            uploader.delete_video("")


class TestFactoryFunction:
    """Test cases for the create_uploader_from_config factory function."""
    
    def test_create_uploader_from_config(self):
        """Test factory function creates uploader with config values."""
        mock_config = Mock()
        mock_config.youtube_api_key = "config_api_key"
        mock_config.youtube_client_id = "config_client_id"
        mock_config.youtube_client_secret = "config_client_secret"
        
        uploader = create_uploader_from_config(mock_config)
        
        assert uploader.api_key == "config_api_key"
        assert uploader.client_id == "config_client_id"
        assert uploader.client_secret == "config_client_secret"