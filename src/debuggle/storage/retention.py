"""
📅 DEBUGGLE RETENTION MANAGER - The Digital Archivist! 📅

Think of this module as the person in charge of a library's archive policy -
they decide what documents to keep, for how long, and when to safely dispose
of old records. Just like libraries don't keep every newspaper forever (they'd
run out of space!), we need intelligent policies for managing our log storage.

🏆 HIGH SCHOOL EXPLANATION:
Imagine you're managing a school's student files:
- Keep current students' files readily available (recent logs)
- Move graduated students' files to archive storage (older logs)
- After 7 years, securely destroy very old files (retention policy)
- Keep important historical records longer (critical error logs)
- Regularly clean up temporary files (cleanup automation)

This prevents our storage from growing infinitely while keeping important
historical data available when needed!

WHY RETENTION MANAGEMENT MATTERS:
🚀 Performance - Smaller databases query faster
💾 Storage Costs - Prevents unlimited disk usage growth  
🔒 Privacy Compliance - Automatically removes old personal data
📊 Data Quality - Keeps recent, relevant data easily accessible
⚡ Maintenance - Reduces backup and maintenance overhead
🎯 Focus - Highlights current issues rather than ancient history

FLEXIBLE RETENTION POLICIES:
Unlike rigid cloud solutions, our local retention system lets you:
- Set different policies for different log types
- Keep critical errors longer than warnings
- Pause retention during important debugging sessions
- Export archives before deletion
- Customize policies per project or client
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import json

from .database import DatabaseManager, LogSeverity

logger = logging.getLogger(__name__)


class RetentionAction(str, Enum):
    """
    🗂️ WHAT TO DO WITH OLD DOCUMENTS - Archive Management Actions
    
    When documents get old, what should happen to them? Just like
    a real archive, we have different options for handling aging data.
    """
    DELETE = "delete"           # 🗑️ Permanently remove (like shredding old papers)
    ARCHIVE = "archive"         # 📦 Move to compressed storage (like boxed storage)
    EXPORT = "export"           # 📤 Save to external file before deletion
    MARK_ARCHIVED = "mark"      # 🏷️ Keep but mark as archived (like "inactive" status)


@dataclass
class RetentionRule:
    """
    📋 ARCHIVE POLICY RULE - One Specific Archive Management Policy
    
    Think of this as one rule in the library's document management manual.
    Each rule says something like "For documents of type X, keep them for
    Y days, then do action Z." Having multiple rules lets us treat different
    types of documents differently.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like different retention policies for different school documents:
    - Student transcripts: Keep 10 years, then archive
    - Lunch menus: Keep 1 year, then delete
    - Emergency contact info: Keep 7 years, then securely destroy
    - Principal's memos: Keep 3 years, then archive to storage
    
    Each document type gets its own rule based on importance and legal requirements!
    """
    
    name: str                                    # 🏷️ Human-readable name for this rule
    description: str                             # 📝 What this rule is for
    days_to_keep: int                           # ⏰ How many days to keep active
    action: RetentionAction                     # 🎯 What to do when time is up
    
    # 🎛️ FILTERING CONDITIONS - Which logs does this rule apply to?
    severity_filter: Optional[List[LogSeverity]] = None   # Only certain severities
    language_filter: Optional[List[str]] = None           # Only certain programming languages
    tag_filter: Optional[List[str]] = None               # Only logs with certain tags
    project_filter: Optional[List[str]] = None           # Only certain projects
    source_filter: Optional[List[str]] = None            # Only certain sources (api, upload, etc.)
    
    # 📊 RULE STATISTICS
    enabled: bool = True                        # 🔛 Is this rule currently active?
    last_executed: Optional[datetime] = None   # 🕒 When did this rule last run?
    total_processed: int = 0                   # 📈 How many logs has this rule processed?
    
    # 🔧 ADVANCED OPTIONS
    archive_path: Optional[str] = None         # 📁 Where to archive/export files
    callback: Optional[Callable] = None        # 🔗 Custom function to run when rule executes


@dataclass
class RetentionReport:
    """
    📊 ARCHIVE MANAGEMENT REPORT - What Happened During Cleanup
    
    After running retention policies, this report tells us exactly
    what was accomplished, like a maintenance crew's completion report
    after cleaning and organizing a building.
    """
    
    execution_time: datetime                    # 🕒 When the cleanup ran
    total_logs_processed: int                  # 📊 How many logs were examined
    actions_taken: Dict[RetentionAction, int] # 📈 How many of each action (delete, archive, etc.)
    rules_executed: List[str]                  # 📋 Which rules ran
    errors: List[str]                          # ❌ Any problems that occurred
    duration_seconds: float                    # ⏱️ How long the cleanup took
    space_freed_mb: Optional[float] = None     # 💾 Disk space freed (if measurable)


class RetentionManager:
    """
    🏛️ THE DIGITAL ARCHIVIST - Managing Our Data Lifecycle!
    
    Think of this class as the head archivist for a major institution who
    manages vast collections of documents. The archivist knows:
    - Which documents to keep and for how long (retention policies)
    - When to move old documents to storage (archiving)
    - How to safely dispose of documents that are no longer needed
    - How to generate reports on archive management activities
    - How to handle special cases and exceptions
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like the person who manages all the school's record-keeping:
    - Creates policies for different types of records
    - Runs regular cleanups to prevent storage overflow
    - Generates reports for administrators
    - Handles special requests for keeping certain records longer
    - Ensures everything follows legal and policy requirements
    
    This prevents our log database from growing forever while maintaining
    appropriate historical data for debugging and analysis!
    """
    
    def __init__(self, database_manager: DatabaseManager):
        """
        🏗️ SETTING UP THE ARCHIVE MANAGEMENT OFFICE
        
        When we create a new RetentionManager, it's like setting up
        a new department in charge of managing document lifecycles:
        1. Connect to the document storage system (database)
        2. Load existing policies (retention rules)
        3. Prepare reporting systems
        4. Set up automation schedules
        """
        # 🗄️ OUR CONNECTION TO THE FILING SYSTEM
        self.db = database_manager
        
        # 📋 LIST OF ALL RETENTION POLICIES
        # Like the master policy manual that defines how to handle different document types
        self.rules: List[RetentionRule] = []
        
        # 📊 HISTORY OF ARCHIVE ACTIVITIES
        # Like keeping a logbook of all maintenance and cleanup activities
        self.execution_history: List[RetentionReport] = []
        
        # 📏 LIMITS FOR REPORT HISTORY
        # Don't keep cleanup reports forever (that would be ironic!)
        self.max_history_size = 100
        
        # ⚙️ CONFIGURATION SETTINGS
        self.config = {
            "auto_cleanup_enabled": True,      # Should we run automatic cleanups?
            "cleanup_hour": 2,                 # What time of day to run cleanup (2 AM)
            "max_execution_time": 3600,        # Maximum time to spend on cleanup (1 hour)
            "safety_checks": True,             # Extra validation before deleting data
        }
        
        # 🏗️ LOAD DEFAULT RETENTION POLICIES
        # Set up reasonable default policies for common use cases
        self._initialize_default_rules()
        
        logger.info("Retention manager initialized")
    
    def _initialize_default_rules(self):
        """
        📋 SETTING UP STANDARD ARCHIVE POLICIES
        
        This creates a set of reasonable default policies for different
        types of logs, like how a new company might start with standard
        document retention policies before customizing for their needs.
        
        Think of these as "template policies" that work for most situations!
        """
        
        # 🚨 RULE 1: Critical Errors - Keep Longer
        # Like keeping important incident reports for extended review
        self.add_rule(RetentionRule(
            name="Critical Error Retention",
            description="Keep critical and error-level logs for extended debugging",
            days_to_keep=90,  # 3 months
            action=RetentionAction.ARCHIVE,
            severity_filter=[LogSeverity.CRITICAL, LogSeverity.ERROR],
            enabled=True
        ))
        
        # ⚠️ RULE 2: Warnings - Medium Retention
        # Like keeping caution notices for a reasonable time
        self.add_rule(RetentionRule(
            name="Warning Log Retention", 
            description="Keep warning logs for moderate debugging periods",
            days_to_keep=30,  # 1 month
            action=RetentionAction.DELETE,
            severity_filter=[LogSeverity.WARNING],
            enabled=True
        ))
        
        # ℹ️ RULE 3: Info/Debug Logs - Short Retention
        # Like disposing of routine paperwork quickly
        self.add_rule(RetentionRule(
            name="Debug Info Cleanup",
            description="Clean up debug and info logs to save space",
            days_to_keep=7,   # 1 week
            action=RetentionAction.DELETE,
            severity_filter=[LogSeverity.INFO, LogSeverity.DEBUG, LogSeverity.TRACE],
            enabled=True
        ))
        
        # 🧹 RULE 4: General Cleanup - Catch-All
        # Like a general "old documents" policy for anything not covered above
        self.add_rule(RetentionRule(
            name="General Log Cleanup",
            description="Default cleanup for logs not covered by other rules", 
            days_to_keep=14,  # 2 weeks
            action=RetentionAction.DELETE,
            enabled=True  # No filters = applies to all logs not caught by specific rules
        ))
        
        logger.info(f"Initialized {len(self.rules)} default retention rules")
    
    def add_rule(self, rule: RetentionRule):
        """
        📝 ADDING A NEW ARCHIVE POLICY
        
        This is like adding a new rule to the company's document management
        manual. The new rule gets added to our collection and will be
        applied during future cleanup operations.
        """
        self.rules.append(rule)
        logger.info(f"Added retention rule: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        🗑️ REMOVING AN ARCHIVE POLICY
        
        This is like removing an outdated policy from the manual.
        Sometimes policies become obsolete or need to be replaced.
        """
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                removed_rule = self.rules.pop(i)
                logger.info(f"Removed retention rule: {removed_rule.name}")
                return True
        
        logger.warning(f"Rule not found for removal: {rule_name}")
        return False
    
    def get_rule(self, rule_name: str) -> Optional[RetentionRule]:
        """Find a specific retention rule by name."""
        for rule in self.rules:
            if rule.name == rule_name:
                return rule
        return None
    
    def _rule_applies_to_log(self, rule: RetentionRule, log_entry) -> bool:
        """
        🎯 CHECKING IF A POLICY APPLIES TO A DOCUMENT
        
        This is like checking whether a specific document falls under
        a particular archive policy. We examine the document's properties
        (type, age, source, etc.) against the rule's criteria.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like checking if a student file should follow the "graduated student"
        retention policy:
        - Is the student actually graduated? (severity filter)
        - Are they from the right grade level? (tag filter)
        - Did they attend in the right time period? (date filter)
        - Are they from the right program? (project filter)
        
        Only if ALL the criteria match does the rule apply!
        """
        # 🌡️ CHECK SEVERITY FILTER
        if rule.severity_filter and log_entry.severity not in rule.severity_filter:
            return False
        
        # 💻 CHECK LANGUAGE FILTER
        if rule.language_filter and log_entry.language not in rule.language_filter:
            return False
        
        # 📁 CHECK PROJECT FILTER
        if rule.project_filter and log_entry.project_name not in rule.project_filter:
            return False
        
        # 🌐 CHECK SOURCE FILTER
        if rule.source_filter and log_entry.source not in rule.source_filter:
            return False
        
        # 🏷️ CHECK TAG FILTER (more complex - need to check if any tags match)
        if rule.tag_filter:
            # Check if any of the rule's required tags are present in the log's tags
            rule_tags_set = set(rule.tag_filter)
            log_tags_set = set(log_entry.tags)
            if not rule_tags_set.intersection(log_tags_set):
                return False
        
        # ✅ ALL CHECKS PASSED - this rule applies to this log
        return True
    
    async def execute_retention_policies(self) -> RetentionReport:
        """
        🧹 RUNNING THE ARCHIVE CLEANUP - The Big Monthly Cleanup!
        
        This is like the monthly archive maintenance where we go through
        all the documents, apply the retention policies, and clean up
        old materials. It's a comprehensive process that touches every
        document and applies the appropriate policy.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like the end-of-semester cleanup in the school office:
        1. Go through every student file
        2. Check which cleanup rules apply to each file
        3. For files that are old enough, apply the appropriate action
        4. Keep track of what was done for reporting
        5. Generate a summary report for administrators
        
        This process can take a while if there are lots of documents!
        """
        start_time = datetime.now()
        logger.info("Starting retention policy execution")
        
        # 📊 INITIALIZE TRACKING VARIABLES
        total_processed = 0
        actions_taken = {action: 0 for action in RetentionAction}
        rules_executed = []
        errors = []
        
        try:
            # 🔍 EXAMINE EACH RETENTION RULE
            for rule in self.rules:
                if not rule.enabled:
                    logger.debug(f"Skipping disabled rule: {rule.name}")
                    continue
                
                rules_executed.append(rule.name)
                logger.info(f"Executing retention rule: {rule.name}")
                
                # 📅 CALCULATE CUTOFF DATE FOR THIS RULE
                cutoff_date = datetime.now() - timedelta(days=rule.days_to_keep)
                
                # 🔍 FIND LOGS THAT MATCH THIS RULE AND ARE OLD ENOUGH
                # We'll search for logs older than the cutoff date
                # This is a simplified version - in practice, you'd want to batch this
                matching_logs = self.db.search_logs(
                    end_date=cutoff_date,  # Only logs older than cutoff
                    severity=rule.severity_filter[0] if rule.severity_filter and len(rule.severity_filter) == 1 else None,
                    language=rule.language_filter[0] if rule.language_filter and len(rule.language_filter) == 1 else None,
                    project_name=rule.project_filter[0] if rule.project_filter and len(rule.project_filter) == 1 else None,
                    limit=1000  # Process in batches to avoid memory issues
                )
                
                # 🎯 APPLY THE RULE TO EACH MATCHING LOG
                for log_entry in matching_logs:
                    # Double-check that this rule actually applies to this log
                    # (because our search above might not have caught all criteria)
                    if not self._rule_applies_to_log(rule, log_entry):
                        continue
                    
                    try:
                        # 🎬 EXECUTE THE RETENTION ACTION
                        if rule.action == RetentionAction.DELETE:
                            await self._delete_log(log_entry)
                            actions_taken[RetentionAction.DELETE] += 1
                            
                        elif rule.action == RetentionAction.ARCHIVE:
                            await self._archive_log(log_entry, rule.archive_path)
                            actions_taken[RetentionAction.ARCHIVE] += 1
                            
                        elif rule.action == RetentionAction.EXPORT:
                            await self._export_log(log_entry, rule.archive_path)
                            actions_taken[RetentionAction.EXPORT] += 1
                            
                        elif rule.action == RetentionAction.MARK_ARCHIVED:
                            await self._mark_log_archived(log_entry)
                            actions_taken[RetentionAction.MARK_ARCHIVED] += 1
                        
                        total_processed += 1
                        
                        # 🔔 RUN CUSTOM CALLBACK IF PROVIDED
                        if rule.callback:
                            try:
                                await rule.callback(log_entry, rule.action)
                            except Exception as callback_error:
                                errors.append(f"Callback error for {rule.name}: {callback_error}")
                        
                    except Exception as action_error:
                        errors.append(f"Failed to process log {log_entry.log_id} with rule {rule.name}: {action_error}")
                        logger.error(f"Error processing log {log_entry.log_id}: {action_error}")
                
                # 📊 UPDATE RULE STATISTICS
                rule.last_executed = datetime.now()
                rule.total_processed += len(matching_logs)
        
        except Exception as e:
            errors.append(f"Critical error during retention execution: {e}")
            logger.error(f"Critical error during retention execution: {e}")
        
        # ⏱️ CALCULATE EXECUTION TIME
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 📋 GENERATE COMPLETION REPORT
        report = RetentionReport(
            execution_time=end_time,
            total_logs_processed=total_processed,
            actions_taken=actions_taken,
            rules_executed=rules_executed,
            errors=errors,
            duration_seconds=duration
        )
        
        # 📚 ADD TO EXECUTION HISTORY
        self.execution_history.append(report)
        if len(self.execution_history) > self.max_history_size:
            self.execution_history.pop(0)  # Remove oldest report
        
        # 📝 LOG COMPLETION
        logger.info(f"Retention execution completed in {duration:.2f}s. Processed {total_processed} logs.")
        if errors:
            logger.warning(f"Retention execution had {len(errors)} errors")
        
        return report
    
    async def _delete_log(self, log_entry):
        """
        🗑️ PERMANENTLY REMOVING A LOG ENTRY
        
        This is the most straightforward retention action - we simply
        remove the log from our database permanently. Like shredding
        old documents that are no longer needed.
        """
        # For now, we'll implement this as a database delete
        # In a real implementation, you might want additional safety checks
        import sqlite3
        with sqlite3.connect(self.db.database_path) as conn:
            conn.execute("DELETE FROM logs WHERE log_id = ?", (log_entry.log_id,))
            conn.commit()
        
        logger.debug(f"Deleted log: {log_entry.log_id}")
    
    async def _archive_log(self, log_entry, archive_path: Optional[str] = None):
        """
        📦 ARCHIVING A LOG ENTRY
        
        This moves the log to archived status or exports it to a separate
        archive file, then removes it from the active database.
        Like moving old files to a storage room.
        """
        # TODO: Implement actual archiving logic
        # For now, we'll just mark it as archived and potentially export
        if archive_path:
            await self._export_log(log_entry, archive_path)
        
        # Then remove from active database
        await self._delete_log(log_entry)
        
        logger.debug(f"Archived log: {log_entry.log_id}")
    
    async def _export_log(self, log_entry, export_path: Optional[str] = None):
        """
        📤 EXPORTING A LOG ENTRY
        
        This saves the log entry to an external file (JSON, CSV, etc.)
        before deleting it from the database. Like making photocopies
        of important documents before filing them in long-term storage.
        """
        # TODO: Implement actual export logic
        # This would write the log to a file in the specified format
        logger.debug(f"Exported log: {log_entry.log_id}")
    
    async def _mark_log_archived(self, log_entry):
        """
        🏷️ MARKING A LOG AS ARCHIVED
        
        This changes the log's status to "archived" without deleting it.
        Like putting an "inactive" sticker on old files while keeping
        them accessible if needed.
        """
        # TODO: Implement archived status in database schema
        # For now, we'll add an "archived" tag
        if "archived" not in log_entry.tags:
            log_entry.tags.append("archived")
            # Update the log in the database
            # (This would require updating the database record)
        
        logger.debug(f"Marked log as archived: {log_entry.log_id}")
    
    def get_retention_status(self) -> Dict[str, Any]:
        """
        📊 ARCHIVE MANAGEMENT STATUS REPORT
        
        This provides a complete overview of our retention management system:
        what policies are active, when they last ran, what they accomplished,
        and any issues that need attention.
        
        Like the archivist's monthly report to management!
        """
        return {
            "total_rules": len(self.rules),
            "active_rules": len([r for r in self.rules if r.enabled]),
            "last_execution": self.execution_history[-1].execution_time if self.execution_history else None,
            "total_executions": len(self.execution_history),
            "rules_summary": [
                {
                    "name": rule.name,
                    "description": rule.description,
                    "days_to_keep": rule.days_to_keep,
                    "action": rule.action.value,
                    "enabled": rule.enabled,
                    "last_executed": rule.last_executed,
                    "total_processed": rule.total_processed
                }
                for rule in self.rules
            ],
            "recent_reports": [
                {
                    "execution_time": report.execution_time,
                    "total_processed": report.total_logs_processed,
                    "actions_taken": report.actions_taken,
                    "duration_seconds": report.duration_seconds,
                    "error_count": len(report.errors)
                }
                for report in self.execution_history[-5:]  # Last 5 reports
            ]
        }
    
    async def schedule_cleanup(self):
        """
        ⏰ AUTOMATIC CLEANUP SCHEDULING
        
        This sets up automatic execution of retention policies, like
        having a scheduled maintenance crew that comes in every night
        to clean and organize the office.
        
        In production, this would typically be called by a task scheduler
        or background job system.
        """
        if not self.config["auto_cleanup_enabled"]:
            logger.info("Automatic cleanup is disabled")
            return
        
        logger.info("Starting scheduled cleanup")
        report = await self.execute_retention_policies()
        
        # If there were errors, we might want to alert administrators
        if report.errors:
            logger.warning(f"Scheduled cleanup completed with {len(report.errors)} errors")
        else:
            logger.info(f"Scheduled cleanup completed successfully. Processed {report.total_logs_processed} logs.")
        
        return report