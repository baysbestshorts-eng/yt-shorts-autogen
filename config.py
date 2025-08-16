"""Configuration module for loading environment variables and settings."""

import os
from typing import Optional
from dotenv import load_dotenv


class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass


class Config:
    """Configuration class for managing environment variables and settings."""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration by loading environment variables."""
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
    
    @property
    def youtube_api_key(self) -> str:
        """Get YouTube API key from environment."""
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            raise ConfigError("YOUTUBE_API_KEY environment variable is required")
        return api_key
    
    @property
    def youtube_client_id(self) -> str:
        """Get YouTube client ID from environment."""
        client_id = os.getenv('YOUTUBE_CLIENT_ID')
        if not client_id:
            raise ConfigError("YOUTUBE_CLIENT_ID environment variable is required")
        return client_id
    
    @property
    def youtube_client_secret(self) -> str:
        """Get YouTube client secret from environment."""
        client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
        if not client_secret:
            raise ConfigError("YOUTUBE_CLIENT_SECRET environment variable is required")
        return client_secret
    
    @property
    def output_dir(self) -> str:
        """Get output directory, defaults to './output'."""
        return os.getenv('OUTPUT_DIR', './output')
    
    @property
    def video_quality(self) -> str:
        """Get video quality setting, defaults to 'high'."""
        return os.getenv('VIDEO_QUALITY', 'high')
    
    @property
    def max_duration(self) -> int:
        """Get maximum video duration in seconds, defaults to 60."""
        try:
            return int(os.getenv('MAX_DURATION', '60'))
        except ValueError:
            return 60
    
    @property
    def debug(self) -> bool:
        """Get debug mode setting, defaults to False."""
        return os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')
    
    @property
    def log_level(self) -> str:
        """Get log level, defaults to 'INFO'."""
        return os.getenv('LOG_LEVEL', 'INFO').upper()