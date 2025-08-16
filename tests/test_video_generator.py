"""Tests for the video generator module."""

import os
import pytest
import tempfile
from unittest.mock import patch, mock_open
from video_generator import (
    VideoGenerator, 
    VideoConfig, 
    VideoGenerationError, 
    create_video_generator
)


class TestVideoConfig:
    """Test cases for the VideoConfig dataclass."""
    
    def test_default_values(self):
        """Test that VideoConfig has correct default values."""
        config = VideoConfig()
        
        assert config.duration == 60
        assert config.quality == "high"
        assert config.output_path == "./output"
        assert config.title == "Generated Video"
        assert config.description == ""
    
    def test_custom_values(self):
        """Test that VideoConfig accepts custom values."""
        config = VideoConfig(
            duration=30,
            quality="medium",
            output_path="/custom/path",
            title="Custom Title",
            description="Custom description"
        )
        
        assert config.duration == 30
        assert config.quality == "medium"
        assert config.output_path == "/custom/path"
        assert config.title == "Custom Title"
        assert config.description == "Custom description"


class TestVideoGenerator:
    """Test cases for the VideoGenerator class."""
    
    def test_valid_config_initialization(self):
        """Test that VideoGenerator initializes with valid config."""
        config = VideoConfig(duration=30, quality="medium", title="Test Video")
        generator = VideoGenerator(config)
        
        assert generator.config == config
    
    def test_invalid_duration_zero_raises_error(self):
        """Test that zero duration raises VideoGenerationError."""
        config = VideoConfig(duration=0)
        
        with pytest.raises(VideoGenerationError, match="Duration must be positive"):
            VideoGenerator(config)
    
    def test_invalid_duration_negative_raises_error(self):
        """Test that negative duration raises VideoGenerationError."""
        config = VideoConfig(duration=-10)
        
        with pytest.raises(VideoGenerationError, match="Duration must be positive"):
            VideoGenerator(config)
    
    def test_invalid_duration_too_long_raises_error(self):
        """Test that duration over 60 seconds raises VideoGenerationError."""
        config = VideoConfig(duration=120)
        
        with pytest.raises(VideoGenerationError, match="Duration cannot exceed 60 seconds"):
            VideoGenerator(config)
    
    def test_invalid_quality_raises_error(self):
        """Test that invalid quality raises VideoGenerationError."""
        config = VideoConfig(quality="ultra")
        
        with pytest.raises(VideoGenerationError, match="Quality must be 'low', 'medium', or 'high'"):
            VideoGenerator(config)
    
    def test_empty_title_raises_error(self):
        """Test that empty title raises VideoGenerationError."""
        config = VideoConfig(title="")
        
        with pytest.raises(VideoGenerationError, match="Title cannot be empty"):
            VideoGenerator(config)
    
    def test_whitespace_title_raises_error(self):
        """Test that whitespace-only title raises VideoGenerationError."""
        config = VideoConfig(title="   ")
        
        with pytest.raises(VideoGenerationError, match="Title cannot be empty"):
            VideoGenerator(config)
    
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('time.time', return_value=1234567890)
    def test_generate_video_success(self, mock_time, mock_file, mock_makedirs):
        """Test successful video generation."""
        config = VideoConfig(title="Test Video", output_path="/test/output")
        generator = VideoGenerator(config)
        content = {"text": "Test content"}
        
        result = generator.generate_video(content)
        
        expected_path = "/test/output/video_1234567890.mp4"
        assert result == expected_path
        mock_makedirs.assert_called_once_with("/test/output", exist_ok=True)
        mock_file.assert_called_once_with(expected_path, 'w')
    
    def test_generate_video_empty_content_raises_error(self):
        """Test that empty content raises VideoGenerationError."""
        config = VideoConfig()
        generator = VideoGenerator(config)
        
        with pytest.raises(VideoGenerationError, match="Content cannot be empty"):
            generator.generate_video({})
    
    def test_generate_video_missing_text_raises_error(self):
        """Test that missing text field raises VideoGenerationError."""
        config = VideoConfig()
        generator = VideoGenerator(config)
        content = {"image": "test.jpg"}
        
        with pytest.raises(VideoGenerationError, match="Content must include 'text' field"):
            generator.generate_video(content)
    
    @patch('builtins.open', new_callable=mock_open, read_data="Title: Test\nDuration: 30s\nContent: Test content")
    @patch('os.path.exists', return_value=True)
    def test_get_video_info_success(self, mock_exists, mock_file):
        """Test successful video info retrieval."""
        config = VideoConfig()
        generator = VideoGenerator(config)
        
        info = generator.get_video_info("test_video.mp4")
        
        assert info["Title"] == "Test"
        assert info["Duration"] == "30s"
        assert info["Content"] == "Test content"
        mock_exists.assert_called_once_with("test_video.mp4")
    
    @patch('os.path.exists', return_value=False)
    def test_get_video_info_file_not_found_raises_error(self, mock_exists):
        """Test that non-existent video file raises VideoGenerationError."""
        config = VideoConfig()
        generator = VideoGenerator(config)
        
        with pytest.raises(VideoGenerationError, match="Video file not found"):
            generator.get_video_info("nonexistent.mp4")
    
    @patch('builtins.open', side_effect=Exception("Read error"))
    @patch('os.path.exists', return_value=True)
    def test_get_video_info_read_error_raises_error(self, mock_exists, mock_file):
        """Test that read error raises VideoGenerationError."""
        config = VideoConfig()
        generator = VideoGenerator(config)
        
        with pytest.raises(VideoGenerationError, match="Failed to read video info"):
            generator.get_video_info("test_video.mp4")
    
    def test_cleanup_temp_files(self):
        """Test that cleanup_temp_files runs without error."""
        config = VideoConfig()
        generator = VideoGenerator(config)
        
        # Should not raise any exception
        generator.cleanup_temp_files()


class TestFactoryFunction:
    """Test cases for the create_video_generator factory function."""
    
    def test_create_video_generator_defaults(self):
        """Test factory function with default parameters."""
        generator = create_video_generator()
        
        assert generator.config.quality == "high"
        assert generator.config.duration == 60
        assert generator.config.output_path == "./output"
        assert generator.config.title == "Auto-generated Short"
    
    def test_create_video_generator_custom_params(self):
        """Test factory function with custom parameters."""
        generator = create_video_generator(quality="medium", duration=30)
        
        assert generator.config.quality == "medium"
        assert generator.config.duration == 30
        assert generator.config.output_path == "./output"
        assert generator.config.title == "Auto-generated Short"