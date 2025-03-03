import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import pandas as pd
from datetime import datetime, timedelta

def visualize_commit_history(commits):
    """
    Visualize commit history with Plotly
    
    Args:
        commits (list): List of commit data dictionaries
        
    Returns:
        plotly.graph_objects.Figure: A Plotly figure object
    """
    # Extract commit dates and count by date
    dates = [commit['date'] for commit in commits]
    date_counter = Counter(dates)
    
    # Prepare data for visualization
    date_df = pd.DataFrame({
        'Date': list(date_counter.keys()),
        'Commits': list(date_counter.values())
    })
    
    # Sort by date
    date_df['Date'] = pd.to_datetime(date_df['Date'])
    date_df = date_df.sort_values('Date')
    
    # Fill in missing dates with zero commits
    date_range = pd.date_range(start=date_df['Date'].min(), end=date_df['Date'].max())
    date_df = date_df.set_index('Date').reindex(date_range, fill_value=0).reset_index()
    date_df = date_df.rename(columns={'index': 'Date'})
    
    # Create commit activity heatmap
    fig = px.bar(
        date_df, 
        x='Date', 
        y='Commits',
        labels={'Date': 'Date', 'Commits': 'Number of Commits'},
        title='Commit Activity Over Time'
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Commits',
        plot_bgcolor='white',
        hovermode='closest',
        height=400,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    # Color scale
    fig.update_traces(
        marker_color='#2563EB',
        hovertemplate='Date: %{x}<br>Commits: %{y}<extra></extra>'
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
    # Extract file names and scores
    files = [result['file'].split('/')[-1] if '/' in result['file'] else result['file'] for result in file_results]
    scores = [result['score'] for result in file_results]
    issues_count = [len(result['issues']) for result in file_results]
    
    # Truncate long filenames
    truncated_files = [f[:20] + '...' if len(f) > 20 else f for f in files]
    
    # Determine colors based on score
    colors = ['#EF4444' if score < 6 else '#F59E0B' if score < 8 else '#10B981' for score in scores]
    
    # Create bar chart
    fig = go.Figure()
    
    # Add score bars
    fig.add_trace(go.Bar(
        x=truncated_files,
        y=scores,
        name='Quality Score',
        marker_color=colors,
        text=scores,
        textposition='auto',
        hovertemplate='%{x}<br>Score: %{y:.1f}/10<extra></extra>'
    ))
    
    # Add reference line for "good" score
    fig.add_shape(
        type='line',
        x0=-0.5,
        y0=8,
        x1=len(files) - 0.5,
        y1=8,
        line=dict(
            color='green',
            width=2,
            dash='dot'
        )
    )
    
    # Add annotation for the reference line
    fig.add_annotation(
        x=len(files) - 1,
        y=8.1,
        text="Good Score Threshold",
        showarrow=False,
        font=dict(
            color="green"
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Code Quality Scores by File',
        xaxis_title='Files',
        yaxis_title='Quality Score (0-10)',
        yaxis_range=[0, 10.5],
        plot_bgcolor='white',
        hovermode='closest',
        height=500,
        margin=dict(l=40, r=40, t=60, b=80)
    )
    
    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=45)
    
    return fig

def visualize_issues_by_type(issues):
    """
    Visualize code issues by type
    
    Args:
        issues (list): Flattened list of all issues
        
    Returns:
        plotly.graph_objects.Figure: A Plotly figure object
    """
    # Count issues by type
    issue_types = [issue['type'] for issue in issues]
    type_counter = Counter(issue_types)
    
    # Prepare data for visualization
    issue_df = pd.DataFrame({
        'Issue Type': list(type_counter.keys()),
        'Count': list(type_counter.values())
    })
    
    # Sort by count
    issue_df = issue_df.sort_values('Count', ascending=False)
    
    # Create bar chart
    fig = px.bar(
        issue_df, 
        x='Issue Type', 
        y='Count',
        title='Issues by Type',
        color='Count',
        color_continuous_scale=['#10B981', '#F59E0B', '#EF4444']
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Issue Type',
        yaxis_title='Number of Occurrences',
        plot_bgcolor='white',
        hovermode='closest',
        height=400,
        margin=dict(l=40, r=40, t=60, b=80)
    )
    
    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=45)
    
    return fig
