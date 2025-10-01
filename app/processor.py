import re
import time
from typing import List, Tuple, Optional
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import TerminalFormatter
from pygments.util import ClassNotFound
from langdetect import detect, DetectorFactory

# Set seed for consistent language detection
DetectorFactory.seed = 0

# Known error patterns and their explanations
ERROR_PATTERNS = {
    # Python errors
    r'IndexError': 'Array/list access out of bounds - trying to access an index that doesn\'t exist',
    r'KeyError': 'Dictionary key not found - the key you\'re looking for doesn\'t exist',
    r'AttributeError': 'Object attribute/method not found - the object doesn\'t have this property',
    r'ImportError|ModuleNotFoundError': 'Module import failed - the package/module cannot be found',
    r'SyntaxError': 'Code syntax is invalid - there\'s a typo or formatting error in your code',
    r'TypeError': 'Wrong data type used - operation not supported between given types',
    r'ValueError': 'Correct type but inappropriate value - value is not acceptable for the operation',
    r'FileNotFoundError': 'File or directory not found - the specified path doesn\'t exist',
    r'PermissionError': 'Insufficient permissions - don\'t have rights to access/modify the resource',
    r'ZeroDivisionError': 'Division by zero - cannot divide a number by zero',
    
    # JavaScript errors
    r'ReferenceError': 'Variable is not defined or out of scope',
    r'TypeError.*undefined': 'Trying to use undefined value - variable hasn\'t been initialized',
    r'SyntaxError.*Unexpected': 'Syntax error - unexpected character or token in code',
    r'RangeError': 'Number is out of acceptable range',
    
    # Java errors
    r'NullPointerException': 'Trying to use a null object reference',
    r'ArrayIndexOutOfBoundsException': 'Array index is outside valid range',
    r'ClassNotFoundException': 'Required class file not found in classpath',
    r'NumberFormatException': 'String cannot be converted to number format',
}

# Language detection patterns
LANGUAGE_PATTERNS = {
    'python': [r'Traceback \(most recent call last\)', r'File ".*\.py"', r'^\s*at .*\.py:\d+'],
    'javascript': [r'at .*\.js:\d+', r'ReferenceError:', r'TypeError:.*undefined'],
    'java': [r'Exception in thread', r'at .*\.java:\d+', r'Caused by:'],
    'csharp': [r'Unhandled exception:', r'at .*\.cs:line \d+', r'System\..*Exception'],
    'cpp': [r'Segmentation fault', r'core dumped', r'terminate called'],
    'go': [r'panic:', r'goroutine \d+', r'runtime error:'],
}


