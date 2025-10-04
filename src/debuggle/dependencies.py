"""
📦 HOSPITAL SUPPLY CHAIN - Dependency Injection System! 📦

This file is like the central supply chain and equipment management
system for our digital hospital. It ensures that every department
has access to the medical equipment, specialists, and resources
they need to do their job effectively.

🏥 SUPPLY CHAIN MANAGEMENT:
- Medical equipment distribution (LogProcessor, DatabaseManager, etc.)
- Specialist assignment (service classes)
- Resource allocation (singleton patterns for efficiency)
- Quality control (validation and error handling)

🔧 EQUIPMENT INVENTORY:
- Core diagnostic tools (LogProcessor)
- Data storage systems (DatabaseManager, SearchManager)
- Communication systems (AlertManager, ConnectionManager)
- Specialized services (AnalysisService, UploadService, etc.)

🏆 HIGH SCHOOL EXPLANATION:
Think of this like the supply chain management for a large hospital:
- Medical equipment gets delivered where it's needed (dependency injection)
- Expensive equipment is shared between departments (singletons)
- Quality control ensures everything works properly (validation)
- Inventory management prevents shortages (proper lifecycle management)

Instead of each department buying their own equipment (creating objects),
they request what they need from the central supply system. This is more
efficient and ensures everyone has access to the same high-quality tools!
"""

from functools import lru_cache
from fastapi import FastAPI, Depends
import logging
from typing import Optional

# Import all our medical equipment and specialists
# Note: Using absolute imports to avoid issues during refactoring
try:
    from src.debuggle.core.processor import LogProcessor
except ImportError:
    from .processor import LogProcessor  # Fallback to current structure

try:
    from src.debuggle.storage import DatabaseManager, SearchManager, RetentionManager
except ImportError:
    from .storage import DatabaseManager, SearchManager, RetentionManager

try:
    from src.debuggle.realtime import connection_manager, error_monitor
except ImportError:
    from .realtime import connection_manager, error_monitor

try:
    from src.debuggle.alerting import AlertManager
except ImportError:
    from .services.alerting import AlertManager

# Set up logging for our supply chain operations
logger = logging.getLogger(__name__)

def setup_all_dependencies(app: FastAPI):
    """
    📦 ESTABLISH HOSPITAL SUPPLY CHAIN! 📦
    
    This function sets up the entire supply chain and equipment
    distribution system for our digital hospital. Like having
    a professional logistics company organize all the medical
    equipment and specialist assignments.
    
    🏥 SUPPLY CHAIN SETUP:
    - Medical equipment distribution centers
    - Specialist assignment protocols
    - Quality control checkpoints
    - Inventory management systems
    """
    logger.info("📦 Setting up hospital supply chain...")
    
    # Initialize core medical equipment (will be created on-demand)
    logger.info("🔧 Preparing medical equipment inventory...")
    
    # Test that all equipment is available and working
    try:
        # Test core diagnostic equipment
        processor = get_log_processor()
        database = get_database_manager()
        logger.info("✅ Core medical equipment operational")
        
        # Test communication systems
        alert_manager = get_alert_manager()
        logger.info("✅ Communication systems operational")
        
        logger.info("✅ Hospital supply chain fully operational!")
        
    except Exception as e:
        logger.error(f"❌ Supply chain setup failed: {e}")
        raise


# =============================================================================
# 🔧 CORE MEDICAL EQUIPMENT - Essential diagnostic and treatment tools
# =============================================================================

@lru_cache()
def get_log_processor() -> LogProcessor:
    """
    🔬 CHIEF DIAGNOSTIC EQUIPMENT - LogProcessor! 🔬
    
    This provides access to our main diagnostic equipment (LogProcessor)
    that analyzes errors and generates insights. Like having a top-of-the-line
    MRI machine that multiple departments can share.
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like having a shared MRI machine in a hospital:
    - Expensive equipment that multiple departments need
    - Only one is needed for the whole hospital (singleton)
    - Always available when departments need it
    - Maintained by specialists to ensure quality
    
    Returns:
        LogProcessor: The main error analysis equipment
    """
    logger.debug("🔬 Providing chief diagnostic equipment (LogProcessor)")
    return LogProcessor()


@lru_cache()
def get_database_manager() -> DatabaseManager:
    """
    💾 MEDICAL RECORDS SYSTEM - DatabaseManager! 💾
    
    This provides access to our central medical records system that
    stores all patient data (logs) and treatment history. Like having
    a central medical records database that all departments can access.
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like the central medical records system in a hospital:
    - All patient information stored in one secure location
    - Multiple departments need access to the same records
    - Only one database needed for the whole hospital (singleton)
    - Professional database administrators maintain it
    
    Returns:
        DatabaseManager: The central medical records system
    """
    logger.debug("💾 Providing medical records system (DatabaseManager)")
    return DatabaseManager("logs.db")


