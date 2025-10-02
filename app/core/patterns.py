"""
Error pattern matching and classification system.

This module provides intelligent pattern recognition for various error types
across multiple programming languages and frameworks.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Pattern, Union


class ErrorSeverity(Enum):
    """Error severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ErrorCategory(Enum):
    """High-level error categories."""
    SYNTAX = "syntax"
    RUNTIME = "runtime"
    LOGIC = "logic"
    NETWORK = "network"
    DATABASE = "database"
    PERMISSION = "permission"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"


@dataclass
class ErrorPattern:
    """Defines an error pattern with matching and fix information."""
    name: str
    pattern: Union[str, Pattern[str]]
    category: ErrorCategory
    severity: ErrorSeverity
    languages: List[str]
    explanation: str
    what_happened: str
    quick_fixes: List[str]
    prevention_tip: str
    learn_more_url: str
    
    def __post_init__(self):
        """Compile string patterns to regex objects."""
        if isinstance(self.pattern, str):
            self.pattern = re.compile(self.pattern, re.IGNORECASE | re.MULTILINE)


@dataclass
class ErrorMatch:
    """Represents a matched error pattern with context."""
    pattern: ErrorPattern
    matched_text: str
    confidence: float
    context: Optional[str] = None
    line_number: Optional[int] = None
    file_path: Optional[str] = None


class BasePatternMatcher(ABC):
    """Abstract base class for language-specific pattern matchers."""
    
    @abstractmethod
    def get_patterns(self) -> List[ErrorPattern]:
        """Return list of error patterns for this matcher."""
        pass
    
    @abstractmethod
    def get_language_indicators(self) -> List[Pattern[str]]:
        """Return regex patterns that indicate this language."""
        pass
    
    def extract_context(self, text: str, match: re.Match) -> Optional[str]:
        """Extract additional context from around the matched error."""
        lines = text.split('\n')
        match_line = None
        
        for i, line in enumerate(lines):
            if match.group(0) in line:
                match_line = i
                break
        
        if match_line is not None:
            # Return 3 lines of context around the error
            start = max(0, match_line - 1)
            end = min(len(lines), match_line + 2)
            return '\n'.join(lines[start:end])
        
        return None


