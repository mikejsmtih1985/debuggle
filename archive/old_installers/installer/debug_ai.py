#!/usr/bin/env python3
"""
Buggle - Debuggle's AI Assistant
================================

Meet Buggle, your intelligent debugging companion powered by multiple AI providers.
Buggle can analyze errors, suggest fixes, walk through installations, and learn
from your specific development environment.

Buggle is designed to work with:
- OpenAI GPT models
- Anthropic Claude
- Google Gemini
- Local models via Ollama
- Fallback to rule-based responses

Buggle's personality:
- Friendly and encouraging
- Technically precise but approachable  
- Remembers context across conversations
- Adapts explanations to user expertise level
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import hashlib

# AI Provider imports (with graceful fallbacks)
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import google.generativeai as genai
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """Context for maintaining conversation state"""
    user_id: str
    session_id: str
    environment_info: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    user_expertise_level: str  # beginner, intermediate, advanced
    preferred_explanation_style: str  # concise, detailed, step-by-step
    current_task: Optional[str] = None
    error_context: Optional[Dict[str, Any]] = None

@dataclass
class AIResponse:
    """Structured AI response"""
    message: str
    suggestions: List[str]
    code_examples: List[str] = None
    follow_up_questions: List[str] = None
    confidence_level: float = 0.8
    source: str = "debug_ai"

class BuggleAI:
    """Buggle - Debuggle's AI Assistant"""
    
    def __init__(self):
        self.name = "Buggle"
        self.personality = {
            "tone": "friendly and encouraging",
            "expertise": "debugging and development workflows",
            "approach": "practical problem-solving with clear explanations"
        }
        
        # Initialize AI providers
        self.providers = self._initialize_providers()
        self.active_provider = self._select_best_provider()
        
        # Conversation management
        self.conversations: Dict[str, ConversationContext] = {}
        self.knowledge_base = self._load_knowledge_base()
        
        logger.info(f"Buggle AI initialized with provider: {self.active_provider}")
    
    def _initialize_providers(self) -> Dict[str, Any]:
        """Initialize available AI providers"""
        providers = {}
        
        # OpenAI
        if HAS_OPENAI and os.getenv('OPENAI_API_KEY'):
            try:
                openai.api_key = os.getenv('OPENAI_API_KEY')
                providers['openai'] = {
                    'client': openai,
                    'model': 'gpt-4',
                    'available': True,
                    'priority': 1
                }
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")
        
        # Anthropic Claude
        if HAS_ANTHROPIC and os.getenv('ANTHROPIC_API_KEY'):
            try:
                providers['anthropic'] = {
                    'client': anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY')),
                    'model': 'claude-3-sonnet-20240229',
                    'available': True,
                    'priority': 2
                }
            except Exception as e:
                logger.warning(f"Anthropic initialization failed: {e}")
        
        # Google Gemini
        if HAS_GOOGLE and os.getenv('GOOGLE_API_KEY'):
            try:
                genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
                providers['google'] = {
                    'client': genai.GenerativeModel('gemini-pro'),
                    'model': 'gemini-pro',
                    'available': True,
                    'priority': 3
                }
            except Exception as e:
                logger.warning(f"Google AI initialization failed: {e}")
        
        # Ollama (local models)
        if HAS_REQUESTS:
            try:
                # Test if Ollama is running
                response = requests.get('http://localhost:11434/api/version', timeout=2)
                if response.status_code == 200:
                    providers['ollama'] = {
                        'client': 'http://localhost:11434',
                        'model': 'llama2',  # Default model
                        'available': True,
                        'priority': 4
                    }
            except Exception:
                pass  # Ollama not available
        
        # Always have fallback
        providers['fallback'] = {
            'client': None,
            'model': 'rule-based',
            'available': True,
            'priority': 999
        }
        
        return providers
    
    def _select_best_provider(self) -> str:
        """Select the best available AI provider"""
        available = [(name, info) for name, info in self.providers.items() 
                    if info['available']]
        
        if not available:
            return 'fallback'
        
        # Sort by priority (lower number = higher priority)
        available.sort(key=lambda x: x[1]['priority'])
        return available[0][0]
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load Debug's knowledge base"""
        return {
            "common_errors": {
                "import_error": {
                    "description": "Python import failures",
                    "solutions": [
                        "Check if package is installed: pip list | grep package_name",
                        "Verify virtual environment is activated",
                        "Check Python path: python -c 'import sys; print(sys.path)'",
                        "Install missing package: pip install package_name"
                    ]
                },
                "connection_error": {
                    "description": "Network or database connection issues",
                    "solutions": [
                        "Check network connectivity: ping target_host",
                        "Verify firewall settings",
                        "Check if service is running: systemctl status service_name",
                        "Review connection string format"
                    ]
                },
                "syntax_error": {
                    "description": "Code syntax issues",
                    "solutions": [
                        "Check for missing brackets, quotes, or colons",
                        "Verify proper indentation",
                        "Use IDE syntax highlighting",
                        "Run code through linter: pylint filename.py"
                    ]
                }
            },
            "environment_guidance": {
                "wsl": "I see you're using WSL! This is great for development. Remember to install packages within WSL, not Windows.",
                "docker": "Docker environments are awesome for consistency! Make sure volumes are properly mounted for persistence.",
                "vscode": "VS Code is an excellent choice! I can help you configure extensions and settings for optimal debugging."
            },
            "installation_help": {
                "dependencies": "I'll help you get all dependencies installed automatically. No need to worry about the details!",
                "vscode_extension": "The VS Code extension will give you real-time error monitoring. It's like having me right in your editor!",
                "troubleshooting": "If anything goes wrong, I'll analyze the error and give you specific steps to fix it."
            }
        }
    
    async def chat(self, message: str, user_id: str = "default", 
                  context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Main chat interface with Buggle"""
        
        # Get or create conversation context
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d')}"
        if session_id not in self.conversations:
            self.conversations[session_id] = ConversationContext(
                user_id=user_id,
                session_id=session_id,
                environment_info=context or {},
                conversation_history=[],
                user_expertise_level="intermediate",
                preferred_explanation_style="detailed"
            )
        
        conv_context = self.conversations[session_id]
        conv_context.conversation_history.append({"role": "user", "content": message})
        
        # Generate response based on active provider
        if self.active_provider == 'openai':
            response = await self._chat_openai(message, conv_context)
        elif self.active_provider == 'anthropic':
            response = await self._chat_anthropic(message, conv_context)
        elif self.active_provider == 'google':
            response = await self._chat_google(message, conv_context)
        elif self.active_provider == 'ollama':
            response = await self._chat_ollama(message, conv_context)
        else:
            response = await self._chat_fallback(message, conv_context)
        
        # Store response in conversation history
        conv_context.conversation_history.append({"role": "assistant", "content": response.message})
        
        return response
    
    async def _chat_openai(self, message: str, context: ConversationContext) -> AIResponse:
        """Chat using OpenAI GPT"""
        try:
            client = self.providers['openai']['client']
            
            # Build system prompt
            system_prompt = self._build_system_prompt(context)
            
            # Build conversation messages
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(context.conversation_history[-10:])  # Last 10 exchanges
            
            response = await client.ChatCompletion.acreate(
                model=self.providers['openai']['model'],
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            return self._parse_ai_response(content, "openai")
            
        except Exception as e:
            logger.error(f"OpenAI chat failed: {e}")
            return await self._chat_fallback(message, context)
    
    async def _chat_anthropic(self, message: str, context: ConversationContext) -> AIResponse:
        """Chat using Anthropic Claude"""
        try:
            client = self.providers['anthropic']['client']
            
            # Build system prompt
            system_prompt = self._build_system_prompt(context)
            
            # Build conversation for Claude
            conversation = ""
            for msg in context.conversation_history[-10:]:
                role = "Human" if msg["role"] == "user" else "Assistant"
                conversation += f"{role}: {msg['content']}\n\n"
            
            response = await client.messages.create(
                model=self.providers['anthropic']['model'],
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": conversation}]
            )
            
            content = response.content[0].text
            return self._parse_ai_response(content, "anthropic")
            
        except Exception as e:
            logger.error(f"Anthropic chat failed: {e}")
            return await self._chat_fallback(message, context)
    
    async def _chat_google(self, message: str, context: ConversationContext) -> AIResponse:
        """Chat using Google Gemini"""
        try:
            model = self.providers['google']['client']
            
            # Build prompt with context
            system_prompt = self._build_system_prompt(context)
            full_prompt = f"{system_prompt}\n\nUser: {message}\nDebug:"
            
            response = model.generate_content(full_prompt)
            content = response.text
            
            return self._parse_ai_response(content, "google")
            
        except Exception as e:
            logger.error(f"Google AI chat failed: {e}")
            return await self._chat_fallback(message, context)
    
    async def _chat_ollama(self, message: str, context: ConversationContext) -> AIResponse:
        """Chat using local Ollama models"""
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(context)
            
            # Make request to Ollama
            import aiohttp
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.providers['ollama']['model'],
                    "prompt": f"{system_prompt}\n\nUser: {message}\nDebug:",
                    "stream": False
                }
                
                async with session.post(
                    f"{self.providers['ollama']['client']}/api/generate",
                    json=payload
                ) as response:
                    result = await response.json()
                    content = result.get('response', '')
                    
                    return self._parse_ai_response(content, "ollama")
                    
        except Exception as e:
            logger.error(f"Ollama chat failed: {e}")
            return await self._chat_fallback(message, context)
    
    async def _chat_fallback(self, message: str, context: ConversationContext) -> AIResponse:
        """Fallback rule-based responses when AI is unavailable"""
        
        message_lower = message.lower()
        
        # Installation help
        if any(word in message_lower for word in ['install', 'setup', 'configure']):
            return AIResponse(
                message="Hi! I'm Buggle, your debugging companion! 🤖\n\n"
                       "I can help you install Debuggle with zero configuration. The new installer "
                       "automatically detects your environment and handles everything for you!\n\n"
                       "Just run: `python3 install.py`\n\n"
                       "I'll detect if you're using WSL, Docker, or any other environment and "
                       "configure everything perfectly. Need help with a specific error?",
                suggestions=[
                    "Run the one-click installer: python3 install.py",
                    "Try the web interface: python3 install.py --web",
                    "Get environment info: python3 installer/demo.py"
                ],
                source="fallback"
            )
        
        # Error analysis
        elif any(word in message_lower for word in ['error', 'bug', 'issue', 'problem']):
            return AIResponse(
                message="I'd love to help you debug that issue! 🔍\n\n"
                       "I can analyze errors, suggest fixes, and even create GitHub issues "
                       "for complex problems. Could you share:\n\n"
                       "1. The error message you're seeing\n"
                       "2. What you were trying to do\n"
                       "3. Your environment (WSL, Docker, etc.)\n\n"
                       "I'll give you specific steps to fix it!",
                suggestions=[
                    "Share the full error message",
                    "Tell me about your environment",
                    "Describe what you were trying to do"
                ],
                source="fallback"
            )
        
        # VS Code help
        elif any(word in message_lower for word in ['vscode', 'vs code', 'extension']):
            return AIResponse(
                message="VS Code integration is one of my favorite features! 💻\n\n"
                       "The Debuggle extension gives you real-time error monitoring right "
                       "in your editor. It automatically:\n\n"
                       "• Detects errors as you code\n"
                       "• Shows intelligent suggestions\n"
                       "• Connects to Debuggle's analysis engine\n\n"
                       "The installer sets this up automatically. Want me to help configure it?",
                suggestions=[
                    "Install with VS Code integration: python3 install.py --vscode",
                    "Check VS Code extension status",
                    "Configure workspace settings"
                ],
                source="fallback"
            )
        
        # General greeting/help
        else:
            return AIResponse(
                message=f"Hello! I'm Buggle, your AI debugging companion! 👋\n\n"
                       f"I'm here to help you with:\n"
                       f"🔧 Installing and configuring Debuggle\n"
                       f"🐛 Analyzing and fixing errors\n"
                       f"💻 Setting up your development environment\n"
                       f"🚀 Optimizing your debugging workflow\n\n"
                       f"What would you like help with today?",
                suggestions=[
                    "Install Debuggle with one command",
                    "Help me fix an error",
                    "Set up VS Code integration",
                    "Explain how Debuggle works"
                ],
                source="fallback"
            )
    
    def _build_system_prompt(self, context: ConversationContext) -> str:
        """Build system prompt for AI models"""
        
        env_info = ""
        if context.environment_info:
            env_info = f"\nUser's environment: {json.dumps(context.environment_info, indent=2)}"
        
        return f"""You are Buggle, the friendly AI assistant for Debuggle - an intelligent error analysis tool.

Your personality:
- Friendly and encouraging, never condescending
- Technically precise but approachable
- Focus on practical solutions
- Remember context from previous messages
- Adapt explanations to user expertise level: {context.user_expertise_level}

Your capabilities:
- Help with Debuggle installation and configuration
- Analyze errors and suggest specific fixes
- Guide users through debugging workflows
- Explain complex technical concepts clearly
- Provide code examples when helpful

Context about Debuggle:
- It's an intelligent error analysis system
- Has a one-click installer that auto-detects environments
- Includes VS Code extension for real-time monitoring
- Works with WSL, Docker, Cloud environments
- Can automatically create GitHub issues for edge cases

{env_info}

Always be helpful, specific, and encouraging. If you don't know something, be honest but offer to help find the answer."""
    
    def _parse_ai_response(self, content: str, source: str) -> AIResponse:
        """Parse AI response into structured format"""
        
        # Simple parsing - in a real implementation, this would be more sophisticated
        lines = content.strip().split('\n')
        message = content
        suggestions = []
        code_examples = []
        
        # Extract code blocks
        in_code_block = False
        current_code = []
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    if current_code:
                        code_examples.append('\n'.join(current_code))
                        current_code = []
                    in_code_block = False
                else:
                    in_code_block = True
            elif in_code_block:
                current_code.append(line)
            elif line.strip().startswith('- ') or line.strip().startswith('• '):
                suggestions.append(line.strip()[2:])
        
        return AIResponse(
            message=message,
            suggestions=suggestions,
            code_examples=code_examples if code_examples else None,
            source=source
        )
    
    def get_installation_guidance(self, environment_type: str) -> str:
        """Get specific installation guidance for environment"""
        guidance = self.knowledge_base["environment_guidance"].get(
            environment_type, 
            "I'll help you get Debuggle installed in your environment!"
        )
        return f"Debug says: {guidance}"
    
    def analyze_error(self, error_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze an error and provide Debug's insights"""
        
        # Simple pattern matching for common errors
        error_lower = error_message.lower()
        
        if 'import' in error_lower and 'error' in error_lower:
            error_type = 'import_error'
        elif 'connection' in error_lower:
            error_type = 'connection_error'
        elif 'syntax' in error_lower:
            error_type = 'syntax_error'
        else:
            error_type = 'unknown'
        
        if error_type in self.knowledge_base["common_errors"]:
            error_info = self.knowledge_base["common_errors"][error_type]
            return {
                "buggle_analysis": f"Buggle here! I recognize this as a {error_info['description']}.",
                "solutions": error_info["solutions"],
                "confidence": 0.8,
                "follow_up": "Would you like me to walk you through any of these solutions step by step?"
            }
        
        return {
            "buggle_analysis": "Buggle here! This error is new to me, but I can still help!",
            "solutions": [
                "Let's look at the full error message together",
                "Check the documentation for the specific tool/library",
                "Try running with more verbose output",
                "I can create a GitHub issue with all the details"
            ],
            "confidence": 0.4,
            "follow_up": "Can you share more context about what you were trying to do?"
        }

# Global Buggle instance
buggle_ai = None

def get_buggle() -> BuggleAI:
    """Get the global Buggle AI instance"""
    global buggle_ai
    if buggle_ai is None:
        buggle_ai = BuggleAI()
    return buggle_ai

# Convenient functions for easy integration
async def ask_buggle(message: str, user_id: str = "default", context: Optional[Dict[str, Any]] = None) -> str:
    """Ask Buggle a question and get a response"""
    buggle = get_buggle()
    response = await buggle.chat(message, user_id, context)
    return response.message

def buggle_says(message: str) -> str:
    """Get Buggle's opinion on something (synchronous, rule-based)"""
    buggle = get_buggle()
    if 'install' in message.lower():
        return "Buggle says: The new one-click installer makes this super easy! Just run `python3 install.py` and I'll handle everything! 🚀"
    elif 'error' in message.lower():
        return "Buggle says: I love solving errors! Share the details and I'll give you specific steps to fix it. 🔍"
    else:
        return "Buggle says: I'm here to help with all your debugging needs! What can I assist you with? 🤖"

if __name__ == '__main__':
    # Demo Buggle AI
    async def demo():
        buggle = get_buggle()
        
        print("🤖 Buggle AI Demo")
        print("================")
        print(f"Active provider: {buggle.active_provider}")
        print()
        
        # Test conversations
        test_messages = [
            "Hello Debug! Can you help me install Debuggle?",
            "I'm getting an import error with my Python code",
            "How do I set up VS Code integration?",
            "My code is throwing a connection error"
        ]
        
        for message in test_messages:
            print(f"User: {message}")
            response = await buggle.chat(message)
            print(f"Buggle: {response.message}")
            if response.suggestions:
                print("Suggestions:")
                for suggestion in response.suggestions:
                    print(f"  • {suggestion}")
            print()
    
    # Run demo
    try:
        import asyncio
        asyncio.run(demo())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")