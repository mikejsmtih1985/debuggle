"""
📤 File Upload Department - Models for Medical File Processing

This is the file upload department of our hospital! Just like how a hospital
processes different types of medical documents (X-rays, lab reports, patient files),
we process different types of code files and transform them into clean diagnostic reports.

Think of this like the medical records department:
- FileUploadMetadata: The processing receipt and technical details
- FileUploadResponse: The complete processed file with diagnosis

🏆 HIGH SCHOOL EXPLANATION:
Like taking your film to get developed at a photo lab:
1. You drop off a roll of film (upload a log file)
2. Lab processes it and records technical details (FileUploadMetadata)
3. You get back developed photos with information sheet (FileUploadResponse)
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class FileUploadMetadata(BaseModel):
    """
    📊 FILE PROCESSING RECEIPT - Technical Details About Your Upload
    
    This is like the receipt you get when you drop off your dry cleaning -
    it tells you exactly what was processed, when it was done, and any
    special notes about the service.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like getting a report card for your file upload:
    - filename: "math_homework.py" (what you called your file)
    - file_size: "5,432 bytes" (how big your file was)
    - lines: "247 lines" (how much content it had)
    - language_detected: "Python" (what type of code it was)
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