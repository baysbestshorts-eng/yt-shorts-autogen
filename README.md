# YouTube Shorts Auto-Generator

An automated workflow for generating and uploading YouTube Shorts videos using the YouTube Data API v3.

## Features

- **Automated Video Generation**: Generate video content programmatically
- **YouTube Upload Integration**: Automatically upload videos to YouTube after generation
- **Secure Authentication**: Support for OAuth2 authentication with secure credential handling
- **Flexible Privacy Settings**: Control video privacy (private, public, unlisted)
- **Command Line Interface**: Easy-to-use CLI for running workflows
- **Error Handling & Logging**: Comprehensive error handling and logging throughout the process

## Prerequisites

- Python 3.7 or higher
- YouTube Data API v3 access
- Google Cloud Project with YouTube Data API enabled

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/baysbestshorts-eng/yt-shorts-autogen.git
   cd yt-shorts-autogen
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## YouTube API Setup

### 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3:
   - Navigate to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click on it and press "Enable"

### 2. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Configure the OAuth consent screen if prompted
4. Choose "Desktop application" as the application type
5. Download the credentials JSON file and save it as `client_secrets.json` in the project root

### 3. Set up Authentication (Choose one method)

#### Method A: Using client_secrets.json file (Recommended for local development)

Place the downloaded `client_secrets.json` file in the project root directory.

#### Method B: Using Environment Variables (Recommended for production/CI)

Set the following environment variables:

```bash
export YOUTUBE_CLIENT_ID="your_client_id_here"
export YOUTUBE_CLIENT_SECRET="your_client_secret_here"
```

For GitHub Actions, add these as repository secrets:
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`

## Usage

### Basic Usage

```bash
python main.py --title "My Awesome Short" --description "This is an amazing YouTube Short!" --tags "shorts,awesome,cool"
```

### Advanced Usage

```bash
# Generate video without uploading
python main.py --title "Test Video" --description "Test description" --tags "test" --no-upload

# Upload with public privacy
python main.py --title "Public Video" --description "Public description" --tags "public,video" --privacy public

# Custom output directory
python main.py --title "Custom Video" --description "Custom description" --tags "custom" --output-dir /path/to/output
```

### Command Line Options

- `--title`: Video title (required)
- `--description`: Video description (required)
- `--tags`: Comma-separated list of video tags (required)
- `--output-dir`: Directory to save generated videos (default: "output")
- `--privacy`: YouTube privacy status - "private", "public", or "unlisted" (default: "private")
- `--no-upload`: Generate video only, don't upload to YouTube

## Direct Upload Usage

You can also use the upload functionality directly:

```bash
python upload_to_youtube.py /path/to/video.mp4 "Video Title" "Video Description" "tag1,tag2,tag3"
```

## GitHub Actions Integration

To use this in GitHub Actions, create a workflow file (e.g., `.github/workflows/upload-video.yml`):

```yaml
name: Generate and Upload YouTube Short

on:
  workflow_dispatch:
    inputs:
      title:
        description: 'Video Title'
        required: true
      description:
        description: 'Video Description'
        required: true
      tags:
        description: 'Video Tags (comma-separated)'
        required: true

jobs:
  generate-and-upload:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run workflow
      env:
        YOUTUBE_CLIENT_ID: ${{ secrets.YOUTUBE_CLIENT_ID }}
        YOUTUBE_CLIENT_SECRET: ${{ secrets.YOUTUBE_CLIENT_SECRET }}
      run: |
        python main.py --title "${{ github.event.inputs.title }}" --description "${{ github.event.inputs.description }}" --tags "${{ github.event.inputs.tags }}" --privacy private
```

## Security Considerations

- **Never commit `client_secrets.json`** to version control
- **Never commit `token.pickle`** to version control
- Use environment variables or GitHub Secrets for production deployments
- Default privacy setting is "private" for safety
- Review YouTube's API quotas and terms of service

## File Structure

```
yt-shorts-autogen/
├── main.py                 # Main workflow orchestrator
├── upload_to_youtube.py    # YouTube upload module
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── client_secrets.json    # OAuth credentials (not in repo)
└── token.pickle          # Authentication token (not in repo)
```

## Error Handling

The application includes comprehensive error handling:

- **Authentication errors**: Clear messages when credentials are missing or invalid
- **Upload errors**: Automatic retry logic for transient failures
- **File errors**: Validation of video file existence and permissions
- **API errors**: Proper handling of YouTube API rate limits and errors

## Logging

All operations are logged with appropriate levels:
- `INFO`: Normal operation progress
- `WARNING`: Recoverable issues (e.g., retries)
- `ERROR`: Failures that prevent operation completion

## Troubleshooting

### Common Issues

1. **"No authentication method available"**
   - Ensure `client_secrets.json` exists OR environment variables are set
   - Verify the JSON file format is correct

2. **"Video file not found"**
   - Check the video file path
   - Ensure the file exists and is readable

3. **"API quota exceeded"**
   - YouTube API has daily quotas
   - Wait for the quota to reset or request a quota increase

4. **"Authentication required"**
   - Delete `token.pickle` and re-authenticate
   - Check that OAuth consent screen is properly configured

### Getting Help

- Check the logs for detailed error messages
- Verify your Google Cloud Project settings
- Ensure YouTube Data API v3 is enabled
- Review YouTube API documentation for additional guidance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Disclaimer

This tool is for educational and legitimate use only. Ensure compliance with YouTube's Terms of Service and Community Guidelines when using this tool.