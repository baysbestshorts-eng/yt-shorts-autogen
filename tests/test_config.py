"""Tests for the configuration module."""

import os
import pytest
from unittest.mock import patch
from config import Config, ConfigError


class TestConfig:
    """Test cases for the Config class."""
    
    def test_config_loads_env_file(self, tmp_path):
        """Test that Config can load from a specific env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("YOUTUBE_API_KEY=test_key\nYOUTUBE_CLIENT_ID=test_id\nYOUTUBE_CLIENT_SECRET=test_secret")
        
        config = Config(str(env_file))
        
        assert config.youtube_api_key == "test_key"
        assert config.youtube_client_id == "test_id"
        assert config.youtube_client_secret == "test_secret"
    
    @patch.dict(os.environ, {
        'YOUTUBE_API_KEY': 'env_key',
        'YOUTUBE_CLIENT_ID': 'env_id',
        'YOUTUBE_CLIENT_SECRET': 'env_secret'
    })
    def test_config_loads_from_environment(self):
        """Test that Config can load from environment variables."""
        config = Config()
        
        assert config.youtube_api_key == "env_key"
        assert config.youtube_client_id == "env_id"
        assert config.youtube_client_secret == "env_secret"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_youtube_api_key_raises_error(self):
        """Test that missing YouTube API key raises ConfigError."""
        config = Config()
        
        with pytest.raises(ConfigError, match="YOUTUBE_API_KEY environment variable is required"):
            config.youtube_api_key
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_youtube_client_id_raises_error(self):
        """Test that missing YouTube client ID raises ConfigError."""
        config = Config()
        
        with pytest.raises(ConfigError, match="YOUTUBE_CLIENT_ID environment variable is required"):
            config.youtube_client_id
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_youtube_client_secret_raises_error(self):
        """Test that missing YouTube client secret raises ConfigError."""
        config = Config()
        
        with pytest.raises(ConfigError, match="YOUTUBE_CLIENT_SECRET environment variable is required"):
            config.youtube_client_secret
    
    @patch.dict(os.environ, {}, clear=True)
    def test_default_values(self):
        """Test that default values are used when environment variables are not set."""
        config = Config()
        
        assert config.output_dir == "./output"
        assert config.video_quality == "high"
        assert config.max_duration == 60
        assert config.debug is False
        assert config.log_level == "INFO"
    
    @patch.dict(os.environ, {
        'OUTPUT_DIR': '/custom/output',
        'VIDEO_QUALITY': 'medium',
        'MAX_DURATION': '30',
        'DEBUG': 'true',
        'LOG_LEVEL': 'debug'
    })
    def test_custom_values(self):
        """Test that custom environment values are used correctly."""
        config = Config()
        
        assert config.output_dir == "/custom/output"
        assert config.video_quality == "medium"
        assert config.max_duration == 30
        assert config.debug is True
        assert config.log_level == "DEBUG"
    
    @patch.dict(os.environ, {'MAX_DURATION': 'invalid'})
    def test_invalid_max_duration_uses_default(self):
        """Test that invalid max_duration value falls back to default."""
        config = Config()
        
        assert config.max_duration == 60
    
    @patch.dict(os.environ, {'DEBUG': 'yes'})
    def test_debug_boolean_variations(self):
        """Test that various boolean values for DEBUG are handled correctly."""
        config = Config()
        assert config.debug is True
        
        with patch.dict(os.environ, {'DEBUG': '1'}):
            config = Config()
            assert config.debug is True
        
        with patch.dict(os.environ, {'DEBUG': 'false'}):
            config = Config()
            assert config.debug is False
        
        with patch.dict(os.environ, {'DEBUG': '0'}):
            config = Config()
            assert config.debug is False