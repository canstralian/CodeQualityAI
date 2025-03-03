
import unittest
from unittest.mock import patch, MagicMock
from github_api import GitHubRepo

class TestGitHubRepoPositive(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.repo = GitHubRepo("owner", "repo", "access_token")

    @patch('github_api.GitHubRepo._make_request')
    def test_get_repo_info(self, mock_make_request):
        """Test get_repo_info returns expected repository information."""
        # Define mock API response
        mock_make_request.return_value = {
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "description": "Test repository",
            "stargazers_count": 10,
            "forks_count": 5,
            "watchers_count": 8,
            "language": "Python",
            "created_at": "2023-01-01T12:00:00Z",
            "updated_at": "2023-02-01T12:00:00Z",
            "default_branch": "main",
            "license": {"name": "MIT License"},
            "html_url": "https://github.com/owner/test-repo"
        }

        # Call the method
        repo_info = self.repo.get_repo_info()

        # Verify request was made correctly
        mock_make_request.assert_called_once_with("/repos/owner/repo")

        # Verify result
        self.assertEqual(repo_info["name"], "test-repo")
        self.assertEqual(repo_info["full_name"], "owner/test-repo")
        self.assertEqual(repo_info["stars"], 10)
        self.assertEqual(repo_info["language"], "Python")
        self.assertEqual(repo_info["license"], "MIT License")

    @patch('github_api.GitHubRepo._make_request')
    def test_get_commit_history(self, mock_make_request):
        """Test get_commit_history returns correctly formatted commit data."""
        # Define mock API response
        mock_make_request.return_value = [
            {
                "sha": "abc123",
                "commit": {
                    "author": {
                        "name": "Test User",
                        "email": "test@example.com",
                        "date": "2023-03-01T12:00:00Z"
                    },
                    "message": "Initial commit"
                },
                "html_url": "https://github.com/owner/repo/commit/abc123"
            }
        ]

        # Call the method
        commits = self.repo.get_commit_history(limit=1)

        # Verify request was made correctly
        mock_make_request.assert_called_once_with("/repos/owner/repo/commits", {'per_page': 1})

        # Verify result
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0]["hash"], "abc123")
        self.assertEqual(commits[0]["author"], "Test User")
        self.assertEqual(commits[0]["message"], "Initial commit")

    @patch('github_api.GitHubRepo._make_request')
    def test_get_repository_files(self, mock_make_request):
        """Test get_repository_files returns filtered file list."""
        # Mock get_repo_info to return default branch
        self.repo.get_repo_info = MagicMock(return_value={"default_branch": "main"})

        # Define mock API response
        mock_make_request.return_value = {
            "tree": [
                {
                    "path": "file1.py",
                    "type": "blob",
                    "size": 100,
                    "url": "https://api.github.com/repos/owner/repo/git/blobs/abc123"
                },
                {
                    "path": "file2.js",
                    "type": "blob",
                    "size": 200,
                    "url": "https://api.github.com/repos/owner/repo/git/blobs/def456"
                },
                {
                    "path": "dir",
                    "type": "tree",
                    "url": "https://api.github.com/repos/owner/repo/git/trees/ghi789"
                }
            ]
        }

        # Call the method with python files only
        files = self.repo.get_repository_files(max_files=1, file_extensions=["py"])

        # Verify request was made correctly
        mock_make_request.assert_called_with("/repos/owner/repo/git/trees/main", {"recursive": 1})

        # Verify result
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["path"], "file1.py")
        self.assertEqual(files[0]["size"], 100)

    @patch('github_api.GitHubRepo._make_request')
    def test_get_file_content(self, mock_make_request):
        """Test get_file_content returns decoded file content."""
        # Define mock API response
        import base64
        content = "print('Hello, World!')"
        encoded_content = base64.b64encode(content.encode()).decode()
        
        mock_make_request.return_value = {
            "type": "file",
            "content": encoded_content
        }

        # Call the method
        file_content = self.repo.get_file_content("file.py")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with("/repos/owner/repo/contents/file.py")

        # Verify result
        self.assertEqual(file_content, content)

    @patch('github_api.logger')
    @patch('github_api.requests.get')
    def test_make_request_successful(self, mock_get, mock_logger):
        """Test _make_request handles successful API responses."""
        # Mock requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"success": True}
        mock_get.return_value = mock_response

        # Call the method
        result = self.repo._make_request("/test/endpoint")

        # Verify request was made correctly
        mock_get.assert_called_once()
        
        # Verify result
        self.assertEqual(result, {"success": True})
        mock_logger.debug.assert_called()

