"""
🏗️ COMMON MEDICAL FORMS - Shared Templates & Enums! 🏗️

This file is like the shared forms and reference materials that all
departments in our digital hospital use. Instead of each department
creating their own version of basic forms, everyone uses these
standardized templates.

🏥 SHARED FORM TEMPLATES:
- LogSeverity: How serious is this medical case?
- LanguageEnum: What programming language are we diagnosing?
- HealthResponse: Basic hospital status report
- ErrorResponse: Standard incident report form
- TierFeature: Service level descriptions
- TiersResponse: Available service packages

🏆 HIGH SCHOOL EXPLANATION:
Think of this like the shared office supplies at a school:
- Standard forms that all teachers use (LogSeverity, LanguageEnum)
- Common report templates (HealthResponse, ErrorResponse)
- Service level descriptions (what you get with basic vs premium)

Every department uses these same standards so everything works together
smoothly and patients get consistent service across the hospital!
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


# =============================================================================
# 🌡️ SEVERITY & PRIORITY SCALES - How serious is this?
# =============================================================================

class LogSeverity(str, Enum):
    """
    🌡️ LOG SEVERITY LEVELS - How Serious Is This Message?
    
    Just like a thermometer shows temperature, these levels show how
    serious a log message is. This helps prioritize which problems
    need immediate attention versus which are just informational.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like the triage system in a hospital emergency room:
    - TRACE: "Just checking in" (like a routine checkup)
    - DEBUG: "Learning what's happening" (like monitoring vital signs)
    - INFO: "Here's what's happening" (like updating family on patient status)
    - WARNING: "Something might be wrong" (like abnormal test results)
    - ERROR: "Something is definitely wrong" (like a broken bone)
    - CRITICAL: "Emergency situation!" (like a heart attack)
    """
    TRACE = "trace"      # 🔍 Detailed debugging info
    DEBUG = "debug"      # 🐛 Developer debugging messages  
    INFO = "info"        # ℹ️ General information
    WARNING = "warning"  # ⚠️ Something might be wrong
    ERROR = "error"      # ❌ Something definitely went wrong
    CRITICAL = "critical" # 🚨 System-threatening emergency


# =============================================================================
# 🗺️ PROGRAMMING LANGUAGE SUPPORT - What languages do we speak?
# =============================================================================

class LanguageEnum(str, Enum):
    """
    🗺️ PROGRAMMING LANGUAGE MENU - What Languages Do We Speak?
    
    This is like a restaurant menu that lists all the languages (cuisines) we can handle!
    Just like a restaurant might specialize in Italian, Chinese, and Mexican food,
    Debuggle specializes in different programming languages.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like choosing your foreign language class - you can pick Spanish,
    French, German, etc. Each programming language has its own "grammar rules" and
    common mistakes, just like human languages do.
    
    The "AUTO" option is like having a smart translator who can figure out what
    language you're speaking automatically!
    """
    
    # 🐍 THE SNAKE LANGUAGE - great for beginners, data science, and AI
    PYTHON = "python"
    
    # 🌐 THE WEB LANGUAGE - powers websites and interactive features
    JAVASCRIPT = "javascript"
    
    # ☕ THE ENTERPRISE LANGUAGE - used in big business applications
    JAVA = "java"
    
    # 🏢 THE MICROSOFT LANGUAGE - popular for Windows applications
    CSHARP = "csharp"
    
    # ⚡ THE SPEED DEMON - when you need maximum performance
    CPP = "cpp"
    
    # 🚀 THE GOOGLE LANGUAGE - simple and efficient for servers
    GO = "go"
    
    # 🦀 THE SAFE LANGUAGE - prevents many common programming mistakes
    RUST = "rust"
    
    # 🤖 THE SMART DETECTIVE - "figure it out yourself!" option
    AUTO = "auto"


# =============================================================================
# 🏥 HOSPITAL STATUS & HEALTH REPORTS - How is our facility doing?
# =============================================================================

class HealthResponse(BaseModel):
    """
    💓 HOSPITAL VITAL SIGNS REPORT - System Health Status! 💓
    
    This is like the daily vital signs report for our entire digital hospital.
    Just like doctors check a patient's heart rate, blood pressure, and temperature,
    this report shows the health of all our hospital systems.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like the daily status report from a school:
    - "All systems operational" (like "school is open, everything working")
    - "Cafeteria having issues" (like "lunch service delayed")
    - "Library computers down" (like "some services temporarily unavailable")
    
    This helps patients and staff know if everything is working normally
    or if there are any issues to be aware of.
    """
    
    # �️ SERVICE NAME - which hospital service is this?
    # Like caller ID showing you who's calling
    service: str = Field(..., description="Service name")
    
    # 🔢 VERSION NUMBER - what version of the software is running?
    # Like asking "What iOS version are you running?" on your phone
    version: str = Field(..., description="Service version")
    
    # 💚 HEALTH STATUS - are we healthy, sick, or somewhere in between?
    # Like "OK", "WARNING", or "ERROR" traffic light colors  
    status: str = Field(..., description="Service status")
    
    # ⏱️ RESPONSE TIME - how long did this health check take?
    # Measured in seconds, so 0.1 = 100 milliseconds
    response_time: Optional[float] = Field(None, description="Response time in seconds")
    
    # 📊 ADDITIONAL DETAILS - any extra health information?
    # Like detailed vitals from a medical checkup
    details: Optional[Dict[str, Any]] = Field(None, description="Additional health information")
    
    # 🌡️ SYSTEM METRICS - technical performance numbers
    # Like blood pressure, heart rate, temperature from a checkup
    metrics: Optional[Dict[str, float]] = Field(None, description="System performance metrics")
    
    # ⏰ TIMESTAMP - when was this health check performed?
    # Unix timestamp (seconds since January 1, 1970)
    timestamp: Optional[float] = Field(None, description="When health was checked (Unix timestamp)")


class ErrorResponse(BaseModel):
    """
    📋 INCIDENT REPORT FORM - Standard Error Documentation! 📋
    
    This is like the standard incident report form that hospitals use
    when something goes wrong. Instead of everyone writing incident
    reports differently, this ensures consistent documentation.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like the standard form you fill out when there's
    an accident at school:
    - What happened? (message)
    - How serious was it? (status code)
    - What type of incident? (error type)
    - When did it happen? (timestamp)
    - Any additional details? (details)
    
    This helps administrators understand what went wrong and how
    to prevent similar incidents in the future.
    """
    
    # 📋 INCIDENT IDENTIFICATION
    status: str = Field(
        description="📋 Incident status (like 'error', 'warning', 'resolved')"
    )
    message: str = Field(
        description="📝 What happened (main incident description)"
    )
    
    # 🔢 TECHNICAL CODE - error code for debugging and support
    code: Optional[str] = Field(
        None,
        description="🔢 Technical error code (for IT support)"
    )
    
    # 📖 INCIDENT TYPE - categorization for tracking
    type: Optional[str] = Field(
        None,
        description="📖 Type of incident (validation_error, server_error, etc.)"
    )
    
    # 📄 ADDITIONAL DETAILS - more information if available
    details: Optional[str] = Field(
        None,
        description="📄 Additional technical details (for troubleshooting)"
    )
    
    # ⏰ INCIDENT TIMESTAMP
    timestamp: float = Field(
        description="⏰ When this incident occurred"
    )
    
    # 🆔 INCIDENT TRACKING
    incident_id: Optional[str] = Field(
        None,
        description="🆔 Unique incident ID (for tracking and support)"
    )


# =============================================================================
# 🎫 SERVICE TIER DESCRIPTIONS - What services do we offer?
# =============================================================================

class TierFeature(BaseModel):
    """
    🎫 SERVICE FEATURE DESCRIPTION - What You Get! 🎫
    
    This describes a specific feature or service that comes with
    different service levels, like describing what's included
    in different hotel room types.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like describing what you get with different
    movie theater ticket types:
    - Basic ticket: "Access to movie and standard seating"
    - Premium ticket: "Access to movie, reclining seats, and free popcorn"
    - VIP ticket: "All premium features plus private lounge access"
    
    Each feature has a name and description so customers know
    exactly what value they're getting.
    """
    
    name: str = Field(
        description="🏷️ Name of this feature or service"
    )
    description: str = Field(
        description="📝 What this feature provides"
    )
    included: bool = Field(
        description="✅ Is this feature included in this service tier?"
    )


class TiersResponse(BaseModel):
    """
    🎫 SERVICE TIER MENU - Available Service Packages! 🎫
    
    This is like the service menu at a hotel or airline that shows
    different service levels (economy, business, first class) and
    what features come with each level.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like the different lunch plans at school:
    - Basic plan: "Sandwich and drink"
    - Premium plan: "Sandwich, drink, dessert, and salad bar access"
    - Deluxe plan: "All premium items plus specialty entrees"
    
    This helps customers choose the right service level for their needs.
    """
    
    current_tier: str = Field(
        description="� What service level is currently active"
    )
    available_tiers: Dict[str, List[TierFeature]] = Field(
        description="🎫 All available service tiers and their features"
    )


# Export all our common forms and templates
__all__ = [
    "LogSeverity",
    "LanguageEnum", 
    "HealthResponse",
    "ErrorResponse",
    "TierFeature",
    "TiersResponse"
]