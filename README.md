# GitHub Repository Analyzer

A powerful Streamlit-based tool for analyzing GitHub repositories, providing code quality insights, and suggesting improvements using pattern-based detection.

[![Follow me on HF](https://huggingface.co/datasets/huggingface/badges/resolve/main/follow-me-on-HF-xl-dark.svg)](https://huggingface.co/Chunte)

[![Open in Spaces](https://huggingface.co/datasets/huggingface/badges/resolve/main/open-in-hf-spaces-xl.svg)](https://huggingface.co/spaces)

![GitHub Repository Analyzer](generated-icon.png)

## 📋 Overview

GitHub Repository Analyzer is a web application that helps developers and teams analyze and improve their code quality. The tool provides:

1. **Code Quality Analysis**: Pattern-based detection of common code issues and anti-patterns
2. **Visualization**: Interactive graphs and charts for code metrics and commit history
3. **Improvement Suggestions**: Actionable recommendations with example code fixes
4. **Repository Insights**: Overview of repository activity, contributors, and structure

## 🎯 Features

- **Repository Analysis**: Load any public GitHub repository via URL
- **File Filtering**: Choose specific file types to analyze
- **Customizable Analysis Depth**: Basic, Standard, or Deep analysis options
- **Code Issue Detection**: Identify coding problems like:
  - Long functions
  - Complex code structures
  - Inconsistent naming
  - Missing documentation
  - Potential security issues
  - Performance bottlenecks
- **Visual Reports**: Clean, interactive visualizations using Plotly
- **Improvement Suggestions**: Practical code examples showing how to fix issues

## 🚀 Getting Started

### Online Demo

Try the application online at:
- [Replit](https://github-repo-analyzer.replit.app)
- [Hugging Face Spaces](https://huggingface.co/spaces/username/github-repo-analyzer)

### Local Installation

See the [Installation Guide](INSTALLATION.md) for detailed setup instructions.

Quick start:
```bash
# Clone repository
git clone https://github.com/yourusername/github-repo-analyzer.git
cd github-repo-analyzer

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run main.py
```

## 📊 Usage

1. Enter a GitHub repository URL (e.g., `https://github.com/streamlit/streamlit`)
2. Configure analysis settings:
   - Select file types to analyze (Python, JavaScript, etc.)
   - Set analysis depth (Basic, Standard, Deep)
   - Set maximum files to analyze
3. Click "Analyze Repository"
4. Explore the results across different tabs:
   - Repository Overview
   - Code Quality Analysis
   - Commit History
   - Improvement Suggestions

### Screenshots

*Screenshots coming soon*

## 🧠 How It Works

GitHub Repository Analyzer uses a combination of:

1. **GitHub API Integration**: Fetches repository metadata, commit history, and file contents using REST API
2. **Pattern Analysis**: Uses regular expressions and language-specific rules to detect code issues
3. **Visualization Engine**: Transforms analysis data into interactive charts
4. **Recommendation System**: Generates tailored improvement suggestions based on detected issues

## 🌟 Use Cases

- **Code Reviews**: Automate the initial code review process and focus human reviewers on complex issues
- **Technical Debt**: Identify areas of code with the highest technical debt for refactoring
- **Onboarding**: Help new team members understand code quality standards
- **Continuous Improvement**: Regular analysis to track code quality trends over time

## 🔒 Privacy & Security

- Only public repositories can be analyzed
- No code is stored or saved outside of your browser session
- Analysis happens in real-time without saving repository content
- GitHub API token is optional and never stored

## 🛠️ Technical Details

Built with:
- [Streamlit](https://streamlit.io) - Web application framework
- [Plotly](https://plotly.com) - Interactive visualizations
- [GitHub API](https://docs.github.com/en/rest) - Repository access
- Pattern-based code analysis

## 📄 Documentation

- [Installation Guide](INSTALLATION.md) - Setup instructions
- [Deployment Guide](DEPLOYMENT.md) - Hosting options
- [Contributing Guide](CONTRIBUTING.md) - Contribution guidelines

## 🤝 Contributing

Contributions are welcome! Please read the [Contributing Guide](CONTRIBUTING.md) for details on how to submit pull requests, report issues, and suggest improvements.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- The Streamlit team for creating an amazing framework for data applications
- GitHub for providing a comprehensive API
- All contributors and users of this tool

---

Made with ❤️ by Canstralian/Chemically Motivated Solutions

*This project is not affiliated with GitHub and is provided as-is under the MIT License*add emojis to make the read more engaging and then add some more relevant, working badges for the repo on github, possibly tied in with the .yml workflow
