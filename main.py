#!/usr/bin/env python3
"""
AI YouTube Shorts Generator
Main entry point for the automated YouTube Shorts generation system.
"""

import os
import sys
import logging
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from scraper import ContentScraper
from rewriter_tts import ContentRewriter, TextToSpeech
from image_generator import ImageGenerator
from video_editor import VideoEditor
from uploader import YouTubeUploader
from voice_changer import VoiceChanger
from utils import setup_logging, validate_config

def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent / 'config.yaml'
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logging.error(f"Error parsing configuration file: {e}")
        sys.exit(1)

def main():
    """Main execution function"""
    # Load environment variables
    load_dotenv()
    
    # Load configuration
    config = load_config()
    
    # Setup logging
    setup_logging(config.get('logging', {}))
    
    # Validate configuration
    if not validate_config(config):
        logging.error("Configuration validation failed")
        sys.exit(1)
    
    logging.info("Starting AI YouTube Shorts Generator")
    
    try:
        # Initialize modules
        scraper = ContentScraper(config['scraper'])
        rewriter = ContentRewriter(config['rewriter'])
        tts = TextToSpeech(config['tts'])
        image_gen = ImageGenerator(config['image_generator'])
        video_editor = VideoEditor(config['video_editor'])
        voice_changer = VoiceChanger(config['voice_changer'])
        uploader = YouTubeUploader(config['uploader'])
        
        # Generate content pipeline
        logging.info("Step 1: Scraping content...")
        raw_content = scraper.scrape_content()
        
        logging.info("Step 2: Rewriting content...")
        rewritten_content = rewriter.rewrite_content(raw_content)
        
        logging.info("Step 3: Generating speech...")
        audio_file = tts.generate_speech(rewritten_content)
        
        logging.info("Step 4: Applying voice effects...")
        processed_audio = voice_changer.process_audio(audio_file)
        
        logging.info("Step 5: Generating images...")
        images = image_gen.generate_images(rewritten_content)
        
        logging.info("Step 6: Creating video...")
        video_file = video_editor.create_video(images, processed_audio, rewritten_content)
        
        logging.info("Step 7: Uploading to YouTube...")
        video_url = uploader.upload_video(video_file, rewritten_content)
        
        logging.info(f"Video successfully uploaded: {video_url}")
        
    except Exception as e:
        logging.error(f"Error in main pipeline: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