@lru_cache()
def get_search_manager() -> SearchManager:
    """
    🔍 MEDICAL RECORDS SEARCH SYSTEM - SearchManager! 🔍
    
    This provides access to our medical records search system that
    helps doctors quickly find relevant patient information and
    historical cases. Like having a smart search system for medical records.
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like having a smart search system for medical records:
    - Doctors can quickly find similar cases
    - Search through thousands of patient records instantly
    - Find patterns across multiple patients
    - Essential for research and diagnosis
    
    Returns:
        SearchManager: The medical records search system
    """
    logger.debug("🔍 Providing medical records search system (SearchManager)")
    database = get_database_manager()  # Get the database first
    return SearchManager(database)


@lru_cache()
def get_retention_manager() -> RetentionManager:
    """
    📅 MEDICAL RECORDS RETENTION SYSTEM - RetentionManager! 📅
    
    This provides access to our medical records retention system that
    manages how long we keep patient records and when to archive them.
    Like having a professional records management system.
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like having a professional filing system that:
    - Knows how long to keep different types of records
    - Automatically archives old records when appropriate
    - Ensures compliance with privacy regulations
    - Manages storage space efficiently
    
    Returns:
        RetentionManager: The medical records retention system
    """
    logger.debug("📅 Providing medical records retention system (RetentionManager)")
    database = get_database_manager()  # Get the database first
    return RetentionManager(database)


# =============================================================================
# 🚨 COMMUNICATION & ALERT SYSTEMS - Real-time monitoring and notifications
# =============================================================================

@lru_cache()
def get_alert_manager() -> AlertManager:
    """
    🚨 EMERGENCY ALERT SYSTEM - AlertManager! 🚨
    
    This provides access to our emergency alert system that monitors
    for critical situations and sends notifications to the appropriate
    medical staff. Like having a comprehensive emergency alert system.
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like the emergency alert system in a hospital:
    - Monitors all patients for critical conditions
    - Automatically alerts the right doctors when problems arise
    - Manages different types of alerts (code blue, fire, etc.)
    - Ensures critical situations get immediate attention
    
    Returns:
        AlertManager: The emergency alert system
    """
    logger.debug("🚨 Providing emergency alert system (AlertManager)")
    return AlertManager(error_monitor)


def get_connection_manager():
    """
    📡 HOSPITAL COMMUNICATION HUB - ConnectionManager! 📡
    
    This provides access to our hospital-wide communication system
    that enables real-time communication between departments and
    with external systems.
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like the communication system in a hospital:
    - Intercom system for department-to-department communication
    - Emergency broadcast system for critical announcements
    - Patient monitoring displays throughout the facility
    - Real-time status updates for all departments
    
    Returns:
        ConnectionManager: The hospital communication hub
    """
    logger.debug("📡 Providing hospital communication hub (ConnectionManager)")
    return connection_manager


def get_error_monitor():
    """
    👁️ PATIENT MONITORING SYSTEM - ErrorMonitor! 👁️
    
    This provides access to our real-time patient monitoring system
    that watches for any signs of problems or emergencies across
    all hospital systems.
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like the central monitoring station in a hospital:
    - Watches vital signs for all patients simultaneously
    - Alerts medical staff to any concerning changes
    - Tracks patterns and trends across the facility
    - Provides early warning for potential problems
    
    Returns:
        ErrorMonitor: The patient monitoring system
    """
    logger.debug("👁️ Providing patient monitoring system (ErrorMonitor)")
    return error_monitor


# =============================================================================
# 🧠 MEDICAL SPECIALISTS - Business logic and service coordination
# =============================================================================
# Note: These will be implemented as we create the service layer

# =============================================================================
# � FUTURE ROADMAP - Advanced Services (Post-Core Implementation)
# =============================================================================
# 
# These services are planned for future implementation after the core
# CLI functionality is rock-solid. Focus: Ship what works, enhance later.
#
# def get_analysis_service():
#     """Future: Advanced error analysis coordination service"""
#     pass
#
# def get_upload_service():
#     """Future: File upload and processing service"""
#     pass
#
# def get_dashboard_service():
#     """Future: Analytics and visualization service"""
#     pass


# =============================================================================
# 🔧 EQUIPMENT TESTING & VALIDATION - Quality control systems
# =============================================================================

def validate_all_dependencies():
    """
    ✅ EQUIPMENT QUALITY CONTROL CHECK! ✅
    
    This performs a comprehensive quality control check on all
    medical equipment and systems to ensure everything is working
    properly before patients arrive.
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like the daily equipment check in a hospital:
    - Test all medical equipment before the day starts
    - Ensure all computers and systems are working
    - Verify communication systems are operational
    - Check that all departments have what they need
    
    If anything is broken, we find out now instead of when
    a patient needs it!
    """
    logger.info("✅ Starting equipment quality control check...")
    
    try:
        # Test core medical equipment
        processor = get_log_processor()
        database = get_database_manager()
        search = get_search_manager()
        retention = get_retention_manager()
        
        # Test communication systems
        alerts = get_alert_manager()
        comms = get_connection_manager()
        monitor = get_error_monitor()
        
        logger.info("✅ All equipment passed quality control!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Equipment quality control failed: {e}")
        return False


# Export all our supply chain functions
__all__ = [
    "setup_all_dependencies",
    "get_log_processor",
    "get_database_manager", 
    "get_search_manager",
    "get_retention_manager",
    "get_alert_manager",
    "get_connection_manager",
    "get_error_monitor",
    "validate_all_dependencies"
]