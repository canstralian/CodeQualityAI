import unittest
from unittest.mock import MagicMock, patch

from utils import (
    create_html_card,
    create_repo_card,
    display_code_with_issues,
    format_commit_message,
    get_file_extension,
    handle_error,
    load_custom_css,
    parse_repo_url,
    truncate_text,
)


class TestUtils(unittest.TestCase):

    @patch("utils.st")
    def test_load_custom_css(self, mock_st):
        """Test that load_custom_css reads from styles.css file."""
        with patch(
            "builtins.open", unittest.mock.mock_open(read_data="body { color: blue; }")
        ):
            load_custom_css()
            mock_st.markdown.assert_called_once()

    def test_parse_repo_url_github_com(self):
        """Test parse_repo_url with github.com URL."""
        # Test with valid github.com URL
        owner, repo = parse_repo_url("https://github.com/owner/repo")
        self.assertEqual(owner, "owner")
        self.assertEqual(repo, "repo")

        # Test with valid github.com URL with trailing slash
        owner, repo = parse_repo_url("https://github.com/owner/repo/")
        self.assertEqual(owner, "owner")
        self.assertEqual(repo, "repo")

        # Test with valid github.com URL with additional path
        owner, repo = parse_repo_url("https://github.com/owner/repo/tree/main")
        self.assertEqual(owner, "owner")
        self.assertEqual(repo, "repo")

    def test_parse_repo_url_invalid(self):
        """Test parse_repo_url with invalid URLs."""
        # Test with invalid URL
        owner, repo = parse_repo_url("not a url")
        self.assertIsNone(owner)
        self.assertIsNone(repo)

        # Test with non-GitHub URL
        owner, repo = parse_repo_url("https://example.com/owner/repo")
        self.assertIsNone(owner)
        self.assertIsNone(repo)

        # Test with incomplete GitHub URL
        owner, repo = parse_repo_url("https://github.com/owner")
        self.assertIsNone(owner)
        self.assertIsNone(repo)

    @patch("utils.st")
    def test_handle_error(self, mock_st):
        """Test handle_error function displays an error message."""
        handle_error("Test error message")
        mock_st.error.assert_called_once_with("Test error message")

    def test_create_repo_card(self):
        """Test create_repo_card generates HTML card with repository info."""
        repo_info = {
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "description": "Test repository",
            "language": "Python",
            "stars": 10,
            "forks": 5,
            "url": "https://github.com/owner/test-repo",
        }

        card_html = create_repo_card(repo_info)

        # Check that the card contains repository information
        self.assertIn("test-repo", card_html)
        self.assertIn("owner/test-repo", card_html)
        self.assertIn("Test repository", card_html)
        self.assertIn("Python", card_html)
        self.assertIn("10", card_html)  # stars
        self.assertIn("5", card_html)  # forks
        self.assertIn("https://github.com/owner/test-repo", card_html)

    def test_get_file_extension(self):
        """Test get_file_extension returns the correct file extension."""
        # Test with file with extension
        self.assertEqual(get_file_extension("file.py"), "py")
        self.assertEqual(get_file_extension("path/to/file.js"), "js")
        self.assertEqual(get_file_extension("file.with.multiple.dots.txt"), "txt")

        # Test with file without extension
        self.assertEqual(get_file_extension("file"), "")

        # Test with hidden file
        self.assertEqual(get_file_extension(".gitignore"), "gitignore")

    def test_create_html_card(self):
        """Test create_html_card generates HTML card with proper styling."""
        # Test info card
        info_card = create_html_card("Info Title", "Info content", "info")
        self.assertIn("Info Title", info_card)
        self.assertIn("Info content", info_card)
        self.assertIn("card-info", info_card)

        # Test warning card
        warning_card = create_html_card("Warning Title", "Warning content", "warning")
        self.assertIn("Warning Title", warning_card)
        self.assertIn("Warning content", warning_card)
        self.assertIn("card-warning", warning_card)

        # Test error card
        error_card = create_html_card("Error Title", "Error content", "error")
        self.assertIn("Error Title", error_card)
        self.assertIn("Error content", error_card)
        self.assertIn("card-error", error_card)

    def test_display_code_with_issues(self):
        """Test display_code_with_issues generates HTML with highlighted lines."""
        code = """def hello():
    print("Hello World")
    x = 5
    return None"""

        issues = [
            {"line": 2, "type": "Print statement", "message": "Avoid print statements"},
            {"line": 3, "type": "Variable naming", "message": "Use descriptive names"},
        ]

        html = display_code_with_issues(code, issues)

        # Check that the HTML includes the code
        self.assertIn("def hello():", html)
        self.assertIn('print("Hello World")', html)

        # Check that issues are highlighted
        self.assertIn("line-issue", html)
        self.assertIn("Print statement: Avoid print statements", html)
        self.assertIn("Variable naming: Use descriptive names", html)

    def test_truncate_text(self):
        """Test truncate_text truncates text to specified length."""
        # Test with text shorter than max_length
        self.assertEqual(truncate_text("Short text", 20), "Short text")

        # Test with text longer than max_length
        self.assertEqual(truncate_text("This is a very long text", 10), "This is...")

        # Test with exactly max_length
        self.assertEqual(truncate_text("Exactly 10", 10), "Exactly 10")

        # Test with empty text
        self.assertEqual(truncate_text("", 10), "")

    def test_format_commit_message(self):
        """Test format_commit_message formats commit messages correctly."""
        # Test with short message
        self.assertEqual(format_commit_message("Short message"), "Short message")

        # Test with multi-line message
        self.assertEqual(
            format_commit_message("First line\nSecond line\nThird line"), "First line"
        )

        # Test with empty message
        self.assertEqual(format_commit_message(""), "")


if __name__ == "__main__":
    unittest.main()
