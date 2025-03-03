"""
Utility functions for the GitHub Repository Analyzer
"""

import re
import streamlit as st
from datetime import datetime
import pytz
import traceback
from logger import logger


def load_custom_css():
    """
    Load custom CSS for styling the application
    """
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def parse_repo_url(url):
    """
    Parse a GitHub repository URL to extract owner and repo name

    Args:
        url (str): GitHub repository URL

    Returns:
        tuple: (owner, repo_name) or (None, None) if parsing fails
    """
    # GitHub URL patterns
    patterns = [
        r"github\.com/([^/]+)/([^/]+)/?$",  # https://github.com/owner/repo
        r"github\.com/([^/]+)/([^/]+)\.git$",  # https://github.com/owner/repo.git
        r"github\.com:([^/]+)/([^/]+)\.git$",  # git@github.com:owner/repo.git
        r"^([^/]+)/([^/]+)$",  # owner/repo (shorthand)
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1), match.group(2)

    return None, None


def handle_error(error_message):
    """
    Display a user-friendly error message and log the error

    Args:
        error_message (str): The error message to display
    """
    logger.error(f"Application error: {error_message}")
    logger.debug(f"Error context: {traceback.format_exc()}")
    st.error(f"Error: {error_message}")
    st.stop()


def truncate_text(text, max_length=100):
    """
    Truncate text to a maximum length

    Args:
        text (str): Text to truncate
        max_length (int, optional): Maximum length. Defaults to 100.

    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def format_timestamp(timestamp):
    """
    Format a timestamp for display

    Args:
        timestamp (str): ISO format timestamp

    Returns:
        str: Formatted timestamp
    """
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        # Convert to local timezone
        local_tz = datetime.now().astimezone().tzinfo
        dt = dt.replace(tzinfo=pytz.UTC).astimezone(local_tz)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp


def create_html_card(title, content, card_type="info"):
    """
    Create an HTML card for displaying information

    Args:
        title (str): Card title
        content (str): Card content
        card_type (str, optional): Card type (info, warning, error). Defaults to "info".

    Returns:
        str: HTML string for the card
    """
    card_class = f"issue-card {card_type}"
    html = f"""
    <div class="{card_class}">
        <strong>{title}</strong>
        <p>{content}</p>
    </div>
    """
    return html


def display_code_with_issues(code, issues):
    """
    Display code with highlighted issues

    Args:
        code (str): Source code to display
        issues (list): List of issues with line numbers
    """
    lines = code.split("\n")
    line_numbers = [issue.get("line", 0) for issue in issues]

    html = "<div style=\"font-family: 'JetBrains Mono', monospace; background-color: #F3F4F6; padding: 1rem; border-radius: 0.375rem; overflow-x: auto;\">"
    for i, line in enumerate(lines, 1):
        if i in line_numbers:
            # Get the issue for this line
            issue = next((issue for issue in issues if issue.get("line", 0) == i), None)
            line_class = f"error"
            if issue and issue.get("severity") == "warning":
                line_class = "warning"
            elif issue and issue.get("severity") == "info":
                line_class = "info"

            html += f'<div style="background-color: rgba(239, 68, 68, 0.1); padding: 0.25rem 0.5rem; display: flex;">'
            html += f'<span style="color: #6B7280; margin-right: 1rem; user-select: none;">{i}</span>'
            html += f"<span>{line}</span>"
            html += f"</div>"
        else:
            html += f'<div style="padding: 0.25rem 0.5rem; display: flex;">'
            html += f'<span style="color: #6B7280; margin-right: 1rem; user-select: none;">{i}</span>'
            html += f"<span>{line}</span>"
            html += f"</div>"

    html += "</div>"

    return html


def format_commit_message(message):
    """
    Format commit message for display

    Args:
        message (str): Commit message

    Returns:
        str: Formatted commit message
    """
    # Limit to the first line if multi-line
    lines = message.split("\n")
    message = lines[0]

    # Truncate if too long
    return truncate_text(message, 80)


def create_repo_card(repo_info):
    """
    Create an HTML card for repository information

    Args:
        repo_info (dict): Repository information

    Returns:
        str: HTML string for the repository card
    """
    html = f"""
    <div class="repo-card">
        <h3>{repo_info['name']}</h3>
        <p>{repo_info.get('description', 'No description')}</p>
        <p>
            <span>⭐ {repo_info.get('stars', 0)} Stars</span> &nbsp;|&nbsp;
            <span>🍴 {repo_info.get('forks', 0)} Forks</span> &nbsp;|&nbsp;
            <span>👁️ {repo_info.get('watchers', 0)} Watchers</span>
        </p>
        <p>Language: {repo_info.get('language', 'Not specified')}</p>
        <p>Updated: {format_timestamp(repo_info.get('updated_at', ''))}</p>
    </div>
    """
    return html


def get_file_extension(filename):
    """
    Extract file extension from filename

    Args:
        filename (str): Filename

    Returns:
        str: File extension without dot
    """
    if "." in filename:
        return filename.split(".")[-1].lower()
    return ""


def get_language_from_extension(extension):
    """
    Get programming language name from file extension

    Args:
        extension (str): File extension

    Returns:
        str: Programming language name
    """
    language_map = {
        "py": "Python",
        "js": "JavaScript",
        "ts": "TypeScript",
        "jsx": "React JSX",
        "tsx": "React TSX",
        "html": "HTML",
        "css": "CSS",
        "scss": "SCSS",
        "sass": "Sass",
        "less": "Less",
        "java": "Java",
        "c": "C",
        "cpp": "C++",
        "cs": "C#",
        "go": "Go",
        "rb": "Ruby",
        "php": "PHP",
        "swift": "Swift",
        "kt": "Kotlin",
        "rs": "Rust",
        "r": "R",
        "sh": "Shell",
        "bash": "Bash",
        "ps1": "PowerShell",
        "sql": "SQL",
        "md": "Markdown",
        "json": "JSON",
        "yml": "YAML",
        "yaml": "YAML",
        "xml": "XML",
        "ini": "INI",
        "toml": "TOML",
    }

    return language_map.get(extension, "Unknown")
