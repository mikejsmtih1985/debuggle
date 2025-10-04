"""
Hospital Departments Registry - All Medical Departments Connected!

This is like the hospital's main directory that connects you to all the different
medical departments. Instead of wandering around looking for the right department,
this central registry helps route patients (API requests) to the correct specialists.

HIGH SCHOOL EXPLANATION:
Think of this like a school's main office directory:
- "Need to see the nurse?" → Route to health services
- "Want to submit homework?" → Route to academic department  
- "Need transcripts?" → Route to records office
- "Emergency?" → Route to emergency services

Each department has specialists who know exactly how to handle
their specific types of requests!
"""

from fastapi import APIRouter

# Import all department routers
from .analysis import router as analysis_router
from .upload import router as upload_router
from .dashboard import router as dashboard_router
from .alerts import router as alerts_router
from .ingestion import router as ingestion_router
from .storage import router as storage_router
from .common import router as common_router
from .realtime import router as realtime_router

# Create the main hospital router that connects all departments
main_router = APIRouter()

# Register all department routers
main_router.include_router(common_router)      # System-wide routes (health, info)
main_router.include_router(analysis_router)   # Error analysis department
main_router.include_router(upload_router)     # File upload department
main_router.include_router(dashboard_router)  # Analytics dashboard department
main_router.include_router(alerts_router)     # Alert system department
main_router.include_router(ingestion_router)  # Data ingestion department
main_router.include_router(storage_router)    # Storage and search department
main_router.include_router(realtime_router)   # Real-time WebSocket department

# Export the main router so the app factory can use it
router = main_router