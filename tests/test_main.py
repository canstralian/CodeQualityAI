
import unittest
from unittest.mock import patch, MagicMock
import streamlit as st
from main import main, display_results

class TestGitHubRepositoryAnalyzer(unittest.TestCase):

    @patch('main.load_custom_css')
    @patch('main.GitHubRepo')
    @patch('main.CodeAnalyzer')
    @patch('main.visualize_commit_history')
    @patch('main.visualize_code_quality')
    @patch('main.visualize_issues_by_type')
    @patch('main.handle_error')
    @patch('main.logger')
    def test_main_function_success(self, mock_logger, mock_handle_error, mock_visualize_issues_by_type, 
                                    mock_visualize_code_quality, mock_visualize_commit_history, 
                                    mock_CodeAnalyzer, mock_GitHubRepo, mock_load_custom_css):
        """Test the main function runs successfully with valid inputs."""
        # Setup mock objects
        mock_load_custom_css.return_value = None
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_repo_info.return_value = {
            'full_name': 'owner/repo',
            'name': 'repo',
            'stars': 10,
            'forks': 5,
            'language': 'Python',
            'license': 'MIT'
        }
        mock_repo_instance.get_commit_history.return_value = [{'author': 'author', 'date': '2021-01-01', 'message': 'Initial commit'}]
        mock_repo_instance.get_repository_files.return_value = [{'path': 'file.py'}]
        mock_repo_instance.get_file_content.return_value = 'print("Hello World")'
        mock_GitHubRepo.return_value = mock_repo_instance

        mock_analyzer_instance = MagicMock()
        mock_analyzer_instance.analyze_code.return_value = {
            'score': 8,
            'issues': []
        }
        mock_CodeAnalyzer.return_value = mock_analyzer_instance

        # Simulate Streamlit inputs
        st.session_state.repo_analyzed = False
        st.session_state.repo_data = {}
        st.session_state.analysis_results = {}
        st.session_state.file_contents = {}
        st.session_state.selected_tab = 0

        # Mock parse_repo_url function
        with patch('main.parse_repo_url', return_value=('owner', 'repo')):
            # Simulate button click
            with patch('streamlit.button', return_value=True):
                with patch('streamlit.spinner'):
                    main()

        # Assertions
        mock_logger.info.assert_called()
        self.assertTrue(st.session_state.repo_analyzed)
        self.assertIn('info', st.session_state.repo_data)
        self.assertEqual(len(st.session_state.analysis_results), 1)

    @patch('streamlit.tabs')
    @patch('streamlit.header')
    @patch('streamlit.markdown')
    @patch('streamlit.metric')
    @patch('streamlit.dataframe')
    @patch('streamlit.write')
    @patch('streamlit.subheader')
    @patch('streamlit.plotly_chart')
    @patch('main.visualize_code_quality')
    @patch('main.visualize_issues_by_type')
    @patch('main.visualize_commit_history')
    def test_display_results_with_data(self, mock_viz_commit, mock_viz_issues, mock_viz_quality,
                                      mock_plotly, mock_subheader, mock_write, mock_dataframe, 
                                      mock_metric, mock_markdown, mock_header, mock_tabs):
        """Test display_results function with valid data."""
        # Setup mock data
        st.session_state.repo_data = {
            'info': {'full_name': 'owner/repo', 'name': 'repo', 'stars': 10, 'forks': 5, 'language': 'Python', 'license': 'MIT'},
            'commits': [{'author': 'author', 'date': '2021-01-01T00:00:00Z', 'message': 'Initial commit', 'hash': 'abc123'}],
            'files': [{'path': 'file.py'}]
        }
        st.session_state.analysis_results = [
            {
                'file_path': 'file.py',
                'extension': 'py',
                'result': {'score': 8, 'issues': [], 'filename': 'file.py', 'suggestions': []}
            }
        ]
        st.session_state.file_contents = {'file.py': 'print("Hello World")'}
        
        # Mock tab instances
        mock_tab_instances = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_tabs.return_value = mock_tab_instances

        # Mock visualization functions to return figure objects
        mock_viz_commit.return_value = MagicMock()
        mock_viz_issues.return_value = MagicMock()
        mock_viz_quality.return_value = MagicMock()

        # Call the function
        display_results()

        # Assertions
        mock_tabs.assert_called_once()
        mock_header.assert_called()
        mock_metric.assert_called()
        mock_viz_commit.assert_called_once()
        mock_viz_quality.assert_called_once()

    @patch('streamlit.tabs')
    @patch('streamlit.success')
    @patch('main.visualize_code_quality')
    @patch('main.visualize_issues_by_type')
    @patch('main.visualize_commit_history')
    def test_display_results_no_issues(self, mock_viz_commit, mock_viz_issues, mock_viz_quality,
                                      mock_success, mock_tabs):
        """Test display_results function when no issues are detected."""
        # Setup mock data
        st.session_state.repo_data = {
            'info': {'full_name': 'owner/repo', 'name': 'repo', 'stars': 10, 'forks': 5, 'language': 'Python', 'license': 'MIT'},
            'commits': [{'author': 'author', 'date': '2021-01-01T00:00:00Z', 'message': 'Initial commit', 'hash': 'abc123'}],
            'files': [{'path': 'file.py'}]
        }
        st.session_state.analysis_results = [
            {
                'file_path': 'file.py',
                'extension': 'py',
                'result': {'score': 8, 'issues': [], 'filename': 'file.py', 'suggestions': []}
            }
        ]
        st.session_state.file_contents = {'file.py': 'print("Hello World")'}
        
        # Mock tab instances
        mock_tab_instances = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_tabs.return_value = mock_tab_instances

        # Mock visualization functions to return figure objects
        mock_viz_commit.return_value = MagicMock()
        mock_viz_issues.return_value = MagicMock()
        mock_viz_quality.return_value = MagicMock()

        # Call the function
        display_results()

        # Assertions for the "No issues detected" success message
        mock_success.assert_called_with("No issues detected in the analyzed files. Great job!")

