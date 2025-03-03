# GitHub Repository Analyzer

![GitHub Repository Analyzer](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-red)

A powerful web-based tool for analyzing GitHub repositories, providing code quality insights, and suggesting improvements using AI-powered pattern detection.

## 🔍 Features

- **Repository Analysis**: Fetch and analyze repository metadata, commit history, and code files
- **Code Quality Assessment**: Evaluate code quality based on language-specific patterns and best practices
- **Visualization**: Interactive charts for commit history and code quality metrics
- **Improvement Suggestions**: Actionable recommendations to enhance code quality with example code
- **Multi-language Support**: Analyze Python, JavaScript, Java, and more

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/github-repo-analyzer.git
   cd github-repo-analyzer
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run main.py
   ```

4. Open your browser and navigate to `http://localhost:8501`

### Using GitHub Tokens (Optional)

For increased API rate limits, set your GitHub personal access token as an environment variable:

```bash
export GITHUB_TOKEN=your_token_here
```

## 🔧 Project Structure

```
├── .streamlit/                # Streamlit configuration
│   └── config.toml            # Streamlit server and theme settings
├── main.py                    # Application entry point
├── github_api.py              # GitHub API integration
├── code_analysis.py           # Code quality analysis logic
├── visualization.py           # Data visualization components
├── utils.py                   # Utility functions
└── styles.css                 # Custom CSS styles
```

## 📊 How It Works

1. **Input a GitHub Repository URL**: Enter any public GitHub repository URL
2. **Select Analysis Options**: Choose file types, analysis depth, and other settings
3. **Analyze**: The tool fetches repository data from GitHub's API
4. **View Results**: Navigate through tabs to see commit history, code quality metrics, and suggestions

## 🧠 Code Analysis Engine

The analysis engine uses a combination of:

- **Pattern matching**: Regular expressions to detect common code issues
- **Language-specific rules**: Custom logic for different programming languages
- **Simulated AI analysis**: Heuristic-based quality assessment

### Analysis Types

- **Basic**: Quick pattern-based scan (fastest)
- **Standard**: Comprehensive code structure analysis (recommended)
- **Deep**: Detailed analysis with more intensive checks

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [Streamlit](https://streamlit.io/) for the interactive web framework
- [Plotly](https://plotly.com/python/) for data visualization
- [GitHub API](https://docs.github.com/en/rest) for repository data access