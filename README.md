# YT Shorts AutoGen

A Python application for automatically generating and uploading YouTube Shorts videos.

## Features

- **Video Generation Pipeline**: Create short videos with configurable duration, quality, and content
- **YouTube Upload Integration**: Upload videos to YouTube with proper metadata and privacy settings
- **Environment Configuration**: Secure configuration management with environment variables
- **Comprehensive Testing**: Full test coverage with pytest

## Installation

1. Clone the repository:
```bash
git clone https://github.com/baysbestshorts-eng/yt-shorts-autogen.git
cd yt-shorts-autogen
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your YouTube API credentials
```

## Configuration

Copy `.env.example` to `.env` and configure the following variables:

```bash
# YouTube API Configuration
YOUTUBE_API_KEY=your_youtube_api_key_here
YOUTUBE_CLIENT_ID=your_client_id_here
YOUTUBE_CLIENT_SECRET=your_client_secret_here

# Video Generation Settings
OUTPUT_DIR=./output
VIDEO_QUALITY=high
MAX_DURATION=60

# Optional Settings
DEBUG=false
LOG_LEVEL=INFO
```

## Usage

### Basic Video Generation

```python
from video_generator import create_video_generator
from config import Config

# Create video generator
generator = create_video_generator(quality="high", duration=60)

# Generate a video
content = {"text": "This is my YouTube Short content!"}
video_path = generator.generate_video(content)
print(f"Video generated: {video_path}")
```

### YouTube Upload

```python
from youtube_uploader import create_uploader_from_config, VideoMetadata
from config import Config

# Load configuration
config = Config()

# Create uploader and authenticate
uploader = create_uploader_from_config(config)
uploader.authenticate()

# Upload video
metadata = VideoMetadata(
    title="My Awesome Short",
    description="Generated with YT Shorts AutoGen",
    tags=["shorts", "auto-generated"],
    privacy_status="public"
)

result = uploader.upload_video(video_path, metadata)
print(f"Video uploaded: {result['video_id']}")
```

## Testing

This project includes comprehensive pytest-style tests covering:

### Running Tests

Run all tests:
```bash
pytest tests/ -v
```

Run tests with coverage:
```bash
pytest tests/ --cov=. --cov-report=term-missing
```

Run specific test files:
```bash
pytest tests/test_video_generator.py -v
pytest tests/test_youtube_uploader.py -v
pytest tests/test_config.py -v
```

### Test Categories

#### 1. Configuration Tests (`test_config.py`)
Tests environment variable loading and configuration management:

```bash
$ pytest tests/test_config.py -v
================================================= test session starts ==================================================
tests/test_config.py::TestConfig::test_config_loads_env_file PASSED                                              [  1%]
tests/test_config.py::TestConfig::test_config_loads_from_environment PASSED                                      [  3%]
tests/test_config.py::TestConfig::test_missing_youtube_api_key_raises_error PASSED                               [  5%]
tests/test_config.py::TestConfig::test_missing_youtube_client_id_raises_error PASSED                             [  7%]
tests/test_config.py::TestConfig::test_missing_youtube_client_secret_raises_error PASSED                         [  9%]
tests/test_config.py::TestConfig::test_default_values PASSED                                                     [ 11%]
tests/test_config.py::TestConfig::test_custom_values PASSED                                                      [ 13%]
tests/test_config.py::TestConfig::test_invalid_max_duration_uses_default PASSED                                  [ 15%]
tests/test_config.py::TestConfig::test_debug_boolean_variations PASSED                                           [ 17%]
```

#### 2. Video Generator Tests (`test_video_generator.py`)
Tests video generation pipeline with happy path and error cases:

```bash
$ pytest tests/test_video_generator.py -v
================================================= test session starts ==================================================
tests/test_video_generator.py::TestVideoConfig::test_default_values PASSED                                       [ 19%]
tests/test_video_generator.py::TestVideoConfig::test_custom_values PASSED                                        [ 21%]
tests/test_video_generator.py::TestVideoGenerator::test_valid_config_initialization PASSED                       [ 23%]
tests/test_video_generator.py::TestVideoGenerator::test_invalid_duration_zero_raises_error PASSED                [ 25%]
tests/test_video_generator.py::TestVideoGenerator::test_invalid_duration_negative_raises_error PASSED            [ 26%]
tests/test_video_generator.py::TestVideoGenerator::test_invalid_duration_too_long_raises_error PASSED            [ 28%]
tests/test_video_generator.py::TestVideoGenerator::test_invalid_quality_raises_error PASSED                      [ 30%]
tests/test_video_generator.py::TestVideoGenerator::test_empty_title_raises_error PASSED                          [ 32%]
tests/test_video_generator.py::TestVideoGenerator::test_whitespace_title_raises_error PASSED                     [ 34%]
tests/test_video_generator.py::TestVideoGenerator::test_generate_video_success PASSED                            [ 36%]
tests/test_video_generator.py::TestVideoGenerator::test_generate_video_empty_content_raises_error PASSED         [ 38%]
tests/test_video_generator.py::TestVideoGenerator::test_generate_video_missing_text_raises_error PASSED          [ 40%]
tests/test_video_generator.py::TestVideoGenerator::test_get_video_info_success PASSED                            [ 42%]
tests/test_video_generator.py::TestVideoGenerator::test_get_video_info_file_not_found_raises_error PASSED        [ 44%]
tests/test_video_generator.py::TestVideoGenerator::test_get_video_info_read_error_raises_error PASSED            [ 46%]
tests/test_video_generator.py::TestVideoGenerator::test_cleanup_temp_files PASSED                                [ 48%]
tests/test_video_generator.py::TestFactoryFunction::test_create_video_generator_defaults PASSED                  [ 50%]
tests/test_video_generator.py::TestFactoryFunction::test_create_video_generator_custom_params PASSED             [ 51%]
```