class TestGitHubRepoAnalyzerNegative(unittest.TestCase):

    @patch('main.parse_repo_url')
    @patch('main.handle_error')
    @patch('main.logger')
    def test_invalid_repo_url(self, mock_logger, mock_handle_error, mock_parse_repo_url):
        """Test that an invalid GitHub repository URL raises an error."""
        mock_parse_repo_url.return_value = (None, None)  # Simulate invalid URL parsing
        
        # Simulate button click
        with patch('streamlit.button', return_value=True):
            with patch('streamlit.spinner'):
                with patch('streamlit.sidebar'):
                    main()  # Call the main function which triggers the analysis
                    
        mock_handle_error.assert_called_with("Invalid GitHub repository URL. Please provide a valid URL.")
        mock_logger.error.assert_called()

    @patch('main.parse_repo_url')
    @patch('main.GitHubRepo')
    @patch('main.handle_error')
    @patch('main.logger')
    def test_github_repo_initialization_failure(self, mock_logger, mock_handle_error, mock_GitHubRepo, mock_parse_repo_url):
        """Test that failure to initialize GitHubRepo raises an error."""
        mock_parse_repo_url.return_value = ('owner', 'repo')
        mock_GitHubRepo.side_effect = Exception("GitHub API error")
        
        # Simulate button click
        with patch('streamlit.button', return_value=True):
            with patch('streamlit.spinner'):
                with patch('streamlit.sidebar'):
                    main()  # Call the main function which triggers the analysis
                    
        mock_handle_error.assert_called_with("GitHub API error")
        mock_logger.error.assert_called()

    @patch('main.parse_repo_url')
    @patch('main.GitHubRepo')
    @patch('main.logger')
    def test_analysis_with_no_files(self, mock_logger, mock_GitHubRepo, mock_parse_repo_url):
        """Test that analysis proceeds correctly when no files are retrieved."""
        mock_parse_repo_url.return_value = ('owner', 'repo')
        
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_repo_info.return_value = {
            'full_name': 'owner/repo', 'name': 'repo', 'stars': 10, 'forks': 5, 
            'language': 'Python', 'license': 'MIT', 'default_branch': 'main'
        }
        mock_repo_instance.get_commit_history.return_value = [{'author': 'author', 'date': '2021-01-01T00:00:00Z', 'message': 'Initial commit', 'hash': 'abc123'}]
        mock_repo_instance.get_repository_files.return_value = []  # Simulate no files
        mock_GitHubRepo.return_value = mock_repo_instance
        
        # Simulate button click
        with patch('streamlit.button', return_value=True):
            with patch('streamlit.spinner'):
                with patch('streamlit.sidebar'):
                    with patch('main.CodeAnalyzer'):
                        main()  # Call the main function which triggers the analysis

        # Check that the analysis results are empty
        self.assertEqual(st.session_state.analysis_results, [])
        mock_logger.info.assert_any_call("Analysis complete. Processed 0 files")

    @patch('main.parse_repo_url')
    @patch('main.GitHubRepo')
    @patch('main.logger')
    def test_analysis_with_excluded_files(self, mock_logger, mock_GitHubRepo, mock_parse_repo_url):
        """Test that files in excluded directories are skipped."""
        mock_parse_repo_url.return_value = ('owner', 'repo')
        
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_repo_info.return_value = {
            'full_name': 'owner/repo', 'name': 'repo', 'stars': 10, 'forks': 5, 
            'language': 'Python', 'license': 'MIT', 'default_branch': 'main'
        }
        mock_repo_instance.get_commit_history.return_value = [{'author': 'author', 'date': '2021-01-01T00:00:00Z', 'message': 'Initial commit', 'hash': 'abc123'}]
        mock_repo_instance.get_repository_files.return_value = [
            {"path": "node_modules/example.js"},
            {"path": "venv/lib/site-packages/example.py"},
        ]
        mock_GitHubRepo.return_value = mock_repo_instance
        
        # Simulate button click
        with patch('streamlit.button', return_value=True):
            with patch('streamlit.spinner'):
                with patch('streamlit.sidebar'):
                    with patch('main.CodeAnalyzer'):
                        main()  # Call the main function which triggers the analysis

        # Check that the analysis results are empty (all files were excluded)
        self.assertEqual(st.session_state.analysis_results, [])
        mock_logger.debug.assert_any_call("Skipping excluded directory file: node_modules/example.js")
        mock_logger.debug.assert_any_call("Skipping excluded directory file: venv/lib/site-packages/example.py")

