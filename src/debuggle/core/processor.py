"""
LogProcessor - The Master Detective of Programming Errors! 🕵️‍♂️🔍

Think of this module as the "Chief Detective" at a police station who coordinates
the entire investigation process. When a crime (programming error) is reported:

1. The Chief Detective (LogProcessor) receives the case
2. Assigns specialists: Pattern Analyst (ErrorAnalyzer), Context Investigator (ContextExtractor)
3. Coordinates the investigation across all departments
4. Compiles the final report with findings and recommendations

This is the "brain" that makes Debuggle so much better than ChatGPT because:
- It uses specialized algorithms designed specifically for programming errors
- It automatically extracts context that humans forget to provide
- It applies consistent analysis methodology every time
- It learns from patterns across thousands of error types

The modular architecture means each component is like a specialist detective:
- ErrorAnalyzer: Identifies what type of error occurred (like a forensic expert)
- ContextExtractor: Gathers environmental clues (like a scene investigator)  
- PatternMatcher: Recognizes known criminal patterns (like a profiler)
"""

# Import Python's built-in tools - like getting standard police equipment
import logging  # For recording investigation notes (system logs)
import time     # For measuring how long investigations take
from typing import Dict, List, Optional, Tuple, Any  # Type hints for clarity

# Import our specialized detective units - like calling in the expert teams
from .analyzer import ErrorAnalyzer, AnalysisRequest, AnalysisResult  # The forensics lab
from .context import ContextExtractor, DevelopmentContext              # The scene investigators
from .patterns import ErrorPatternMatcher                              # The criminal profilers


# Set up our investigation logging system - like a police station's record-keeping
logger = logging.getLogger(__name__)


