"""
Enhanced error patterns with actionable fix suggestions.
This module provides detailed error analysis and fix recommendations.
"""
import re

# Enhanced error patterns with detailed fix suggestions
ERROR_FIX_PATTERNS = {
    # Python errors with actionable fixes
    'IndexError': {
        'explanation': 'Array/list access out of bounds - trying to access an index that doesn\'t exist',
        'what_happened': 'You tried to access a position in a list/array that doesn\'t exist',
        'quick_fixes': [
            'Check list length: `if len(my_list) > index: item = my_list[index]`',
            'Use safe indexing: `item = my_list[index] if index < len(my_list) else None`',
            'Try-catch approach: `try: item = my_list[index] except IndexError: item = None`'
        ],
        'prevention': 'Always verify array/list bounds before accessing elements',
        'learn_more': 'https://docs.python.org/3/tutorial/errors.html#handling-exceptions'
    },
    'KeyError': {
        'explanation': 'Dictionary key not found - the key you\'re looking for doesn\'t exist',
        'what_happened': 'You tried to access a dictionary key that doesn\'t exist',
        'quick_fixes': [
            'Use .get() method: `value = my_dict.get(\'key\', \'default_value\')`',
            'Check if key exists: `if \'key\' in my_dict: value = my_dict[\'key\']`',
            'Use try-except: `try: value = my_dict[\'key\'] except KeyError: value = None`'
        ],
        'prevention': 'Always check if keys exist before accessing or use .get() method',
        'learn_more': 'https://docs.python.org/3/tutorial/datastructures.html#dictionaries'
    },
    'AttributeError': {
        'explanation': 'Object attribute/method not found - the object doesn\'t have this property',
        'what_happened': 'You tried to use a method or attribute that doesn\'t exist on this object',
        'quick_fixes': [
            'Check available attributes: `print(dir(my_object))`',
            'Use hasattr(): `if hasattr(my_object, \'method_name\'):`',
            'Verify object type: `print(type(my_object))`'
        ],
        'prevention': 'Check documentation or use dir() to see available methods/attributes',
        'learn_more': 'https://docs.python.org/3/reference/datamodel.html#attribute-access'
    },
    'TypeError': {
        'explanation': 'Wrong data type used - operation not supported between given types',
        'what_happened': 'You tried to perform an operation on incompatible data types',
        'quick_fixes': [
            'Convert types: `str(number)` or `int(string)` or `float(string)`',
            'Check types first: `if isinstance(value, (int, float)):`',
            'Use type-safe operations: `"{}".format(value)` instead of + with mixed types'
        ],
        'prevention': 'Always verify data types before operations, use explicit type conversion',
        'learn_more': 'https://docs.python.org/3/library/functions.html#type'
    },
    'ValueError': {
        'explanation': 'Correct type but inappropriate value - value is not acceptable for the operation',
        'what_happened': 'The data type is correct, but the specific value can\'t be used',
        'quick_fixes': [
            'Validate input: `if value.isdigit(): number = int(value)`',
            'Use try-except: `try: result = int(value) except ValueError: result = 0`',
            'Check value ranges: `if 0 <= value <= 100:`'
        ],
        'prevention': 'Validate input values before processing them',
        'learn_more': 'https://docs.python.org/3/library/exceptions.html#ValueError'
    },
    'FileNotFoundError': {
        'explanation': 'File or directory not found - the specified path doesn\'t exist',
        'what_happened': 'You tried to open or access a file that doesn\'t exist',
        'quick_fixes': [
            'Check if file exists: `if os.path.exists(filepath):`',
            'Use try-except: `try: with open(file) as f: ... except FileNotFoundError: ...`',
            'Use absolute paths: `os.path.abspath(filename)`'
        ],
        'prevention': 'Always verify file paths exist before accessing files',
        'learn_more': 'https://docs.python.org/3/library/exceptions.html#FileNotFoundError'
    },
    'ZeroDivisionError': {
        'explanation': 'Division by zero - cannot divide a number by zero',
        'what_happened': 'You tried to divide a number by zero, which is mathematically undefined',
        'quick_fixes': [
            'Check denominator: `if denominator != 0: result = numerator / denominator`',
            'Use conditional: `result = numerator / denominator if denominator else 0`',
            'Handle with try-except: `try: result = a/b except ZeroDivisionError: result = float(\'inf\')`'
        ],
        'prevention': 'Always check if the denominator is non-zero before division',
        'learn_more': 'https://docs.python.org/3/library/exceptions.html#ZeroDivisionError'
    },
    
    # JavaScript errors with fixes
    'ReferenceError': {
        'explanation': 'Variable is not defined or out of scope',
        'what_happened': 'You tried to use a variable that hasn\'t been declared or is out of scope',
        'quick_fixes': [
            'Declare variable: `let myVariable = \'default_value\';`',
            'Check if defined: `if (typeof myVariable !== \'undefined\')`',
            'Use optional chaining: `myObject?.property?.method?.()`'
        ],
        'prevention': 'Always declare variables before use, check scope carefully',
        'learn_more': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Errors/Not_defined'
    },
    'TypeError (JavaScript)': {
        'explanation': 'Trying to use undefined/null value or wrong method',
        'what_happened': 'You tried to call a method on undefined/null or used wrong data type',
        'quick_fixes': [
            'Check for null/undefined: `if (value != null) { value.method(); }`',
            'Use optional chaining: `value?.method?.()`',
            'Provide defaults: `const safeValue = value || \'default\';`'
        ],
        'prevention': 'Always check for null/undefined before using objects',
        'learn_more': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Errors/TypeError'
    },
    'SyntaxError (JavaScript)': {
        'explanation': 'Code syntax is invalid - there\'s a formatting or grammar error',
        'what_happened': 'Your JavaScript code has invalid syntax that prevents it from running',
        'quick_fixes': [
            'Check for missing brackets: `{ }`, `[ ]`, `( )`',
            'Verify semicolons: Add `;` at end of statements',
            'Check quotes: Ensure matching `\'` or `"` quotes'
        ],
        'prevention': 'Use a code editor with syntax highlighting and linting',
        'learn_more': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Errors/Unexpected_token'
    },
    
    # Java errors with fixes
    'NullPointerException': {
        'explanation': 'Trying to use a null object reference',
        'what_happened': 'You tried to call a method or access a field on a null object',
        'quick_fixes': [
            'Null check: `if (object != null) { object.method(); }`',
            'Use Optional: `Optional.ofNullable(object).ifPresent(obj -> obj.method());`',
            'Initialize object: `MyObject object = new MyObject();`'
        ],
        'prevention': 'Always initialize objects and check for null before use',
        'learn_more': 'https://docs.oracle.com/javase/tutorial/essential/exceptions/runtime.html'
    },
    'ArrayIndexOutOfBoundsException': {
        'explanation': 'Array index is outside valid range',
        'what_happened': 'You tried to access an array position that doesn\'t exist',
        'quick_fixes': [
            'Check bounds: `if (index >= 0 && index < array.length)`',
            'Use enhanced for loop: `for (Type item : array) { ... }`',
            'Get length first: `int size = array.length; if (index < size) ...`'
        ],
        'prevention': 'Always verify array bounds before accessing elements',
        'learn_more': 'https://docs.oracle.com/javase/tutorial/java/nutsandbolts/arrays.html'
    },
    'ClassNotFoundException': {
        'explanation': 'Required class file not found in classpath',
        'what_happened': 'Java couldn\'t find a class file that your code is trying to use',
        'quick_fixes': [
            'Check classpath: Ensure all required JARs are included',
            'Verify package name: `import com.example.MyClass;`',
            'Rebuild project: Clean and rebuild to regenerate class files'
        ],
        'prevention': 'Ensure all dependencies are properly configured in your build system',
        'learn_more': 'https://docs.oracle.com/javase/tutorial/essential/exceptions/runtime.html'
    },
    
    # C# errors with fixes
    'NullReferenceException': {
        'explanation': 'Attempt to use a null object reference',
        'what_happened': 'You tried to access a member of a null object',
        'quick_fixes': [
            'Null check: `if (object != null) { object.Method(); }`',
            'Null-conditional operator: `object?.Method();`',
            'Initialize object: `MyClass object = new MyClass();`'
        ],
        'prevention': 'Always initialize objects and use null checks',
        'learn_more': 'https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/operators/null-conditional-operators'
    },
    
    # Generic error categories
    'Connection refused': {
        'explanation': 'Cannot connect to a service or database',
        'what_happened': 'Your application tried to connect to another service, but the connection was rejected',
        'quick_fixes': [
            'Check if service is running: Verify the target service is active',
            'Verify connection string: Check host, port, and credentials',
            'Check firewall: Ensure network connectivity is allowed'
        ],
        'prevention': 'Implement retry logic and proper error handling for network operations',
        'learn_more': 'Check your service/database documentation for connection troubleshooting'
    }
}


