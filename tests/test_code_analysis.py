
import unittest
from unittest.mock import patch, MagicMock
from code_analysis import CodeAnalyzer

class TestCodeAnalyzer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = CodeAnalyzer()
        
    @patch('code_analysis.logger')
    def test_initialization(self, mock_logger):
        """Test that CodeAnalyzer initializes correctly."""
        # Verify that transformers import is attempted
        mock_logger.info.assert_called_once_with("Transformers library successfully imported")
        
    @patch('code_analysis.logger')
    def test_initialization_without_transformers(self, mock_logger):
        """Test initialization when transformers library is not available."""
        # Reset the mock logger
        mock_logger.reset_mock()
        
        # Patch the import to raise ImportError
        with patch('code_analysis.transformers', side_effect=ImportError("No module named 'transformers'")):
            analyzer = CodeAnalyzer()
            self.assertFalse(analyzer.model_loaded)
            mock_logger.warning.assert_called_once()
            
    @patch('code_analysis.logger')
    def test_load_model_success(self, mock_logger):
        """Test loading the model successfully."""
        # Reset the mock logger
        mock_logger.reset_mock()
        
        # Patch required imports
        with patch('code_analysis.T5ForConditionalGeneration'), \
             patch('code_analysis.RobertaTokenizer'), \
             patch('code_analysis.torch'):
            self.analyzer.load_model()
            self.assertTrue(self.analyzer.model_loaded)
            mock_logger.info.assert_any_call("Starting to load AI code analysis model")
            mock_logger.info.assert_any_call("AI code analysis model loaded successfully")
            
    @patch('code_analysis.logger')
    def test_load_model_failure(self, mock_logger):
        """Test handling model loading failure."""
        # Reset the mock logger
        mock_logger.reset_mock()
        
        # Patch required imports to raise an exception
        with patch('code_analysis.T5ForConditionalGeneration', side_effect=Exception("Model loading error")):
            self.analyzer.load_model()
            self.assertFalse(self.analyzer.model_loaded)
            mock_logger.error.assert_called_once()
            
    @patch('code_analysis.logger')
    def test_analyze_code_basic_depth(self, mock_logger):
        """Test analyzing code with basic depth."""
        code = """
def hello():
    print("Hello World")
    return None
"""
        result = self.analyzer.analyze_code(code, "test.py", "py", depth="Basic")
        
        # Verify basics of the result
        self.assertEqual(result["filename"], "test.py")
        self.assertIsInstance(result["score"], float)
        self.assertTrue(0 <= result["score"] <= 10)
        self.assertIsInstance(result["issues"], list)
        self.assertIsInstance(result["suggestions"], list)
        
    @patch('code_analysis.logger')
    def test_analyze_code_deep_depth(self, mock_logger):
        """Test analyzing code with deep depth."""
        code = """
def hello():
    print("Hello World")
    return None
"""
        result = self.analyzer.analyze_code(code, "test.py", "py", depth="Deep")
        
        # Deep analysis should have more issues
        self.assertGreater(len(result["issues"]), 0)
        
    @patch('code_analysis.logger')
    def test_analyze_code_empty(self, mock_logger):
        """Test analyzing empty code."""
        result = self.analyzer.analyze_code("", "empty.py", "py")
        
        # Empty code should have a minimal result
        self.assertEqual(result["filename"], "empty.py")
        self.assertEqual(result["issues"], [])
        
    @patch('code_analysis.logger')
    def test_analyze_code_with_error(self, mock_logger):
        """Test error handling during code analysis."""
        # Patch _pattern_analysis to raise an exception
        with patch.object(self.analyzer, '_pattern_analysis', side_effect=Exception("Analysis error")):
            result = self.analyzer.analyze_code("print('test')", "error.py", "py")
            
            # Should return a result with error information
            self.assertEqual(result["filename"], "error.py")
            self.assertEqual(result["score"], 0.0)
            self.assertEqual(len(result["issues"]), 1)
            self.assertEqual(result["issues"][0]["type"], "Analysis Error")
            
    def test_pattern_analysis_python(self):
        """Test pattern analysis on Python code."""
        code = """
def very_long_function_name_that_does_too_many_things(param1, param2, param3):
    # This function is too long
    result = param1 + param2 + param3
    if result > 10:
        if param1 > 5:
            if param2 > 3:
                print("Nested condition")
    return result
"""
        result = self.analyzer._pattern_analysis(code, "py")
        
        # Should detect issues like long function, nested conditions
        self.assertIsInstance(result["issues"], list)
        self.assertGreater(len(result["issues"]), 0)
        
        # Check for specific issue types
        issue_types = [issue["type"] for issue in result["issues"]]
        self.assertIn("Long function", issue_types)
        self.assertIn("Complex code", issue_types)
        
    def test_pattern_analysis_javascript(self):
        """Test pattern analysis on JavaScript code."""
        code = """
function processData(data) {
    // This is a complex function
    if (data.valid) {
        if (data.processed) {
            if (data.ready) {
                console.log("Ready to go!");
            }
        }
    }
    return data;
}
"""
        result = self.analyzer._pattern_analysis(code, "js")
        
        # Should detect issues like nested conditions
        self.assertIsInstance(result["issues"], list)
        self.assertGreater(len(result["issues"]), 0)
        
        # Check for complex code detection
        issue_types = [issue["type"] for issue in result["issues"]]
        self.assertIn("Complex code", issue_types)
        
    def test_generate_suggestions(self):
        """Test generating suggestions based on issues."""
        issues = [
            {"type": "Long line", "line": 1, "severity": "warning", "message": "Line too long"},
            {"type": "Missing documentation", "line": 5, "severity": "info", "message": "Add docs"}
        ]
        
        suggestions = self.analyzer._generate_suggestions("print('test')", issues, "py")
        
        # Should generate suggestions for each issue type
        self.assertEqual(len(suggestions), 2)
        suggestion_titles = [s["title"] for s in suggestions]
        self.assertIn("Improve Line Length", suggestion_titles)
        self.assertIn("Add Documentation", suggestion_titles)
        
    def test_simulated_ai_analysis(self):
        """Test simulated AI analysis results."""
        code = """
def hello():
    print("Hello World")
    # Repeat this line many times to make the function large
    # ...
""" * 20  # Make the code large enough to trigger file size issue
        
        result = self.analyzer._simulated_ai_analysis(code, "py")
        
        # Should detect issues like file size
        self.assertIsInstance(result["issues"], list)
        self.assertGreater(len(result["issues"]), 0)
        
        # Check for file size issue
        file_size_issues = [i for i in result["issues"] if i["type"] == "File size"]
        self.assertGreater(len(file_size_issues), 0)

