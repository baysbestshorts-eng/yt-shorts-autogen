"""Video generation pipeline for creating YouTube Shorts."""

import os
import time
from typing import Dict, List, Optional
from dataclasses import dataclass


class VideoGenerationError(Exception):
    """Custom exception for video generation errors."""
    pass


@dataclass
class VideoConfig:
    """Configuration for video generation."""
    duration: int = 60  # seconds
    quality: str = "high"
    output_path: str = "./output"
    title: str = "Generated Video"
    description: str = ""


class VideoGenerator:
    """Main class for generating videos for YouTube Shorts."""
    
    def __init__(self, config: VideoConfig):
        """Initialize the video generator with configuration."""
        self.config = config
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate the video configuration."""
        if self.config.duration <= 0:
            raise VideoGenerationError("Duration must be positive")
        
        if self.config.duration > 60:
            raise VideoGenerationError("Duration cannot exceed 60 seconds for YouTube Shorts")
        
        if self.config.quality not in ["low", "medium", "high"]:
            raise VideoGenerationError("Quality must be 'low', 'medium', or 'high'")
        
        if not self.config.title.strip():
            raise VideoGenerationError("Title cannot be empty")
    
    def generate_video(self, content: Dict[str, str]) -> str:
        """
        Generate a video with the given content.
        
        Args:
            content: Dictionary containing video content (text, images, etc.)
            
        Returns:
            str: Path to the generated video file
            
        Raises:
            VideoGenerationError: If video generation fails
        """
        if not content:
            raise VideoGenerationError("Content cannot be empty")
        
        if "text" not in content:
            raise VideoGenerationError("Content must include 'text' field")
        
        # Simulate video generation process
        output_dir = self.config.output_path
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a unique filename
        timestamp = int(time.time())
        filename = f"video_{timestamp}.mp4"
        output_file = os.path.join(output_dir, filename)
        
        # Simulate processing time
        time.sleep(0.1)
        
        # Create a dummy video file for demonstration
        with open(output_file, 'w') as f:
            f.write(f"# Generated Video File\n")
            f.write(f"Title: {self.config.title}\n")
            f.write(f"Duration: {self.config.duration}s\n")
            f.write(f"Quality: {self.config.quality}\n")
            f.write(f"Content: {content['text']}\n")
        
        return output_file
    
    def get_video_info(self, video_path: str) -> Dict[str, str]:
        """
        Get information about a generated video.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dict containing video information
            
        Raises:
            VideoGenerationError: If video file doesn't exist or is invalid
        """
        if not os.path.exists(video_path):
            raise VideoGenerationError(f"Video file not found: {video_path}")
        
        try:
            with open(video_path, 'r') as f:
                content = f.read()
            
            # Parse the dummy video file content
            info = {}
            for line in content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            
            return info
        except Exception as e:
            raise VideoGenerationError(f"Failed to read video info: {e}")
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary files created during video generation."""
        # Simulate cleanup process
        pass


def create_video_generator(quality: str = "high", duration: int = 60) -> VideoGenerator:
    """Factory function to create a video generator with common settings."""
    config = VideoConfig(
        duration=duration,
        quality=quality,
        output_path="./output",
        title="Auto-generated Short"
    )
    return VideoGenerator(config)