if __name__ == '__main__':
    unittest.main()
import unittest
from unittest.mock import patch, MagicMock
import streamlit as st
from main import main, display_results


class TestGitHubRepositoryAnalyzer(unittest.TestCase):
    """Test cases for the GitHub Repository Analyzer main application."""

    @patch('main.load_custom_css')
    @patch('main.GitHubRepo')
    @patch('main.CodeAnalyzer')
    @patch('main.visualize_commit_history')
    @patch('main.visualize_code_quality')
    @patch('main.visualize_issues_by_type')
    @patch('main.handle_error')
    @patch('main.logger')
    def test_main_function_success(self, mock_logger, mock_handle_error, mock_visualize_issues_by_type, 
                                   mock_visualize_code_quality, mock_visualize_commit_history, 
                                   mock_CodeAnalyzer, mock_GitHubRepo, mock_load_custom_css):
        """Test the main function runs successfully with valid inputs."""
        # Setup mock objects
        mock_load_custom_css.return_value = None
        mock_repo_instance = MagicMock()
        mock_GitHubRepo.return_value = mock_repo_instance
        
        # Mock repo info response
        mock_repo_instance.get_repo_info.return_value = {
            "name": "test-repo",
            "full_name": "testuser/test-repo",
            "description": "Test repository",
            "stars": 10,
            "forks": 5,
            "watchers": 3,
            "language": "Python",
            "created_at": "2023-01-01",
            "updated_at": "2023-02-01",
            "default_branch": "main",
            "license": "MIT",
            "url": "https://github.com/testuser/test-repo"
        }
        
        # Mock commit history response
        mock_repo_instance.get_commit_history.return_value = [
            {
                "hash": "abcd1234",
                "author": "Test User",
                "email": "test@example.com",
                "date": "2023-02-01T12:00:00Z",
                "message": "Test commit",
                "url": "https://github.com/testuser/test-repo/commit/abcd1234"
            }
        ]
        
        # Mock repository files response
        mock_repo_instance.get_repository_files.return_value = [
            {
                "path": "test.py",
                "size": 100,
                "url": "https://api.github.com/repos/testuser/test-repo/contents/test.py"
            }
        ]
        
        # Mock file content response
        mock_repo_instance.get_file_content.return_value = "def test():\n    return True"
        
        # Mock analyzer instance
        mock_analyzer_instance = MagicMock()
        mock_CodeAnalyzer.return_value = mock_analyzer_instance
        
        # Mock analysis result
        mock_analyzer_instance.analyze_code.return_value = {
            "filename": "test.py",
            "score": 8.5,
            "issues": [],
            "suggestions": []
        }
        
        # Set up session state and button click
        st.session_state.repo_analyzed = False
        st.session_state.repo_data = {}
        st.session_state.analysis_results = {}
        st.session_state.file_contents = {}
        st.session_state.selected_tab = 0
        
        # Mock parse_repo_url function
        with patch('main.parse_repo_url', return_value=("testuser", "test-repo")):
            # Mock the analyze button click
            with patch('streamlit.button', return_value=True):
                # Call the main function
                main()
                
        # Verify logger calls
        mock_logger.info.assert_any_call("Starting GitHub Repository Analyzer application")
        
        # Verify GitHubRepo instantiation
        mock_GitHubRepo.assert_called_once_with("testuser", "test-repo", access_token=None)
        
        # Verify repo_info was called
        mock_repo_instance.get_repo_info.assert_called_once()
        
        # Verify get_commit_history was called
        mock_repo_instance.get_commit_history.assert_called_once_with(limit=50)
        
        # Verify CodeAnalyzer instantiation
        mock_CodeAnalyzer.assert_called_once()
        
        # Verify no errors were handled
        mock_handle_error.assert_not_called()

    @patch('main.st')
    @patch('main.logger')
    @patch('main.parse_repo_url')
    @patch('main.handle_error')
    def test_main_function_invalid_url(self, mock_handle_error, mock_parse_repo_url, mock_logger, mock_st):
        """Test the main function handles invalid repository URLs."""
        # Mock parse_repo_url to return None, None (invalid URL)
        mock_parse_repo_url.return_value = (None, None)
        
        # Mock the button click
        mock_st.button.return_value = True
        
        # Create a spinner context manager
        mock_spinner = MagicMock()
        mock_st.spinner.return_value.__enter__.return_value = mock_spinner
        
        # Call the main function
        main()
        
        # Verify error was handled
        mock_handle_error.assert_called_once_with(
            "Invalid GitHub repository URL. Please provide a valid URL."
        )

    @patch('main.st')
    @patch('main.logger')
    @patch('main.GitHubRepo')
    @patch('main.parse_repo_url')
    @patch('main.handle_error')
    def test_main_function_api_error(self, mock_handle_error, mock_parse_repo_url, 
                                     mock_GitHubRepo, mock_logger, mock_st):
        """Test the main function handles GitHub API errors."""
        # Mock parse_repo_url to return valid values
        mock_parse_repo_url.return_value = ("testuser", "test-repo")
        
        # Mock GitHubRepo to raise an exception when get_repo_info is called
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_repo_info.side_effect = Exception("API rate limit exceeded")
        mock_GitHubRepo.return_value = mock_repo_instance
        
        # Mock the button click
        mock_st.button.return_value = True
        
        # Create a spinner context manager
        mock_spinner = MagicMock()
        mock_st.spinner.return_value.__enter__.return_value = mock_spinner
        
        # Call the main function
        main()
        
        # Verify error was logged
        mock_logger.error.assert_any_call("Fatal error during repository analysis: API rate limit exceeded")
        
        # Verify error was handled
        mock_handle_error.assert_called_once_with("API rate limit exceeded")

    @patch('main.st')
    @patch('main.visualize_commit_history')
    @patch('main.visualize_code_quality')
    @patch('main.visualize_issues_by_type')
    def test_display_results(self, mock_visualize_issues_by_type, mock_visualize_code_quality, 
                             mock_visualize_commit_history, mock_st):
        """Test the display_results function correctly displays analysis results."""
        # Setup mock visualization functions
        mock_quality_fig = MagicMock()
        mock_visualize_code_quality.return_value = mock_quality_fig
        
        mock_issues_fig = MagicMock()
        mock_visualize_issues_by_type.return_value = mock_issues_fig
        
        mock_commits_fig = MagicMock()
        mock_visualize_commit_history.return_value = mock_commits_fig
        
        # Setup tabs
        mock_tabs = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.tabs.return_value = mock_tabs
        
        # Setup session state
        st.session_state.repo_data = {
            "info": {
                "name": "test-repo",
                "full_name": "testuser/test-repo",
                "description": "Test repository",
                "stars": 10,
                "forks": 5,
                "language": "Python",
                "license": "MIT"
            },
            "commits": [
                {
                    "hash": "abcd1234",
                    "author": "Test User",
                    "date": "2023-02-01T12:00:00Z",
                    "message": "Test commit"
                }
            ],
            "files": [{"path": "test.py"}]
        }
        
        st.session_state.analysis_results = [
            {
                "file_path": "test.py",
                "extension": "py",
                "result": {
                    "filename": "test.py",
                    "score": 8.5,
                    "issues": [
                        {
                            "line": 10,
                            "type": "Long line",
                            "severity": "warning",
                            "message": "Line exceeds 88 characters"
                        }
                    ],
                    "suggestions": [
                        {
                            "title": "Improve Line Length",
                            "description": "Break long lines into multiple lines.",
                            "example": "# Example code"
                        }
                    ]
                }
            }
        ]
        
        st.session_state.file_contents = {
            "test.py": "def test():\n    return True"
        }
        
        # Call the display_results function
        display_results()
        
        # Verify visualizations were created
        mock_visualize_code_quality.assert_called_once_with(st.session_state.analysis_results)
        mock_visualize_issues_by_type.assert_called_once()
        mock_visualize_commit_history.assert_called_once_with(st.session_state.repo_data["commits"])
        
        # Verify plotly charts were displayed
        mock_st.plotly_chart.assert_any_call(mock_quality_fig, use_container_width=True)
        mock_st.plotly_chart.assert_any_call(mock_issues_fig, use_container_width=True)
        mock_st.plotly_chart.assert_any_call(mock_commits_fig, use_container_width=True)


if __name__ == '__main__':
    unittest.main()