class TestGitHubRepoNegative(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.repo = GitHubRepo("owner", "repo", "access_token")

    @patch('github_api.GitHubRepo._make_request')
    def test_get_repo_info_with_error(self, mock_make_request):
        """Test get_repo_info handles API errors."""
        # Mock make_request to raise an exception
        mock_make_request.side_effect = Exception("API error")

        # Expect the method to raise the exception
        with self.assertRaises(Exception):
            self.repo.get_repo_info()

    @patch('github_api.GitHubRepo._make_request')
    def test_get_commit_history_empty(self, mock_make_request):
        """Test get_commit_history returns empty list when no commits exist."""
        # Mock make_request to return empty list
        mock_make_request.return_value = []

        # Call the method
        commits = self.repo.get_commit_history()

        # Verify result
        self.assertEqual(commits, [])

    @patch('github_api.GitHubRepo._make_request')
    @patch('github_api.logger')
    def test_get_file_content_not_file(self, mock_logger, mock_make_request):
        """Test get_file_content returns None if path is not a file."""
        # Mock make_request to return a directory
        mock_make_request.return_value = {"type": "dir"}

        # Call the method
        content = self.repo.get_file_content("dir")

        # Verify result
        self.assertIsNone(content)
        mock_logger.warning.assert_called()

    @patch('github_api.GitHubRepo._make_request')
    @patch('github_api.logger')
    def test_get_file_content_empty(self, mock_logger, mock_make_request):
        """Test get_file_content returns None if content is empty."""
        # Mock make_request to return empty content
        mock_make_request.return_value = {"type": "file", "content": ""}

        # Call the method
        content = self.repo.get_file_content("file.py")

        # Verify result
        self.assertIsNone(content)
        mock_logger.warning.assert_called()

    @patch('github_api.handle_error')
    @patch('github_api.logger')
    @patch('github_api.requests.get')
    def test_make_request_unauthorized(self, mock_get, mock_logger, mock_handle_error):
        """Test _make_request handles 401 unauthorized responses."""
        # Mock requests.get
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.headers = {"Content-Type": "application/json"}
        mock_get.return_value = mock_response

        # Call the method
        self.repo._make_request("/test/endpoint")

        # Verify error handling
        mock_logger.error.assert_called()
        mock_handle_error.assert_called()

    @patch('github_api.time.sleep', return_value=None)
    @patch('github_api.logger')
    @patch('github_api.requests.get')
    def test_make_request_rate_limit(self, mock_get, mock_logger, mock_sleep):
        """Test _make_request handles rate limit responses."""
        # Setup first response to be rate limited
        mock_response1 = MagicMock()
        mock_response1.status_code = 403
        mock_response1.headers = {
            "Content-Type": "application/json",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(time.time()) + 10)
        }
        
        # Setup second response (after retry) to be successful
        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.headers = {"Content-Type": "application/json"}
        mock_response2.json.return_value = {"success": True}
        
        # Configure mock to return different responses on subsequent calls
        mock_get.side_effect = [mock_response1, mock_response2]

        # Call the method
        result = self.repo._make_request("/test/endpoint")

        # Verify request was retried
        self.assertEqual(mock_get.call_count, 2)
        
        # Verify sleep was called for rate limit
        mock_sleep.assert_called()
        
        # Verify result
        self.assertEqual(result, {"success": True})

if __name__ == '__main__':
    unittest.main()
