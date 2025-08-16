"""
AI YouTube Shorts Generator Modules
"""

from .scraper import ContentScraper, ScrapedContent
from .rewriter_tts import ContentRewriter, TextToSpeech, RewrittenContent
from .image_generator import ImageGenerator, GeneratedImage
from .video_editor import VideoEditor, VideoSegment, VideoMetadata
from .uploader import YouTubeUploader
from .voice_changer import VoiceChanger
from .utils import (
    setup_logging, validate_config, sanitize_filename, 
    generate_content_hash, ensure_directory, clean_text,
    extract_keywords, retry_with_backoff, create_timestamp
)

__version__ = "1.0.0"
__author__ = "AI YouTube Shorts Generator"

__all__ = [
    'ContentScraper', 'ScrapedContent',
    'ContentRewriter', 'TextToSpeech', 'RewrittenContent',
    'ImageGenerator', 'GeneratedImage',
    'VideoEditor', 'VideoSegment', 'VideoMetadata',
    'YouTubeUploader',
    'VoiceChanger',
    'setup_logging', 'validate_config', 'sanitize_filename',
    'generate_content_hash', 'ensure_directory', 'clean_text',
    'extract_keywords', 'retry_with_backoff', 'create_timestamp'
]