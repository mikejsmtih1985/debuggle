"""
🤖 DEBUGGLE EXTERNAL INTELLIGENCE NETWORK - AI Integration Hub! 🤖

Think of this module as a sophisticated communication center that connects
Debuggle's local analysis capabilities with external AI services. Just like
how a hospital might consult with specialists from other institutions for
complex cases, this module lets Debuggle tap into advanced AI reasoning
when needed - while still maintaining its core promise of privacy and
local-first operation.

🏆 HIGH SCHOOL EXPLANATION:
Imagine you're working on a difficult math problem:
- 📚 LOCAL CAPABILITY: You have your textbook and calculator (Debuggle's built-in analysis)
- 🎓 EXTERNAL CONSULTATION: You can call a tutor for extra help (AI integration)
- 🔒 PRIVACY CONTROL: You decide what information to share and when
- 🏠 LOCAL FIRST: Even without the tutor, you can still solve most problems

WHY THIS APPROACH IS BRILLIANT:
✅ **Best of Both Worlds** - Lightning-fast local analysis + AI superpowers when wanted
✅ **Privacy by Design** - External services are opt-in, not required
✅ **Graceful Degradation** - Full functionality even without AI services
✅ **Cost Control** - Only use expensive AI when it adds real value
✅ **No Vendor Lock-in** - Easy to switch AI providers or disable entirely

🎯 INTEGRATION PHILOSOPHY:
This module follows the "Swiss Army Knife" principle - each integration is a
specialized tool that enhances the core experience without replacing it.
Users get professional-grade debugging whether they use AI or not!
"""

from .claude import ClaudeAnalyzer

__version__ = "1.0.0"
__all__ = [
    "ClaudeAnalyzer"
]