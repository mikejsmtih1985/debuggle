"""
🤖 CLAUDE AI SPECIALIST - Advanced Error Analysis Consultant! 🧠

This module integrates with Anthropic's Claude AI to provide sophisticated,
context-aware error analysis that goes beyond pattern matching. Think of
Claude as a senior developer consultant who can provide nuanced insights,
suggest specific code fixes, and understand complex debugging scenarios.

🏆 HIGH SCHOOL EXPLANATION:
Imagine you have a challenging physics problem:
- 📖 TEXTBOOK SOLUTION: Look up the formula and apply it (Debuggle's built-in analysis)
- 👨‍🏫 EXPERT TUTOR: Explain the underlying concepts and provide custom guidance (Claude)
- 🤝 BEST APPROACH: Use both - the textbook for quick answers, the tutor for deep understanding

🎯 CLAUDE'S UNIQUE STRENGTHS FOR DEBUGGING:
✅ **Contextual Reasoning** - Understands not just what went wrong, but why
✅ **Code-Aware Analysis** - Can suggest specific fixes based on your actual code
✅ **Pattern Recognition** - Identifies complex error patterns across languages
✅ **Educational Explanations** - Helps you understand and prevent similar issues

🔒 PRIVACY & CONTROL PHILOSOPHY:
- **Opt-in Only**: Claude analysis is completely optional via --claude flag
- **Minimal Data**: Only sends error message and essential context (no full files)
- **Graceful Fallback**: Full Debuggle functionality without Claude
- **User Control**: Clear indication when AI services are being used

🚀 INTEGRATION ARCHITECTURE:
This module acts as a translation layer between Debuggle's structured analysis
and Claude's natural language reasoning, combining the best of both approaches.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import the Anthropic client, but don't fail if it's not installed
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False


@dataclass
class ClaudeEnhancedAnalysis:
    """
    🎯 ENHANCED ANALYSIS CONTAINER - Claude's Professional Diagnosis
    
    This data structure contains Claude's advanced analysis alongside
    Debuggle's standard analysis, providing users with both quick
    answers and deep insights when they want them.
    """
    
    # 🔍 CORE ANALYSIS - Standard Debuggle results (always present)
    original_analysis: str
    error_type: str
    language: str
    severity: str
    
    # 🤖 CLAUDE ENHANCEMENTS - AI-powered insights (when available)
    claude_explanation: Optional[str] = None
    specific_fix_suggestion: Optional[str] = None
    prevention_advice: Optional[str] = None
    confidence_score: Optional[float] = None
    similar_patterns: Optional[list] = None
    
    # 📊 METADATA - Analysis details
    used_claude: bool = False
    claude_model: Optional[str] = None
    analysis_timestamp: datetime = None
    
    def __post_init__(self):
        if self.analysis_timestamp is None:
            self.analysis_timestamp = datetime.now()


class ClaudeAnalyzer:
    """
    🧠 CLAUDE AI CONSULTANT - Professional Error Analysis Enhancement
    
    This class acts as a bridge between Debuggle's fast local analysis and
    Claude's sophisticated reasoning capabilities. It's designed to enhance
    rather than replace Debuggle's core functionality.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like having both a quick reference guide and a personal tutor:
    - 📚 QUICK REFERENCE: Debuggle gives you immediate answers (always works)
    - 👨‍🏫 PERSONAL TUTOR: Claude provides detailed explanations (when you want them)
    - 🤝 COMBINED POWER: Together they make you a better developer
    
    The key insight: Claude doesn't replace Debuggle's analysis - it enriches it!
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        """
        🏗️ SETTING UP THE AI CONSULTATION OFFICE
        
        Initialize the Claude integration with proper error handling and
        graceful degradation. Like setting up a consultation service that
        works even when the specialist isn't available.
        
        Args:
            api_key: Claude API key (will try environment variable if None)
            model: Claude model to use for analysis
        """
        # 🔑 API KEY MANAGEMENT - Secure credential handling
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.model = model
        self.client = None
        self.available = False
        
        # 📊 USAGE TRACKING - Help users understand their AI usage
        self.requests_made = 0
        self.total_tokens_used = 0
        
        # 🚀 INITIALIZATION - Set up the AI consultation service
        self._initialize_client()
    
    def _initialize_client(self):
        """
        🔧 CLIENT SETUP - Establishing connection to Claude's brain
        
        This method safely initializes the Claude client with proper
        error handling. Like testing a phone connection before making
        an important call - we want to know if it works before we need it.
        """
        if not CLAUDE_AVAILABLE:
            logger.info("🤖 Claude integration: Anthropic package not installed (pip install anthropic)")
            return
        
        if not self.api_key:
            logger.info("🤖 Claude integration: No API key provided (set ANTHROPIC_API_KEY environment variable)")
            return
        
        try:
            # 📞 ESTABLISHING CONNECTION - Test the AI consultation line
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.available = True
            logger.info(f"🤖 Claude integration: Ready with model {self.model}")
            
        except Exception as e:
            logger.warning(f"🤖 Claude integration: Failed to initialize - {e}")
            self.available = False
    
    def is_available(self) -> bool:
        """
        ✅ AVAILABILITY CHECK - Is the AI consultant ready to help?
        
        Quick check to see if Claude integration is ready to use.
        This lets users know upfront whether AI enhancement is available.
        """
        return self.available and self.client is not None
    
    def enhance_analysis(
        self,
        original_analysis: str,
        error_message: str,
        error_type: str,
        language: str,
        severity: str,
        file_path: Optional[str] = None,
        project_context: Optional[Dict[str, Any]] = None
    ) -> ClaudeEnhancedAnalysis:
        """
        🚀 AI-POWERED ANALYSIS ENHANCEMENT - Claude's Professional Opinion
        
        This is the core method that takes Debuggle's standard analysis and
        asks Claude to provide additional insights, specific fixes, and
        prevention advice. Like getting a second opinion from a specialist.
        
        🏆 HIGH SCHOOL EXPLANATION:
        You've already solved a math problem (Debuggle's analysis), but now
        you're asking the teacher to:
        1. 🔍 Explain why your solution works (deeper understanding)
        2. 💡 Suggest a better approach (optimization)
        3. 🛡️ Show how to avoid similar mistakes (prevention)
        4. 📊 Rate how confident they are in the analysis (quality assessment)
        
        Args:
            original_analysis: Debuggle's standard analysis
            error_message: The actual error that occurred
            error_type: Type of error (IndexError, NullPointerException, etc.)
            language: Programming language
            severity: How serious the error is
            file_path: Where the error occurred (optional)
            project_context: Additional project information (optional)
            
        Returns:
            ClaudeEnhancedAnalysis: Combined analysis with AI insights
        """
        # 🏁 START WITH WHAT WE HAVE - Debuggle's reliable baseline
        enhanced = ClaudeEnhancedAnalysis(
            original_analysis=original_analysis,
            error_type=error_type,
            language=language,
            severity=severity
        )
        
        # 🤖 AI ENHANCEMENT - Only if Claude is available
        if not self.is_available():
            logger.info("🤖 Claude not available - returning standard analysis")
            return enhanced
        
        try:
            # 🎯 REQUEST CLAUDE'S EXPERTISE - Ask for professional consultation
            claude_response = self._query_claude(
                original_analysis=original_analysis,
                error_message=error_message,
                error_type=error_type,
                language=language,
                severity=severity,
                file_path=file_path,
                project_context=project_context
            )
            
            # 📊 PARSE AND INTEGRATE - Combine Claude's insights with our analysis
            if claude_response:
                enhanced.claude_explanation = claude_response.get('explanation')
                enhanced.specific_fix_suggestion = claude_response.get('fix_suggestion')
                enhanced.prevention_advice = claude_response.get('prevention_advice')
                enhanced.confidence_score = claude_response.get('confidence_score', 0.8)
                enhanced.similar_patterns = claude_response.get('similar_patterns', [])
                enhanced.used_claude = True
                enhanced.claude_model = self.model
                
                # 📈 USAGE TRACKING - Help users understand AI usage
                self.requests_made += 1
                self.total_tokens_used += claude_response.get('tokens_used', 0)
                
                logger.info(f"🤖 Claude analysis completed (confidence: {enhanced.confidence_score:.1%})")
            
        except Exception as e:
            logger.warning(f"🤖 Claude analysis failed: {e}")
            # Don't fail the entire analysis - just continue without Claude
        
        return enhanced
    
    def _query_claude(
        self,
        original_analysis: str,
        error_message: str,
        error_type: str,
        language: str,
        severity: str,
        file_path: Optional[str] = None,
        project_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        💬 CLAUDE CONSULTATION SESSION - Direct communication with AI specialist
        
        This method crafts a specialized prompt for Claude that provides context
        about the error while asking for specific, actionable insights that
        complement Debuggle's analysis.
        
        🧠 PROMPT ENGINEERING STRATEGY:
        We provide Claude with:
        1. 📋 Debuggle's analysis as baseline context
        2. 🎯 Specific questions about fixes and prevention
        3. 🔍 Structured format for consistent responses
        4. 💡 Examples of the kind of insights we want
        """
        try:
            # 🎯 CRAFT THE CONSULTATION REQUEST - Structured prompt for best results
            prompt = self._build_claude_prompt(
                original_analysis=original_analysis,
                error_message=error_message,
                error_type=error_type,
                language=language,
                severity=severity,
                file_path=file_path,
                project_context=project_context
            )
            
            # 📞 MAKE THE API CALL - Request Claude's professional opinion
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,  # Reasonable limit for debugging advice
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # 📊 PARSE CLAUDE'S RESPONSE - Extract structured insights
            return self._parse_claude_response(response)
            
        except Exception as e:
            logger.error(f"🤖 Claude API error: {e}")
            return None
    
    def _build_claude_prompt(
        self,
        original_analysis: str,
        error_message: str,
        error_type: str,
        language: str,
        severity: str,
        file_path: Optional[str] = None,
        project_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        📝 CONSULTATION REQUEST BUILDER - Craft the perfect question for Claude
        
        This method builds a structured prompt that helps Claude provide
        the most useful insights for developers. Like preparing talking
        points before consulting with a specialist.
        """
        
        # 🎯 BASE CONSULTATION REQUEST - Core information for Claude
        prompt_parts = [
            "You are a senior software engineer helping debug an error.",
            "I've already done initial analysis with a local debugging tool.",
            "Please provide additional insights that would help a developer fix and prevent this error.",
            "",
            f"**Error Type:** {error_type}",
            f"**Language:** {language}",
            f"**Severity:** {severity}",
        ]
        
        # 📍 LOCATION CONTEXT - Where the error occurred
        if file_path:
            prompt_parts.append(f"**File:** {file_path}")
        
        # 🏗️ PROJECT CONTEXT - Additional background information
        if project_context:
            if project_context.get('framework'):
                prompt_parts.append(f"**Framework:** {project_context['framework']}")
            if project_context.get('dependencies'):
                prompt_parts.append(f"**Key Dependencies:** {', '.join(project_context['dependencies'][:3])}")
        
        prompt_parts.extend([
            "",
            "**Raw Error:**",
            error_message,
            "",
            "**Local Analysis (already provided to user):**",
            original_analysis,
            "",
            "**Please provide (in JSON format):**",
            "1. `explanation`: A deeper explanation of why this error occurs",
            "2. `fix_suggestion`: Specific code changes or commands to fix this",
            "3. `prevention_advice`: How to prevent similar errors in the future",
            "4. `confidence_score`: Your confidence in this analysis (0.0-1.0)",
            "5. `similar_patterns`: Array of related error patterns to watch for",
            "",
            "Focus on actionable advice that complements the local analysis.",
            "Be concise but thorough. Respond only with valid JSON."
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_claude_response(self, response) -> Optional[Dict[str, Any]]:
        """
        🔍 RESPONSE INTERPRETER - Extract structured insights from Claude
        
        Parse Claude's response and extract the structured information
        we need for enhanced analysis. Like interpreting a specialist's
        report and extracting the key recommendations.
        """
        try:
            # 📝 EXTRACT THE CORE CONTENT - Get Claude's actual response
            content = response.content[0].text.strip()
            
            # 🧹 CLEAN UP JSON - Remove any markdown formatting
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # 📊 PARSE STRUCTURED RESPONSE - Convert to usable data
            parsed = json.loads(content)
            
            # 📈 ADD USAGE METADATA - Track token usage for cost awareness
            parsed['tokens_used'] = response.usage.input_tokens + response.usage.output_tokens
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.warning(f"🤖 Failed to parse Claude response as JSON: {e}")
            # Try to extract useful information anyway
            return {
                'explanation': response.content[0].text,
                'confidence_score': 0.5,
                'tokens_used': getattr(response.usage, 'input_tokens', 0) + getattr(response.usage, 'output_tokens', 0)
            }
        
        except Exception as e:
            logger.error(f"🤖 Failed to parse Claude response: {e}")
            return None
    
    def format_enhanced_output(self, analysis: ClaudeEnhancedAnalysis) -> str:
        """
        🎨 PROFESSIONAL REPORT FORMATTER - Present analysis in readable format
        
        Transform the enhanced analysis into a beautifully formatted output
        that clearly shows both Debuggle's analysis and Claude's insights.
        Like creating a professional consultation report.
        
        🏆 HIGH SCHOOL EXPLANATION:
        You have both your homework solution and your teacher's feedback.
        This method presents them together in a way that's easy to read
        and understand, showing clearly what came from where.
        """
        
        # 🎯 START WITH DEBUGGLE'S RELIABLE ANALYSIS
        output_parts = [
            "🚀 Debuggle Enhanced Analysis",
            "=" * 50,
            "",
            "📊 **Local Analysis:**",
            analysis.original_analysis,
        ]
        
        # 🤖 ADD CLAUDE'S INSIGHTS (if available)
        if analysis.used_claude and analysis.claude_explanation:
            output_parts.extend([
                "",
                f"🤖 **Claude AI Insights** (confidence: {analysis.confidence_score:.1%}):",
                "",
                "💡 **Deeper Explanation:**",
                analysis.claude_explanation,
            ])
            
            if analysis.specific_fix_suggestion:
                output_parts.extend([
                    "",
                    "🔧 **Specific Fix Suggestion:**",
                    analysis.specific_fix_suggestion,
                ])
            
            if analysis.prevention_advice:
                output_parts.extend([
                    "",
                    "🛡️ **Prevention Advice:**",
                    analysis.prevention_advice,
                ])
            
            if analysis.similar_patterns:
                output_parts.extend([
                    "",
                    "🔍 **Related Patterns to Watch:**",
                    "• " + "\n• ".join(analysis.similar_patterns),
                ])
        
        # 📊 ANALYSIS METADATA - Show what tools were used
        output_parts.extend([
            "",
            "=" * 50,
            f"🛠️ Analysis by: Debuggle" + (f" + Claude AI ({analysis.claude_model})" if analysis.used_claude else ""),
            f"⏱️ Generated: {analysis.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        ])
        
        if analysis.used_claude:
            output_parts.append("🤖 AI enhancement: Enabled")
        else:
            output_parts.append("🤖 AI enhancement: Not used (add --claude flag to enable)")
        
        return "\n".join(output_parts)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        📊 USAGE STATISTICS - Help users track their AI consumption
        
        Provide transparency about Claude API usage to help users
        understand and control their costs.
        """
        return {
            'available': self.is_available(),
            'requests_made': self.requests_made,
            'total_tokens_used': self.total_tokens_used,
            'estimated_cost_usd': self.total_tokens_used * 0.000003,  # Rough estimate
            'model': self.model
        }