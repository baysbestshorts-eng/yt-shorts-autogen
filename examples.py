#!/usr/bin/env python3
"""
Example script demonstrating how to use the YouTube Shorts Auto-Generator.

This script shows various usage patterns and can be used for testing
the functionality without requiring actual YouTube API credentials.
"""

import os
import sys
import logging
from datetime import datetime

# Add the current directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import YouTubeShortsWorkflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_video_generation_only():
    """Example: Generate video without uploading to YouTube."""
    print("\n" + "="*50)
    print("EXAMPLE 1: Video Generation Only")
    print("="*50)
    
    workflow = YouTubeShortsWorkflow()
    
    result = workflow.run_workflow(
        title="Example Video - No Upload",
        description="This is an example video generated without uploading to YouTube.",
        tags=["example", "test", "automation"],
        output_dir="examples",
        auto_upload=False  # Don't upload to YouTube
    )
    
    print(f"Result: {'Success' if result is None else 'Failed'}")
    return result is None


def example_with_custom_settings():
    """Example: Generate video with custom settings."""
    print("\n" + "="*50)
    print("EXAMPLE 2: Custom Settings (No Upload)")
    print("="*50)
    
    workflow = YouTubeShortsWorkflow()
    
    # Custom title with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = f"Custom Video - {timestamp}"
    
    result = workflow.run_workflow(
        title=title,
        description=f"Custom video generated at {timestamp} with specific settings.",
        tags=["custom", "timestamp", "demo", "youtube-shorts"],
        output_dir="custom_output",
        privacy_status="private",  # This would be used if upload was enabled
        auto_upload=False  # Don't upload to YouTube
    )
    
    print(f"Result: {'Success' if result is None else 'Failed'}")
    return result is None


def example_upload_simulation():
    """Example: Show what upload would look like (without actual upload)."""
    print("\n" + "="*50)
    print("EXAMPLE 3: Upload Simulation")
    print("="*50)
    
    # This demonstrates what would happen with upload enabled
    # but we'll keep auto_upload=False for safety
    
    print("This example shows what would happen with YouTube upload enabled:")
    print("1. Video would be generated")
    print("2. YouTube API authentication would occur")
    print("3. Video would be uploaded with metadata")
    print("4. Video ID and URL would be returned")
    
    workflow = YouTubeShortsWorkflow()
    
    result = workflow.run_workflow(
        title="Upload Simulation Video",
        description="This video demonstrates the upload workflow (without actual upload).",
        tags=["simulation", "upload", "demo"],
        output_dir="upload_simulation",
        privacy_status="private",
        auto_upload=False  # Keep false for safety
    )
    
    print(f"Video generation result: {'Success' if result is None else 'Failed'}")
    print("Note: To enable actual uploads, set auto_upload=True and configure YouTube API credentials")
    
    return result is None


def cleanup_example_files():
    """Clean up example files created during testing."""
    import shutil
    
    print("\n" + "="*50)
    print("CLEANUP")
    print("="*50)
    
    directories_to_remove = ["examples", "custom_output", "upload_simulation"]
    
    for directory in directories_to_remove:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
                print(f"Removed directory: {directory}")
            except Exception as e:
                print(f"Failed to remove {directory}: {e}")
        else:
            print(f"Directory {directory} doesn't exist (nothing to clean)")


def main():
    """Run all examples."""
    print("YouTube Shorts Auto-Generator - Examples")
    print("="*60)
    
    success_count = 0
    total_examples = 3
    
    try:
        # Run examples
        if example_video_generation_only():
            success_count += 1
        
        if example_with_custom_settings():
            success_count += 1
        
        if example_upload_simulation():
            success_count += 1
        
        # Show results
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        print(f"Successful examples: {success_count}/{total_examples}")
        
        if success_count == total_examples:
            print("✅ All examples completed successfully!")
        else:
            print("⚠️  Some examples failed. Check the logs above.")
        
        # Ask about cleanup
        response = input("\nWould you like to clean up example files? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            cleanup_example_files()
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()