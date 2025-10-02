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
        """Clean the text and return it formatted for web display."""
        # For our simplified approach, we don't need syntax highlighting
        # Instead, return clean text that the HTML interface can style
        return text.strip()
    
    def extract_error_tags(self, text: str) -> List[str]:
        """Extract simple, friendly tags that anyone can understand."""
        tags = set()
        
        # Simple problem categories
        if re.search(r'connection.*(?:refused|failed|timeout)', text, re.IGNORECASE):
            tags.add('Connection Problems')
        if re.search(r'(?:invalid|failed).*(?:password|login|auth)', text, re.IGNORECASE):
            tags.add('Login Issues')
        if re.search(r'(?:failed|cannot|unable).*(?:read|write|access).*file', text, re.IGNORECASE):
            tags.add('File Problems')
        if re.search(r'email.*(?:rejected|failed)|smtp', text, re.IGNORECASE):
            tags.add('Email Issues')
        if re.search(r'timeout|timed out', text, re.IGNORECASE):
            tags.add('Slow Response')
        if re.search(r'database|db|sql', text, re.IGNORECASE):
            tags.add('Database')
        if re.search(r'cache', text, re.IGNORECASE):
            tags.add('Memory Storage')
        if re.search(r'scheduler|task|job', text, re.IGNORECASE):
            tags.add('Scheduled Jobs')
        if re.search(r'null.*pointer|attempt.*invoke.*null', text, re.IGNORECASE):
            tags.add('Programming Bug')
        if re.search(r'deadlock', text, re.IGNORECASE):
            tags.add('System Conflict')
        
        # Severity levels in simple terms
        if re.search(r'\b(ERROR|FATAL)\b', text, re.IGNORECASE):
            tags.add('Serious Problems')
        if re.search(r'\b(WARN|WARNING)\b', text, re.IGNORECASE):
            tags.add('Minor Warnings')
        if re.search(r'completed successfully', text, re.IGNORECASE):
            tags.add('Some Things Working')
        
        # Add a friendly overall assessment
        error_count = len(re.findall(r'\b(ERROR|FATAL)\b', text, re.IGNORECASE))
        success_count = len(re.findall(r'completed successfully', text, re.IGNORECASE))
        
        if error_count == 0 and success_count > 0:
            tags.add('Mostly Healthy')
        elif error_count > success_count:
            tags.add('Needs Attention')
        else:
            tags.add('Mixed Results')
        
        return sorted(list(tags))
    
    def generate_summary(self, text: str) -> Optional[str]:
        """Generate a simple, easy-to-understand summary."""
        lines = text.split('\n')
        
        # Count different types of problems
        connection_problems = len(re.findall(r'connection.*(?:refused|failed|timeout)', text, re.IGNORECASE))
        login_problems = len(re.findall(r'(?:invalid|failed).*(?:password|login|auth)', text, re.IGNORECASE))
        file_problems = len(re.findall(r'(?:failed|cannot|unable).*(?:read|write|access).*file', text, re.IGNORECASE))
        email_problems = len(re.findall(r'email.*(?:rejected|failed)|smtp.*(?:connect|failed)', text, re.IGNORECASE))
        timeout_problems = len(re.findall(r'timeout|timed out', text, re.IGNORECASE))
        
        # Count serious vs normal activities
        serious_problems = len(re.findall(r'\b(ERROR|FATAL)\b', text, re.IGNORECASE))
        warnings = len(re.findall(r'\b(WARN|WARNING)\b', text, re.IGNORECASE))
        normal_activities = len(re.findall(r'completed successfully|operation completed', text, re.IGNORECASE))
        
        # Build a friendly summary
        summary_parts = []
        
        # Start with the overall health
        if serious_problems == 0 and warnings == 0:
            summary_parts.append("🎉 Great news! Your system is running smoothly with no problems detected.")
        elif serious_problems > 10:
            summary_parts.append("😟 Your system has quite a few problems that need attention.")
        elif serious_problems > 0:
            summary_parts.append(f"⚠️ Your system has {serious_problems} problems that should be fixed.")
        else:
            summary_parts.append("👍 Your system is mostly healthy with just some minor warnings.")
        
        # Explain specific problem types
        problem_explanations = []
        if connection_problems > 0:
            problem_explanations.append(f"Can't connect to other services ({connection_problems} times)")
        if login_problems > 0:
            problem_explanations.append(f"People using wrong passwords ({login_problems} times)")
        if file_problems > 0:
            problem_explanations.append(f"Trouble reading files ({file_problems} times)")
        if email_problems > 0:
            problem_explanations.append(f"Email sending issues ({email_problems} times)")
        if timeout_problems > 0:
            problem_explanations.append(f"Things taking too long to respond ({timeout_problems} times)")
        
        if problem_explanations:
            summary_parts.append(f"Main issues: {', '.join(problem_explanations)}")
        
        # Add some positive notes
        if normal_activities > 0:
            summary_parts.append(f"✅ Good news: {normal_activities} things completed successfully!")
        
        # Simple advice
        if serious_problems > 0:
            summary_parts.append("💡 Recommendation: Ask someone technical to look at the connection and login problems first.")
        elif warnings > 0:
            summary_parts.append("💡 The warnings aren't urgent, but it's good to keep an eye on them.")
        
        return " ".join(summary_parts)
    
    def clean_and_deduplicate(self, text: str) -> str:
        """Transform technical log into simple, understandable explanations."""
        lines = text.split('\n')
        simplified_lines = []
        problem_counts = {}
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Convert this technical line into simple English
            simple_explanation = self._explain_in_simple_terms(stripped)
            
            # Count similar problems
            problem_key = self._get_problem_category(stripped)
            if problem_key in problem_counts:
                problem_counts[problem_key] += 1
            else:
                problem_counts[problem_key] = 1
                if simple_explanation:  # Only add unique explanations
                    simplified_lines.append(simple_explanation)
        
        # Add summary of repeated problems
        final_lines = []
        added_explanations = set()
        
        for line in simplified_lines:
            if line not in added_explanations:
                final_lines.append(line)
                added_explanations.add(line)
        
        # Add counts for repeated problems
        for problem, count in problem_counts.items():
            if count > 1 and problem != "unknown":
                final_lines.append(f"⚠️  The '{problem}' problem happened {count} times")
        
        return '\n'.join(final_lines)
    
    def _extract_core_message(self, log_line: str) -> str:
        """Extract the core message from a log line, ignoring timestamp and level."""
        # Remove common timestamp patterns
        line = re.sub(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[,.]?\d*', '', log_line)
        line = re.sub(r'^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*?\]', '', line)
        
        # Remove log levels
        line = re.sub(r'\[(DEBUG|INFO|WARN|WARNING|ERROR|FATAL|TRACE)\]', '', line, flags=re.IGNORECASE)
        line = re.sub(r'(DEBUG|INFO|WARN|WARNING|ERROR|FATAL|TRACE)', '', line, flags=re.IGNORECASE)
        
        # Remove logger names (like com.example.app.Service)
        line = re.sub(r'[a-zA-Z0-9]+\.[a-zA-Z0-9.]+\s*-\s*', '', line)
        
        return line.strip()
    
    def _explain_in_simple_terms(self, log_line: str) -> Optional[str]:
        """Convert a technical log line into simple, understandable language."""
        line = log_line.lower()
        
        # Extract timestamp for context - make it prettier
        time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', log_line)
        if time_match:
            time_str = time_match.group(1)
            # Format time nicely: convert 24h to 12h format for readability
            try:
                from datetime import datetime
                dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                time_display = dt.strftime('%I:%M:%S %p on %b %d')
            except:
                time_display = time_str
        else:
            time_display = "At some point"
        
        # Database connection problems
        if 'connection refused' in line and ('database' in line or 'db' in line or 'sql' in line):
            return f"❌ At {time_display}: The app tried to talk to the database, but the database wasn't listening or was turned off."
        
        # General connection problems
        if 'connection refused' in line or 'failed to connect' in line:
            return f"❌ At {time_display}: The app tried to connect to another service, but it couldn't reach it (like calling a phone that's turned off)."
        
        # Authentication failures
        if 'invalid password' in line or 'authentication failed' in line or 'login failed' in line:
            return f"🔒 At {time_display}: Someone tried to log in with the wrong password."
        
        # Account locked
        if 'account' in line and 'locked' in line:
            return f"🔒 At {time_display}: An account got locked because someone tried the wrong password too many times."
        
        # File problems
        if 'failed to read file' in line or 'file not found' in line or 'cannot access file' in line:
            return f"📁 At {time_display}: The app tried to open a file, but the file wasn't there or couldn't be opened."
        
        # Email problems
        if 'smtp' in line or 'email' in line:
            if 'rejected' in line:
                return f"📧 At {time_display}: The app tried to send an email, but the email server didn't accept it."
            elif 'could not connect' in line:
                return f"📧 At {time_display}: The app tried to send an email, but couldn't connect to the email server."
        
        # Network timeouts
        if 'timeout' in line or 'timed out' in line:
            return f"⏱️ At {time_display}: The app was waiting for something, but it took too long and gave up (like waiting for a webpage that never loads)."
        
        # Null pointer exceptions
        if 'nullpointerexception' in line or 'attempt to invoke method' in line and 'null' in line:
            return f"🐛 At {time_display}: The app tried to use something that didn't exist (like trying to open a box that isn't there)."
        
        # Cache problems
        if 'cache miss' in line:
            return f"🗃️ At {time_display}: The app looked for some saved information, but it wasn't there, so it had to get it the slow way."
        
        # Cache rebuild failed
        if 'cache rebuild failed' in line:
            return f"🗃️ At {time_display}: The app tried to organize its saved information, but something went wrong."
        
        # Task/Scheduler failures
        if 'task' in line and ('failed' in line or 'timeout' in line):
            return f"⚙️ At {time_display}: A scheduled job (like a daily cleanup) didn't finish properly."
        
        # Deadlock
        if 'deadlock' in line:
            return f"🔄 At {time_display}: Two parts of the app got stuck waiting for each other (like two people trying to go through a door at the same time)."
        
        # Success messages - make them positive
        if 'operation completed successfully' in line or 'completed successfully' in line:
            service = self._extract_service_name(log_line)
            return f"✅ At {time_display}: {service} finished its job successfully."
        
        # Info messages about normal operations
        if any(level in line for level in ['[info]', '[debug]', 'info:', 'debug:']):
            if 'completed successfully' in line:
                return None  # Skip, already handled above
            return f"ℹ️ At {time_display}: Normal system activity (everything working as expected)."
        
        # If we can't explain it simply, return None to skip it
        return None
    
    def _get_problem_category(self, log_line: str) -> str:
        """Categorize the type of problem for counting duplicates."""
        line = log_line.lower()
        
        if 'connection refused' in line or 'failed to connect' in line:
            return "connection problems"
        elif 'invalid password' in line or 'authentication failed' in line:
            return "login problems"
        elif 'account' in line and 'locked' in line:
            return "account lockouts"
        elif 'failed to read file' in line or 'file not found' in line:
            return "file problems"
        elif 'email' in line or 'smtp' in line:
            return "email problems"
        elif 'timeout' in line or 'timed out' in line:
            return "timeout problems"
        elif 'nullpointerexception' in line or ('null' in line and 'pointer' in line):
            return "programming errors"
        elif 'cache' in line:
            return "cache problems"
        elif 'task' in line and 'failed' in line:
            return "scheduled job problems"
        elif 'deadlock' in line:
            return "system conflicts"
        else:
            return "unknown"
    
    def _extract_service_name(self, log_line: str) -> str:
        """Extract the service name from a log line for friendlier messages."""
        # Look for service names like com.example.app.DatabaseService
        service_match = re.search(r'com\.example\.app\.(\w+)', log_line)
        if service_match:
            service = service_match.group(1)
            # Convert CamelCase to readable names
            service = re.sub(r'([A-Z])', r' \1', service).strip()
            return f"The {service.lower()}"
        
        return "The system"
    
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