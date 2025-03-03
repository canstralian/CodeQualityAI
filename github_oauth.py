
"""
GitHub OAuth Authentication Handler

This module provides OAuth authentication with GitHub, including authorization
URL generation, token exchange, and user information retrieval.
"""

import os
from typing import Any, Dict, Optional, Union
from urllib.parse import urlencode

import requests
import streamlit as st


class GitHubOAuth:
    """
    Handles GitHub OAuth authentication workflow with GitHub API
    
    This class manages the OAuth flow including authorization, token exchange,
    and retrieval of user information from GitHub.
    """

    def __init__(self):
        """
        Initialize GitHub OAuth with client ID and secret from environment variables
        
        Environment Variables:
            GITHUB_CLIENT_ID: The OAuth client ID for the GitHub App
            GH_CLIENT_SECRET: The OAuth client secret for the GitHub App
            GITHUB_REDIRECT_URI: The URI GitHub will redirect to after authentication
        """
        # Use environment variables for configuration
        self.client_id = os.getenv("GITHUB_CLIENT_ID")
        self.client_secret = os.getenv("GH_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GITHUB_REDIRECT_URI", "")
        self.webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        self.app_id = os.getenv("GITHUB_APP_ID")
        
        # Set API endpoints
        self.base_url = "https://github.com"
        self.api_url = "https://api.github.com"
        
        # Initialize cache
        self._token_cache = {}
        self._user_info_cache = {}
        
        # Validate required configuration
        self._validate_configuration()
    
    def _validate_configuration(self) -> None:
        """
        Validate that required configuration values are present
        
        Displays warnings in Streamlit for missing configuration
        """
        if not self.client_id:
            st.warning(
                "GitHub OAuth client ID not configured. Set GITHUB_CLIENT_ID environment variable."
            )
        
        if not self.client_secret:
            st.warning(
                "GitHub OAuth client secret not configured. Set GH_CLIENT_SECRET environment variable."
            )

    def _add_redirect_uri(self, params: Dict[str, str]) -> Dict[str, str]:
        """
        Add redirect URI to parameters if it exists
        
        Args:
            params: Dictionary of parameters
            
        Returns:
            Dictionary with redirect_uri added if available
        """
        if self.redirect_uri:
            params["redirect_uri"] = self.redirect_uri
        return params

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Get the GitHub authorization URL
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            str: Complete authorization URL for GitHub OAuth
        """
        params = {
            "client_id": self.client_id,
            "scope": "repo,read:user,user:email",
        }
        
        # Add redirect URI if configured
        params = self._add_redirect_uri(params)
        
        # Add state parameter if provided
        if state:
            params["state"] = state
            
        # Build and return the full authorization URL
        return f"{self.base_url}/login/oauth/authorize?{urlencode(params)}"

    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code received from GitHub
            
        Returns:
            Optional[Dict[str, Any]]: Token response or None if exchange fails
        """
        # Validate input
        if not code:
            st.error("No authorization code provided")
            return None
            
        # Check if we have this code cached
        if code in self._token_cache:
            return self._token_cache[code]

        # Prepare request payload
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
        }
        
        # Add redirect URI if configured
        payload = self._add_redirect_uri(payload)
        
        # Set headers for JSON response
        headers = {"Accept": "application/json"}

        try:
            # Make the request with timeout to prevent hanging
            response = requests.post(
                f"{self.base_url}/login/oauth/access_token", 
                data=payload, 
                headers=headers,
                timeout=10
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Parse and cache the response
            token_data = response.json()
            self._token_cache[code] = token_data
            return token_data
            
        except requests.RequestException as e:
            st.error(f"Error exchanging code for token: {str(e)}")
            return None

    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get authenticated user information from GitHub
        
        Args:
            access_token: OAuth access token for authentication
            
        Returns:
            Optional[Dict[str, Any]]: User data or None if retrieval fails
        """
        # Validate input
        if not access_token:
            st.error("No access token provided")
            return None
            
        # Check if we have this token cached
        if access_token in self._user_info_cache:
            return self._user_info_cache[access_token]

        # Set up authentication headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            # Make the request with timeout to prevent hanging
            response = requests.get(
                f"{self.api_url}/user", 
                headers=headers,
                timeout=10
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Parse and cache the response
            user_data = response.json()
            self._user_info_cache[access_token] = user_data
            return user_data
            
        except requests.RequestException as e:
            st.error(f"Error fetching user info: {str(e)}")
            return None
            
    def clear_cache(self) -> None:
        """
        Clear the token and user info caches
        
        Call this method to force new API requests instead of using cached data
        """
        self._token_cache = {}
        self._user_info_cache = {}
