"""
Visualization module for GitHub Repository Analyzer
"""

import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd
import random
from collections import Counter

def visualize_commit_history(commits):
    """
    Visualize commit history with Plotly
    
    Args:
        commits (list): List of commit data dictionaries
        
    Returns:
        plotly.graph_objects.Figure: A Plotly figure object
    """
    if not commits:
        # Create an empty figure with a message
        fig = go.Figure()
        fig.add_annotation(
            text="No commit data available",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Convert commit dates to datetime objects
    dates = []
    for commit in commits:
        try:
            date_str = commit.get('date', '')
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            dates.append(date_obj)
        except:
            # Skip commits with invalid dates
            continue
    
    # Count commits by date
    date_counts = Counter([date.date() for date in dates])
    
    # Convert to DataFrame for plotting
    df = pd.DataFrame({
        'date': list(date_counts.keys()),
        'count': list(date_counts.values())
    })
    
    # Sort by date
    df = df.sort_values('date')
    
    # Create figure
    fig = px.line(
        df, 
        x='date', 
        y='count',
        title='Commit History',
        labels={'date': 'Date', 'count': 'Number of Commits'},
        line_shape='linear'
    )
    
    # Add dots for each data point
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['count'],
            mode='markers',
            marker=dict(color='#2563EB', size=8),
            showlegend=False
        )
    )
    
    # Update layout
    fig.update_layout(
        hovermode='x unified',
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='#E5E7EB',
            showgrid=True
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='#E5E7EB',
            showgrid=True
        ),
        plot_bgcolor='white',
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig

def visualize_code_quality(file_results):
    """
    Visualize code quality metrics with Plotly
    
    Args:
        file_results (list): List of file analysis results
        
    Returns:
        plotly.graph_objects.Figure: A Plotly figure object
    """
    if not file_results:
        # Create an empty figure with a message
        fig = go.Figure()
        fig.add_annotation(
            text="No file analysis data available",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Extract file paths and scores
    files = []
    scores = []
    issue_counts = []
    
    for result in file_results:
        file_path = result['file_path']
        score = result['result']['score']
        issues = len(result['result']['issues'])
        
        # Truncate long file paths for better display
        if len(file_path) > 40:
            file_path = "..." + file_path[-37:]
        
        files.append(file_path)
        scores.append(score)
        issue_counts.append(issues)
    
    # Color map based on score ranges
    color_map = {
        "high": "#10B981",    # Green for scores 7-10
        "medium": "#F59E0B",  # Amber for scores 4-6.9
        "low": "#EF4444"      # Red for scores 0-3.9
    }
    
    # Assign colors based on scores
    colors = [
        color_map["high"] if score >= 7 else 
        color_map["medium"] if score >= 4 else 
        color_map["low"] 
        for score in scores
    ]
    
    # Create tooltip text
    hover_text = [f"File: {f}<br>Score: {s}/10<br>Issues: {i}" for f, s, i in zip(files, scores, issue_counts)]
    
    # Create figure
    fig = go.Figure()
    
    # Add bar chart
    fig.add_trace(
        go.Bar(
            x=files,
            y=scores,
            marker_color=colors,
            hovertext=hover_text,
            hoverinfo="text",
            name="Quality Score"
        )
    )
    
    # Add a horizontal line at score 7 (good quality threshold)
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=7,
        x1=len(files) - 0.5,
        y1=7,
        line=dict(
            color="#10B981",
            width=2,
            dash="dash",
        )
    )
    
    # Add a horizontal line at score 4 (medium quality threshold)
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=4,
        x1=len(files) - 0.5,
        y1=4,
        line=dict(
            color="#F59E0B",
            width=2,
            dash="dash",
        )
    )
    
    # Update layout
    fig.update_layout(
        title="Code Quality Scores by File",
        xaxis=dict(
            title="Files",
            tickangle=45,
            title_font=dict(size=14),
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            title="Quality Score (0-10)",
            range=[0, 10.5],
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='#E5E7EB',
            showgrid=True
        ),
        plot_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
        ),
        margin=dict(l=10, r=10, t=50, b=150)
    )
    
    return fig

