import streamlit as st
import pandas as pd
import os
import time
from github_api import GitHubRepo
from code_analysis import CodeAnalyzer
from visualization import visualize_commit_history, visualize_code_quality
from utils import load_custom_css, parse_repo_url, handle_error

# Page configuration
st.set_page_config(
    page_title="GitHub Repository Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_custom_css()

# App title and description
st.markdown('<h1 class="main-title">GitHub Repository Analyzer</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Analyze GitHub repositories, get code quality insights and improvement suggestions</p>', 
    unsafe_allow_html=True
)

# Sidebar for inputs
with st.sidebar:
    st.markdown('<h2 class="sidebar-title">Repository Settings</h2>', unsafe_allow_html=True)
    
    # GitHub repository URL input
    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/username/repository",
        help="Enter the full URL of the GitHub repository you want to analyze"
    )
    
    # Analysis options
    st.markdown('<h3 class="sidebar-section">Analysis Options</h3>', unsafe_allow_html=True)
    
    analyze_commits = st.checkbox("Analyze Commit History", value=True)
    analyze_code_quality = st.checkbox("Analyze Code Quality", value=True)
    
    # Number of files to analyze (for performance)
    max_files = st.slider(
        "Maximum files to analyze", 
        min_value=1, 
        max_value=20, 
        value=5,
        help="Limit the number of files to analyze for performance reasons"
    )
    
    # Specific file types to focus on
    file_types = st.multiselect(
        "File types to analyze",
        options=["py", "js", "ts", "java", "go", "cpp", "c", "cs", "php", "rb"],
        default=["py", "js", "java"],
        help="Select specific file extensions to focus the analysis"
    )
    
    # Analysis depth
    analysis_depth = st.select_slider(
        "Analysis depth",
        options=["Basic", "Standard", "Deep"],
        value="Standard",
        help="Deeper analysis takes more time but provides more insights"
    )
    
    # Start analysis button
    analyze_button = st.button("Analyze Repository", type="primary")