#### 3. YouTube Uploader Tests (`test_youtube_uploader.py`)
Tests YouTube API integration with mocked API calls and error handling:

```bash
$ pytest tests/test_youtube_uploader.py -v
================================================= test session starts ==================================================
tests/test_youtube_uploader.py::TestVideoMetadata::test_default_values PASSED                                    [ 53%]
tests/test_youtube_uploader.py::TestVideoMetadata::test_custom_values PASSED                                     [ 55%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_valid_credentials_initialization PASSED                [ 57%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_empty_api_key_raises_error PASSED                      [ 59%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_empty_client_id_raises_error PASSED                    [ 61%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_empty_client_secret_raises_error PASSED                [ 63%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_authenticate_success PASSED                            [ 65%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_authenticate_missing_credentials_raises_error PASSED   [ 67%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_upload_video_success PASSED                            [ 69%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_upload_video_not_authenticated_raises_error PASSED     [ 71%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_upload_video_file_not_found_raises_error PASSED        [ 73%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_upload_video_empty_title_raises_error PASSED           [ 75%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_upload_video_invalid_privacy_status_raises_error PASSED [ 76%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_upload_video_empty_file_raises_error PASSED            [ 78%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_update_video_metadata_success PASSED                   [ 80%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_update_video_metadata_not_authenticated_raises_error PASSED [ 82%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_update_video_metadata_empty_video_id_raises_error PASSED [ 84%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_update_video_metadata_empty_title_raises_error PASSED  [ 86%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_get_video_status_success PASSED                        [ 88%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_get_video_status_not_authenticated_raises_error PASSED [ 90%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_get_video_status_empty_video_id_raises_error PASSED    [ 92%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_delete_video_success PASSED                            [ 94%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_delete_video_not_authenticated_raises_error PASSED     [ 96%]
tests/test_youtube_uploader.py::TestYouTubeUploader::test_delete_video_empty_video_id_raises_error PASSED        [ 98%]
tests/test_youtube_uploader.py::TestFactoryFunction::test_create_uploader_from_config PASSED                     [100%]
```

### Test Coverage

The test suite provides comprehensive coverage including:

- **Happy Path Testing**: Normal operation scenarios
- **Error Handling**: Invalid inputs, missing files, authentication failures
- **Edge Cases**: Boundary conditions, empty values, malformed data
- **Configuration Management**: Environment variable loading and validation
- **Mocked API Calls**: YouTube API interactions without real API calls

### Example Test Output

```bash
$ pytest tests/ -v --tb=short
================================================= test session starts ==================================================
platform linux -- Python 3.12.3, pytest-8.4.1, pluggy-1.6.0 -- /usr/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/yt-shorts-autogen/yt-shorts-autogen
plugins: mock-3.14.1
collected 52 items

tests/test_config.py::TestConfig::test_config_loads_env_file PASSED                                              [  1%]
tests/test_config.py::TestConfig::test_config_loads_from_environment PASSED                                      [  3%]
tests/test_config.py::TestConfig::test_missing_youtube_api_key_raises_error PASSED                               [  5%]
...
tests/test_youtube_uploader.py::TestFactoryFunction::test_create_uploader_from_config PASSED                     [100%]

================================================== 52 passed in 0.20s ==================================================
```

## Continuous Integration

The project includes a GitHub Actions CI workflow that:

- Tests against multiple Python versions (3.8, 3.9, 3.10, 3.11)
- Runs the full test suite
- Generates coverage reports
- Uploads coverage to Codecov

The CI workflow runs on:
- Push to `main` and `develop` branches
- Pull requests to `main` branch

## Development

### Adding New Tests

When adding new functionality, ensure you include tests:

1. **Unit Tests**: Test individual functions and methods
2. **Integration Tests**: Test component interactions
3. **Error Handling**: Test all error conditions
4. **Edge Cases**: Test boundary conditions

### Test Structure

```
tests/
├── __init__.py
├── test_config.py          # Configuration and environment variable tests
├── test_video_generator.py # Video generation pipeline tests
└── test_youtube_uploader.py # YouTube API integration tests
```

### Running Specific Test Categories

```bash
# Test configuration management
pytest tests/test_config.py -k "test_missing" -v

# Test video generation happy path
pytest tests/test_video_generator.py -k "test_generate_video_success" -v

# Test YouTube upload error handling
pytest tests/test_youtube_uploader.py -k "raises_error" -v
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `pytest tests/ -v`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.