def extract_error_context(text: str, error_type: str) -> str:
    """Extract specific context about the error for more targeted advice."""
    lines = text.split('\n')
    
    for line in lines:
        if error_type in line:
            # For IndexError, try to extract the index that was accessed
            if error_type == 'IndexError':
                if 'list index out of range' in line:
                    return "Attempted to access an index that doesn't exist"
            
            # For KeyError, try to extract the missing key
            elif error_type == 'KeyError':
                key_match = re.search(r"KeyError: ['\"]([^'\"]+)['\"]", line)
                if key_match:
                    key = key_match.group(1)
                    return f"The key '{key}' was not found in the dictionary"
            
            # For AttributeError, try to extract the missing attribute
            elif error_type == 'AttributeError':
                attr_match = re.search(r"has no attribute ['\"]([^'\"]+)['\"]", line)
                if attr_match:
                    attr = attr_match.group(1)
                    return f"The attribute/method '{attr}' doesn't exist on this object"
            
            # For TypeError, provide context about the operation
            elif error_type == 'TypeError':
                if 'unsupported operand type' in line:
                    return "You tried to perform an operation between incompatible types"
                elif 'not callable' in line:
                    return "You tried to call something that isn't a function"
            
            # Return the error line itself as context
            return line.strip()
    
    return f"Error occurred but specific details couldn't be extracted"


def generate_enhanced_error_summary(text: str) -> str:
    """Generate enhanced error summary with actionable fix suggestions."""
    import re
    
    # Detect specific error types and provide detailed help
    for error_type, details in ERROR_FIX_PATTERNS.items():
        if error_type in text:
            # Extract additional context from the error
            context = extract_error_context(text, error_type)
            
            summary_parts = [
                f"🚨 **{error_type} Detected**",
                "",
                f"🔍 **What happened:** {details['what_happened']}",
                ""
            ]
            
            # Add context-specific information if available
            if context and context != f"Error occurred but specific details couldn't be extracted":
                summary_parts.extend([
                    f"📋 **Specific details:** {context}",
                    ""
                ])
            
            # Add quick fixes
            summary_parts.extend([
                "🛠️ **Quick fixes:**"
            ])
            for i, fix in enumerate(details['quick_fixes'], 1):
                summary_parts.append(f"   {i}. {fix}")
            
            summary_parts.extend([
                "",
                f"💡 **Prevention tip:** {details['prevention']}",
                "",
                f"📚 **Learn more:** {details['learn_more']}"
            ])
            
            return "\n".join(summary_parts)
    
    return ""