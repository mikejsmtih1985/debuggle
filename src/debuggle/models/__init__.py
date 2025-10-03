"""
🏥 Hospital Medical Forms Directory - All Official Medical Forms in One Place!

This is like the hospital's main forms directory where you can find all the official
medical forms, charts, and documentation needed throughout the hospital. Instead of
running around to different departments, everything is organized here for easy access.

Think of this like a hospital's forms central station:
- Common forms used everywhere (intake forms, consent forms)
- Department-specific forms (lab reports, surgical notes)
- Administrative forms (billing, insurance)
- Emergency forms (alert reports, triage sheets)

🏆 HIGH SCHOOL EXPLANATION:
Like the school's main office where you can get any form you need:
- Enrollment forms, transcript requests, permission slips
- All organized by category so you know exactly where to look
- Everything officially approved and ready to use
- One-stop shopping for all your paperwork needs!

USAGE EXAMPLES:
    from debuggle.models import AnalyzeRequest, HealthResponse
    from debuggle.models.analysis import AnalyzeOptions
    from debuggle.models.alerts import AlertRuleRequest
"""

# 🏥 COMMON MEDICAL FORMS - Used Throughout the Hospital
# These are the basic forms that every department uses
from .common import (
    LogSeverity,
    LanguageEnum,
    HealthResponse,
    ErrorResponse,
    TierFeature,
    TiersResponse
)

# 🔬 ANALYSIS DEPARTMENT FORMS - Laboratory & Diagnostic Reports
# Forms used by the medical analysis and diagnostic departments
from .analysis import (
    AnalyzeOptions,
    AnalyzeRequest,
    AnalyzeMetadata,
    AnalyzeResponse
)

# 📤 FILE UPLOAD DEPARTMENT FORMS - Medical File Processing
# Forms used when patients submit medical files for analysis
from .upload import (
    FileUploadMetadata,
    FileUploadResponse
)

# 📊 DASHBOARD DEPARTMENT FORMS - Hospital Analytics & Statistics
# Forms used by the analytics department for performance reports
from .dashboard import (
    DashboardStatsRequest,
    DashboardStatsResponse,
    ChartTypeAPI,
    TimeRangeAPI,
    ChartDataRequest,
    ChartDataResponse,
    DashboardRequest,
    DashboardResponse,
    DashboardListResponse,
    SystemMetricsResponse
)

# 🚨 ALERT SYSTEM DEPARTMENT FORMS - Emergency Notification System
# Forms used by the emergency alert and notification systems
from .alerts import (
    AlertSeverityAPI,
    AlertChannelAPI,
    AlertRuleRequest,
    AlertRuleResponse,
    AlertResponse,
    AlertAcknowledgeRequest,
    AlertStatsResponse
)

# 🚀 DATA INGESTION DEPARTMENT FORMS - Large-Scale Processing
# Forms used by the data processing center for bulk operations
from .ingestion import (
    IngestionSourceAPI,
    ProcessingPriorityAPI,
    IngestionStatusAPI,
    BatchIngestionRequest,
    StreamingIngestionRequest,
    IngestionJobResponse,
    IngestionStatsResponse,
    StreamDataRequest,
    BulkUploadRequest
)

# 💾 MEDICAL RECORDS DEPARTMENT FORMS - Storage & Search
# Forms used by the medical records department for storing and finding records
from .storage import (
    SearchRequest,
    SearchResponse,
    LogStorageRequest,
    LogStorageResponse,
    RetentionPolicyRequest,
    RetentionPolicyResponse,
    LogAnalyticsResponse
)

# 📋 QUICK REFERENCE - Most Commonly Used Forms
# Like a "frequently requested forms" counter at the main desk
__all__ = [
    # Core Common Forms
    "LogSeverity",
    "LanguageEnum", 
    "HealthResponse",
    "ErrorResponse",
    "TierFeature",
    "TiersResponse",
    
    # Analysis Forms
    "AnalyzeOptions",
    "AnalyzeRequest", 
    "AnalyzeMetadata",
    "AnalyzeResponse",
    
    # Upload Forms
    "FileUploadMetadata",
    "FileUploadResponse",
    
    # Dashboard Forms
    "DashboardStatsRequest",
    "DashboardStatsResponse",
    "ChartTypeAPI",
    "TimeRangeAPI",
    "ChartDataRequest",
    "ChartDataResponse",
    "DashboardRequest",
    "DashboardResponse",
    "DashboardListResponse",
    "SystemMetricsResponse",
    
    # Alert System Forms
    "AlertSeverityAPI",
    "AlertChannelAPI",
    "AlertRuleRequest",
    "AlertRuleResponse", 
    "AlertResponse",
    "AlertAcknowledgeRequest",
    "AlertStatsResponse",
    
    # Ingestion Forms
    "IngestionSourceAPI",
    "ProcessingPriorityAPI",
    "IngestionStatusAPI",
    "BatchIngestionRequest",
    "StreamingIngestionRequest",
    "IngestionJobResponse",
    "IngestionStatsResponse",
    "StreamDataRequest",
    "BulkUploadRequest",
    
    # Storage & Search Forms
    "SearchRequest",
    "SearchResponse",
    "LogStorageRequest", 
    "LogStorageResponse",
    "RetentionPolicyRequest",
    "RetentionPolicyResponse",
    "LogAnalyticsResponse"
]
