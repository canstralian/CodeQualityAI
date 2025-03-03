import streamlit as st
import re
import base64

def load_custom_css():
    """
    Load custom CSS for styling the application
    """
    with open('styles.css', 'r') as f:
        css = f.read()
    
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

def parse_repo_url(url):
    """
    Parse a GitHub repository URL to extract owner and repo name
    
    Args:
        url (str): GitHub repository URL
        
    Returns:
        tuple: (owner, repo_name) or (None, None) if parsing fails
    """
    # Define patterns for GitHub URLs
    patterns = [
        r'github\.com/([^/]+)/([^/]+)/?$',  # https://github.com/owner/repo
        r'github\.com/([^/]+)/([^/]+)\.git$',  # https://github.com/owner/repo.git
        r'github\.com:([^/]+)/([^/]+)\.git$',  # git@github.com:owner/repo.git
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            owner = match.group(1)
            repo_name = match.group(2)
            return owner, repo_name
    
    return None, None

def handle_error(error_message):
    """
    Display a user-friendly error message
    
    Args:
        error_message (str): The error message to display
    """
    # Create a styled error message
    st.markdown(
        f"""
        <div class="error-box">
            <h3>⚠️ Error</h3>
            <p>{error_message}</p>
            <p>Please check your input and try again.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

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
    return text[:max_length - 3] + "..."

def format_timestamp(timestamp):
    """
    Format a timestamp for display
    
    Args:
        timestamp (str): ISO format timestamp
        
    Returns:
        str: Formatted timestamp
    """
    # Example: "2023-01-15T14:30:45Z" -> "Jan 15, 2023"
    try:
        date_part = timestamp.split('T')[0]
        year, month, day = date_part.split('-')
        
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        return f"{month_names[int(month) - 1]} {int(day)}, {year}"
    except:
        return timestamp