if __name__ == '__main__':
    unittest.main()
import unittest
from unittest.mock import patch, MagicMock
from code_analysis import CodeAnalyzer


class TestCodeAnalyzer(unittest.TestCase):
    """Test cases for the CodeAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = CodeAnalyzer()

    def test_initialization(self):
        """Test CodeAnalyzer initialization."""
        # Verify model_loaded flag depends on transformers availability
        with patch('importlib.import_module') as mock_import:
            # Simulate transformers being available
            mock_import.return_value = MagicMock()
            analyzer = CodeAnalyzer()
            self.assertTrue(analyzer.model_loaded)
            
            # Simulate transformers not being available
            mock_import.side_effect = ImportError("No module named 'transformers'")
            analyzer = CodeAnalyzer()
            self.assertFalse(analyzer.model_loaded)

    def test_analyze_code_empty(self):
        """Test analyzing empty code."""
        result = self.analyzer.analyze_code("", "empty.py", "py", "Basic")
        
        # The score should be 10 (perfect) when no code to analyze
        self.assertEqual(result["score"], 10.0)
        self.assertEqual(len(result["issues"]), 0)

    def test_analyze_code_python(self):
        """Test analyzing Python code."""
        code = """
def long_function():
    # This is a long function
    x = 1
    y = 2
    z = 3
    
    # More code to make it long
    if x > 0:
        if y > 0:
            if z > 0:
                print("All positive")
                
    very_long_variable_name_that_exceeds_the_recommended_line_length_for_python_according_to_pep8_style_guide = "too long"
    
    return x + y + z
"""
        result = self.analyzer.analyze_code(code, "test.py", "py", "Standard")
        
        # Verify we have a score and issues
        self.assertIsInstance(result["score"], float)
        self.assertGreater(len(result["issues"]), 0)
        
        # Verify we have suggestions
        self.assertGreater(len(result["suggestions"]), 0)
        
        # Check for specific issue types we expect in this code
        issue_types = [issue["type"] for issue in result["issues"]]
        self.assertIn("Long line", issue_types)
        self.assertIn("Complex code", issue_types)

    def test_analyze_code_javascript(self):
        """Test analyzing JavaScript code."""
        code = """
function longFunction() {
    // This is a long function
    let x = 1;
    let y = 2;
    let z = 3;
    
    // More code to make it long
    if (x > 0) {
        if (y > 0) {
            if (z > 0) {
                console.log("All positive");
            }
        }
    }
    
    const veryLongVariableNameThatExceedsTheRecommendedLineLengthForJavaScriptAccordingToAirbnbStyleGuide = "too long";
    
    return x + y + z;
}
"""
        result = self.analyzer.analyze_code(code, "test.js", "js", "Standard")
        
        # Verify we have a score and issues
        self.assertIsInstance(result["score"], float)
        self.assertGreater(len(result["issues"]), 0)
        
        # Verify we have suggestions
        self.assertGreater(len(result["suggestions"]), 0)
        
        # Check for specific issue types we expect in this code
        issue_types = [issue["type"] for issue in result["issues"]]
        self.assertIn("Long line", issue_types)
        self.assertIn("Complex code", issue_types)

    def test_analyze_code_depth_basic(self):
        """Test analyzing code with Basic depth."""
        code = """
