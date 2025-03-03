"""
GitHub Repository API Interface
"""

import base64
import time
import traceback

import requests

from logger import logger
from utils import format_commit_message, get_file_extension, handle_error, truncate_text


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
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}

        # Add token if provided
        if access_token:
            self.headers["Authorization"] = f"token {access_token}"

    def _make_request(self, endpoint, params=None, method="GET"):
        """
        Make a request to the GitHub API with rate limit handling

        Args:
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            method (str, optional): HTTP method

        Returns:
            dict or list: Response data
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"Making GitHub API request: {method} {url}")

        try:
            # Set timeout to avoid hanging requests (10 seconds for connection, 30 seconds for read)
            timeout = (10, 30)
            
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=timeout)
            else:
                response = requests.request(
                    method, url, headers=self.headers, json=params, timeout=timeout
                )

            logger.debug(f"GitHub API response status: {response.status_code}")
            
            # Check if response is JSON before proceeding
            content_type = response.headers.get("Content-Type", "")
            is_json_response = "application/json" in content_type or response.text.strip().startswith(("{", "["))
            
            if not is_json_response and response.status_code == 200:
                logger.warning(f"Non-JSON response received from GitHub API: {content_type}")

            # Handle various API response codes
            if response.status_code >= 400:
                # Handle rate limiting
                if (
                    response.status_code == 403
                    and "X-RateLimit-Remaining" in response.headers
                    and int(response.headers["X-RateLimit-Remaining"]) == 0
                ):
                    reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                    current_time = int(time.time())
                    wait_time = max(reset_time - current_time, 0) + 1
                    
                    # Cap the maximum wait time to 5 minutes (300 seconds)
                    max_wait_time = 300
                    sleep_time = min(wait_time, max_wait_time)

                    logger.warning(
                        f"GitHub API rate limit exceeded. Reset in {wait_time} seconds, waiting {sleep_time} seconds"
                    )

                    if wait_time > max_wait_time:
                        logger.error(
                            f"GitHub API rate limit exceeded with long reset time ({wait_time}s)"
                        )
                        handle_error(
                            "GitHub API rate limit exceeded. Please try again later or use a GitHub token."
                        )

                    logger.info(f"Waiting for rate limit reset: {sleep_time} seconds")
                    time.sleep(sleep_time)
                    logger.info("Retrying request after rate limit wait")
                    
                    # Use an iterative approach instead of recursion to avoid stack overflow
                    for retry_attempt in range(3):  # Limit retries to 3 attempts
                        logger.info(f"Retry attempt {retry_attempt + 1} for {endpoint}")
                        retry_response = requests.get(url, headers=self.headers, params=params) if method == "GET" else requests.request(method, url, headers=self.headers, json=params)
                        
                        if retry_response.status_code == 200:
                            logger.info(f"Retry successful for {endpoint}")
                            return retry_response.json()
                        
                        if retry_response.status_code != 403 or int(retry_response.headers.get("X-RateLimit-Remaining", 1)) > 0:
                            # If the error is not rate limiting, break and let the regular error handling take over
                            break
                            
                        # Exponential backoff
                        backoff_time = min(2 ** retry_attempt * 5, 60)  # 5s, 10s, 20s up to 60s max
                        logger.info(f"Rate limit still exceeded, backing off for {backoff_time}s")
                        time.sleep(backoff_time)
                    
                    # If we get here, the retries failed
                    logger.error(f"Failed to recover from rate limit after retries for {endpoint}")
                    handle_error("GitHub API rate limit exceeded. Please try again later or use a GitHub token with higher limits.")

                # Handle permission errors
                elif response.status_code == 401:
                    logger.error(f"Authentication error: Invalid or expired token")
                    handle_error(
                        "GitHub API authentication failed. Please check your access token."
                    )
                elif (
                    response.status_code == 403
                    and "X-RateLimit-Remaining" not in response.headers
                ):
                    logger.error(
                        f"Permission denied: Insufficient permissions for {url}"
                    )
                    handle_error(
                        "Permission denied. Your token may not have the required permissions."
                    )
                elif response.status_code == 404:
                    logger.error(f"Resource not found: {url}")
                    handle_error(
                        f"GitHub resource not found. Please check that the repository exists and is accessible."
                    )

            # Check for successful response
            response.raise_for_status()

            logger.debug(f"GitHub API request successful: {method} {url}")
            return response.json()

        except requests.exceptions.Timeout as timeout_err:
            error_message = f"Timeout accessing GitHub API: {str(timeout_err)}"
            logger.error(f"GitHub API request timed out: {error_message}")
            logger.debug(f"Timeout details: {traceback.format_exc()}")
            handle_error(f"GitHub API request timed out. Please try again later. ({str(timeout_err)})")
            
        except requests.exceptions.ConnectionError as conn_err:
            error_message = f"Connection error accessing GitHub API: {str(conn_err)}"
            logger.error(f"GitHub API connection failed: {error_message}")
            logger.debug(f"Connection error details: {traceback.format_exc()}")
            handle_error(f"GitHub API connection failed. Please check your network connection. ({str(conn_err)})")
            
        except requests.exceptions.RequestException as e:
            error_message = f"Error accessing GitHub API: {str(e)}"
            logger.error(f"GitHub API request failed: {error_message}")

            try:
                if hasattr(e, 'response') and e.response is not None:
                    if "application/json" in e.response.headers.get("Content-Type", ""):
                        error_data = e.response.json()
                        if "message" in error_data:
                            error_message = f"GitHub API Error: {error_data['message']}"
                            logger.error(f"GitHub API error message: {error_data['message']}")
                            
                            # Check for specific GitHub error codes
                            if "documentation_url" in error_data:
                                logger.info(f"GitHub API documentation reference: {error_data['documentation_url']}")
            except (ValueError, AttributeError) as json_err:
                logger.debug(f"Could not parse error response as JSON: {str(json_err)}")

            logger.debug(f"GitHub API error details: {traceback.format_exc()}")
            handle_error(error_message)

    def get_repo_info(self):
        """
        Get basic information about the repository

        Returns:
            dict: Repository information
        """
        if hasattr(self, '_repo_info_cache'):
            return self._repo_info_cache

        endpoint = f"/repos/{self.owner}/{self.repo_name}"
        data = self._make_request(endpoint)

        repo_info = {
            "name": data.get("name", ""),
            "full_name": data.get("full_name", ""),
            "description": data.get("description", "No description"),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "watchers": data.get("watchers_count", 0),
            "language": data.get("language", "Not specified"),
            "created_at": data.get("created_at", ""),
            "updated_at": data.get("updated_at", ""),
            "default_branch": data.get("default_branch", "main"),
            "license": data.get("license", {}).get("name", "No license"),
            "url": data.get("html_url", ""),
        }

        # Cache the repository information
        self._repo_info_cache = repo_info
        return repo_info

    def get_commit_history(self, limit=100):
        """
        Get commit history for the repository

        Args:
            limit (int, optional): Maximum number of commits to retrieve

        Returns:
            list: List of commit data
        """
        endpoint = f"/repos/{self.owner}/{self.repo_name}/commits"
        params = {"per_page": min(limit, 100)}  # GitHub API limit is 100 per page

        commits_data = []
        page = 1

        while len(commits_data) < limit:
            params["page"] = page
            page_data = self._make_request(endpoint, params)

            if not page_data:
                break

            for commit in page_data:
                # Extract commit information
                commit_info = {
                    "hash": commit.get("sha", ""),
                    "author": commit.get("commit", {})
                    .get("author", {})
                    .get("name", "Unknown"),
                    "email": commit.get("commit", {})
                    .get("author", {})
                    .get("email", ""),
                    "date": commit.get("commit", {}).get("author", {}).get("date", ""),
                    "message": format_commit_message(
                        commit.get("commit", {}).get("message", "")
                    ),
                    "url": commit.get("html_url", ""),
                }

                commits_data.append(commit_info)

                if len(commits_data) >= limit:
                    break

            page += 1

            # If we got fewer results than requested, we've reached the end
            if len(page_data) < params["per_page"]:
                break

        return commits_data

    def get_repository_files(self, max_files=10, file_extensions=None):
        """
        Get files from the repository for analysis

        Args:
            max_files (int, optional): Maximum number of files to retrieve
            file_extensions (list, optional): List of file extensions to include

        Returns:
            list: List of file data
        """
        # Get default branch
        repo_info = self.get_repo_info()
        branch = repo_info.get("default_branch", "main")

        # Get tree recursively
        endpoint = f"/repos/{self.owner}/{self.repo_name}/git/trees/{branch}"
        params = {"recursive": 1}

        try:
            tree_data = self._make_request(endpoint, params)

            # Filter for files with the specified extensions
            files = []
            for item in tree_data.get("tree", []):
                if item.get("type") == "blob":
                    path = item.get("path", "")

                    # Skip if no file extensions provided
                    if file_extensions is None:
                        files.append(
                            {
                                "path": path,
                                "size": item.get("size", 0),
                                "url": item.get("url", ""),
                            }
                        )
                        continue

                    # Check file extension
                    ext = get_file_extension(path)
                    if ext in file_extensions:
                        files.append(
                            {
                                "path": path,
                                "size": item.get("size", 0),
                                "url": item.get("url", ""),
                            }
                        )

                    # Break if we have enough files
                    if len(files) >= max_files:
                        break

            return files[:max_files]

        except Exception as e:
            # If tree is too large, fallback to listing directories
            if str(e).find("Git Repository is empty") != -1:
                handle_error("This repository appears to be empty.")

            # Fallback to getting a limited set of files from the API
            return self._fallback_get_files(branch, max_files, file_extensions)

    def _fallback_get_files(self, branch, max_files, file_extensions):
        """
        Fallback method to get files when tree is too large
        """
        endpoint = f"/repos/{self.owner}/{self.repo_name}/contents"
        params = {"ref": branch}

        files = []
        dirs_to_check = [""]  # Start with root

        while dirs_to_check and len(files) < max_files:
            current_dir = dirs_to_check.pop(0)

            # Adjust endpoint for subdirectories
            current_endpoint = endpoint
            if current_dir:
                current_endpoint = f"{endpoint}/{current_dir}"

            try:
                contents = self._make_request(current_endpoint, params)

                for item in contents:
                    if len(files) >= max_files:
                        break

                    item_path = item.get("path", "")

                    if item.get("type") == "file":
                        # Check file extension
                        if file_extensions is None:
                            files.append(
                                {
                                    "path": item_path,
                                    "size": item.get("size", 0),
                                    "url": item.get("url", ""),
                                }
                            )
                        else:
                            ext = get_file_extension(item_path)
                            if ext in file_extensions:
                                files.append(
                                    {
                                        "path": item_path,
                                        "size": item.get("size", 0),
                                        "url": item.get("url", ""),
                                    }
                                )

                    elif item.get("type") == "dir":
                        # Add directory to the queue (breadth-first search)
                        dirs_to_check.append(item_path)

            except:
                # Skip directories that cannot be accessed
                continue

        return files[:max_files]

    def get_file_content(self, file_path):
        """
        Get the content of a specific file

        Args:
            file_path (str): Path to the file in the repository

        Returns:
            str: File content or None if the file cannot be retrieved
        """
        # Check if content is already cached
        cache_key = f"{self.owner}/{self.repo_name}/{file_path}"
        if hasattr(self, '_file_content_cache') and cache_key in self._file_content_cache:
            logger.debug(f"Using cached content for {file_path}")
            return self._file_content_cache[cache_key]
        
        # Initialize cache if it doesn't exist
        if not hasattr(self, '_file_content_cache'):
            self._file_content_cache = {}
            
        endpoint = f"/repos/{self.owner}/{self.repo_name}/contents/{file_path}"

        try:
            data = self._make_request(endpoint)

            if data.get("type") != "file":
                logger.warning(f"Requested path is not a file: {file_path}")
                return None

            # Decode content from base64
            content = data.get("content", "")
            if content:
                try:
                    content = base64.b64decode(content.replace("\n", "")).decode("utf-8")
                    # Cache the content
                    self._file_content_cache[cache_key] = content
                    return content
                except UnicodeDecodeError as ude:
                    logger.error(f"Failed to decode file content for {file_path}: {str(ude)}")
                    return None

            logger.warning(f"No content found for file: {file_path}")
            return None

        except Exception as e:
            # If the file is too large, use the blob API
            if "This API returns blobs up to 1 MB in size" in str(e):
                logger.info(f"File too large, using blob API for: {file_path}")
                content = self._get_large_file_content(file_path)
                if content:
                    # Cache the content from blob API
                    self._file_content_cache[cache_key] = content
                return content

            # For other errors, log and return None
            logger.error(f"Error getting file content for {file_path}: {str(e)}")
            return None

    def _get_large_file_content(self, file_path):
        """
        Get content of a large file using the blob API

        Args:
            file_path (str): Path to the file in the repository

        Returns:
            str: File content or None if the file cannot be retrieved
        """
        # Cache key for storing results
        cache_key = f"{self.owner}/{self.repo_name}/{file_path}"
        
        # Use cached repo_info if available to reduce API calls
        if hasattr(self, '_repo_info_cache'):
            repo_info = self._repo_info_cache
            logger.debug(f"Using cached repo info for blob retrieval of {file_path}")
        else:
            logger.debug(f"Fetching repo info for blob retrieval of {file_path}")
            repo_info = self.get_repo_info()
            
        branch = repo_info.get("default_branch", "main")

        endpoint = f"/repos/{self.owner}/{self.repo_name}/contents/{file_path}"
        params = {"ref": branch}

        try:
            data = self._make_request(endpoint, params)

            if not data or "sha" not in data:
                logger.warning(f"Could not retrieve SHA for file {file_path}")
                return None

            file_sha = data.get("sha")
            logger.debug(f"Retrieved SHA {file_sha} for file {file_path}")

            # Get the blob
            blob_endpoint = f"/repos/{self.owner}/{self.repo_name}/git/blobs/{file_sha}"
            blob_data = self._make_request(blob_endpoint)

            if not blob_data:
                logger.warning(f"Could not retrieve blob data for file {file_path}")
                return None

            # Decode content from base64
            content = blob_data.get("content", "")
            if not content:
                logger.warning(f"No content in blob for file {file_path}")
                return None
                
            # This might be base64-encoded, so decode it
            try:
                decoded_content = base64.b64decode(content.replace("\n", "")).decode("utf-8")
                # Store in cache
                if not hasattr(self, '_file_content_cache'):
                    self._file_content_cache = {}
                self._file_content_cache[cache_key] = decoded_content
                return decoded_content
            except UnicodeDecodeError as ude:
                logger.error(f"Failed to decode blob content for {file_path}: {str(ude)}")
                return None
            except Exception as e:
                logger.error(f"Error processing blob content for {file_path}: {str(e)}")
                # Return the raw content if we can't decode it
                return content

        except Exception as e:
            logger.error(f"Error retrieving large file {file_path}: {str(e)}")
            logger.debug(f"Large file retrieval error details: {traceback.format_exc()}")
            return None