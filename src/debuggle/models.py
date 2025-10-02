"""
🏗️ DEBUGGLE DATA BLUEPRINTS - The Architectural Plans! 🏗️

Think of this file as the "blueprint library" for a construction company!
Just like architects need detailed plans before building a house, programmers
need detailed "data models" before building software features.

🎯 WHAT THIS MODULE DOES:
This file defines all the "data shapes" that Debuggle uses - like templates
that tell us exactly what information we expect and how it should be organized.

🏠 THE BLUEPRINT ANALOGY:
- LanguageEnum: Like a list of approved building materials ("wood", "brick", "steel")
- AnalyzeRequest: Like a work order form ("I want a house with 3 bedrooms, 2 baths")
- AnalyzeResponse: Like the completion report ("Here's your finished house with details")
- Metadata models: Like the inspector's report ("took 5 days, used 1000 bricks")

🔍 HOW DATA MODELS WORK:
1. Define exactly what data we expect (like a form with required fields)
2. Validate that incoming data matches our expectations (like checking ID at a club)
3. Provide helpful error messages when data doesn't match (like a GPS recalculating)
4. Document what each field means (like labels on a circuit breaker box)

Real-world analogy: This is like having standardized forms at a doctor's office -
everyone fills out the same patient information form so the system works smoothly!
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum


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


class AnalyzeOptions(BaseModel):
    """
    🎛️ INVESTIGATION CONTROL PANEL - How Deep Should We Dig?
    
    This is like the control panel on a detective's dashboard - it lets you decide
    how thorough you want the investigation to be. Think of it like ordering at
    a restaurant where you can customize your meal!
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like choosing options when ordering a pizza:
    - highlight: "Make it colorful and easy to read" (like adding visual toppings)
    - summarize: "Give me the TL;DR version" (like asking for a quick explanation)
    - tags: "Categorize it for me" (like organizing your music by genre)
    - max_lines: "Don't make it too long" (like setting a page limit on an essay)
    """
    
    # 🌈 MAKE IT PRETTY - should we add colors and formatting?
    # Like asking "do you want syntax highlighting in your code editor?"
    highlight: bool = Field(default=True, description="Apply syntax highlighting")
    
    # 📝 EXECUTIVE SUMMARY - should we write a human readable explanation?
    # Like asking "do you want the CliffsNotes version?"
    summarize: bool = Field(default=True, description="Generate error summary")
    
    # 🏷️ FILING LABELS - should we add category stickers?
    # Like asking "do you want us to organize this with labels?"
    tags: bool = Field(default=True, description="Generate error tags")
    
    # 📏 LENGTH LIMIT - how much text should we process?
    # Like saying "I only have time to read the first 1000 lines"
    # We set reasonable limits: minimum 1 line, maximum 5000 lines
    max_lines: int = Field(default=1000, ge=1, le=5000, description="Maximum lines to process")


class AnalyzeRequest(BaseModel):
    """
    📋 CRIME REPORT INTAKE FORM - Everything We Need to Start Investigating
    
    This is like the form you fill out when reporting a crime to the police!
    It captures all the essential information our detective agency needs to
    start working on your case.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like a doctor's patient intake form:
    - log_input: "What are your symptoms?" (the error message)
    - language: "What language do you speak?" (programming language)
    - options: "How detailed should the examination be?" (analysis preferences)
    
    The form has built-in validation to make sure we get useful information!
    """
    
    # 📄 THE EVIDENCE - the actual error message or log file content
    # This is the "crime scene photo" - we need at least 1 character,
    # but won't process more than 50,000 characters (that's about 20 pages)
    log_input: str = Field(..., min_length=1, max_length=50000, description="Raw log or stack trace")
    
    # 🗣️ LANGUAGE HINT - what programming language is this from?
    # Defaults to AUTO ("figure it out yourself!") if not specified
    language: LanguageEnum = Field(default=LanguageEnum.AUTO, description="Programming language")
    
    # ⚙️ INVESTIGATION PREFERENCES - how thorough should we be?
    # Uses sensible defaults if you don't specify (like a "standard package")
    options: AnalyzeOptions = Field(default_factory=AnalyzeOptions, description="Processing options")
    
    @field_validator('log_input')
    @classmethod
    def validate_log_input(cls, v):
        """
        🔍 EVIDENCE QUALITY CHECK - Make Sure We Got Something Useful
        
        This is like a receptionist checking that you actually wrote something
        on the form before passing it to the detective. We can't investigate
        an empty crime report!
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like a teacher checking that you didn't turn in a blank homework paper -
        we need actual content to work with, not just empty spaces!
        """
        if not v.strip():  # If it's just whitespace or empty
            raise ValueError('log_input cannot be empty or whitespace only')
        return v


class AnalyzeMetadata(BaseModel):
    """
    📊 INVESTIGATION STATISTICS - Behind-the-Scenes Details
    
    This is like the "investigation report footnotes" that tell you interesting
    details about how the analysis was performed. Think of it like the nutrition
    facts label on food - technical details for those who want to know!
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like the stats at the end of a video game level:
    - lines: "You processed 247 lines of code!" (like enemies defeated)
    - language_detected: "This was Python code!" (like the level theme)
    - processing_time_ms: "Analysis took 150 milliseconds!" (like completion time)
    - truncated: "Had to cut off some text due to size" (like reaching time limit)
    """
    
    # 📏 HOW MUCH TEXT - how many lines did we actually look at?
    # Like counting pages in a book you just read
    lines: int = Field(..., description="Number of lines processed")
    
    # 🔍 LANGUAGE DETECTION RESULT - what programming language was this?
    # Like a detective saying "after investigation, this is definitely Spanish"
    language_detected: str = Field(..., description="Detected or specified language")
    
    # ⏱️ SPEED MEASUREMENT - how fast was our analysis?
    # Measured in milliseconds (1000 milliseconds = 1 second)
    # Like timing how long it takes to solve a math problem
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    
    # ✂️ DID WE HAVE TO CUT IT SHORT? - was the input too long?
    # Like having to summarize a 500-page book because you only had time for 100 pages
    truncated: bool = Field(default=False, description="Whether input was truncated")


class AnalyzeResponse(BaseModel):
    """
    📋 COMPLETE INVESTIGATION REPORT - Here's What We Found!
    
    This is like the final police report that gets delivered to you after the
    investigation is complete. It contains everything: the cleaned-up evidence,
    a summary of what happened, category labels, and technical details.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like getting your graded essay back from the teacher:
    - cleaned_log: Your essay with corrections and highlighting (the improved version)
    - summary: Teacher's comment at the top ("Good work on thesis, watch grammar")
    - tags: Categories like "A+ Work", "Needs Grammar Help", "Creative Writing"
    - metadata: Details like "Graded in 10 minutes, 3 pages, marked as English essay"
    """
    
    # 🎨 THE MASTERPIECE - your error message, but cleaned up and prettified
    # Like getting your photo back from a professional photo editor
    cleaned_log: str = Field(..., description="Analyzed and formatted log")
    
    # 📖 PLAIN ENGLISH EXPLANATION - what happened in human terms?
    # Like having a translator explain a foreign movie to you
    # This might be None if we couldn't figure out what the error was
    summary: Optional[str] = Field(None, description="Plain English error explanation")
    
    # 🏷️ CATEGORY STICKERS - quick labels to organize this error
    # Like hashtags on social media posts: #PythonError #Beginner #FixableInMinutes
    tags: List[str] = Field(default_factory=list, description="Error category tags")
    
    # 📊 THE TECHNICAL DETAILS - stats about how the analysis was performed
    # Like the "behind the scenes" extras on a DVD
    metadata: AnalyzeMetadata = Field(..., description="Processing metadata")


class HealthResponse(BaseModel):
    """
    🏥 SYSTEM HEALTH CHECKUP - Is Everything Working OK?
    
    This is like a quick health checkup for our service - a simple way to ask
    "Are you alive and working properly?" It's like taking your pulse or
    checking if a website is online.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like asking a friend "How are you doing?" and getting back:
    - status: "I'm doing great!" or "I'm feeling sick"
    - service: "This is John speaking" (who is responding)
    - version: "I'm John v2.5" (which version of the system is running)
    """
    
    # 💚 HEALTH STATUS - are we healthy, sick, or somewhere in between?
    # Like "OK", "WARNING", or "ERROR" traffic light colors
    status: str = Field(..., description="Service status")
    
    # 🏷️ WHO'S TALKING - which service is responding to this health check?
    # Like caller ID showing you who's calling
    service: str = Field(..., description="Service name")
    
    # 🔢 VERSION NUMBER - what version of the software is running?
    # Like asking "What iOS version are you running?" on your phone
    version: str = Field(..., description="Service version")


class TierFeature(BaseModel):
    """
    🏆 SERVICE LEVEL DESCRIPTION - What Do You Get at Each Level?
    
    This describes one "tier" or level of service we offer. Think of it like
    different membership levels at a gym: Basic, Premium, and VIP each come
    with different features and benefits.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like describing different Netflix subscription plans:
    - name: "Premium Plan" (what it's called)
    - icon: "👑" (a visual symbol for this tier)
    - features: ["4K Video", "Multiple Screens", "Downloads"] (what you get)
    """
    
    # 🎭 TIER NAME - what do we call this service level?
    # Like "Basic", "Pro", "Enterprise", or "Student Plan"
    name: str = Field(..., description="Tier name")
    
    # 🎨 VISUAL SYMBOL - what icon represents this tier?
    # Like emoji or symbols to make it visually recognizable
    icon: str = Field(..., description="Tier icon")
    
    # 📋 WHAT YOU GET - list of features included at this level
    # Like a bullet-point list of benefits
    features: List[str] = Field(..., description="Available features")


class TiersResponse(BaseModel):
    """
    📊 COMPLETE PRICING MENU - All Available Service Levels
    
    This is like a complete menu at a restaurant showing all the different
    meal deals available. Each tier is like a different combo meal with
    different features and prices.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like a phone plan comparison chart that shows Basic, Standard, and Premium
    plans side by side, so you can pick which one fits your needs and budget.
    """
    
    # 📋 ALL THE OPTIONS - complete list of available service tiers
    # Like an array of different membership levels you can choose from
    tiers: List[TierFeature] = Field(..., description="Available service tiers")


class FileUploadMetadata(BaseModel):
    """
    📁 FILE PROCESSING RECEIPT - Details About Your Uploaded File
    
    This is like a receipt you get when dropping off film for development
    at a photo lab. It tells you exactly what file you submitted and how
    the processing went.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like the details you see when uploading a video to YouTube:
    - filename: "my_vacation_video.mp4" (what you called your file)
    - file_size: "25.3 MB" (how big the file was)
    - lines: "1,247 lines processed" (how much content we analyzed)
    - language_detected: "Python" (what type of content it was)
    - processing_time_ms: "1,500ms" (how long it took to process)
    - truncated: "Had to cut it short due to size" (if we couldn't process it all)
    """
    
    # 🏷️ ORIGINAL NAME - what did you call this file?
    # Like the original title of a document you uploaded
    filename: str = Field(..., description="Original filename")
    
    # 📏 FILE SIZE - how big was your file?
    # Measured in bytes (1,024 bytes = 1 KB, 1,024 KB = 1 MB)
    file_size: int = Field(..., description="File size in bytes")
    
    # 📊 CONTENT VOLUME - how many lines of text did we process?
    # Like counting pages in a book you submitted for review
    lines: int = Field(..., description="Number of lines processed")
    
    # 🔍 CONTENT TYPE - what programming language was this?
    # Like identifying a document as "English essay" vs "Spanish poem"
    language_detected: str = Field(..., description="Detected or specified language")
    
    # ⏱️ PROCESSING TIME - how long did it take to analyze?
    # In milliseconds (1000ms = 1 second)
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    
    # ✂️ WAS IT TOO BIG? - did we have to cut off part of the file?
    # Like when you have to summarize a book because it's too long to read fully
    truncated: bool = Field(default=False, description="Whether input was truncated")


class FileUploadResponse(BaseModel):
    """
    📦 FILE ANALYSIS DELIVERY - Your Processed File is Ready!
    
    This is like getting your developed photos back from the photo lab,
    but instead of photos, you're getting back your analyzed and cleaned-up
    error logs with explanations and insights.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like getting your graded project back from the teacher,
    complete with corrections, feedback, category grades, and processing notes.
    """
    
    # 🎨 YOUR FILE, BUT BETTER - cleaned up and formatted nicely
    # Like getting your essay back with proper formatting and highlighting
    cleaned_log: str = Field(..., description="Analyzed and formatted log")
    
    # 📖 TEACHER'S EXPLANATION - what the errors mean in plain English
    # Might be None if the errors were too complex to explain simply
    summary: Optional[str] = Field(None, description="Plain English error explanation")
    
    # 🏷️ CATEGORY LABELS - quick tags to classify your file's contents
    # Like subject tags: "Math", "Science", "Easy Fix", "Needs Attention"
    tags: List[str] = Field(default_factory=list, description="Error category tags")
    
    # 📊 PROCESSING RECEIPT - technical details about how we handled your file
    # Like the metadata about when and how your file was processed
    metadata: FileUploadMetadata = Field(..., description="File processing metadata")


class ErrorResponse(BaseModel):
    """
    🚨 OOPS REPORT - When Something Goes Wrong With Our Service
    
    This is like an error message you see when a website crashes or when
    your phone app stops working. It tells you what went wrong and
    (hopefully) how to fix it.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like getting an error message when your computer won't start:
    - error: "Could not connect to internet" (main problem description)
    - details: "WiFi password might be wrong, or router is offline" (more info)
    - code: "ERROR_WIFI_001" (technical error code for support)
    """
    
    # 🚨 MAIN PROBLEM - what went wrong in simple terms?
    # Like the headline of a news article - the key issue in one sentence
    error: str = Field(..., description="Error message")
    
    # 📝 MORE DETAILS - additional explanation if available
    # Like the article body that explains the headline in more depth
    # This might be None if we don't have extra details
    details: Optional[str] = Field(None, description="Detailed error information")
    
    # 🔢 TECHNICAL CODE - error code for debugging and support
    # Like error codes on blue screens or appliance displays
    # This might be None if we don't have a specific code
    code: Optional[str] = Field(None, description="Error code")