class PythonPatternMatcher(BasePatternMatcher):
    """Pattern matcher for Python errors."""
    
    def get_language_indicators(self) -> List[Pattern[str]]:
        """Python-specific indicators."""
        return [
            re.compile(r'Traceback \(most recent call last\)', re.IGNORECASE),
            re.compile(r'File ".*\.py"', re.IGNORECASE),
            re.compile(r'^\s*File ".*\.py", line \d+', re.MULTILINE),
        ]
    
    def get_patterns(self) -> List[ErrorPattern]:
        """Python error patterns."""
        return [
            ErrorPattern(
                name="IndexError",
                pattern=r'IndexError: (?:list )?index out of range',
                category=ErrorCategory.RUNTIME,
                severity=ErrorSeverity.HIGH,
                languages=["python"],
                explanation="Array/list access out of bounds - trying to access an index that doesn't exist",
                what_happened="You tried to access a position in a list/array that doesn't exist",
                quick_fixes=[
                    "Check list length: `if len(my_list) > index: item = my_list[index]`",
                    "Use safe indexing: `item = my_list[index] if index < len(my_list) else None`",
                    "Try-catch approach: `try: item = my_list[index] except IndexError: item = None`"
                ],
                prevention_tip="Always verify array/list bounds before accessing elements",
                learn_more_url="https://docs.python.org/3/tutorial/errors.html#handling-exceptions"
            ),
            ErrorPattern(
                name="KeyError",
                pattern=r'KeyError: [\'"]([^\'"]+)[\'"]',
                category=ErrorCategory.RUNTIME,
                severity=ErrorSeverity.HIGH,
                languages=["python"],
                explanation="Dictionary key not found - the key you're looking for doesn't exist",
                what_happened="You tried to access a dictionary key that doesn't exist",
                quick_fixes=[
                    "Use .get() method: `value = my_dict.get('key', 'default_value')`",
                    "Check if key exists: `if 'key' in my_dict: value = my_dict['key']`",
                    "Use try-except: `try: value = my_dict['key'] except KeyError: value = None`"
                ],
                prevention_tip="Always check if keys exist before accessing or use .get() method",
                learn_more_url="https://docs.python.org/3/tutorial/datastructures.html#dictionaries"
            ),
            ErrorPattern(
                name="AttributeError",
                pattern=r"AttributeError: '(\w+)' object has no attribute '(\w+)'",
                category=ErrorCategory.RUNTIME,
                severity=ErrorSeverity.MEDIUM,
                languages=["python"],
                explanation="Object attribute/method not found - the object doesn't have this property",
                what_happened="You tried to use a method or attribute that doesn't exist on this object",
                quick_fixes=[
                    "Check available attributes: `print(dir(my_object))`",
                    "Use hasattr(): `if hasattr(my_object, 'method_name'):`",
                    "Verify object type: `print(type(my_object))`"
                ],
                prevention_tip="Check documentation or use dir() to see available methods/attributes",
                learn_more_url="https://docs.python.org/3/reference/datamodel.html#attribute-access"
            ),
            ErrorPattern(
                name="TypeError",
                pattern=r"TypeError: (.+)",
                category=ErrorCategory.RUNTIME,
                severity=ErrorSeverity.MEDIUM,
                languages=["python"],
                explanation="Wrong data type used - operation not supported between given types",
                what_happened="You tried to perform an operation on incompatible data types",
                quick_fixes=[
                    "Convert types: `str(number)` or `int(string)` or `float(string)`",
                    "Check types first: `if isinstance(value, (int, float)):`",
                    "Use type-safe operations: `'{}' .format(value)` instead of + with mixed types"
                ],
                prevention_tip="Always verify data types before operations, use explicit type conversion",
                learn_more_url="https://docs.python.org/3/library/functions.html#type"
            ),
            ErrorPattern(
                name="FileNotFoundError",
                pattern=r"FileNotFoundError: \[Errno 2\] No such file or directory: '([^']+)'",
                category=ErrorCategory.RUNTIME,
                severity=ErrorSeverity.HIGH,
                languages=["python"],
                explanation="File or directory not found - the specified path doesn't exist",
                what_happened="You tried to open or access a file that doesn't exist",
                quick_fixes=[
                    "Check if file exists: `if os.path.exists(filepath):`",
                    "Use try-except: `try: with open(file) as f: ... except FileNotFoundError: ...`",
                    "Use absolute paths: `os.path.abspath(filename)`"
                ],
                prevention_tip="Always verify file paths exist before accessing files",
                learn_more_url="https://docs.python.org/3/library/exceptions.html#FileNotFoundError"
            ),
        ]


class JavaScriptPatternMatcher(BasePatternMatcher):
    """Pattern matcher for JavaScript errors."""
    
    def get_language_indicators(self) -> List[Pattern[str]]:
        """JavaScript-specific indicators."""
        return [
            re.compile(r'at .*\.js:\d+:\d+', re.IGNORECASE),
            re.compile(r'ReferenceError:', re.IGNORECASE),
            re.compile(r'TypeError.*undefined', re.IGNORECASE),
        ]
    
    def get_patterns(self) -> List[ErrorPattern]:
        """JavaScript error patterns."""
        return [
            ErrorPattern(
                name="ReferenceError",
                pattern=r'ReferenceError: (\w+) is not defined',
                category=ErrorCategory.RUNTIME,
                severity=ErrorSeverity.HIGH,
                languages=["javascript"],
                explanation="Variable is not defined or out of scope",
                what_happened="You tried to use a variable that hasn't been declared or is out of scope",
                quick_fixes=[
                    "Declare variable: `let myVariable = 'default_value';`",
                    "Check if defined: `if (typeof myVariable !== 'undefined')`",
                    "Use optional chaining: `myObject?.property?.method?.()`"
                ],
                prevention_tip="Always declare variables before use, check scope carefully",
                learn_more_url="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Errors/Not_defined"
            ),
            ErrorPattern(
                name="TypeError",
                pattern=r"TypeError: (.+)",
                category=ErrorCategory.RUNTIME,
                severity=ErrorSeverity.MEDIUM,
                languages=["javascript"],
                explanation="Trying to use undefined/null value or wrong method",
                what_happened="You tried to call a method on undefined/null or used wrong data type",
                quick_fixes=[
                    "Check for null/undefined: `if (value != null) { value.method(); }`",
                    "Use optional chaining: `value?.method?.()`",
                    "Provide defaults: `const safeValue = value || 'default';`"
                ],
                prevention_tip="Always check for null/undefined before using objects",
                learn_more_url="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Errors/TypeError"
            ),
        ]


