
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
