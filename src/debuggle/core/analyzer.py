"""
🕵️ DETECTIVE HEADQUARTERS - Core Error Analysis Engine 🕵️

Think of this file as the main detective agency headquarters! This is where all the 
error investigation work gets coordinated. Just like how a detective agency has:
- A reception desk (AnalysisRequest) where cases come in
- Investigation reports (AnalysisResult) that document findings
- The Chief Detective (ErrorAnalyzer) who runs the whole operation

🎯 WHAT THIS MODULE DOES:
This is the "brain" of Debuggle - it takes in error messages (like crime reports)
and figures out what went wrong, how bad it is, and what you should do about it.

🏢 THE DETECTIVE AGENCY STRUCTURE:
- AnalysisRequest: The intake form when someone reports a problem
- AnalysisResult: The complete investigation report with findings
- ErrorAnalyzer: The head detective who coordinates everything

🔍 HOW THE INVESTIGATION WORKS:
1. Someone brings in an error (like reporting a crime)
2. We figure out what programming language it's in (like identifying the crime scene type)
3. We look for patterns that match known problems (like checking mug shots)
4. We write up a report with our findings and advice
5. We give practical suggestions for fixing the problem

Real-world analogy: This is like a detective agency that specializes in solving
"computer crimes" - but instead of catching bad guys, we're catching bugs!
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

from .patterns import ErrorPatternMatcher, ErrorMatch, ErrorSeverity


logger = logging.getLogger(__name__)


@dataclass
class AnalysisRequest:
    """
    📋 CRIME REPORT INTAKE FORM 📋
    
    Think of this as the form you fill out when reporting a problem to our detective agency!
    Just like when you call the police, they ask you specific questions to understand
    what happened - this class captures all those details.
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like a detailed order form at a restaurant. You specify:
    - What you want analyzed (the error text)
    - Any hints about what type of problem it might be (language)
    - How detailed you want the investigation to be (include options)
    - How many possible solutions you want to see (max_matches)
    """
    
    # 📝 THE MAIN EVIDENCE - This is the error message or code that's causing trouble
    # Like giving the detective a photo of the crime scene
    text: str
    
    # 🗣️ LANGUAGE HINT - Tell us what programming language this is (Python, JavaScript, etc.)
    # Like telling the detective "this happened in the kitchen" vs "this happened in the garage"
    # If you don't know, we'll try to figure it out ourselves!
    language: Optional[str] = None
    
    # 🔍 INVESTIGATION DEPTH SETTINGS - How thorough should we be?
    # Like asking "do you want the full investigation or just the basics?"
    
    # Should we look around the error for more clues? (like examining the crime scene)
    include_context: bool = True
    
    # Should we give you advice on how to fix it? (like a detective giving safety tips)
    include_suggestions: bool = True
    
    # Should we categorize and label the problem? (like filing the case in the right folder)
    include_tags: bool = True
    
    # How many different possible explanations should we consider? (like interviewing multiple witnesses)
    # Default is 5 - that's usually enough to find the real culprit!
    max_matches: int = 5


@dataclass
class AnalysisResult:
    """
    📊 COMPLETE INVESTIGATION REPORT 📊
    
    This is like the final police report after investigating a case!
    It contains everything we discovered during our investigation, organized
    in a way that's easy to understand and act upon.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this as a comprehensive book report about your error:
    - What the original problem was (like quoting the book)
    - What type of problem we think it is (like identifying the genre)
    - The main issue we found (like the book's main theme)
    - All the issues we discovered (like all the important plot points)
    - Quick labels to categorize it (like book tags: "mystery", "romance")
    - A human-friendly summary (like a book review)
    - Practical advice (like "if you liked this book, try...")
    """
    
    # 📝 ORIGINAL EVIDENCE - The exact error message you gave us (unchanged)
    # Like keeping the original crime scene photo in the file
    original_text: str
    
    # 🔍 LANGUAGE DETECTION - What programming language we think this is
    # Like a detective saying "this looks like a kitchen accident, not a garage accident"
    detected_language: Optional[str]
    
    # 🎯 PRIMARY SUSPECT - The main error we think is causing your problem
    # Like identifying the main culprit in a crime
    primary_error: Optional[ErrorMatch]
    
    # 👥 ALL SUSPECTS - Every possible error we found (sorted by how likely they are)
    # Like a lineup of all possible suspects, with the most likely first
    all_matches: List[ErrorMatch]
    
    # 🏷️ CASE LABELS - Quick tags to categorize this problem
    # Like putting stickers on a file folder: "urgent", "python", "syntax error"
    tags: List[str]
    
    # 📄 EXECUTIVE SUMMARY - A human-readable explanation of what we found
    # Like the "TL;DR" version of our investigation report
    summary: Optional[str]
    
    # 💡 PRACTICAL ADVICE - Step-by-step suggestions for fixing the problem
    # Like a detective giving you tips on how to prevent this from happening again
    suggestions: List[str]
    
    # 📈 INVESTIGATION METADATA - Behind-the-scenes info about our analysis
    # Like noting how long the investigation took, how many clues we checked, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def has_errors(self) -> bool:
        """
        🚨 QUICK CHECK: Did we find any problems?
        
        This is like asking "did the detective find any clues?" - a simple yes/no answer.
        Returns True if we found at least one error, False if everything looks clean.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like checking if your backpack has any homework in it - either it does or it doesn't!
        """
        return len(self.all_matches) > 0
    
    @property
    def severity_level(self) -> Optional[str]:
        """
        🌡️ HOW BAD IS THE WORST PROBLEM?
        
        This finds the most serious problem we discovered, like a triage nurse in
        a hospital who looks at all the patients and says "this one needs help first!"
        
        🏆 HIGH SCHOOL EXPLANATION:
        Imagine you have multiple homework assignments due:
        - "critical" = due in 1 hour (drop everything and fix this!)
        - "high" = due tomorrow (fix this today)
        - "medium" = due next week (fix this when you have time)
        - "low" = due next month (fix this eventually)
        - "info" = just a helpful tip (like a study suggestion)
        
        This method finds the most urgent one and tells you that level.
        """
        # 🔍 NO PROBLEMS FOUND - like checking an empty waiting room
        if not self.all_matches:
            return None
        
        # 📋 GET ALL THE SEVERITY LEVELS - like making a list of all patient conditions
        severities = [match.pattern.severity.value for match in self.all_matches]
        
        # 🏥 TRIAGE ORDER - most urgent first (like emergency room priority)
        # We start with "critical" (life-threatening) and work our way down
        severity_order = ["critical", "high", "medium", "low", "info"]
        
        # 🔍 FIND THE WORST CASE - go through the list and return the first match
        # Like a nurse saying "we have 3 minor cuts and 1 broken bone - treat the bone first!"
        for level in severity_order:
            if level in severities:
                return level
        
        # 🤷 SHOULDN'T HAPPEN - but just in case we somehow miss everything
        return None


class ErrorAnalyzer:
    """
    🕵️‍♂️ THE CHIEF DETECTIVE - Main Error Analysis Engine 🕵️‍♂️
    
    This is the head detective who runs the entire error investigation department!
    Just like a police chief coordinates different units (forensics, patrol, etc.),
    this class coordinates all the different parts of error analysis.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this as the principal of a school who:
    - Receives reports of problems (error messages)
    - Assigns the right specialists to investigate (pattern matchers)
    - Reviews all the evidence and makes decisions
    - Writes up official reports for parents/teachers (analysis results)
    - Gives guidance on how to prevent future problems
    
    🔍 WHAT THE CHIEF DETECTIVE DOES:
    1. Takes in crime reports (error messages)
    2. Assigns the right detectives (pattern matchers) to investigate
    3. Reviews all the evidence they collect
    4. Writes comprehensive reports with findings
    5. Provides actionable advice to prevent future incidents
    """
    
    def __init__(self):
        """
        🏢 SETTING UP THE DETECTIVE AGENCY HEADQUARTERS
        
        When we create a new ErrorAnalyzer, it's like opening a new detective agency!
        We need to hire our specialists and set up our investigation tools.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like setting up a new school - you need to:
        - Hire the right teachers (pattern matcher)
        - Set up the record-keeping system (logger)
        - Make sure everything is ready for students to arrive
        """
        # 🔍 HIRE OUR PATTERN RECOGNITION SPECIALIST
        # This is like hiring a detective who's really good at recognizing
        # different types of crimes based on the evidence
        self.pattern_matcher = ErrorPatternMatcher()
        
        # 📁 SET UP OUR INVESTIGATION LOG BOOK
        # Every good detective agency keeps detailed records of what they do
        # This helps us track our work and debug any problems in our own system
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        🔍 THE MAIN INVESTIGATION PROCESS 🔍
        
        This is the core method - like the main investigation procedure that our
        detective agency follows for every case. It's a step-by-step process that
        ensures we don't miss anything important.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Think of this like following a recipe to bake a cake, but instead of making
        dessert, we're "cooking up" a complete analysis of your error:
        
        1. Start the timer (to see how long our investigation takes)
        2. Figure out what programming language this is (like identifying ingredients)
        3. Look for matching error patterns (like checking if the cake is burnt or raw)
        4. Pick the most likely explanation (like diagnosing the main baking problem)
        5. Create helpful labels and tags (like writing "needs more flour" on a sticky note)
        6. Write a summary and suggestions (like giving baking tips for next time)
        7. Package everything into a nice report (like presenting a beautiful cake)
        
        Args:
            request: The case file with all the details about what you want investigated
            
        Returns:
            A complete investigation report with our findings and recommendations
        """
        # ⏱️ START THE INVESTIGATION TIMER
        # Like a detective noting "Case opened at 3:15 PM" in their notebook
        # We track this to see how efficient our analysis process is
        start_time = time.time()
        
        try:
            # 🔍 STEP 1: IDENTIFY THE PROGRAMMING LANGUAGE
            # Like a detective identifying what type of crime scene this is
            # (kitchen accident vs garage mishap vs office incident)
            detected_language = request.language
            if not detected_language or detected_language.lower() == 'auto':
                # 🤔 We don't know the language, so let's figure it out!
                # Like looking at clues to determine where an incident happened
                detected_language = self.pattern_matcher.detect_language(request.text)
                self.logger.debug(f"Detected language: {detected_language}")
            
            # 🔍 STEP 2: LOOK FOR MATCHING ERROR PATTERNS
            # Like going through our "mug shot" database to find similar crimes
            # We limit results to avoid overwhelming the user (like showing top suspects only)
            matches = self.pattern_matcher.find_matches(
                request.text, 
                detected_language
            )[:request.max_matches]  # Only keep the top matches (like interviewing the most likely suspects)
            
            # 🎯 STEP 3: IDENTIFY THE PRIMARY SUSPECT
            # Like a detective saying "based on all evidence, this is our main suspect"
            # We pick the first match because they're sorted by confidence and severity
            primary_error = matches[0] if matches else None
            
            # 🏷️ STEP 4: CREATE CLASSIFICATION TAGS
            # Like putting colored stickers on a case file: "urgent", "python", "beginner-friendly"
            tags = []
            if request.include_tags:
                tags = self._generate_tags(matches, detected_language, request.text)
            
            # 📄 STEP 5: WRITE AN EXECUTIVE SUMMARY
            # Like writing the "TL;DR" version for busy people who just want the main point
            summary = None
            if request.include_suggestions and primary_error:
                summary = self._generate_summary(primary_error, request.text)
            
            # 💡 STEP 6: GENERATE PRACTICAL ADVICE
            # Like a detective giving safety tips: "here's how to prevent this from happening again"
            suggestions = []
            if request.include_suggestions and matches:
                suggestions = self._generate_suggestions(matches)
            
            # 📈 STEP 7: COMPILE INVESTIGATION STATISTICS
            # Like a detective noting "case closed in 45 minutes, interviewed 12 witnesses"
            # This metadata helps us improve our investigation process over time
            processing_time = time.time() - start_time
            metadata = {
                # How long did our investigation take? (in milliseconds for precision)
                'processing_time_ms': int(processing_time * 1000),
                
                # How many different error patterns did we check?
                # (like "we checked 50 different mug shots")
                'patterns_checked': len(self.pattern_matcher.all_patterns),
                
                # How many potential matches did we find?
                # (like "we found 3 possible suspects")
                'matches_found': len(matches),
                
                # Did we have to detect the language ourselves?
                # (like "we had to figure out what type of crime scene this was")
                'language_detection_used': request.language is None or request.language.lower() == 'auto'
            }
            
            # 📁 STEP 8: PACKAGE EVERYTHING INTO THE FINAL REPORT
            # Like putting all our findings into an official police report folder
            # Everything is organized and ready to present to the "client" (the user)
            return AnalysisResult(
                original_text=request.text,           # The original "crime report"
                detected_language=detected_language,  # What type of "crime scene" this was
                primary_error=primary_error,          # Our main suspect
                all_matches=matches,                  # All possible suspects we found
                tags=tags,                           # Classification stickers for the file
                summary=summary,                     # Executive summary for quick reading
                suggestions=suggestions,             # Practical advice and next steps
                metadata=metadata                    # Behind-the-scenes investigation stats
            )
            
        except Exception as e:
            # 🚨 EMERGENCY PROTOCOL: Something went wrong during our investigation!
            # Like when a detective's investigation hits an unexpected snag
            # We log the problem for our records and still give the user SOMETHING useful
            self.logger.error(f"Error during analysis: {e}", exc_info=True)
            
            # 🎆 FALLBACK PLAN: Even if our investigation fails, we don't leave the user hanging
            # Like a detective saying "I couldn't solve your case, but here's what I tried"
            # This ensures the user always gets a response, even if it's just an error message
            return AnalysisResult(
                original_text=request.text,                    # Still return their original problem
                detected_language=detected_language,           # Language we detected (if any)
                primary_error=None,                           # No main error found (investigation failed)
                all_matches=[],                               # No matches found (empty evidence)
                tags=["analysis-failed"],                     # Mark this as a failed investigation
                summary=f"Error analysis failed: {str(e)}",   # Honest explanation of what went wrong
                suggestions=["Please check the input format and try again"],  # Basic helpful advice
                metadata={                                    # Record what happened for debugging
                    'error': str(e), 
                    'processing_time_ms': int((time.time() - start_time) * 1000)
                }
            )
    
    def _generate_tags(self, matches: List[ErrorMatch], language: Optional[str], text: str) -> List[str]:
        """
        🏷️ THE FILING CLERK - Generate Descriptive Tags
        
        This helper method is like a filing clerk who puts colored stickers and labels
        on case files so they're easy to find and organize later. Each tag tells you
        something important about the error at a glance.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Think of this like organizing your music playlist with tags:
        - "Rock", "Pop", "Classical" (genre = error category)
        - "Favorite", "Workout", "Study" (usage = severity/context)
        - "2020s", "90s" (era = programming language)
        
        This method creates similar tags for errors so you can quickly understand:
        - What programming language it's from
        - How serious the problem is
        - What category of error it is
        - Any special characteristics
        """
        # 📦 START WITH AN EMPTY LABEL COLLECTION
        # We use a 'set' to automatically avoid duplicate tags
        # Like having a collection of unique stickers - no duplicates allowed!
        tags = set()
        
        # Add language tag
        if language:
            tags.add(f"{language.title()}")
        
        # Add error type tags
        for match in matches:
            tags.add(match.pattern.name)
            tags.add(match.pattern.category.value.title().replace("_", " "))
            
            if match.pattern.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
                tags.add("Needs Immediate Attention")
            
        # Add contextual tags
        if "stack trace" in text.lower() or "traceback" in text.lower():
            tags.add("Stack Trace")
        
        if len(matches) > 1:
            tags.add("Multiple Errors")
        elif len(matches) == 1:
            tags.add("Single Error")
        else:
            tags.add("No Errors Detected")
        
        # Add severity tag
        if matches:
            severity_levels = [match.pattern.severity.value for match in matches]
            if "critical" in severity_levels:
                tags.add("Critical Issue")
            elif "high" in severity_levels:
                tags.add("High Priority")
            else:
                tags.add("Medium Priority")
        
        return sorted(list(tags))
    
    def _generate_summary(self, primary_error: ErrorMatch, original_text: str) -> str:
        """Generate a human-readable summary of the primary error."""
        pattern = primary_error.pattern
        
        summary_parts = [
            f"🚨 **{pattern.name} Detected**",
            "",
            f"🔍 **What happened:** {pattern.what_happened}",
            ""
        ]
        
        # Add context-specific information if available
        if primary_error.context:
            summary_parts.extend([
                f"📋 **Code context:**",
                f"```",
                primary_error.context,
                f"```",
                ""
            ])
        
        # Add quick fixes
        if pattern.quick_fixes:
            summary_parts.extend([
                "🛠️ **Quick fixes:**"
            ])
            for i, fix in enumerate(pattern.quick_fixes, 1):
                summary_parts.append(f"   {i}. {fix}")
            
            summary_parts.extend([
                "",
                f"💡 **Prevention tip:** {pattern.prevention_tip}",
                "",
                f"📚 **Learn more:** {pattern.learn_more_url}"
            ])
        
        return "\n".join(summary_parts)
    
    def _generate_suggestions(self, matches: List[ErrorMatch]) -> List[str]:
        """Generate actionable suggestions based on all matches."""
        suggestions = []
        
        if not matches:
            suggestions.append("No specific errors detected. Consider checking for:")
            suggestions.extend([
                "- Syntax errors or typos",
                "- Logic errors in your code flow",
                "- Environment or configuration issues"
            ])
            return suggestions
        
        # Add suggestions from each match
        for match in matches[:3]:  # Limit to top 3 matches
            pattern = match.pattern
            
            suggestions.append(f"For {pattern.name}:")
            for fix in pattern.quick_fixes[:2]:  # Limit to 2 fixes per error
                suggestions.append(f"  • {fix}")
        
        # Add general suggestions based on error categories
        categories = set(match.pattern.category for match in matches)
        
        if any(cat.value in ['syntax', 'runtime'] for cat in categories):
            suggestions.append("General debugging tips:")
            suggestions.extend([
                "  • Use a debugger to step through your code",
                "  • Add print statements to trace execution flow",
                "  • Check your IDE for syntax highlighting and warnings"
            ])
        
        return suggestions
    
    def quick_analyze(self, text: str, language: Optional[str] = None) -> Optional[str]:
        """
        Quick analysis for simple use cases.
        
        Args:
            text: Error text to analyze
            language: Optional language hint
            
        Returns:
            Simple string summary or None if no errors found
        """
        request = AnalysisRequest(
            text=text,
            language=language,
            include_context=False,
            include_suggestions=True,
            include_tags=False,
            max_matches=1
        )
        
        result = self.analyze(request)
        
        if result.primary_error:
            pattern = result.primary_error.pattern
            return f"{pattern.name}: {pattern.explanation}"
        
        return None