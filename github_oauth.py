import os
import requests
import json
import streamlit as st
from urllib.parse import urlencode


class GitHubOAuth:
    """
    Handles GitHub OAuth authentication
    """

    def __init__(self):
        """
        Initialize GitHub OAuth with client ID and secret from environment variables
        """
        self.client_id = os.getenv("GITHUB_CLIENT_ID")
        self.client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GITHUB_REDIRECT_URI", "")
        self.base_url = "https://github.com"
        self.api_url = "https://api.github.com"

        if not self.client_id or not self.client_secret:
            st.warning(
                "GitHub OAuth credentials not configured. Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables."
            )

    def get_authorization_url(self, state=None):
        """
        Get the GitHub authorization URL
        """
        params = {
            "client_id": self.client_id,
            "scope": "repo,read:user,user:email",
        }

        if self.redirect_uri:
            params["redirect_uri"] = self.redirect_uri

        if state:
            params["state"] = state

        return f"{self.base_url}/login/oauth/authorize?{urlencode(params)}"

    def exchange_code_for_token(self, code):
        """
        Exchange authorization code for access token
        """
        if not code:
            return None

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
        }

        if self.redirect_uri:
            payload["redirect_uri"] = self.redirect_uri

        headers = {"Accept": "application/json"}

        response = requests.post(
            f"{self.base_url}/login/oauth/access_token", data=payload, headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error exchanging code for token: {response.status_code}")
            return None

    def get_user_info(self, access_token):
        """
        Get authenticated user information
        """
        if not access_token:
            return None

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = requests.get(f"{self.api_url}/user", headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching user info: {response.status_code}")
            return None
