"""
Utility functions for the AI YouTube Shorts Generator
"""

import os
import logging
import logging.handlers
import json
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml

def setup_logging(config: Dict[str, Any]) -> None:
    """
    Set up logging configuration
    
    Args:
        config: Logging configuration dictionary
    """
    log_level = getattr(logging, config.get('level', 'INFO').upper())
    log_format = config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = config.get('file', 'logs/app.log')
    max_size = config.get('max_size', '10MB')
    backup_count = config.get('backup_count', 5)
    
    # Create logs directory if it doesn't exist
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert max_size to bytes
    size_multipliers = {'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
    max_bytes = int(max_size[:-2]) * size_multipliers.get(max_size[-2:], 1024**2)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
        ]
    )

def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration file structure and required fields
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    required_sections = [
        'scraper', 'rewriter', 'tts', 'image_generator', 
        'video_editor', 'uploader', 'voice_changer'
    ]
    
    for section in required_sections:
        if section not in config:
            logging.error(f"Missing required configuration section: {section}")
            return False
    
    # Validate specific configurations
    if not validate_api_keys():
        return False
    
    return True

def validate_api_keys() -> bool:
    """
    Validate that required API keys are present in environment
    
    Returns:
        bool: True if all required keys are present, False otherwise
    """
    required_keys = [
        'OPENAI_API_KEY',
        'YOUTUBE_API_KEY',
        'YOUTUBE_CLIENT_ID',
        'YOUTUBE_CLIENT_SECRET'
    ]
    
    missing_keys = []
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        logging.error(f"Missing required environment variables: {', '.join(missing_keys)}")
        return False
    
    return True

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename

def generate_content_hash(content: str) -> str:
    """
    Generate a hash for content to avoid duplicates
    
    Args:
        content: Content string to hash
        
    Returns:
        str: MD5 hash of the content
    """
    return hashlib.md5(content.encode()).hexdigest()

def ensure_directory(path: str) -> None:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        path: Directory path to create
    """
    Path(path).mkdir(parents=True, exist_ok=True)

def load_json_file(file_path: str) -> Optional[Dict]:
    """
    Load JSON file safely
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dict or None: Loaded JSON data or None if error
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading JSON file {file_path}: {e}")
        return None

def save_json_file(data: Dict, file_path: str) -> bool:
    """
    Save data to JSON file safely
    
    Args:
        data: Data to save
        file_path: Path to save JSON file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ensure_directory(os.path.dirname(file_path))
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2, default=str)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON file {file_path}: {e}")
        return False

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{int(minutes)}m {remaining_seconds:.1f}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{int(hours)}h {int(remaining_minutes)}m"

def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and invalid characters
    
    Args:
        text: Text to clean
        
    Returns:
        str: Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\.,!?;:()-]', '', text)
    return text

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text for tagging
    
    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List[str]: List of extracted keywords
    """
    # Simple keyword extraction - could be enhanced with NLP
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter out common stop words
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 
        'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 
        'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 
        'did', 'she', 'use', 'way', 'will', 'with', 'this', 'that', 'they',
        'have', 'from', 'been', 'were', 'said', 'what', 'when', 'where'
    }
    
    keywords = [word for word in words if word not in stop_words]
    
    # Count frequency and return most common
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:max_keywords]]

def get_file_size(file_path: str) -> str:
    """
    Get human-readable file size
    
    Args:
        file_path: Path to file
        
    Returns:
        str: Formatted file size
    """
    try:
        size = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except OSError:
        return "Unknown"

def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """
    Retry function with exponential backoff
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        base_delay: Base delay in seconds
        
    Returns:
        Result of function or raises last exception
    """
    import time
    
    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                logging.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                time.sleep(delay)
            else:
                logging.error(f"All {max_retries + 1} attempts failed")
    
    raise last_exception

def create_timestamp() -> str:
    """
    Create timestamp string for file naming
    
    Returns:
        str: Timestamp in YYYYMMDD_HHMMSS format
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def is_valid_url(url: str) -> bool:
    """
    Check if string is a valid URL
    
    Args:
        url: URL string to validate
        
    Returns:
        bool: True if valid URL, False otherwise
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None