def visualize_issues_by_type(issues):
    """
    Visualize code issues by type
    
    Args:
        issues (list): Flattened list of all issues
        
    Returns:
        plotly.graph_objects.Figure: A Plotly figure object
    """
    if not issues:
        # Create an empty figure with a message
        fig = go.Figure()
        fig.add_annotation(
            text="No issues detected",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Count issues by type
    issue_types = {}
    for issue in issues:
        issue_type = issue.get('type', 'Unknown')
        if issue_type not in issue_types:
            issue_types[issue_type] = 0
        issue_types[issue_type] += 1
    
    # Convert to lists for plotting
    types = list(issue_types.keys())
    counts = list(issue_types.values())
    
    # Sort by count (descending)
    sorted_indices = sorted(range(len(counts)), key=lambda i: counts[i], reverse=True)
    types = [types[i] for i in sorted_indices]
    counts = [counts[i] for i in sorted_indices]
    
    # Define colors based on issue types
    color_map = {
        "Long line": "#F59E0B",
        "Long function": "#F59E0B",
        "Complex code": "#F59E0B",
        "Inconsistent naming": "#3B82F6",
        "Missing documentation": "#3B82F6",
        "Potential security issue": "#EF4444",
        "File size": "#F59E0B",
        "Code duplication": "#F59E0B",
        "Potential bug": "#EF4444",
        "Performance issue": "#F59E0B",
        "Code maintainability": "#F59E0B",
        "Variable scope": "#3B82F6",
        "Error handling": "#F59E0B",
        "Code organization": "#3B82F6"
    }
    
    # Assign colors, default to gray for unknown types
    colors = [color_map.get(t, "#6B7280") for t in types]
    
    # Create figure
    fig = go.Figure(
        go.Bar(
            x=counts,
            y=types,
            orientation='h',
            marker_color=colors,
            hovertemplate='%{y}: %{x} issues<extra></extra>'
        )
    )
    
    # Update layout
    fig.update_layout(
        title="Issues by Type",
        xaxis=dict(
            title="Number of Issues",
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='#E5E7EB',
            showgrid=True
        ),
        yaxis=dict(
            title="Issue Type",
            title_font=dict(size=14),
            tickfont=dict(size=12),
            automargin=True
        ),
        plot_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
        ),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig

def visualize_commit_activity_by_author(commits):
    """
    Visualize commit activity by author
    
    Args:
        commits (list): List of commit data dictionaries
        
    Returns:
        plotly.graph_objects.Figure: A Plotly figure object
    """
    if not commits:
        # Create an empty figure with a message
        fig = go.Figure()
        fig.add_annotation(
            text="No commit data available",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Count commits by author
    author_counts = {}
    for commit in commits:
        author = commit.get('author', 'Unknown')
        if author not in author_counts:
            author_counts[author] = 0
        author_counts[author] += 1
    
    # Convert to lists for plotting
    authors = list(author_counts.keys())
    counts = list(author_counts.values())
    
    # Sort by count (descending)
    sorted_indices = sorted(range(len(counts)), key=lambda i: counts[i], reverse=True)
    authors = [authors[i] for i in sorted_indices]
    counts = [counts[i] for i in sorted_indices]
    
    # Limit to top 10 authors if there are many
    if len(authors) > 10:
        authors = authors[:10]
        counts = counts[:10]
    
    # Generate colors
    colors = px.colors.qualitative.Plotly[:len(authors)]
    
    # Create figure
    fig = go.Figure(
        go.Bar(
            x=authors,
            y=counts,
            marker_color=colors,
            hovertemplate='%{x}: %{y} commits<extra></extra>'
        )
    )
    
    # Update layout
    fig.update_layout(
        title="Commit Activity by Author",
        xaxis=dict(
            title="Author",
            tickangle=45,
            title_font=dict(size=14),
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            title="Number of Commits",
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='#E5E7EB',
            showgrid=True
        ),
        plot_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
        ),
        margin=dict(l=10, r=10, t=50, b=100)
    )
    
    return fig