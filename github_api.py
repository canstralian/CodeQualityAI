import streamlit as st
import requests
import base64
import json
from datetime import datetime
import re
import time
import os

class GitHubRepo:
    """
    Class to interact with GitHub repositories using the GitHub REST API
    """
    
    def __init__(self, owner, repo_name, access_token=None):
        """
        Initialize with repository owner and name
        
        Args:
            owner (str): Repository owner
            repo_name (str): Repository name
            access_token (str, optional): OAuth access token for authenticated requests
        """
        self.owner = owner
        self.repo_name = repo_name
        self.api_token = access_token or os.getenv("GITHUB_TOKEN", "")
        self.base_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        
        # Set up headers for API requests
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        if self.api_token:
            # Use Bearer authentication if it's an OAuth token
            if access_token:
                self.headers["Authorization"] = f"Bearer {self.api_token}"
            else:
                self.headers["Authorization"] = f"token {self.api_token}"
            self.authenticated = True
        else:
            self.authenticated = False
            st.warning("No GitHub token provided. API rate limits will be restricted. Please sign in with GitHub for better performance.")
        
        # Verify repository exists
        try:
            response = requests.get(self.base_url, headers=self.headers)
            if response.status_code == 404:
                raise Exception(f"Repository {owner}/{repo_name} not found. Please check the URL and try again.")
            elif response.status_code == 403:
                if 'X-RateLimit-Remaining' in response.headers and int(response.headers['X-RateLimit-Remaining']) == 0:
                    raise Exception("GitHub API rate limit exceeded. Please try again later or provide a token.")
                else:
                    raise Exception("Access forbidden. You might need to provide a valid GitHub token.")
            elif response.status_code != 200:
                raise Exception(f"GitHub API error: {response.status_code}")
            
            # Store repository data
            self.repo_data = response.json()
            
        except requests.RequestException as e:
            raise Exception(f"Error connecting to GitHub API: {str(e)}")
    
    def get_repo_info(self):
        """
        Get basic information about the repository
        """
        try:
            # Format dates
            created_at = datetime.strptime(self.repo_data['created_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
            updated_at = datetime.strptime(self.repo_data['updated_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
            
            # Get license info
            license_name = "Not specified"
            if self.repo_data.get('license') and isinstance(self.repo_data['license'], dict):
                license_name = self.repo_data['license'].get('name', "Not specified")
            
            # Get topics
            topics_url = f"{self.base_url}/topics"
            topics_response = requests.get(topics_url, headers=self.headers)
            topics = []
            if topics_response.status_code == 200:
                topics_data = topics_response.json()
                topics = topics_data.get('names', [])
            
            return {
                "name": self.repo_data['name'],
                "full_name": self.repo_data['full_name'],
                "description": self.repo_data.get('description') or "No description provided",
                "owner": self.repo_data['owner']['login'],
                "stars": self.repo_data['stargazers_count'],
                "forks": self.repo_data['forks_count'],
                "open_issues": self.repo_data['open_issues_count'],
                "language": self.repo_data.get('language') or "Not specified",
                "created_at": created_at,
                "updated_at": updated_at,
                "license": license_name,
                "topics": topics,
                "url": self.repo_data['html_url']
            }
        except Exception as e:
            raise Exception(f"Error fetching repository information: {str(e)}")
    
    def get_commit_history(self, limit=100):
        """
        Get commit history for the repository
        """
        try:
            commits_url = f"{self.base_url}/commits"
            params = {"per_page": min(100, limit), "page": 1}
            
            commits = []
            total_commits = 0
            
            while total_commits < limit:
                response = requests.get(commits_url, headers=self.headers, params=params)
                
                if response.status_code != 200:
                    break
                
                commit_data = response.json()
                if not commit_data:
                    break
                
                for commit in commit_data:
                    # Format date
                    date = datetime.strptime(
                        commit['commit']['author']['date'], 
                        "%Y-%m-%dT%H:%M:%SZ"
                    ).strftime("%Y-%m-%d")
                    
                    # Get files changed
                    files_changed = 0
                    commit_detail_url = commit['url']
                    commit_detail_response = requests.get(commit_detail_url, headers=self.headers)
                    if commit_detail_response.status_code == 200:
                        commit_detail = commit_detail_response.json()
                        files_changed = len(commit_detail.get('files', []))
                    
                    # Add commit info
                    commits.append({
                        "sha": commit['sha'],
                        "author": commit['commit']['author']['name'],
                        "email": commit['commit']['author']['email'],
                        "date": date,
                        "message": commit['commit']['message'],
                        "url": commit['html_url'],
                        "files_changed": files_changed
                    })
                    
                    total_commits += 1
                    if total_commits >= limit:
                        break
                
                params["page"] += 1
                
                # Add a small delay to avoid hitting rate limits
                time.sleep(0.5)
            
            return commits
            
        except Exception as e:
            raise Exception(f"Error fetching commit history: {str(e)}")
    
    def get_repository_files(self, max_files=10, file_extensions=None):
        """
        Get files from the repository for analysis
        """
        try:
            files = []
            contents_stack = [{"path": ""}]  # Start with root directory
            
            while contents_stack and len(files) < max_files:
                current = contents_stack.pop(0)
                current_path = current["path"]
                
                # Get contents of current directory
                contents_url = f"{self.base_url}/contents/{current_path}"
                response = requests.get(contents_url, headers=self.headers)
                
                if response.status_code != 200:
                    continue
                
                contents = response.json()
                
                # Handle both single file and directory listing responses
                if not isinstance(contents, list):
                    contents = [contents]
                
                for item in contents:
                    # Skip directories, process them separately
                    if item['type'] == "dir":
                        contents_stack.append({"path": item['path']})
                    elif item['type'] == "file":
                        # Only process files with the specified extensions
                        file_extension = item['name'].split('.')[-1].lower() if '.' in item['name'] else ""
                        
                        if file_extensions and file_extension not in file_extensions:
                            continue
                        
                        # Skip very large files
                        if item['size'] > 500000:  # Skip files larger than ~500KB
                            continue
                        
                        files.append({
                            "name": item['name'],
                            "path": item['path'],
                            "sha": item['sha'],
                            "size": item['size'],
                            "url": item['html_url'],
                            "extension": file_extension
                        })
                        
                        # Stop if we've reached the limit
                        if len(files) >= max_files:
                            break
                
                # Add a small delay to avoid hitting rate limits
                time.sleep(0.5)
            
            return files
            
        except Exception as e:
            raise Exception(f"Error fetching repository files: {str(e)}")
    
    def get_file_content(self, file_path):
        """
        Get the content of a specific file
        """
        try:
            content_url = f"{self.base_url}/contents/{file_path}"
            response = requests.get(content_url, headers=self.headers)
            
            if response.status_code != 200:
                raise Exception(f"Error fetching file: {response.status_code}")
            
            content_data = response.json()
            
            # Decode content from base64
            if content_data.get('encoding') == "base64":
                try:
                    decoded_content = base64.b64decode(content_data['content']).decode('utf-8', errors='replace')
                    return decoded_content
                except UnicodeDecodeError:
                    # Return placeholder for binary files
                    return f"[Binary file: {file_path}]"
            else:
                return f"[Unsupported encoding: {content_data.get('encoding', 'unknown')}]"
                
        except Exception as e:
            raise Exception(f"Error fetching file content: {str(e)}")