def function_with_multiple_issues():
    # This is a function with several issues
    x = 1
    y = 2
    z = 3
    
    # Missing documentation
    
    # Long line
    very_long_variable = "this is a very long string that will exceed the line length limit and should be detected as an issue"
    
    # Complex code
    if x > 0:
        if y > 0:
            if z > 0:
                print("All positive")
                
    # Inconsistent naming
    camelCaseVariable = "not snake_case"
    
    return x + y + z
"""
        # Test with Basic depth - should have fewer issues
        basic_result = self.analyzer.analyze_code(code, "test.py", "py", "Basic")
        
        # Test with Standard depth for comparison
        standard_result = self.analyzer.analyze_code(code, "test.py", "py", "Standard")
        
        # Basic should have fewer issues than Standard
        self.assertLessEqual(len(basic_result["issues"]), len(standard_result["issues"]))

    def test_analyze_code_depth_deep(self):
        """Test analyzing code with Deep depth."""
        code = """
def simple_function():
    # This is a simple function
    x = 1
    y = 2
    return x + y
"""
        # Test with Standard depth
        standard_result = self.analyzer.analyze_code(code, "test.py", "py", "Standard")
        
        # Test with Deep depth - should have more issues
        deep_result = self.analyzer.analyze_code(code, "test.py", "py", "Deep")
        
        # Deep should have more issues than Standard for the same code
        self.assertGreaterEqual(len(deep_result["issues"]), len(standard_result["issues"]))

    def test_analyze_code_error_handling(self):
        """Test error handling during code analysis."""
        # Mock _pattern_analysis to raise an exception
        with patch.object(self.analyzer, '_pattern_analysis') as mock_pattern:
            mock_pattern.side_effect = Exception("Test error")
            
            # Analysis should still complete and return a result with an error
            result = self.analyzer.analyze_code("def test(): pass", "test.py", "py", "Standard")
            
            # Should have a 0 score
            self.assertEqual(result["score"], 0.0)
            
            # Should have an error issue
            self.assertEqual(len(result["issues"]), 1)
            self.assertEqual(result["issues"][0]["type"], "Analysis Error")

    def test_pattern_analysis_python(self):
        """Test pattern analysis for Python code."""
        code = """
# This is a test Python file

def long_function_name_that_exceeds_recommended_length():
    \"\"\"
    This is a function with docstring
    \"\"\"
    return True

def function_without_docstring():
    return False
    
PASSWORD = "hardcoded_password"  # Security issue

def execute_query(user_input):
    query = "SELECT * FROM users WHERE id = " + user_input  # SQL injection
    return query
"""
        result = self.analyzer._pattern_analysis(code, "py")
        
        # Verify we have issues detected
        self.assertGreater(len(result["issues"]), 0)
        
        # Check for specific issue types
        issue_types = [issue["type"] for issue in result["issues"]]
        self.assertIn("Long function", issue_types)
        self.assertIn("Missing documentation", issue_types)
        self.assertIn("Potential security issue", issue_types)

    def test_pattern_analysis_javascript(self):
        """Test pattern analysis for JavaScript code."""
        code = """
// This is a test JavaScript file

function longFunctionNameThatExceedsRecommendedLength() {
    /**
     * This is a function with docstring
     */
    return true;
}

function functionWithoutDocstring() {
    return false;
}
    
const PASSWORD = "hardcoded_password";  // Security issue

function executeQuery(userInput) {
    const query = "SELECT * FROM users WHERE id = " + userInput;  // SQL injection
    return query;
}

// DOM XSS vulnerability
document.getElementById("output").innerHTML = userInput;
"""
        result = self.analyzer._pattern_analysis(code, "js")
        
        # Verify we have issues detected
        self.assertGreater(len(result["issues"]), 0)
        
        # Check for specific issue types
        issue_types = [issue["type"] for issue in result["issues"]]
        self.assertIn("Long function", issue_types)
        self.assertIn("Missing documentation", issue_types)
        self.assertIn("Potential security issue", issue_types)

    def test_generate_suggestions(self):
        """Test generating improvement suggestions."""
        # Create issues of different types
        issues = [
            {"type": "Long line", "line": 5, "message": "Line too long", "severity": "warning"},
            {"type": "Complex code", "line": 10, "message": "Nested conditions", "severity": "warning"},
            {"type": "Missing documentation", "line": 15, "message": "Add docstring", "severity": "info"}
        ]
        
        # Generate suggestions
        suggestions = self.analyzer._generate_suggestions("def test(): pass", issues, "py")
        
        # Verify we have a suggestion for each issue type
        self.assertEqual(len(suggestions), 3)
        
        # Check suggestion titles match issue types
        suggestion_titles = [suggestion["title"] for suggestion in suggestions]
        self.assertIn("Improve Line Length", suggestion_titles)
        self.assertIn("Reduce Complexity", suggestion_titles)
        self.assertIn("Add Documentation", suggestion_titles)
        
        # Check each suggestion has an example
        for suggestion in suggestions:
            self.assertIn("example", suggestion)
            self.assertIsInstance(suggestion["example"], str)


if __name__ == '__main__':
    unittest.main()
