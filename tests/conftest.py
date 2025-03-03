
import pytest
from unittest.mock import MagicMock
import streamlit as st

@pytest.fixture(autouse=True)
def mock_streamlit():
    """
    Mock Streamlit functions to allow tests to run without a Streamlit server.
    This gets automatically used in all tests.
    """
    # Create mock session state if it doesn't exist
    if not hasattr(st, "session_state"):
        st.session_state = MagicMock()
        
    # Mock common Streamlit functions
    st.title = MagicMock()
    st.header = MagicMock()
    st.subheader = MagicMock()
    st.markdown = MagicMock()
    st.sidebar = MagicMock()
    st.button = MagicMock(return_value=False)
    st.spinner = MagicMock()
    st.error = MagicMock()
    st.warning = MagicMock()
    st.success = MagicMock()
    st.info = MagicMock()
    st.text_input = MagicMock(return_value="https://github.com/streamlit/streamlit")
    st.multiselect = MagicMock(return_value=["py", "js"])
    st.select_slider = MagicMock(return_value="Standard")
    st.slider = MagicMock(return_value=10)
    st.tabs = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock(), MagicMock()])
    st.rerun = MagicMock()
    st.metric = MagicMock()
    st.dataframe = MagicMock()
    st.write = MagicMock()
    st.plotly_chart = MagicMock()
    st.expander = MagicMock()
    st.code = MagicMock()
    st.selectbox = MagicMock()
    
    yield st

@pytest.fixture
def github_repo_mock():
    """
    Create a mock GitHubRepo instance
    """
    mock = MagicMock()
    mock.get_repo_info.return_value = {
        'full_name': 'owner/repo',
        'name': 'repo',
        'stars': 10,
        'forks': 5,
        'language': 'Python',
        'license': 'MIT',
        'default_branch': 'main',
        'description': 'Test repository',
        'watchers_count': 8,
        'created_at': '2023-01-01T12:00:00Z',
        'updated_at': '2023-02-01T12:00:00Z',
        'url': 'https://github.com/owner/repo'
    }
    mock.get_commit_history.return_value = [
        {
            'hash': 'abc123',
            'author': 'Test User',
            'email': 'test@example.com',
            'date': '2023-03-01T12:00:00Z',
            'message': 'Initial commit',
            'url': 'https://github.com/owner/repo/commit/abc123'
        }
    ]
    mock.get_repository_files.return_value = [
        {
            'path': 'file.py',
            'size': 100,
            'url': 'https://api.github.com/repos/owner/repo/contents/file.py'
        }
    ]
    mock.get_file_content.return_value = 'def hello():\n    print("Hello World")\n    return None'
    
    return mock

@pytest.fixture
def code_analyzer_mock():
    """
    Create a mock CodeAnalyzer instance
    """
    mock = MagicMock()
    mock.analyze_code.return_value = {
        'filename': 'file.py',
        'score': 8.5,
        'issues': [
            {
                'line': 2,
                'type': 'Print statement',
                'severity': 'warning',
                'message': 'Avoid print statements in production code'
            }
        ],
        'suggestions': [
            {
                'title': 'Use Logging',
                'description': 'Replace print statements with proper logging',
                'example': '# Before\nprint("Hello World")\n\n# After\nimport logging\nlogging.info("Hello World")'
            }
        ]
    }
    
    return mock
