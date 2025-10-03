"""
🔬 Medical Analysis Department - Models for Diagnostic Reports

This is the medical analysis department of our hospital! Just like how a real hospital
has different labs for blood work, X-rays, and MRIs, we have different types of analysis
models for examining code problems.

Think of this like the medical forms used by different hospital departments:
- AnalyzeOptions: The checkboxes on a lab order form
- AnalyzeRequest: The initial patient complaint form
- AnalyzeMetadata: The technical details on a lab report
- AnalyzeResponse: The complete diagnostic report

🏆 HIGH SCHOOL EXPLANATION:
Like going to the doctor when you're sick:
1. You fill out a form describing your symptoms (AnalyzeRequest)
2. Doctor asks what kind of tests you want (AnalyzeOptions)
3. Lab runs the tests and records technical details (AnalyzeMetadata)
4. Doctor gives you the complete results and explanation (AnalyzeResponse)
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from .common import LanguageEnum


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