class LogProcessor:
    """
    The Master Detective - Coordinates All Error Investigation Activities! 🕵️‍♂️📋
    
    This is like the Chief of Police who manages the entire police station.
    When a crime (programming error) is reported:
    
    1. 📞 Receives the initial report (raw error logs)
    2. 🔍 Assigns the right specialists to investigate 
    3. 📊 Coordinates evidence gathering from multiple sources
    4. 📝 Compiles the final investigation report
    5. 💡 Provides recommendations for solving the case
    
    Why this architecture is so powerful:
    - **Modular Design**: Each component has a specific job (like different police departments)
    - **Consistent Results**: Same analysis process every time (no human bias)
    - **Scalable**: Can handle one error or thousands simultaneously
    - **Extensible**: Easy to add new types of analysis (like adding new detective units)
    
    This is what gives Debuggle its competitive advantage over ChatGPT - we have
    a systematic, repeatable, and comprehensive investigation process!
    """
    
    def __init__(self):
        """
        Set up the Police Station - Initialize All Detective Units! 🏢👮‍♂️
        
        This is like setting up a new police station with all the necessary departments:
        - Forensics lab (ErrorAnalyzer) for examining the evidence
        - Scene investigation unit (ContextExtractor) for gathering environmental clues
        - Records department (logger) for documenting everything
        
        We use "lazy initialization" for some components - like having detective units
        on-call rather than always active, to save resources.
        """
        # Set up our main forensics lab - always ready to analyze errors
        self.analyzer = ErrorAnalyzer()
        
        # Set up our scene investigation unit - initialized only when needed (lazy loading)
        # This saves memory and startup time since context extraction is resource-intensive
        self.context_extractor = None  # Will be created when first needed
        
        # Set up our record-keeping system - like a police station's incident log
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def process_log(
        self, 
        log_input: str, 
        language: str = 'auto', 
        highlight: bool = True, 
        summarize: bool = True, 
        tags: bool = True, 
        max_lines: int = 1000
    ) -> Tuple[str, Optional[str], List[str], Dict[str, Any]]:
        """
        The Main Investigation Process - Turn Raw Evidence into Actionable Insights! 🔍📊
        
        This is like the standard police investigation procedure that every detective
        follows when a crime is reported. It ensures consistent, thorough analysis
        every single time, regardless of who's doing the investigation.
        
        Think of it as a crime scene investigation checklist:
        1. 📋 Secure and document the scene (validate input)
        2. 🔍 Collect evidence (analyze the error)
        3. 🏷️ Categorize findings (generate tags)
        4. 📝 Write report summary (generate human-readable explanation)
        5. 📊 Document investigation metadata (processing stats)
        
        This systematic approach is why Debuggle gives consistent, reliable results
        compared to asking ChatGPT, where the quality depends on how well you
        describe the problem and ChatGPT's current "mood"!
        
        Parameters explained (like filling out a police report):
            log_input: The "crime scene evidence" (your error logs/stack traces)
            language: Programming language hint (helps focus the investigation)
            highlight: Whether to format output nicely (legacy - like report formatting)
            summarize: Whether to write a summary report (recommended!)
            tags: Whether to categorize the type of error (helps with patterns)
            max_lines: Investigation scope limit (prevents overwhelming analysis)
            
        Returns (the complete investigation file):
            - cleaned_log: Organized, readable version of the evidence
            - summary: Human-readable explanation of what went wrong
            - tags: Categories/types of errors found (like crime classifications)
            - metadata: Investigation statistics and technical details
        """
        # Start the investigation timer - like logging when the case began
        start_time = time.time()
        
        try:
            # INVESTIGATION STEP 1: Secure the Crime Scene (Input Validation)
            # Like a police officer deciding if they can handle this case or need backup
            lines = log_input.split('\n')
            truncated = len(lines) > max_lines
            if truncated:
                # If the case is too big, focus on the most important evidence
                # Like analyzing the first 1000 witness statements instead of all 10,000
                lines = lines[:max_lines]
                log_input = '\n'.join(lines)
            
            # INVESTIGATION STEP 2: Fill Out the Case Assignment Form
            # This tells our forensics lab exactly what type of analysis we need
            request = AnalysisRequest(
                text=log_input,                                     # The evidence to analyze
                language=language if language != 'auto' else None, # Programming language clue
                include_context=True,                               # Look for surrounding clues
                include_suggestions=summarize,                      # Provide solving recommendations
                include_tags=tags,                                  # Categorize the crime type
                max_matches=5                                       # Don't overwhelm with too many findings
            )
            
            # INVESTIGATION STEP 3: Send to Forensics Lab
            # Our ErrorAnalyzer examines the evidence using specialized algorithms
            result = self.analyzer.analyze(request)
            
            # INVESTIGATION STEP 4: Clean Up the Evidence for the Report
            # Make the raw evidence readable and organized (like cleaning up a messy crime scene photo)
            cleaned_log = self._format_cleaned_log(log_input, result)
            
            # INVESTIGATION STEP 5: Write the Summary Report (if requested)
            # Like a detective writing "Here's what we think happened" in plain English
            summary = result.summary if summarize else None
            
            # INVESTIGATION STEP 6: Apply Crime Classification Tags
            # Like labeling a case as "Burglary", "Fraud", etc. - helps with pattern recognition
            tags_list = result.tags if tags else []
            
            # INVESTIGATION STEP 7: Compile Investigation Statistics
            # Like filling out the case completion report with all the technical details
            processing_time = int((time.time() - start_time) * 1000)  # How long did the investigation take?
            metadata = {
                'lines': len(lines),                                                      # How much evidence we processed
                'language_detected': result.detected_language or 'unknown',              # What programming language we identified
                'processing_time_ms': processing_time,                                   # Investigation duration in milliseconds
                'truncated': truncated,                                                  # Did we have to limit the scope?
                'errors_found': len(result.all_matches),                                # How many errors we found
                'primary_error': result.primary_error.pattern.name if result.primary_error else None  # Main crime type
            }
            
            # Return the complete investigation file
            return cleaned_log, summary, tags_list, metadata
            
        except Exception as e:
            # EMERGENCY PROTOCOL: When Our Investigation Tools Fail!
            # Even the best detective equipment sometimes breaks - we need a backup plan
            # This is like having an emergency procedure when the forensics lab catches fire
            
            # Log the incident for our tech team to investigate later
            self.logger.error(f"Log processing failed: {e}", exc_info=True)
            
            # GRACEFUL DEGRADATION: Still provide something useful to the user
            # Instead of completely failing, we return basic information
            # Like a detective saying "I couldn't solve the case, but here's what I saw"
            processing_time = int((time.time() - start_time) * 1000)
            return (
                log_input,                          # Return the original evidence unchanged
                f"Processing failed: {str(e)}",     # Honest explanation of what went wrong
                ["processing-error"],               # Tag this as a system error
                {
                    # Basic statistics we can calculate even when our tools fail
                    'lines': len(log_input.split('\n')),
                    'language_detected': 'unknown',
                    'processing_time_ms': processing_time,
                    'truncated': False,
                    'error': str(e)  # Include the technical error for debugging
                }
            )
    
    def process_log_with_context(
        self,
        log_input: str,
        project_root: Optional[str] = None,
        file_path: Optional[str] = None,
        language: str = 'auto',
        highlight: bool = True,
        summarize: bool = True,
        tags: bool = True,
        max_lines: int = 1000
    ) -> Tuple[str, Optional[str], List[str], Dict[str, Any], str]:
        """
        🚀 THE CHATGPT KILLER - Investigation with Full Crime Scene Reconstruction! 🏗️🔍
        
        This is what makes Debuggle DRAMATICALLY superior to ChatGPT! When you copy/paste
        an error to ChatGPT, you're like a witness giving incomplete testimony. But we're
        like CSI investigators who reconstruct the entire crime scene!
        
        What ChatGPT gets: "My car won't start" (just the error message)
        What Debuggle gets: 
        - Full diagnostic scan of your car (error + context)
        - Recent maintenance history (git changes)
        - Owner's manual (project documentation) 
        - Mechanic's notes (code comments)
        - Similar cases in the area (error patterns)
        - Environmental conditions (system info)
        
        This comprehensive context lets us provide solutions that are:
        ✅ Specific to YOUR actual codebase (not generic advice)
        ✅ Aware of recent changes that might have caused the issue
        ✅ Informed by your project structure and dependencies
        ✅ Consistent with your coding patterns and conventions
        
        Parameters (the investigation scope):
            log_input: The initial crime report (error logs)
            project_root: The neighborhood to investigate (your project folder)
            file_path: Specific address if known (exact file with the error)
            language: Local dialect (programming language)
            highlight: Report formatting preference
            summarize: Whether to write an executive summary
            tags: Whether to classify the incident type
            max_lines: Investigation scope limit
            
        Returns (the complete case file):
            All the basic investigation results PLUS:
            rich_context: The full crime scene reconstruction that ChatGPT never sees!
        """
        # Start the enhanced investigation timer
        start_time = time.time()
        
        try:
            # PHASE 1: Standard Investigation (same as regular police work)
            # This gets us the basic facts about the error
            cleaned_log, summary, tags_list, metadata = self.process_log(
                log_input, language, highlight, summarize, tags, max_lines
            )
            
            # PHASE 2: Deploy the CSI Team (Context Extraction)
            # This is where we go beyond what ChatGPT can ever do!
            
            # Set up our scene investigation unit if not already deployed
            if self.context_extractor is None:
                # Like calling in the CSI team for the first time
                self.context_extractor = ContextExtractor(project_root)
            
            # Perform comprehensive crime scene reconstruction
            # This examines:
            # - The actual code files involved
            # - Recent changes (git history)
            # - Project structure and dependencies  
            # - Related files and imports
            # - Environment configuration
            dev_context = self.context_extractor.extract_full_context(log_input, file_path)
            
            # PHASE 3: Format the Complete Investigation Report
            # Turn all our findings into a readable, actionable report
            rich_context = self.context_extractor.format_context_for_display(dev_context)
            
            # PHASE 4: Update Investigation Statistics
            # Document how much extra work the context extraction required
            context_time = int((time.time() - start_time) * 1000)
            metadata['context_extraction_time_ms'] = context_time - metadata['processing_time_ms']
            metadata['has_rich_context'] = True  # Flag that we did the full investigation
            metadata['context_sources'] = dev_context.extraction_metadata.get('context_sources', [])
            
            # Return the complete case file with full context
            return cleaned_log, summary, tags_list, metadata, rich_context
            
        except Exception as e:
            self.logger.error(f"Context processing failed: {e}", exc_info=True)
            
            # Fall back to basic processing
            cleaned_log, summary, tags_list, metadata = self.process_log(
                log_input, language, highlight, summarize, tags, max_lines
            )
            
            error_context = f"❌ Context extraction failed: {str(e)}\n\n"
            error_context += "📋 **Basic Error Analysis:**\n"
            error_context += f"```\n{cleaned_log}\n```\n\n"
            if summary:
                error_context += f"**Summary:** {summary}"
            
            metadata['context_extraction_error'] = str(e)
            
            return cleaned_log, summary, tags_list, metadata, error_context
    
    def _format_cleaned_log(self, original_text: str, analysis_result: AnalysisResult) -> str:
        """
        Format the cleaned log output.
        
        For now, this does basic cleanup. In the future, this could include
        syntax highlighting, line numbering, etc.
        """
        # Basic cleanup: remove excessive whitespace and empty lines
        lines = original_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped = line.rstrip()
            if stripped or (cleaned_lines and cleaned_lines[-1]):  # Keep non-empty lines and single empty lines
                cleaned_lines.append(stripped)
        
        # Remove trailing empty lines
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    def detect_language(self, text: str) -> str:
        """Detect programming language from text."""
        detected = self.analyzer.pattern_matcher.detect_language(text)
        return detected or 'unknown'
    
    def extract_error_tags(self, text: str) -> List[str]:
        """Extract error tags from text."""
        request = AnalysisRequest(
            text=text,
            include_context=False,
            include_suggestions=False,
            include_tags=True,
            max_matches=10
        )
        
        result = self.analyzer.analyze(request)
        return result.tags
    
    def generate_summary(self, text: str) -> Optional[str]:
        """Generate error summary from text."""
        request = AnalysisRequest(
            text=text,
            include_context=False,
            include_suggestions=True,
            include_tags=False,
            max_matches=1
        )
        
        result = self.analyzer.analyze(request)
        return result.summary
    
    def quick_analyze(self, text: str, language: Optional[str] = None) -> Optional[str]:
        """Quick analysis for simple use cases."""
        return self.analyzer.quick_analyze(text, language)


# Legacy compatibility: maintain the old class structure for imports
class ErrorAnalysis:
    """Legacy compatibility class."""
    
    def __init__(self):
        self.processor = LogProcessor()
    
    def analyze_error(self, text: str) -> str:
        """Analyze error and return simple string result."""
        result = self.processor.quick_analyze(text)
        return result or "No specific error patterns detected."