class LogProcessor:
    """Handles log beautification, syntax highlighting, and analysis."""
    
    def __init__(self):
        self.formatter = TerminalFormatter()
    
    def detect_language(self, log_text: str) -> str:
        """Detect programming language from log content."""
        # Check for explicit patterns first
        for lang, patterns in LANGUAGE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, log_text, re.MULTILINE | re.IGNORECASE):
                    return lang
        
        # Try general language detection on code-like content
        try:
            # Extract lines that look like code (contain common programming elements)
            code_lines = []
            for line in log_text.split('\n'):
                if re.search(r'[(){}\[\];=]|def |class |function |var |let |const |import |from ', line):
                    code_lines.append(line)
            
            if code_lines:
                code_sample = '\n'.join(code_lines[:10])  # Use first 10 code-like lines
                detected = detect(code_sample)
                
                # Map detected language to programming language if possible
                lang_mapping = {
                    'en': 'python',  # Default fallback
                }
                return lang_mapping.get(detected, 'python')
        except:
            pass
        
        return 'python'  # Default fallback
    
    def apply_syntax_highlighting(self, text: str, language: str) -> str:
        """Apply syntax highlighting to the text."""
        try:
            if language == 'auto':
                lexer = guess_lexer(text)
            else:
                # Map our language enum to pygments lexer names
                lexer_mapping = {
                    'python': 'python',
                    'javascript': 'javascript',
                    'java': 'java',
                    'csharp': 'csharp',
                    'cpp': 'cpp',
                    'go': 'go',
                    'rust': 'rust',
                }
                lexer_name = lexer_mapping.get(language, 'text')
                lexer = get_lexer_by_name(lexer_name)
            
            return highlight(text, lexer, self.formatter).strip()
        except ClassNotFound:
            # If lexer not found, return original text
            return text
    
    def extract_error_tags(self, text: str) -> List[str]:
        """Extract error tags from log text."""
        tags = set()
        
        # Check for known error patterns
        for pattern, _ in ERROR_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                # Extract the main error type
                match = re.search(r'(\w+Error|\w+Exception)', pattern)
                if match:
                    tags.add(match.group(1))
                else:
                    # For patterns like 'TypeError.*undefined', extract 'TypeError'
                    error_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                    if error_match:
                        error_text = error_match.group(0)
                        error_type = re.search(r'(\w+Error|\w+Exception)', error_text)
                        if error_type:
                            tags.add(error_type.group(1))
        
        # Add language tag based on content
        detected_lang = self.detect_language(text)
        tags.add(detected_lang.title())
        
        # Add generic tags based on content
        if re.search(r'stack trace|traceback', text, re.IGNORECASE):
            tags.add('StackTrace')
        if re.search(r'warning', text, re.IGNORECASE):
            tags.add('Warning')
        if re.search(r'error|exception|fail', text, re.IGNORECASE):
            tags.add('Error')
        
        return sorted(list(tags))
    
    def generate_summary(self, text: str) -> Optional[str]:
        """Generate a human-readable summary of the error."""
        # Check against known patterns
        for pattern, explanation in ERROR_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                return explanation
        
        # Generic summaries based on content
        if re.search(r'traceback|stack trace', text, re.IGNORECASE):
            return "Your code encountered an error and stopped execution. Check the stack trace for the specific line that caused the issue."
        
        if re.search(r'warning', text, re.IGNORECASE):
            return "Your code ran but encountered a warning. This might indicate a potential issue that should be addressed."
        
        if re.search(r'compilation|compile', text, re.IGNORECASE):
            return "Your code failed to compile. Check for syntax errors or missing dependencies."
        
        return None
    
    def clean_and_deduplicate(self, text: str) -> str:
        """Clean up repetitive lines and format the log."""
        lines = text.split('\n')
        cleaned_lines = []
        seen_lines = {}
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines at the beginning
            if not stripped and not cleaned_lines:
                continue
            
            # Handle repetitive lines (common in stack traces)
            if stripped in seen_lines:
                seen_lines[stripped] += 1
            else:
                seen_lines[stripped] = 1
                cleaned_lines.append(line)
        
        # Add repetition indicators for lines seen multiple times
        final_lines = []
        for line in cleaned_lines:
            stripped = line.strip()
            count = seen_lines.get(stripped, 1)
            if count > 1:
                final_lines.append(f"{line} [repeated {count} times]")
            else:
                final_lines.append(line)
        
        return '\n'.join(final_lines)
    
    def process_log(self, log_input: str, language: str = 'auto', 
                   highlight: bool = True, summarize: bool = True, 
                   tags: bool = True, max_lines: int = 1000) -> Tuple[str, Optional[str], List[str], dict]:
        """
        Process a log entry with beautification, highlighting, and analysis.
        
        Returns:
            Tuple of (cleaned_log, summary, tags, metadata)
        """
        start_time = time.time()
        
        # Truncate if too many lines
        lines = log_input.split('\n')
        truncated = len(lines) > max_lines
        if truncated:
            lines = lines[:max_lines]
            log_input = '\n'.join(lines)
        
        # Detect language if auto
        detected_language = language
        if language == 'auto':
            detected_language = self.detect_language(log_input)
        
        # Clean and deduplicate
        cleaned_log = self.clean_and_deduplicate(log_input)
        
        # Apply syntax highlighting if requested
        if highlight:
            cleaned_log = self.apply_syntax_highlighting(cleaned_log, detected_language)
        
        # Generate summary if requested
        summary = None
        if summarize:
            summary = self.generate_summary(log_input)
        
        # Extract tags if requested
        extracted_tags = []
        if tags:
            extracted_tags = self.extract_error_tags(log_input)
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Build metadata
        metadata = {
            'lines': len(lines),
            'language_detected': detected_language,
            'processing_time_ms': processing_time,
            'truncated': truncated
        }
        
        return cleaned_log, summary, extracted_tags, metadata