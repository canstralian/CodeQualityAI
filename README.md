# GitHub Repository Analysis Tool

![GitHub Repository Analysis Tool](https://img.shields.io/badge/GitHub-Analysis%20Tool-blue)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B)

A Streamlit-based web application that analyzes GitHub repositories, provides code quality insights, and suggests improvements.

## Features

- 🔍 **Repository Overview**: View basic information about the repository including stars, forks, language, and commit history
- 📊 **Code Quality Analysis**: Analyze code quality across multiple files with pattern-based detection
- 📈 **Visual Insights**: Interactive visualizations of code quality metrics and commit history
- 💡 **Improvement Suggestions**: Receive actionable suggestions to improve code quality with before/after examples

## Screenshots

![Repository Analysis](https://via.placeholder.com/800x450.png?text=Repository+Analysis)
![Code Quality](https://via.placeholder.com/800x450.png?text=Code+Quality+Metrics)

## Technologies Used

- **Streamlit**: Frontend web application framework
- **GitHub REST API**: Direct API integration without dependencies
- **Pandas & Plotly**: Data processing and visualization
- **Pattern Matching**: Lightweight code analysis

## Usage

1. Enter a GitHub repository URL in the sidebar
2. Configure analysis options:
   - Select file types to analyze
   - Set the maximum number of files to analyze
   - Choose analysis depth (Basic, Standard, Deep)
3. Click "Analyze Repository" button
4. View results across the different tabs:
   - Repository Overview
   - Code Quality Analysis
   - Improvement Suggestions

## Local Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install streamlit pandas plotly requests
   ```
3. Run the application:
   ```
   streamlit run main.py
   ```

## Environment Variables

- `GITHUB_TOKEN`: GitHub Personal Access Token for higher API rate limits (optional)

## Deployment

For deployment options, see [DEPLOYMENT.md](./DEPLOYMENT.md)

## Future Enhancements

- GitHub OAuth integration for higher API rate limits
- Full CodeT5 model integration for deeper code analysis
- Automated code fixing capabilities
- Pull Request integration for suggesting changes directly

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Streamlit for the amazing web app framework
- GitHub for providing the API
- The open-source community for inspiration and resources