# Installation Guide

This document provides detailed instructions for setting up the GitHub Repository Analyzer on different platforms.

## Local Installation

### Prerequisites

- Python 3.11 or higher
- Git

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/github-repo-analyzer.git
   cd github-repo-analyzer
   ```

2. Install required packages:

   ```bash
   pip install streamlit pandas plotly requests transformers torch
   ```

3. Run the application:

   ```bash
   streamlit run main.py
   ```

4. The application should open in your default web browser at `http://localhost:8501`

## Replit Installation

1. Create a new Replit project using the "Import from GitHub" option
2. Enter the repository URL: `https://github.com/yourusername/github-repo-analyzer.git`
3. Replit will automatically install dependencies
4. Click "Run" to start the application

## Hugging Face Spaces Installation

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Select "Streamlit" as the SDK
4. Choose a name and visibility setting
5. Link your GitHub repository or upload files directly
6. Hugging Face will automatically deploy your application

## Environment Variables

For better GitHub API rate limits, set up a GitHub token as an environment variable:

### Local

```bash
export GITHUB_TOKEN=your_github_token
```

### Replit

1. Go to the Secrets tab in your Replit project
2. Add a new secret with key `GITHUB_TOKEN` and your token as value

### Hugging Face Spaces

1. Go to Settings > Repository Secrets
2. Add a new secret with key `GITHUB_TOKEN` and your token as value

## Troubleshooting

### Common Issues

1. **GitHub API Rate Limiting**

   - Error message: "API rate limit exceeded"
   - Solution: Set up a GitHub token as described above

2. **Package Dependencies**

   - Error message: "ModuleNotFoundError: No module named X"
   - Solution: Ensure all required packages are installed: `pip install streamlit pandas plotly requests transformers torch`

3. **File Permissions**
   - Error message: "Permission denied"
   - Solution: Check that you have appropriate permissions to read/write in the project directory

### Getting Help

If you encounter issues not covered here, please:

1. Check the [GitHub Issues](https://github.com/yourusername/github-repo-analyzer/issues) page
2. Create a new issue with detailed information about your problem
