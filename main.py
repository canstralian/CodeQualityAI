"""
GitHub Repository Analyzer - Main Application
"""

import os
import traceback

import streamlit as st

from code_analysis import CodeAnalyzer
from github_api import GitHubRepo
from logger import logger
from utils import (
    create_html_card,
    create_repo_card,
    display_code_with_issues,
    get_file_extension,
    handle_error,
    load_custom_css,
    parse_repo_url,
)
from visualization import (
    visualize_code_quality,
    visualize_commit_history,
    visualize_issues_by_type,
)

# Page configuration
st.set_page_config(
    page_title="GitHub Repository Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS
load_custom_css()

# Initialize session state
if "repo_analyzed" not in st.session_state:
    st.session_state.repo_analyzed = False
if "repo_data" not in st.session_state:
    st.session_state.repo_data = {}
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = {}
if "file_contents" not in st.session_state:
    st.session_state.file_contents = {}
if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = 0


def main():
    """
    Main application entry point.

    This function is responsible for the overall flow of the application,
    including setting up the user interface, handling user inputs, and
    orchestrating the analysis of the GitHub repository.
    """
    logger.info("Starting GitHub Repository Analyzer application")

    # Page header
    st.title("GitHub Repository Analyzer")
    st.markdown(
        """
    Analyze any GitHub repository for code quality, visualize commit history, 
    and get actionable improvement suggestions.
    """
    )

    # Sidebar
    with st.sidebar:
        st.header("Repository Settings")
        repo_url = st.text_input(
            "GitHub Repository URL", value="https://github.com/streamlit/streamlit"
        )

        # Analysis settings
        st.subheader("Analysis Settings")

        file_types = st.multiselect(
            "File Types to Analyze",
            [
                "py",
                "js",
                "ts",
                "jsx",
                "tsx",
                "html",
                "css",
                "java",
                "cpp",
                "c",
                "go",
                "rb",
            ],
            default=["py", "js"],
        )

        analysis_depth = st.select_slider(
            "Analysis Depth", options=["Basic", "Standard", "Deep"], value="Standard"
        )

        max_files = st.slider("Maximum Files to Analyze", 1, 50, 10)

        # GitHub token (optional)
        github_token = os.environ.get("GH_TOKEN")
        if not github_token:
            st.markdown("---")
            st.markdown(
                "ℹ️ **Note:** For higher API rate limits, you can set a GitHub token in your environment variables."
            )

        # Analyze button
        analyze_btn = st.button("Analyze Repository", use_container_width=True)

    # Process repository analysis when button is clicked
    if analyze_btn:
        with st.spinner("Analyzing repository... This may take a few moments."):
            try:
                logger.info(f"Starting analysis of repository: {repo_url}")

                # Parse repository URL
                owner, repo_name = parse_repo_url(repo_url)
                if not owner or not repo_name:
                    logger.error(f"Invalid repository URL: {repo_url}")
                    handle_error(
                        "Invalid GitHub repository URL. Please provide a valid URL."
                    )

                # Initialize GitHub repo
                logger.info(f"Initializing GitHub API client for {owner}/{repo_name}")
                repo = GitHubRepo(owner, repo_name, access_token=github_token)

                # Get repository information
                logger.info(f"Fetching repository information for {owner}/{repo_name}")
                repo_info = repo.get_repo_info()

                # Log comprehensive repository information
                logger.info(f"Successfully retrieved repo: {repo_info['full_name']}")
                logger.debug(
                    f"Repository details: name={repo_info['name']}, owner={owner}, "
                    + f"stars={repo_info['stars']}, forks={repo_info['forks']}, "
                    + f"language={repo_info['language']}, license={repo_info['license']}"
                )

                # Get commit history
                logger.info(f"Fetching commit history for {owner}/{repo_name}")
                commits = repo.get_commit_history(limit=50)
                logger.debug(f"Retrieved {len(commits)} commits")

                # Get repository files for analysis
                logger.info(
                    f"Fetching repository files for analysis (max: {max_files}, types: {file_types})"
                )
                files = repo.get_repository_files(
                    max_files=max_files, file_extensions=file_types
                )
                logger.debug(f"Retrieved {len(files)} files for analysis")

                # Initialize results
                analysis_results = []
                file_contents = {}

                # Initialize code analyzer
                logger.info("Initializing code analyzer")
                analyzer = CodeAnalyzer()

                # Analyze each file
                for i, file_info in enumerate(files):
                    file_path = file_info["path"]
                    logger.info(f"Processing file {i+1}/{len(files)}: {file_path}")

                    try:
                        # Skip if file is in excluded directories
                        excluded_dirs = [
                            "node_modules",
                            "venv",
                            ".git",
                            "__pycache__",
                            "dist",
                            "build",
                        ]
                        if any(
                            excluded_dir in file_path for excluded_dir in excluded_dirs
                        ):
                            logger.debug(
                                f"Skipping excluded directory file: {file_path}"
                            )
                            continue

                        # Get file content
                        logger.debug(f"Fetching content for {file_path}")
                        content = repo.get_file_content(file_path)
                        if not content:
                            logger.warning(f"No content retrieved for {file_path}")
                            continue

                        # Store file content
                        file_contents[file_path] = content

                        # Get file extension
                        extension = get_file_extension(file_path)
                        logger.debug(f"File extension for {file_path}: {extension}")

                        # Analyze code quality
                        logger.debug(
                            f"Analyzing code quality for {file_path} with {analysis_depth} depth"
                        )
                        result = analyzer.analyze_code(
                            code=content,
                            filename=file_path,
                            file_extension=extension,
                            depth=analysis_depth,
                        )

                        # Store results
                        analysis_results.append(
                            {
                                "file_path": file_path,
                                "extension": extension,
                                "result": result,
                            }
                        )
                        logger.debug(
                            f"Analysis complete for {file_path}: score={result['score']}, issues={len(result['issues'])}"
                        )

                    except Exception as file_error:
                        logger.error(
                            f"Error processing file {file_path}: {str(file_error)}"
                        )
                        logger.debug(
                            f"File processing error details: {traceback.format_exc()}"
                        )
                        # Continue with other files even if one fails
                        continue

                logger.info(
                    f"Analysis complete. Processed {len(analysis_results)} files"
                )

                # Store data in session state
                st.session_state.repo_data = {
                    "info": repo_info,
                    "commits": commits,
                    "files": files,
                }
                st.session_state.analysis_results = analysis_results
                st.session_state.file_contents = file_contents
                st.session_state.repo_analyzed = True

                # Reset selected tab
                st.session_state.selected_tab = 0

                logger.info("Successfully completed repository analysis")

                # Force a rerun to show results
                st.rerun()

            except Exception as e:
                logger.error(f"Fatal error during repository analysis: {str(e)}")
                logger.debug(f"Analysis error details: {traceback.format_exc()}")
                logger.error(f"Application error: {str(e)}")
                handle_error(str(e))

    # Display results if repository has been analyzed
    if st.session_state.repo_analyzed:
        display_results()


def display_results():
    """
    Display the analysis results in the Streamlit application.

    This function is responsible for creating the tabs and organizing the
    different sections of the application, such as the Repository Overview,
    Code Quality Analysis, Commit History, and Improvement Suggestions.
    """

    # Get data from session state
    repo_data = st.session_state.repo_data
    analysis_results = st.session_state.analysis_results
    file_contents = st.session_state.file_contents

    # Create tabs for different sections
    tabs = st.tabs(
        [
            "Repository Overview",
            "Code Quality Analysis",
            "Commit History",
            "Improvement Suggestions",
        ]
    )

    # Tab 1: Repository Overview
    with tabs[0]:
        st.header("Repository Overview")

        # Repository info card
        repo_info = repo_data["info"]
        st.markdown(create_repo_card(repo_info), unsafe_allow_html=True)

        # Repository stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Files Analyzed", len(analysis_results))
        with col2:
            avg_quality = (
                sum(result["result"]["score"] for result in analysis_results)
                / len(analysis_results)
                if analysis_results
                else 0
            )
            st.metric("Average Quality Score", f"{avg_quality:.1f}/10")
        with col3:
            st.metric("Commits", len(repo_data["commits"]))

        # Recent commits
        st.subheader("Recent Commits")
        commit_data = []
        for commit in repo_data["commits"][:5]:  # Show only 5 most recent
            commit_data.append(
                {
                    "Author": commit["author"],
                    "Date": commit["date"][:10],  # Show only date
                    "Message": commit["message"],
                }
            )

        st.dataframe(commit_data)

        # File list
        st.subheader("Analyzed Files")

        file_list = []
        for result in analysis_results:
            file_path = result["file_path"]
            quality_score = result["result"]["score"]

            # Determine score class
            score_class = "low"
            if quality_score >= 7:
                score_class = "high"
            elif quality_score >= 4:
                score_class = "medium"

            score_html = f'<span class="score-badge score-{score_class}">{quality_score}/10</span>'

            file_list.append(
                {
                    "File": file_path,
                    "Score": score_html,
                    "Issues": len(result["result"]["issues"]),
                }
            )

        # Convert to DataFrame for display
        import pandas as pd

        df = pd.DataFrame(file_list)

        # Use custom HTML for score column
        st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

    # Tab 2: Code Quality Analysis
    with tabs[1]:
        st.header("Code Quality Analysis")

        # Quality score distribution visualization
        st.subheader("Quality Score Distribution")
        quality_fig = visualize_code_quality(analysis_results)
        st.plotly_chart(quality_fig, use_container_width=True)

        # Issues by type visualization
        st.subheader("Issues by Type")

        # Flatten all issues
        all_issues = []
        for result in analysis_results:
            for issue in result["result"]["issues"]:
                all_issues.append(issue)

        if all_issues:
            issues_fig = visualize_issues_by_type(all_issues)
            st.plotly_chart(issues_fig, use_container_width=True)
        else:
            st.info("No issues detected in the analyzed files.")

        # File selection for detailed analysis
        st.subheader("Detailed File Analysis")
        file_options = [result["file_path"] for result in analysis_results]

        if file_options:
            selected_file = st.selectbox("Select a file to analyze", file_options)

            # Get analysis result for selected file
            file_result = next(
                (
                    result
                    for result in analysis_results
                    if result["file_path"] == selected_file
                ),
                None,
            )

            if file_result:
                st.markdown(f"**Quality Score:** {file_result['result']['score']}/10")

                # Display issues
                if file_result["result"]["issues"]:
                    st.markdown("**Issues:**")

                    for issue in file_result["result"]["issues"]:
                        severity = issue.get("severity", "error")
                        st.markdown(
                            create_html_card(
                                title=f"Line {issue.get('line', 'N/A')}: {issue.get('type', 'Issue')}",
                                content=issue.get("message", "No description"),
                                card_type=severity,
                            ),
                            unsafe_allow_html=True,
                        )

                    # Display code with issues highlighted
                    st.markdown("**Code:**")
                    code = file_contents.get(selected_file, "")
                    st.markdown(
                        display_code_with_issues(code, file_result["result"]["issues"]),
                        unsafe_allow_html=True,
                    )
                else:
                    st.success("No issues detected in this file.")

    # Tab 3: Commit History
    with tabs[2]:
        st.header("Commit History")

        # Commit history visualization
        commits_fig = visualize_commit_history(repo_data["commits"])
        st.plotly_chart(commits_fig, use_container_width=True)

        # Commit list
        st.subheader("Commit Details")

        commit_details = []
        for commit in repo_data["commits"]:
            commit_details.append(
                {
                    "Hash": commit["hash"][:7],
                    "Author": commit["author"],
                    "Date": commit["date"],
                    "Message": commit["message"],
                }
            )

        # Convert to DataFrame for display
        import pandas as pd

        commit_df = pd.DataFrame(commit_details)
        st.dataframe(commit_df)

    # Tab 4: Improvement Suggestions
    with tabs[3]:
        st.header("Improvement Suggestions")

        # Get all files with issues
        files_with_issues = [
            result
            for result in analysis_results
            if result["result"]["issues"] and len(result["result"]["issues"]) > 0
        ]

        if files_with_issues:
            # Sort files by number of issues (most to least)
            files_with_issues.sort(
                key=lambda x: len(x["result"]["issues"]), reverse=True
            )

            for result in files_with_issues:
                file_path = result["file_path"]
                issues = result["result"]["issues"]
                suggestions = result["result"].get("suggestions", [])

                st.subheader(file_path)

                # Display score
                quality_score = result["result"]["score"]
                score_class = "low"
                if quality_score >= 7:
                    score_class = "high"
                elif quality_score >= 4:
                    score_class = "medium"

                st.markdown(
                    f"**Quality Score:** <span class='score-badge score-{score_class}'>{quality_score}/10</span>",
                    unsafe_allow_html=True,
                )

                # Display suggestions
                if suggestions:
                    for suggestion in suggestions:
                        st.markdown(
                            create_html_card(
                                title=suggestion.get("title", "Suggestion"),
                                content=suggestion.get("description", "No description"),
                                card_type="info",
                            ),
                            unsafe_allow_html=True,
                        )

                        # Show example if provided
                        if "example" in suggestion:
                            with st.expander("Show Example"):
                                st.code(
                                    suggestion["example"], language=result["extension"]
                                )
                else:
                    # Generate generic suggestions if none provided
                    if issues:
                        st.markdown("**General Suggestions:**")

                        # Group issues by type
                        issue_types = {}
                        for issue in issues:
                            issue_type = issue.get("type", "Unknown")
                            if issue_type not in issue_types:
                                issue_types[issue_type] = []
                            issue_types[issue_type].append(issue)

                        # Generate suggestions for each issue type
                        for issue_type, type_issues in issue_types.items():
                            if issue_type == "Long function":
                                st.markdown(
                                    create_html_card(
                                        title="Refactor Long Functions",
                                        content="Consider breaking down long functions into smaller, more focused functions that each do one thing well.",
                                        card_type="info",
                                    ),
                                    unsafe_allow_html=True,
                                )

                            elif issue_type == "Complex code":
                                st.markdown(
                                    create_html_card(
                                        title="Reduce Complexity",
                                        content="Simplify complex code by breaking it down, removing nested conditions, and using helper functions.",
                                        card_type="info",
                                    ),
                                    unsafe_allow_html=True,
                                )

                            elif issue_type == "Inconsistent naming":
                                st.markdown(
                                    create_html_card(
                                        title="Standardize Naming Conventions",
                                        content="Use consistent naming patterns throughout your codebase for better readability.",
                                        card_type="info",
                                    ),
                                    unsafe_allow_html=True,
                                )

                            elif issue_type == "Missing documentation":
                                st.markdown(
                                    create_html_card(
                                        title="Add Documentation",
                                        content="Add docstrings, comments, and type hints to improve code clarity and maintainability.",
                                        card_type="info",
                                    ),
                                    unsafe_allow_html=True,
                                )

                            elif issue_type == "Potential security issue":
                                st.markdown(
                                    create_html_card(
                                        title="Improve Security",
                                        content="Address security vulnerabilities by validating inputs, using secure libraries, and following security best practices.",
                                        card_type="error",
                                    ),
                                    unsafe_allow_html=True,
                                )

                            else:
                                st.markdown(
                                    create_html_card(
                                        title=f"Fix {issue_type} Issues",
                                        content=f"Address the {len(type_issues)} identified issues of this type to improve code quality.",
                                        card_type="info",
                                    ),
                                    unsafe_allow_html=True,
                                )
        else:
            st.success("No issues detected in the analyzed files. Great job!")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <footer>
            <p>GitHub Repository Analyzer | MIT License | Created with ❤️ by Replit</p>
            <p><img alt="Duplicate this       Space" src="https://huggingface.co/datasets/huggingface/badges/resolve/main/duplicate-this-space-xl.svg"></p>
        </footer>
        """,
        unsafe_allow_html=True,
    )