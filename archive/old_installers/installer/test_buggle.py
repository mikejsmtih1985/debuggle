#!/usr/bin/env python3
"""
Quick Buggle Test
================

Simple test to show off Buggle's capabilities
"""

import sys
from pathlib import Path
import asyncio

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from debug_ai import get_buggle, buggle_says

def test_buggle_basic():
    """Test basic Buggle functionality"""
    print("🤖 BUGGLE QUICK TEST")
    print("=" * 30)
    
    # Test simple responses
    responses = [
        "install help",
        "error debugging", 
        "general question"
    ]
    
    for response_type in responses:
        print(f"\nTest: {response_type}")
        print(f"Buggle: {buggle_says(response_type)}")

def test_buggle_error_analysis():
    """Test Buggle's error analysis"""
    print("\n🔍 BUGGLE ERROR ANALYSIS")
    print("=" * 30)
    
    buggle = get_buggle()
    
    test_errors = [
        "ImportError: No module named 'fastapi'",
        "ConnectionError: Unable to connect to localhost:8000"
    ]
    
    for error in test_errors:
        print(f"\n❌ Error: {error}")
        analysis = buggle.analyze_error(error)
        print(f"🤖 {analysis['buggle_analysis']}")
        print("💡 Top solution:", analysis['solutions'][0])

async def test_buggle_chat():
    """Test Buggle's chat functionality"""
    print("\n💬 BUGGLE CHAT TEST")
    print("=" * 30)
    
    buggle = get_buggle()
    
    test_messages = [
        "Hi Buggle! What's your name?",
        "Help me install Debuggle",
        "I'm getting a Python import error"
    ]
    
    for message in test_messages:
        print(f"\nUser: {message}")
        response = await buggle.chat(message)
        # Truncate long responses for demo
        short_response = response.message[:100] + "..." if len(response.message) > 100 else response.message
        print(f"Buggle: {short_response}")

def main():
    """Run all Buggle tests"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        🤖 MEET BUGGLE - YOUR DEBUG BUDDY                     ║  
║                     Named after "Bug" + "Debuggle" = Buggle!                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Buggle is your friendly AI debugging companion! He can:
• Help with installations and setup
• Analyze errors and suggest fixes  
• Chat about debugging problems
• Work with multiple AI providers or use smart fallbacks
• Create GitHub issues for complex problems

Let's see what Buggle can do!
""")
    
    # Test basic functionality
    test_buggle_basic()
    
    # Test error analysis
    test_buggle_error_analysis()
    
    # Test chat (async)
    asyncio.run(test_buggle_chat())
    
    print(f"\n🎉 That's Buggle! Your new debugging buddy.")
    print(f"💡 To enable real AI providers, set API keys:")
    print(f"   export OPENAI_API_KEY=your_key")
    print(f"   export ANTHROPIC_API_KEY=your_key") 
    print(f"   export GOOGLE_API_KEY=your_key")
    print(f"\n🚀 Ready to install Debuggle with Buggle's help?")
    print(f"   python3 install.py")

if __name__ == '__main__':
    main()