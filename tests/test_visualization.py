
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import plotly.graph_objects as go
from visualization import (
    visualize_commit_history, 
    visualize_code_quality, 
    visualize_issues_by_type, 
    visualize_commit_activity_by_author
)

class TestVisualization(unittest.TestCase):
    
    def test_visualize_commit_history_empty(self):
        """Test visualize_commit_history with empty commits."""
        fig = visualize_commit_history([])
        
        # Should return an empty figure with a message
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 0)
        
        # Check for annotation
        self.assertEqual(len(fig.layout.annotations), 1)
        self.assertEqual(fig.layout.annotations[0].text, "No commit data available")
    
    @patch('visualization.pd.DataFrame')
    @patch('visualization.px.line')
    def test_visualize_commit_history(self, mock_line, mock_dataframe):
        """Test visualize_commit_history with commit data."""
        # Create mock commits
        commits = [
            {"date": "2023-01-01T12:00:00Z", "author": "Test User", "message": "Commit 1"},
            {"date": "2023-01-02T12:00:00Z", "author": "Test User", "message": "Commit 2"},
            {"date": "2023-01-02T14:00:00Z", "author": "Test User", "message": "Commit 3"},
        ]
        
        # Setup mock DataFrame
        mock_df = MagicMock()
        mock_dataframe.return_value = mock_df
        mock_df.sort_values.return_value = mock_df
        
        # Setup mock figure
        mock_fig = MagicMock()
        mock_line.return_value = mock_fig
        
        # Call the function
        fig = visualize_commit_history(commits)
        
        # Verify DataFrame creation
        mock_dataframe.assert_called_once()
        
        # Verify px.line was called
        mock_line.assert_called_once()
        
        # Verify figure methods
        mock_fig.add_trace.assert_called_once()
        mock_fig.update_layout.assert_called_once()
    
    def test_visualize_code_quality_empty(self):
        """Test visualize_code_quality with empty results."""
        fig = visualize_code_quality([])
        
        # Should return an empty figure with a message
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 0)
        
        # Check for annotation
        self.assertEqual(len(fig.layout.annotations), 1)
        self.assertEqual(fig.layout.annotations[0].text, "No file analysis data available")
    
    def test_visualize_code_quality(self):
        """Test visualize_code_quality with file results."""
        # Create mock file results
        file_results = [
            {
                "file_path": "file1.py",
                "result": {"score": 8.5, "issues": [{"type": "Long line", "line": 1}]}
            },
            {
                "file_path": "file2.py",
                "result": {"score": 5.0, "issues": [{"type": "Missing docs", "line": 1}, {"type": "Complex code", "line": 5}]}
            },
            {
                "file_path": "file3.py",
                "result": {"score": 3.0, "issues": [{"type": "Security issue", "line": 1}, {"type": "Long line", "line": 10}]}
            }
        ]
        
        fig = visualize_code_quality(file_results)
        
        # Should return a figure with a bar chart
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 1)
        
        # Verify data points
        self.assertEqual(len(fig.data[0].x), 3)  # 3 files
        self.assertEqual(len(fig.data[0].y), 3)  # 3 scores
        
        # Verify shapes (horizontal lines)
        self.assertEqual(len(fig.layout.shapes), 2)
    
    def test_visualize_issues_by_type_empty(self):
        """Test visualize_issues_by_type with empty issues."""
        fig = visualize_issues_by_type([])
        
        # Should return an empty figure with a message
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 0)
        
        # Check for annotation
        self.assertEqual(len(fig.layout.annotations), 1)
        self.assertEqual(fig.layout.annotations[0].text, "No issues detected")
    
    def test_visualize_issues_by_type(self):
        """Test visualize_issues_by_type with issues."""
        # Create mock issues
        issues = [
            {"type": "Long line", "line": 1, "severity": "warning"},
            {"type": "Long line", "line": 2, "severity": "warning"},
            {"type": "Missing documentation", "line": 5, "severity": "info"},
            {"type": "Security issue", "line": 10, "severity": "error"}
        ]
        
        fig = visualize_issues_by_type(issues)
        
        # Should return a figure with a bar chart
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 1)
        
        # Verify data - should have 3 issue types
        self.assertEqual(len(fig.data[0].x), 3)  # 3 issue types
        self.assertEqual(len(fig.data[0].y), 3)  # 3 issue types
    
    def test_visualize_commit_activity_by_author_empty(self):
        """Test visualize_commit_activity_by_author with empty commits."""
        fig = visualize_commit_activity_by_author([])
        
        # Should return an empty figure with a message
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 0)
        
        # Check for annotation
        self.assertEqual(len(fig.layout.annotations), 1)
        self.assertEqual(fig.layout.annotations[0].text, "No commit data available")
    
    def test_visualize_commit_activity_by_author(self):
        """Test visualize_commit_activity_by_author with commit data."""
        # Create mock commits
        commits = [
            {"author": "User 1", "date": "2023-01-01T12:00:00Z", "message": "Commit 1"},
            {"author": "User 1", "date": "2023-01-02T12:00:00Z", "message": "Commit 2"},
            {"author": "User 2", "date": "2023-01-02T14:00:00Z", "message": "Commit 3"},
            {"author": "User 2", "date": "2023-01-03T12:00:00Z", "message": "Commit 4"},
            {"author": "User 3", "date": "2023-01-03T14:00:00Z", "message": "Commit 5"},
        ]
        
        fig = visualize_commit_activity_by_author(commits)
        
        # Should return a figure with a bar chart
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 1)
        
        # Verify data - should have 3 authors
        self.assertEqual(len(fig.data[0].x), 3)  # 3 authors
        self.assertEqual(len(fig.data[0].y), 3)  # 3 commit counts

if __name__ == '__main__':
    unittest.main()