# Main content area
if repo_url and analyze_button:
    try:
        # Parse repository URL
        owner, repo_name = parse_repo_url(repo_url)
        if not owner or not repo_name:
            st.error("Invalid GitHub repository URL. Please enter a valid URL in the format: https://github.com/username/repository")
        else:
            # Initialize GitHub API client and repository analyzer
            with st.spinner("Fetching repository data..."):
                github_repo = GitHubRepo(owner, repo_name)
                repo_info = github_repo.get_repo_info()
                
                # Display repository info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"<div class='repo-card'><h3>{repo_info['name']}</h3><p>{repo_info['description']}</p></div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div class='stat-card'><p>⭐ Stars</p><h4>{repo_info['stars']}</h4></div>", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<div class='stat-card'><p>🍴 Forks</p><h4>{repo_info['forks']}</h4></div>", unsafe_allow_html=True)
                
                # Tabs for different analysis sections
                tab1, tab2, tab3 = st.tabs(["Repository Overview", "Code Quality Analysis", "Improvement Suggestions"])
                
                # Tab 1: Repository Overview
                with tab1:
                    st.markdown("<h2>Repository Overview</h2>", unsafe_allow_html=True)
                    
                    # Display repository details
                    st.markdown("<h3>Repository Details</h3>", unsafe_allow_html=True)
                    details_col1, details_col2 = st.columns(2)
                    
                    with details_col1:
                        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
                        st.markdown(f"<p><strong>Owner:</strong> {repo_info['owner']}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p><strong>Created:</strong> {repo_info['created_at']}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p><strong>Last Updated:</strong> {repo_info['updated_at']}</p>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with details_col2:
                        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
                        st.markdown(f"<p><strong>Language:</strong> {repo_info['language']}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p><strong>Open Issues:</strong> {repo_info['open_issues']}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p><strong>License:</strong> {repo_info.get('license', 'Not specified')}</p>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Commit history analysis
                    if analyze_commits:
                        st.markdown("<h3>Commit History Analysis</h3>", unsafe_allow_html=True)
                        with st.spinner("Analyzing commit history..."):
                            commits = github_repo.get_commit_history()
                            
                            # Display commit statistics
                            st.markdown(f"<p>Total commits: <strong>{len(commits)}</strong></p>", unsafe_allow_html=True)
                            
                            # Visualize commit history
                            commit_fig = visualize_commit_history(commits)
                            st.plotly_chart(commit_fig, use_container_width=True)
                            
                            # Recent commits table
                            st.markdown("<h4>Recent Commits</h4>", unsafe_allow_html=True)
                            recent_commits = commits[:5]  # Show only 5 most recent commits
                            
                            # Convert to DataFrame for display
                            commit_df = pd.DataFrame([
                                {
                                    "Author": commit['author'],
                                    "Date": commit['date'],
                                    "Message": commit['message'],
                                    "Files Changed": commit['files_changed']
                                } for commit in recent_commits
                            ])
                            
                            st.dataframe(commit_df, use_container_width=True)
                
                # Tab 2: Code Quality Analysis
                with tab2:
                    if analyze_code_quality:
                        st.markdown("<h2>Code Quality Analysis</h2>", unsafe_allow_html=True)
                        
                        with st.spinner("Analyzing code quality... This might take a while depending on repository size."):
                            # Get repository files for analysis
                            files = github_repo.get_repository_files(max_files=max_files, file_extensions=file_types)
                            
                            if not files:
                                st.warning("No matching files found for analysis. Try selecting different file types.")
                            else:
                                # Initialize code analyzer
                                code_analyzer = CodeAnalyzer()
                                
                                # Progress bar for analysis
                                progress_bar = st.progress(0)
                                file_results = []
                                
                                for i, file in enumerate(files):
                                    # Update progress
                                    progress = (i + 1) / len(files)
                                    progress_bar.progress(progress)
                                    
                                    # Analyze file
                                    file_content = github_repo.get_file_content(file['path'])
                                    analysis_result = code_analyzer.analyze_code(
                                        file_content, 
                                        file['name'], 
                                        file['extension'],
                                        depth=analysis_depth
                                    )
                                    
                                    file_results.append({
                                        "file": file['path'],
                                        "score": analysis_result['quality_score'],
                                        "issues": analysis_result['issues'],
                                        "suggestions": analysis_result['suggestions']
                                    })
                                
                                # Complete progress
                                progress_bar.progress(1.0)
                                time.sleep(0.5)  # Small delay for UX
                                progress_bar.empty()  # Remove progress bar
                                
                                # Display overall code quality score
                                overall_score = sum(result['score'] for result in file_results) / len(file_results)
                                
                                # Create score color based on value
                                score_color = "#EF4444"  # Error red
                                if overall_score >= 8:
                                    score_color = "#10B981"  # Success green
                                elif overall_score >= 6:
                                    score_color = "#F59E0B"  # Warning yellow
                                
                                st.markdown(
                                    f"<div class='score-box'><h3>Overall Code Quality Score</h3>"
                                    f"<h2 style='color: {score_color}'>{overall_score:.1f}/10</h2></div>", 
                                    unsafe_allow_html=True
                                )
                                
                                # Visualize code quality metrics
                                quality_fig = visualize_code_quality(file_results)
                                st.plotly_chart(quality_fig, use_container_width=True)
                                
                                # Display detailed analysis per file
                                st.markdown("<h3>File-by-File Analysis</h3>", unsafe_allow_html=True)
                                
                                for result in file_results:
                                    with st.expander(f"{result['file']} (Score: {result['score']:.1f}/10)"):
                                        st.markdown("<h4>Issues Detected</h4>", unsafe_allow_html=True)
                                        
                                        if not result['issues']:
                                            st.success("No significant issues detected in this file.")
                                        else:
                                            for issue in result['issues']:
                                                st.markdown(
                                                    f"<div class='issue-box'><p><strong>{issue['type']}</strong>: {issue['description']}</p></div>", 
                                                    unsafe_allow_html=True
                                                )
                    else:
                        st.info("Code quality analysis was not selected. Enable it in the sidebar to see insights about code quality.")
                
                # Tab 3: Improvement Suggestions
                with tab3:
                    if analyze_code_quality:
                        st.markdown("<h2>Improvement Suggestions</h2>", unsafe_allow_html=True)
                        
                        # Group all suggestions
                        all_suggestions = []
                        for result in file_results:
                            for suggestion in result['suggestions']:
                                all_suggestions.append({
                                    "file": result['file'],
                                    "suggestion": suggestion
                                })
                        
                        # Display suggestions
                        if not all_suggestions:
                            st.success("No improvement suggestions found. Your code looks good!")
                        else:
                            st.markdown(f"<p>Found {len(all_suggestions)} improvement suggestions across your codebase.</p>", unsafe_allow_html=True)
                            
                            for i, item in enumerate(all_suggestions):
                                with st.expander(f"Suggestion {i+1} - {item['file']}"):
                                    suggestion = item['suggestion']
                                    
                                    st.markdown("<h4>Issue</h4>", unsafe_allow_html=True)
                                    st.markdown(f"<p>{suggestion['issue']}</p>", unsafe_allow_html=True)
                                    
                                    st.markdown("<h4>Suggestion</h4>", unsafe_allow_html=True)
                                    st.markdown(f"<p>{suggestion['suggestion']}</p>", unsafe_allow_html=True)
                                    
                                    if 'code_before' in suggestion and 'code_after' in suggestion:
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            st.markdown("<h5>Current Code</h5>", unsafe_allow_html=True)
                                            st.code(suggestion['code_before'], language=item['file'].split('.')[-1])
                                        
                                        with col2:
                                            st.markdown("<h5>Suggested Improvement</h5>", unsafe_allow_html=True)
                                            st.code(suggestion['code_after'], language=item['file'].split('.')[-1])
                    else:
                        st.info("Code quality analysis was not selected. Enable it in the sidebar to see improvement suggestions.")
    
    except Exception as e:
        handle_error(str(e))

# Footer
st.markdown("---")
st.markdown(
    "<div class='footer'><p>GitHub Repository Analyzer | Built with Streamlit and CodeT5 | &copy; 2025</p></div>",
    unsafe_allow_html=True
)
