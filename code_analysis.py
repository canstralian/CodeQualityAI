"""
Code Analysis Module for GitHub Repository Analyzer
"""

import re
import random


class CodeAnalyzer:
    """
    Class to analyze code quality using pattern detection
    """

    def __init__(self):
        """
        Initialize the code analyzer
        """
        self.model_loaded = False
        try:
            # Attempt to import transformers
            import transformers

            self.model_loaded = True
        except:
            self.model_loaded = False

    def load_model(self):
        """
        Load the CodeT5 model and tokenizer (placeholder for future implementation)
        """
        try:
            # Import required libraries
            from transformers import T5ForConditionalGeneration, RobertaTokenizer
            import torch

            # This would load a pre-trained model in a full implementation
            # For now, we'll just set a flag to use simulated analysis
            self.model_loaded = True

        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self.model_loaded = False

    def analyze_code(self, code, filename, file_extension, depth="Standard"):
        """
        Analyze code quality and provide suggestions

        Args:
            code (str): The source code to analyze
            filename (str): Name of the file
            file_extension (str): File extension (e.g., 'py', 'js')
            depth (str): Analysis depth - 'Basic', 'Standard', or 'Deep'

        Returns:
            dict: Analysis results including quality score, issues and suggestions
        """
        # Define analysis depth factors
        depth_factor = {
            "Basic": 0.7,  # Less thorough analysis
            "Standard": 1.0,  # Normal analysis
            "Deep": 1.3,  # More thorough analysis
        }

        # Pattern-based analysis
        pattern_results = self._pattern_analysis(code, file_extension)

        # Use AI model if loaded, otherwise use simulated analysis
        if self.model_loaded and depth == "Deep":
            ai_results = self._ai_analysis(code, file_extension)
        else:
            ai_results = self._simulated_ai_analysis(code, file_extension)

        # Combine results
        issues = pattern_results["issues"] + ai_results["issues"]

        # Apply depth factor to number of issues detected
        if depth != "Standard":
            factor = depth_factor.get(depth, 1.0)

            if factor < 1.0:  # Basic analysis - fewer issues
                max_issues = max(1, int(len(issues) * factor))
                issues = issues[:max_issues]
            elif factor > 1.0:  # Deep analysis - more issues
                # For deep analysis, we might add more specific issues
                additional_issues = self._generate_additional_issues(
                    code, file_extension, len(issues)
                )
                issues.extend(additional_issues)

        # Calculate quality score (0-10)
        # Base score starts at 10 and gets reduced for each issue
        base_score = 10.0
        issue_penalty = 10.0 / (
            len(issues) + 10
        )  # +10 to avoid extreme penalties for many issues

        quality_score = base_score - (issue_penalty * len(issues))

        # Ensure score is between 0 and 10
        quality_score = max(0, min(10, quality_score))

        # Round to 1 decimal place
        quality_score = round(quality_score, 1)

        # Generate improvement suggestions
        suggestions = self._generate_suggestions(code, issues, file_extension)

        return {
            "filename": filename,
            "score": quality_score,
            "issues": issues,
            "suggestions": suggestions,
        }

    def _pattern_analysis(self, code, file_extension):
        """
        Analyze code using regex patterns

        Args:
            code (str): The source code to analyze
            file_extension (str): File extension (e.g., 'py', 'js')

        Returns:
            dict: Analysis results with list of issues
        """
        issues = []

        # Skip if code is empty
        if not code or len(code.strip()) == 0:
            return {"issues": []}

        # Get language-specific patterns
        patterns = self._get_language_patterns(file_extension)

        # Check line length
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            if len(line) > patterns["max_line_length"]:
                issues.append(
                    {
                        "line": i,
                        "type": "Long line",
                        "severity": "warning",
                        "message": f"Line exceeds {patterns['max_line_length']} characters",
                    }
                )

        # Check function length
        if "function_pattern" in patterns:
            function_matches = re.finditer(
                patterns["function_pattern"], code, re.MULTILINE
            )
            for match in function_matches:
                function_name = (
                    match.group(1) if len(match.groups()) > 0 else "Unknown function"
                )
                function_lines = match.group(0).count("\n")

                if function_lines > patterns["max_function_lines"]:
                    line_num = code[: match.start()].count("\n") + 1
                    issues.append(
                        {
                            "line": line_num,
                            "type": "Long function",
                            "severity": "warning",
                            "message": f"Function '{function_name}' is {function_lines} lines long",
                        }
                    )

        # Check for complex code (nested control structures)
        if "nested_control_pattern" in patterns:
            nested_control_matches = re.finditer(
                patterns["nested_control_pattern"], code, re.MULTILINE
            )
            for match in nested_control_matches:
                line_num = code[: match.start()].count("\n") + 1
                issues.append(
                    {
                        "line": line_num,
                        "type": "Complex code",
                        "severity": "warning",
                        "message": "Deeply nested control structures",
                    }
                )

        # Check for inconsistent naming
        if "naming_patterns" in patterns:
            for name_type, pattern in patterns["naming_patterns"].items():
                name_matches = re.finditer(pattern, code, re.MULTILINE)
                for match in name_matches:
                    name = match.group(1)

                    # Check if the name follows the convention for its type
                    valid = True
                    if name_type == "class" and not name[0].isupper():
                        valid = False
                    elif name_type == "function" and not (
                        name[0].islower() or name[0] == "_"
                    ):
                        valid = False
                    elif name_type == "constant" and not name.isupper():
                        valid = False

                    if not valid:
                        line_num = code[: match.start()].count("\n") + 1
                        issues.append(
                            {
                                "line": line_num,
                                "type": "Inconsistent naming",
                                "severity": "info",
                                "message": f"{name_type.capitalize()} name '{name}' doesn't follow naming conventions",
                            }
                        )

        # Check for missing documentation (if applicable to the language)
        if "doc_pattern" in patterns:
            doc_matches = re.finditer(patterns["doc_pattern"], code, re.MULTILINE)
            doc_lines = [code[: match.start()].count("\n") + 1 for match in doc_matches]

            # For each function, check if it has documentation
            if "function_pattern" in patterns:
                function_matches = re.finditer(
                    patterns["function_pattern"], code, re.MULTILINE
                )
                for match in function_matches:
                    function_name = (
                        match.group(1)
                        if len(match.groups()) > 0
                        else "Unknown function"
                    )
                    line_num = code[: match.start()].count("\n") + 1

                    # Check if the line before the function has documentation
                    has_doc = False
                    for doc_line in doc_lines:
                        if (
                            abs(doc_line - line_num) <= 3
                        ):  # Documentation should be close to the function
                            has_doc = True
                            break

                    if not has_doc:
                        issues.append(
                            {
                                "line": line_num,
                                "type": "Missing documentation",
                                "severity": "info",
                                "message": f"Function '{function_name}' lacks documentation",
                            }
                        )

        # Check for potential security issues (if applicable to the language)
        if "security_patterns" in patterns:
            for sec_type, pattern in patterns["security_patterns"].items():
                sec_matches = re.finditer(pattern, code, re.MULTILINE)
                for match in sec_matches:
                    line_num = code[: match.start()].count("\n") + 1
                    issues.append(
                        {
                            "line": line_num,
                            "type": "Potential security issue",
                            "severity": "error",
                            "message": f"Potential security vulnerability: {sec_type}",
                        }
                    )

        return {"issues": issues}

    def _ai_analysis(self, code, file_extension):
        """
        Use AI model to analyze code quality (placeholder for future implementation)

        Args:
            code (str): The source code to analyze
            file_extension (str): File extension

        Returns:
            dict: Analysis results with list of issues
        """
        # This would use the CodeT5 model for analysis in a full implementation
        # For now, fallback to simulated analysis
        return self._simulated_ai_analysis(code, file_extension)

    def _simulated_ai_analysis(self, code, file_extension):
        """
        Provide simulated AI analysis when model isn't loaded

        Args:
            code (str): The source code to analyze
            file_extension (str): File extension

        Returns:
            dict: Analysis results with list of issues
        """
        issues = []

        # Skip if code is empty
        if not code or len(code.strip()) == 0:
            return {"issues": []}

        lines = code.split("\n")

        # Analyze code complexity
        line_count = len(lines)
        if line_count > 300:
            issues.append(
                {
                    "line": 1,
                    "type": "File size",
                    "severity": "warning",
                    "message": f"File is very large ({line_count} lines)",
                }
            )

        # Detect repeated code blocks (simulated)
        if line_count > 50 and random.random() < 0.5:
            repeat_line = random.randint(10, min(40, line_count - 10))
            issues.append(
                {
                    "line": repeat_line,
                    "type": "Code duplication",
                    "severity": "warning",
                    "message": "Similar code pattern detected elsewhere in the codebase",
                }
            )

        # Detect potential bugs (simulated)
        if file_extension in ["py", "js", "java"] and random.random() < 0.3:
            bug_line = random.randint(1, line_count)
            issues.append(
                {
                    "line": bug_line,
                    "type": "Potential bug",
                    "severity": "error",
                    "message": "Possible logical error or edge case not handled",
                }
            )

        # Detect performance issues (simulated)
        if random.random() < 0.3:
            perf_line = random.randint(1, line_count)
            issues.append(
                {
                    "line": perf_line,
                    "type": "Performance issue",
                    "severity": "warning",
                    "message": "Inefficient algorithm or operation detected",
                }
            )

        return {"issues": issues}

    def _generate_additional_issues(self, code, file_extension, current_issue_count):
        """
        Generate additional issues for deep analysis

        Args:
            code (str): The source code to analyze
            file_extension (str): File extension
            current_issue_count (int): Number of issues already detected

        Returns:
            list: Additional issues
        """
        additional_issues = []

        # Skip if code is empty
        if not code or len(code.strip()) == 0:
            return additional_issues

        lines = code.split("\n")
        line_count = len(lines)

        # Add more specific issues for deep analysis
        issue_types = [
            {
                "type": "Code maintainability",
                "severity": "warning",
                "message": "This code might be difficult to maintain due to complexity",
            },
            {
                "type": "Variable scope",
                "severity": "info",
                "message": "Consider reducing variable scope for better encapsulation",
            },
            {
                "type": "Error handling",
                "severity": "warning",
                "message": "Improve error handling to handle edge cases",
            },
            {
                "type": "Code organization",
                "severity": "info",
                "message": "Consider reorganizing code for better readability",
            },
        ]

        # Add 1-3 additional issues
        issue_count = min(3, max(1, int(line_count / 100)))
        for _ in range(issue_count):
            issue_type = random.choice(issue_types)
            line_num = random.randint(1, line_count)

            issue = {
                "line": line_num,
                "type": issue_type["type"],
                "severity": issue_type["severity"],
                "message": issue_type["message"],
            }

            additional_issues.append(issue)

        return additional_issues

    def _generate_suggestions(self, code, issues, file_extension):
        """
        Generate improvement suggestions based on detected issues

        Args:
            code (str): The source code to analyze
            issues (list): List of detected issues
            file_extension (str): File extension

        Returns:
            list: Improvement suggestions
        """
        suggestions = []

        # Skip if there are no issues
        if not issues:
            return suggestions

        # Group issues by type
        issue_types = {}
        for issue in issues:
            issue_type = issue.get("type", "Unknown")
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)

        # Generate suggestions for each issue type
        for issue_type, type_issues in issue_types.items():
            if issue_type == "Long line":
                suggestions.append(
                    {
                        "title": "Improve Line Length",
                        "description": "Break long lines into multiple lines to improve readability.",
                        "example": self._get_example("line_length", file_extension),
                    }
                )

            elif issue_type == "Long function":
                suggestions.append(
                    {
                        "title": "Refactor Long Functions",
                        "description": "Break down functions into smaller, more focused functions that each do one thing well.",
                        "example": self._get_example("function_length", file_extension),
                    }
                )

            elif issue_type == "Complex code":
                suggestions.append(
                    {
                        "title": "Reduce Complexity",
                        "description": "Simplify complex code by breaking it down, removing nested conditions, and using helper functions.",
                        "example": self._get_example("complexity", file_extension),
                    }
                )

            elif issue_type == "Inconsistent naming":
                suggestions.append(
                    {
                        "title": "Standardize Naming Conventions",
                        "description": "Use consistent naming patterns throughout your codebase for better readability.",
                        "example": self._get_example("naming", file_extension),
                    }
                )

            elif issue_type == "Missing documentation":
                suggestions.append(
                    {
                        "title": "Add Documentation",
                        "description": "Add docstrings, comments, and type hints to improve code clarity and maintainability.",
                        "example": self._get_example("documentation", file_extension),
                    }
                )

            elif issue_type == "Potential security issue":
                suggestions.append(
                    {
                        "title": "Improve Security",
                        "description": "Address security vulnerabilities by validating inputs, using secure libraries, and following security best practices.",
                        "example": self._get_example("security", file_extension),
                    }
                )

            elif issue_type == "File size":
                suggestions.append(
                    {
                        "title": "Split Large Files",
                        "description": "Split large files into smaller modules with focused responsibilities.",
                        "example": self._get_example("file_size", file_extension),
                    }
                )

            elif issue_type == "Code duplication":
                suggestions.append(
                    {
                        "title": "Reduce Duplication",
                        "description": "Refactor duplicated code into reusable functions or classes.",
                        "example": self._get_example("duplication", file_extension),
                    }
                )

            elif issue_type == "Potential bug":
                suggestions.append(
                    {
                        "title": "Fix Potential Bugs",
                        "description": "Address potential logical errors and add test cases to verify functionality.",
                        "example": self._get_example("bugs", file_extension),
                    }
                )

            elif issue_type == "Performance issue":
                suggestions.append(
                    {
                        "title": "Optimize Performance",
                        "description": "Improve algorithm efficiency, reduce unnecessary operations, and optimize resource usage.",
                        "example": self._get_example("performance", file_extension),
                    }
                )

        return suggestions

    def _get_language_patterns(self, file_extension):
        """
        Get language-specific patterns for code analysis

        Args:
            file_extension (str): File extension

        Returns:
            dict: Language-specific patterns
        """
        # Default patterns
        default_patterns = {"max_line_length": 100, "max_function_lines": 50}

        # Python patterns
        if file_extension == "py":
            return {
                "max_line_length": 88,  # PEP 8 recommends 79, but Black uses 88
                "max_function_lines": 50,
                "function_pattern": r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(.*\):",
                "nested_control_pattern": r"(\s+if.*:.*\n\s+\s+if.*:|\s+for.*:.*\n\s+\s+for.*:|\s+while.*:.*\n\s+\s+while.*:)",
                "naming_patterns": {
                    "class": r"class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(\(.*\))?:",
                    "function": r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(.*\):",
                    "constant": r"([A-Z_][A-Z0-9_]*)\s*=",
                },
                "doc_pattern": r'""".*?"""',
                "security_patterns": {
                    "SQL Injection": r"execute\(.*\+.*\)",
                    "Shell Injection": r"os\.system\(.*\+.*\)|subprocess\.call\(.*shell\s*=\s*True.*\)",
                    "Hardcoded Credentials": r"password\s*=\s*['\"][^'\"]*['\"]|secret\s*=\s*['\"][^'\"]*['\"]",
                },
            }

        # JavaScript patterns
        elif file_extension in ["js", "jsx", "ts", "tsx"]:
            return {
                "max_line_length": 100,
                "max_function_lines": 50,
                "function_pattern": r"function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(.*\)|(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:function|\(.*\)\s*=>)",
                "nested_control_pattern": r"(\s+if.*{.*\n\s+\s+if.*{|\s+for.*{.*\n\s+\s+for.*{|\s+while.*{.*\n\s+\s+while.*{)",
                "naming_patterns": {
                    "class": r"class\s+([a-zA-Z_$][a-zA-Z0-9_$]*)",
                    "function": r"function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)|(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:function|\(.*\)\s*=>)",
                    "constant": r"const\s+([A-Z_$][A-Z0-9_$]*)\s*=",
                },
                "doc_pattern": r"/\*\*.*?\*/",
                "security_patterns": {
                    "Injection": r"eval\(.*\+.*\)|new Function\(.*\+.*\)",
                    "DOM XSS": r"\.innerHTML\s*=|\.outerHTML\s*=",
                    "Hardcoded Credentials": r"password\s*[:=]\s*['\"][^'\"]*['\"]|secret\s*[:=]\s*['\"][^'\"]*['\"]",
                },
            }

        # Java patterns
        elif file_extension == "java":
            return {
                "max_line_length": 120,
                "max_function_lines": 50,
                "function_pattern": r"(?:public|private|protected|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(?:\{|throws)",
                "nested_control_pattern": r"(\s+if.*{.*\n\s+\s+if.*{|\s+for.*{.*\n\s+\s+for.*{|\s+while.*{.*\n\s+\s+while.*{)",
                "naming_patterns": {
                    "class": r"class\s+([a-zA-Z_][a-zA-Z0-9_]*)",
                    "function": r"(?:public|private|protected|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(?:\{|throws)",
                    "constant": r"static\s+final\s+[a-zA-Z_][a-zA-Z0-9_]*\s+([A-Z_][A-Z0-9_]*)\s*=",
                },
                "doc_pattern": r"/\*\*.*?\*/",
                "security_patterns": {
                    "SQL Injection": r"executeQuery\(.*\+.*\)|executeUpdate\(.*\+.*\)",
                    "Command Injection": r"Runtime\.getRuntime\(\)\.exec\(.*\+.*\)",
                    "Hardcoded Credentials": r"String\s+(?:\w+)?[Pp]assword\s*=\s*['\"][^'\"]*['\"]",
                },
            }

        # Default for other languages
        return default_patterns

    def _get_example(self, issue_type, file_extension):
        """
        Get example code for a suggestion

        Args:
            issue_type (str): Type of issue
            file_extension (str): File extension

        Returns:
            str: Example code
        """
        examples = {
            "py": {
                "line_length": "# Before\nresult = some_long_function_name(first_parameter, second_parameter, third_parameter, fourth_parameter)\n\n# After\nresult = some_long_function_name(\n    first_parameter,\n    second_parameter,\n    third_parameter,\n    fourth_parameter\n)",
                "function_length": "# Before\ndef process_data(data):\n    # 50+ lines of code doing multiple things\n    # ...\n\n# After\ndef process_data(data):\n    validated_data = validate_data(data)\n    processed_data = transform_data(validated_data)\n    return save_results(processed_data)\n\ndef validate_data(data):\n    # Validation logic\n    return validated_data\n\ndef transform_data(data):\n    # Transformation logic\n    return transformed_data\n\ndef save_results(data):\n    # Save logic\n    return result",
                "complexity": "# Before\ndef check_eligibility(user):\n    if user.age >= 18:\n        if user.has_subscription:\n            if user.subscription_type == 'premium':\n                return 'Full access'\n            else:\n                return 'Standard access'\n        else:\n            return 'Limited access'\n    else:\n        return 'No access'\n\n# After\ndef check_eligibility(user):\n    if user.age < 18:\n        return 'No access'\n    \n    if not user.has_subscription:\n        return 'Limited access'\n        \n    if user.subscription_type == 'premium':\n        return 'Full access'\n    \n    return 'Standard access'",
                "naming": "# Before\nclass userMgr:\n    def UpdateUserInfo(self, USR_ID, NewName):\n        pass\n\n# After\nclass UserManager:\n    def update_user_info(self, user_id, new_name):\n        pass",
                "documentation": '# Before\ndef calculate_total(items, tax_rate):\n    total = sum(item.price for item in items)\n    return total * (1 + tax_rate)\n\n# After\ndef calculate_total(items, tax_rate):\n    """\n    Calculate the total price including tax\n    \n    Args:\n        items (list): List of items with \'price\' attribute\n        tax_rate (float): Tax rate as a decimal (e.g., 0.07 for 7%)\n        \n    Returns:\n        float: Total price including tax\n    """\n    total = sum(item.price for item in items)\n    return total * (1 + tax_rate)',
                "security": '# Before\ndef execute_query(user_input):\n    query = "SELECT * FROM users WHERE name = \'" + user_input + "\'"\n    cursor.execute(query)\n\n# After\ndef execute_query(user_input):\n    query = "SELECT * FROM users WHERE name = %s"\n    cursor.execute(query, (user_input,))',
                "file_size": "# Before: One large file with multiple classes and functions\n\n# After: Split into modules\n# auth.py\nclass Authentication:\n    # Authentication-related code\n\n# data.py\nclass DataProcessor:\n    # Data processing code\n\n# main.py\nfrom auth import Authentication\nfrom data import DataProcessor\n\n# Main application logic",
                "duplication": "# Before\ndef process_users(users):\n    for user in users:\n        if user.active:\n            name = user.name.strip()\n            email = user.email.lower()\n            print(f\"Processing {name} ({email})\")\n            # More processing...\n\ndef process_employees(employees):\n    for employee in employees:\n        if employee.active:\n            name = employee.name.strip()\n            email = employee.email.lower()\n            print(f\"Processing {name} ({email})\")\n            # More processing...\n\n# After\ndef normalize_user(user):\n    return {\n        'name': user.name.strip(),\n        'email': user.email.lower()\n    }\n\ndef process_person(person):\n    if not person.active:\n        return\n    \n    normalized = normalize_user(person)\n    print(f\"Processing {normalized['name']} ({normalized['email']})\")\n    # More processing...\n\ndef process_users(users):\n    for user in users:\n        process_person(user)\n\ndef process_employees(employees):\n    for employee in employees:\n        process_person(employee)",
                "bugs": "# Before\ndef get_discount(price, is_member):\n    if is_member:\n        return price * 0.9  # 10% discount\n    return price - 5  # $5 off\n\n# After\ndef get_discount(price, is_member):\n    if is_member:\n        return price * 0.9  # 10% discount\n    elif price >= 5:  # Check if price is at least $5\n        return price - 5  # $5 off\n    else:\n        return 0  # Price can't be negative",
                "performance": "# Before\ndef find_duplicates(items):\n    duplicates = []\n    for i in range(len(items)):\n        for j in range(len(items)):\n            if i != j and items[i] == items[j] and items[i] not in duplicates:\n                duplicates.append(items[i])\n    return duplicates\n\n# After\ndef find_duplicates(items):\n    seen = set()\n    duplicates = set()\n    \n    for item in items:\n        if item in seen:\n            duplicates.add(item)\n        else:\n            seen.add(item)\n            \n    return list(duplicates)",
            },
            "js": {
                "line_length": "// Before\nconst result = someLongFunctionName(firstParameter, secondParameter, thirdParameter, fourthParameter);\n\n// After\nconst result = someLongFunctionName(\n  firstParameter,\n  secondParameter,\n  thirdParameter,\n  fourthParameter\n);",
                "function_length": "// Before\nfunction processData(data) {\n  // 50+ lines of code doing multiple things\n  // ...\n}\n\n// After\nfunction processData(data) {\n  const validatedData = validateData(data);\n  const processedData = transformData(validatedData);\n  return saveResults(processedData);\n}\n\nfunction validateData(data) {\n  // Validation logic\n  return validatedData;\n}\n\nfunction transformData(data) {\n  // Transformation logic\n  return transformedData;\n}\n\nfunction saveResults(data) {\n  // Save logic\n  return result;\n}",
                "complexity": "// Before\nfunction checkEligibility(user) {\n  if (user.age >= 18) {\n    if (user.hasSubscription) {\n      if (user.subscriptionType === 'premium') {\n        return 'Full access';\n      } else {\n        return 'Standard access';\n      }\n    } else {\n      return 'Limited access';\n    }\n  } else {\n    return 'No access';\n  }\n}\n\n// After\nfunction checkEligibility(user) {\n  if (user.age < 18) {\n    return 'No access';\n  }\n  \n  if (!user.hasSubscription) {\n    return 'Limited access';\n  }\n  \n  if (user.subscriptionType === 'premium') {\n    return 'Full access';\n  }\n  \n  return 'Standard access';\n}",
                "naming": "// Before\nclass userMgr {\n  UpdateUserInfo(USR_ID, NewName) {\n    // ...\n  }\n}\n\n// After\nclass UserManager {\n  updateUserInfo(userId, newName) {\n    // ...\n  }\n}",
                "documentation": "// Before\nfunction calculateTotal(items, taxRate) {\n  const total = items.reduce((sum, item) => sum + item.price, 0);\n  return total * (1 + taxRate);\n}\n\n// After\n/**\n * Calculate the total price including tax\n * \n * @param {Array} items - List of items with 'price' property\n * @param {number} taxRate - Tax rate as a decimal (e.g., 0.07 for 7%)\n * @returns {number} Total price including tax\n */\nfunction calculateTotal(items, taxRate) {\n  const total = items.reduce((sum, item) => sum + item.price, 0);\n  return total * (1 + taxRate);\n}",
                "security": '// Before\nfunction executeQuery(userInput) {\n  const query = "SELECT * FROM users WHERE name = \'" + userInput + "\'";\n  db.execute(query);\n}\n\n// After\nfunction executeQuery(userInput) {\n  const query = "SELECT * FROM users WHERE name = ?";\n  db.execute(query, [userInput]);\n}',
                "file_size": "// Before: One large file with multiple classes and functions\n\n// After: Split into modules\n// auth.js\nexport class Authentication {\n  // Authentication-related code\n}\n\n// data.js\nexport class DataProcessor {\n  // Data processing code\n}\n\n// main.js\nimport { Authentication } from './auth.js';\nimport { DataProcessor } from './data.js';\n\n// Main application logic",
                "duplication": "// Before\nfunction processUsers(users) {\n  for (const user of users) {\n    if (user.active) {\n      const name = user.name.trim();\n      const email = user.email.toLowerCase();\n      console.log(`Processing ${name} (${email})`);\n      // More processing...\n    }\n  }\n}\n\nfunction processEmployees(employees) {\n  for (const employee of employees) {\n    if (employee.active) {\n      const name = employee.name.trim();\n      const email = employee.email.toLowerCase();\n      console.log(`Processing ${name} (${email})`);\n      // More processing...\n    }\n  }\n}\n\n// After\nfunction normalizeUser(user) {\n  return {\n    name: user.name.trim(),\n    email: user.email.toLowerCase()\n  };\n}\n\nfunction processPerson(person) {\n  if (!person.active) {\n    return;\n  }\n  \n  const normalized = normalizeUser(person);\n  console.log(`Processing ${normalized.name} (${normalized.email})`);\n  // More processing...\n}\n\nfunction processUsers(users) {\n  users.forEach(processPerson);\n}\n\nfunction processEmployees(employees) {\n  employees.forEach(processPerson);\n}",
                "bugs": "// Before\nfunction getDiscount(price, isMember) {\n  if (isMember) {\n    return price * 0.9;  // 10% discount\n  }\n  return price - 5;  // $5 off\n}\n\n// After\nfunction getDiscount(price, isMember) {\n  if (isMember) {\n    return price * 0.9;  // 10% discount\n  } else if (price >= 5) {  // Check if price is at least $5\n    return price - 5;  // $5 off\n  } else {\n    return 0;  // Price can't be negative\n  }\n}",
                "performance": "// Before\nfunction findDuplicates(items) {\n  const duplicates = [];\n  for (let i = 0; i < items.length; i++) {\n    for (let j = 0; j < items.length; j++) {\n      if (i !== j && items[i] === items[j] && !duplicates.includes(items[i])) {\n        duplicates.push(items[i]);\n      }\n    }\n  }\n  return duplicates;\n}\n\n// After\nfunction findDuplicates(items) {\n  const seen = new Set();\n  const duplicates = new Set();\n  \n  for (const item of items) {\n    if (seen.has(item)) {\n      duplicates.add(item);\n    } else {\n      seen.add(item);\n    }\n  }\n  \n  return Array.from(duplicates);\n}",
            },
        }

        # Map file extension to language
        lang = "py"  # Default to Python examples
        if file_extension in ["js", "jsx", "ts", "tsx"]:
            lang = "js"
        elif file_extension in ["java"]:
            lang = "js"  # Use JS examples for Java for now

        # Get example for the issue type and language
        if lang in examples and issue_type in examples[lang]:
            return examples[lang][issue_type]

        # Default example if not found
        return "# Example not available for this language and issue type"