class JavaPatternMatcher(BasePatternMatcher):
    """Pattern matcher for Java errors."""
    
    def get_language_indicators(self) -> List[Pattern[str]]:
        """Java-specific indicators."""
        return [
            re.compile(r'Exception in thread', re.IGNORECASE),
            re.compile(r'at .*\.java:\d+', re.IGNORECASE),
            re.compile(r'Caused by:', re.IGNORECASE),
        ]
    
    def get_patterns(self) -> List[ErrorPattern]:
        """Java error patterns."""
        return [
            ErrorPattern(
                name="NullPointerException",
                pattern=r'NullPointerException',
                category=ErrorCategory.RUNTIME,
                severity=ErrorSeverity.CRITICAL,
                languages=["java"],
                explanation="Trying to use a null object reference",
                what_happened="You tried to call a method or access a field on a null object",
                quick_fixes=[
                    "Null check: `if (object != null) { object.method(); }`",
                    "Use Optional: `Optional.ofNullable(object).ifPresent(obj -> obj.method());`",
                    "Initialize object: `MyObject object = new MyObject();`"
                ],
                prevention_tip="Always initialize objects and check for null before use",
                learn_more_url="https://docs.oracle.com/javase/tutorial/essential/exceptions/runtime.html"
            ),
        ]


class ErrorPatternMatcher:
    """Main pattern matcher that coordinates language-specific matchers."""
    
    def __init__(self):
        """Initialize with all available pattern matchers."""
        self.matchers = [
            PythonPatternMatcher(),
            JavaScriptPatternMatcher(),
            JavaPatternMatcher(),
        ]
        self._all_patterns = None
        self._language_indicators = None
    
    @property
    def all_patterns(self) -> List[ErrorPattern]:
        """Get all patterns from all matchers."""
        if self._all_patterns is None:
            self._all_patterns = []
            for matcher in self.matchers:
                self._all_patterns.extend(matcher.get_patterns())
        return self._all_patterns
    
    @property
    def language_indicators(self) -> Dict[str, List[Pattern[str]]]:
        """Get language indicators mapped by matcher class name."""
        if self._language_indicators is None:
            self._language_indicators = {}
            for matcher in self.matchers:
                name = matcher.__class__.__name__.replace('PatternMatcher', '').lower()
                self._language_indicators[name] = matcher.get_language_indicators()
        return self._language_indicators
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect the most likely programming language from text."""
        scores = {}
        
        for lang, indicators in self.language_indicators.items():
            score = 0
            for pattern in indicators:
                matches = len(pattern.findall(text))
                score += matches
            
            if score > 0:
                scores[lang] = score
        
        if scores:
            return max(scores, key=scores.get)
        return None
    
    def find_matches(self, text: str, language: Optional[str] = None) -> List[ErrorMatch]:
        """Find all matching error patterns in the text."""
        matches = []
        
        # Filter patterns by language if specified
        patterns = self.all_patterns
        if language:
            patterns = [p for p in patterns if language.lower() in [l.lower() for l in p.languages]]
        
        for pattern in patterns:
            for match in pattern.pattern.finditer(text):
                context = None
                
                # Try to get context from the appropriate matcher
                for matcher in self.matchers:
                    if any(lang in pattern.languages for lang in [
                        matcher.__class__.__name__.replace('PatternMatcher', '').lower()
                    ]):
                        context = matcher.extract_context(text, match)
                        break
                
                error_match = ErrorMatch(
                    pattern=pattern,
                    matched_text=match.group(0),
                    confidence=1.0,  # Could be enhanced with more sophisticated scoring
                    context=context
                )
                matches.append(error_match)
        
        # Sort by severity (critical first) and confidence
        return sorted(matches, key=lambda m: (
            ["critical", "high", "medium", "low", "info"].index(m.pattern.severity.value),
            -m.confidence
        ))
    
    def get_best_match(self, text: str, language: Optional[str] = None) -> Optional[ErrorMatch]:
        """Get the best matching error pattern."""
        matches = self.find_matches(text, language)
        return matches[0] if matches else None