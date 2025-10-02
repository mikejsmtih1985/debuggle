"""
🔍 PATTERN RECOGNITION LABORATORY - Error Pattern Matching & Classification 🔍

Think of this file as a specialized forensics lab where pattern recognition experts
work! Just like how crime scene investigators can look at evidence and say
"this matches the pattern of a burglary" or "this looks like an accident",
this module teaches computers to recognize different types of programming errors.

🎯 WHAT THIS MODULE DOES:
This is the "pattern recognition brain" of Debuggle. It's like having a database
of "error fingerprints" that helps us identify what went wrong in your code.

🕬️ THE FORENSICS LAB SETUP:
- ErrorSeverity: Like a scale from "minor scratch" to "broken bone"
- ErrorCategory: Different types of problems (like "kitchen accidents" vs "car problems")
- ErrorPattern: A detailed profile of a specific error type (like a criminal profile)
- ErrorMatch: When we find evidence that matches a known pattern
- Pattern Matchers: Specialists who know different "languages" (Python, JavaScript, etc.)

🔍 HOW PATTERN RECOGNITION WORKS:
1. We have a library of known error "fingerprints" for different programming languages
2. When you give us an error message, we compare it against our database
3. We find matches and rank them by how confident we are
4. We provide detailed information about what each error means and how to fix it

Real-world analogy: This is like having a medical diagnosis system that can
look at symptoms and say "this looks like a cold" or "this might be the flu"
based on patterns it has learned from thousands of previous cases.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Pattern, Union


class ErrorSeverity(Enum):
    """
    🌡️ ERROR TRIAGE SYSTEM - How Urgent Is This Problem?
    
    Just like a hospital emergency room, we need to prioritize problems based on
    how serious they are. This enum is like the triage nurse who decides
    "who needs help first?"
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like homework deadlines:
    - CRITICAL: Due in 1 hour (drop everything and fix NOW!)
    - HIGH: Due tomorrow (fix this today)
    - MEDIUM: Due next week (fix when you have some free time)
    - LOW: Due next month (fix eventually)
    - INFO: Just a helpful tip (like "you might want to study more")
    """
    CRITICAL = "critical"  # 🚨 Your program will crash or produce wrong results!
    HIGH = "high"          # ⚠️  This will likely cause problems soon
    MEDIUM = "medium"      # 🔄 This should be fixed but isn't urgent
    LOW = "low"            # 📅 Fix this when you have time
    INFO = "info"          # 💡 Just a helpful suggestion or tip


class ErrorCategory(Enum):
    """
    📁 ERROR FILING SYSTEM - What Type of Problem Is This?
    
    Just like organizing files in different folders, we categorize errors by
    what part of programming they relate to. This helps us quickly understand
    what area needs attention.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like categorizing school problems:
    - SYNTAX: Like grammar errors in an English essay (wrong spelling/punctuation)
    - RUNTIME: Like your calculator running out of batteries during a math test
    - LOGIC: Like using the wrong formula (the math is right, but approach is wrong)
    - NETWORK: Like your internet cutting out during online class
    - DATABASE: Like your filing cabinet being locked when you need a document
    - PERMISSION: Like not having the key to a classroom you need to enter
    - CONFIGURATION: Like having your desk set up wrong for efficient studying
    - DEPENDENCY: Like needing a textbook that you don't have
    """
    SYNTAX = "syntax"                    # 📝 Grammar/spelling errors in your code
    RUNTIME = "runtime"                  # 🏃 Problems that happen while your program runs
    LOGIC = "logic"                      # 🤔 Your code works, but doesn't do what you intended
    NETWORK = "network"                  # 🌐 Internet/connection problems
    DATABASE = "database"                # 🗄 Problems with storing/retrieving data
    PERMISSION = "permission"            # 🔒 Not allowed to access something you need
    CONFIGURATION = "configuration"      # ⚙️  Settings or setup problems
    DEPENDENCY = "dependency"            # 📦 Missing tools or libraries your code needs


@dataclass
class ErrorPattern:
    """
    🗺️ CRIMINAL PROFILE - Complete Information About One Type of Error
    
    Think of this as a detailed profile that police keep on a known criminal!
    It contains everything we know about a specific type of error: how to
    recognize it, what it means, and how to "catch" it (fix it).
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like a Pokemon card that describes everything about one Pokemon:
    - Name (what it's called)
    - Type (what category it belongs to)
    - Rarity (how serious/common it is) 
    - Description (what it does)
    - Moves (how to counter it)
    - Where to find more info (like a Pokedex entry)
    
    Each ErrorPattern describes one specific type of programming error completely.
    """
    
    # 🏷️ THE ERROR'S "STAGE NAME" - like "IndexError" or "TypeError"
    name: str
    
    # 🔍 THE "FINGERPRINT" - how we recognize this error in text
    # This is a regex pattern (like a search filter) that matches the error message
    pattern: Union[str, Pattern[str]]
    
    # 📁 WHAT FILING CABINET does this belong in? (syntax, runtime, etc.)
    category: ErrorCategory
    
    # 🌡️ HOW URGENT is this problem? (critical, high, medium, low, info)
    severity: ErrorSeverity
    
    # 🗣️ WHAT PROGRAMMING LANGUAGES can have this error?
    # Like saying "this crime only happens in certain neighborhoods"
    languages: List[str]
    
    # 📝 TECHNICAL EXPLANATION - what this error means in programmer terms
    explanation: str
    
    # 🗨️ PLAIN ENGLISH - what happened in terms a human can understand
    what_happened: str
    
    # 🔧 REPAIR INSTRUCTIONS - step-by-step fixes you can try
    quick_fixes: List[str]
    
    # 🛡️ PREVENTION ADVICE - how to avoid this error in the future
    prevention_tip: str
    
    # 📚 STUDY GUIDE - where to learn more about this type of error
    learn_more_url: str
    
    def __post_init__(self):
        """Compile string patterns to regex objects."""
        if isinstance(self.pattern, str):
            self.pattern = re.compile(self.pattern, re.IGNORECASE | re.MULTILINE)


@dataclass
class ErrorMatch:
    """
    🎯 EVIDENCE MATCH - When We Find a Suspect That Fits the Profile
    
    This represents a "match" between an error we found and a pattern we know about.
    It's like when a detective says "this fingerprint matches John Doe in our database!"
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like when you're trying to identify a song:
    - pattern: The song information from your music app's database
    - matched_text: The lyrics you heard that made you think of this song
    - confidence: How sure you are this is the right song (0.0 = "maybe?" to 1.0 = "definitely!")
    - context: The other lyrics around the part you recognized
    - line_number: Which line in the code the error appeared on
    - file_path: Which file had the problem
    """
    
    # 🗺️ THE MATCHING PROFILE - which ErrorPattern this matches
    # Like pointing to a criminal profile and saying "this is our guy!"
    pattern: ErrorPattern
    
    # 🔍 THE ACTUAL EVIDENCE - the exact text that matched our pattern
    # Like the specific fingerprint or DNA sample we found
    matched_text: str
    
    # 🎯 HOW SURE ARE WE? - confidence level from 0.0 (unsure) to 1.0 (certain)
    # Like a detective saying "I'm 90% sure this is our suspect"
    confidence: float
    
    # 🗺️ SURROUNDING CLUES - text around the error for more context
    # Like taking photos of the area around where evidence was found
    context: Optional[str] = None
    
    # 📍 CRIME SCENE LOCATION - what line number the error occurred on
    line_number: Optional[int] = None
    
    # 🗺️ WHICH BUILDING - what file path contained the error
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
    """
    🐍 PYTHON ERROR SPECIALIST - The Snake Charmer Detective! 🐍
    
    This is our specialist detective who only handles Python programming errors.
    Just like how a doctor might specialize in heart problems or brain surgery,
    this matcher specializes in recognizing Python-specific error patterns.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like a teacher who only teaches Spanish class. They know all
    the common mistakes Spanish students make, all the grammar rules, and can
    quickly spot when someone writes "el problema" instead of "la problema".
    
    This class does the same thing but for Python programming errors!
    """
    
    def get_language_indicators(self) -> List[Pattern[str]]:
        """
        🎯 PYTHON IDENTIFICATION CLUES - How We Know This Is Python
        
        These are like "accent markers" that tell us we're looking at a Python error.
        Just like how you can tell someone is from New York by their accent,
        we can tell an error is from Python by these specific phrases.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like recognizing your friend's handwriting - everyone has unique patterns!
        Python errors have these telltale signs that scream "I'm from Python!"
        """
        return [
            # 📜 THE CLASSIC PYTHON "SIGNATURE" - every Python error starts with this
            # Like how every Harry Potter book starts with "Mr. and Mrs. Dursley..."
            re.compile(r'Traceback \(most recent call last\)', re.IGNORECASE),
            
            # 🗺️ PYTHON FILE REFERENCES - mentions of .py files
            # Like seeing "Chapter 5" and knowing you're reading a book
            re.compile(r'File ".*\.py"', re.IGNORECASE),
            
            # 📍 DETAILED LOCATION INFO - Python's very specific about where errors happen
            # Like GPS coordinates that pinpoint exactly where you are
            re.compile(r'^\s*File ".*\.py", line \d+', re.MULTILINE),
        ]
    
    def get_patterns(self) -> List[ErrorPattern]:
        """Python error patterns."""
        return [
            # 🎵 THE "MUSICAL CHAIRS" ERROR - IndexError 🎵
            # Remember the game Musical Chairs? This error is like when the music stops
            # and you try to sit in chair #10, but there are only 9 chairs!
            ErrorPattern(
                name="IndexError",
                pattern=r'IndexError: (?:list )?index out of range',
                category=ErrorCategory.RUNTIME,
                severity=ErrorSeverity.HIGH,
                languages=["python"],
                explanation="Array/list access out of bounds - trying to access an index that doesn't exist",
                what_happened="You tried to access a position in a list/array that doesn't exist",
                quick_fixes=[
                    # 📏 SAFETY CHECK: Count the chairs before sitting!
                    "Check list length: `if len(my_list) > index: item = my_list[index]`",
                    # 🚫 SAFE BACKUP: Have a backup plan if the chair isn't there
                    "Use safe indexing: `item = my_list[index] if index < len(my_list) else None`",
                    # 🎣 TRY-CATCH NET: Try to sit, but be ready to catch yourself if you fall
                    "Try-catch approach: `try: item = my_list[index] except IndexError: item = None`"
                ],
                prevention_tip="Always verify array/list bounds before accessing elements",
                learn_more_url="https://docs.python.org/3/tutorial/errors.html#handling-exceptions"
            ),
            # 🗺️ THE "LOST PHONE NUMBER" ERROR - KeyError 🗺️
            # This is like looking for "Mom" in your phone contacts, but you saved her as "Mother"!
            # The key (name) you're looking for doesn't exist in your dictionary (phone book)
            ErrorPattern(
                name="KeyError",
                pattern=r'KeyError: [\'"]([^\'"]+)[\'"]',
                category=ErrorCategory.RUNTIME,
                severity=ErrorSeverity.HIGH,
                languages=["python"],
                explanation="Dictionary key not found - the key you're looking for doesn't exist",
                what_happened="You tried to access a dictionary key that doesn't exist",
                quick_fixes=[
                    # 📦 THE SAFE METHOD: Ask nicely with a backup plan
                    "Use .get() method: `value = my_dict.get('key', 'default_value')`",
                    # 🔍 CHECK FIRST: Look before you leap!
                    "Check if key exists: `if 'key' in my_dict: value = my_dict['key']`",
                    # 🎣 SAFETY NET: Try it, but be ready if it fails
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