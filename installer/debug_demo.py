#!/usr/bin/env python3
"""
Buggle AI Integration Example
=============================

Shows how to integrate Buggle AI with real providers and use it in the installer.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from debug_ai import get_buggle, ask_buggle

async def demo_with_real_ai():
    """Demo Buggle with actual AI providers if available"""
    
    print("🤖 BUGGLE AI - REAL PROVIDER DEMO")
    print("=" * 50)
    
    buggle = get_buggle()
    print(f"Active AI Provider: {buggle.active_provider}")
    
    # Check what providers are available
    print("\n🔌 Available AI Providers:")
    for name, info in buggle.providers.items():
        status = "✅" if info["available"] else "❌"
        print(f"   {status} {name}: {info['model']}")
    
    print(f"\n💡 To enable real AI providers, set these environment variables:")
    print(f"   export OPENAI_API_KEY=your_openai_key")
    print(f"   export ANTHROPIC_API_KEY=your_anthropic_key") 
    print(f"   export GOOGLE_API_KEY=your_google_key")
    print(f"   # Or run Ollama locally: ollama serve")
    
    # Demo conversation
    print(f"\n🗣️  CONVERSATION DEMO")
    print(f"=" * 30)
    
    # Simulate installation help scenario
    context = {
        "environment": "wsl",
        "platform": "linux", 
        "has_vscode": True,
        "installation_status": "starting"
    }
    
    questions = [
        "I'm trying to install Debuggle but I'm new to development. Can you help?",
        "What's the difference between the web installer and CLI installer?",
        "I got an error: ModuleNotFoundError: No module named 'fastapi'. What should I do?"
    ]
    
    for question in questions:
        print(f"\nUser: {question}")
        response = await ask_buggle(question, context=context)
        print(f"Buggle: {response}")

def demo_error_analysis():
    """Demo Buggle's error analysis capabilities"""
    
    print("\n🔍 ERROR ANALYSIS DEMO")
    print("=" * 30)
    
    buggle = get_buggle()
    
    # Test various error types
    errors = [
        "ImportError: No module named 'requests'",
        "ConnectionError: Failed to establish a new connection",
        "SyntaxError: invalid syntax (line 42)",
        "AttributeError: 'NoneType' object has no attribute 'get'"
    ]
    
    for error in errors:
        print(f"\n❌ Error: {error}")
        analysis = buggle.analyze_error(error)
        print(f"🤖 {analysis['buggle_analysis']}")
        print("💡 Solutions:")
        for solution in analysis['solutions']:
            print(f"   • {solution}")

def demo_installer_integration():
    """Demo how Buggle integrates with the installer"""
    
    print("\n🚀 INSTALLER INTEGRATION DEMO")
    print("=" * 40)
    
    # Simulate installer scenarios where Buggle would help
    buggle = get_buggle()
    scenarios = [
        {
            "situation": "Environment detection successful",
            "buggle_message": buggle.get_installation_guidance("wsl")
        },
        {
            "situation": "VS Code not found",
            "buggle_message": "Buggle says: No worries! I can install VS Code for you automatically. The installer will use your system's package manager to get it set up perfectly!"
        },
        {
            "situation": "Node.js installation failed", 
            "buggle_message": "Buggle says: I see Node.js installation hit a snag. Let me try a different approach - I'll use the NodeSource repository which usually works better in WSL environments!"
        },
        {
            "situation": "Installation complete",
            "buggle_message": "Buggle says: 🎉 Awesome! Debuggle is now installed and ready to help you catch bugs before they cause problems. Try running some code and watch the magic happen!"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📍 Situation: {scenario['situation']}")
        print(f"🤖 {scenario['buggle_message']}")

async def interactive_buggle_session():
    """Interactive session with Buggle"""
    
    print(f"\n💬 INTERACTIVE BUGGLE SESSION")
    print(f"=" * 40)
    print(f"Chat with Buggle! Type 'quit' to exit.\n")
    
    buggle = get_buggle()
    
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Buggle: Goodbye! Happy debugging! 🤖✨")
                break
            
            if user_input:
                response = await buggle.chat(user_input)
                print(f"Buggle: {response.message}")
                
                if response.suggestions:
                    print("💡 Suggestions:")
                    for suggestion in response.suggestions:
                        print(f"   • {suggestion}")
                print()
                
        except KeyboardInterrupt:
            print(f"\nBuggle: Goodbye! Happy debugging! 🤖✨")
            break
        except Exception as e:
            print(f"Buggle: Oops, I had a glitch: {e}")

def main():
    """Main demo function"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            🤖 MEET BUGGLE - DEBUGGLE'S AI                   ║
║                          Your Intelligent Debugging Companion                ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    print("Buggle is Debuggle's AI assistant that helps with:")
    print("• 🔧 Installation and configuration")
    print("• 🐛 Error analysis and debugging")  
    print("• 💻 Development environment setup")
    print("• 🚀 Workflow optimization")
    print("• 📝 Documentation and guidance")
    
    # Show how Buggle works with different AI backends
    asyncio.run(demo_with_real_ai())
    
    # Demo error analysis
    demo_error_analysis()
    
    # Demo installer integration
    demo_installer_integration()
    
    # Interactive session
    print(f"\n🎮 Want to chat with Buggle? (y/n): ", end="")
    if input().lower().startswith('y'):
        asyncio.run(interactive_buggle_session())

if __name__ == '__main__':
    main()