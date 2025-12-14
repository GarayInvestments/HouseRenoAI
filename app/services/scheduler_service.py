"""
Scheduler Service for Automated QuickBooks Sync

Manages scheduled sync jobs that run 3x daily:
- 8:00 AM EST
- 1:00 PM EST  
- 6:00 PM EST

Uses APScheduler with timezone-aware cron triggers.
"""

import logging
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone as pytz_timezone

from app.services.quickbooks_sync_service import qb_sync_service
from app.db.session import get_db

logger = logging.getLogger(__name__)

# Eastern Time timezone
EST = pytz_timezone('US/Eastern')


class SchedulerService:
    """
    Manages scheduled QuickBooks sync jobs.
    
    Features:
    - 3x daily sync at 8 AM, 1 PM, 6 PM EST
    - Timezone-aware scheduling
    - Manual start/stop/pause controls
    - Job status monitoring
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=EST)
        self.is_running = False
        self.job_id = "quickbooks_sync_job"
        
    async def _run_scheduled_sync(self):
        """Execute scheduled sync job"""
        try:
            logger.info("[SCHEDULER] Starting scheduled QuickBooks sync...")
            
            # Get database session
            db = None
            try:
                db_gen = get_db()
                db = await anext(db_gen)
                
                # Run sync for all entities
                result = await qb_sync_service.sync_all(db, force_full_sync=False)
                
                logger.info(
                    f"[SCHEDULER] Sync complete: "
                    f"customers={result['customers']['records_synced']}, "
                    f"invoices={result['invoices']['records_synced']}, "
                    f"payments={result['payments']['records_synced']}, "
                    f"total_duration={result['total_duration_ms']}ms"
                )
                
            except Exception as e:
                logger.error(f"[SCHEDULER] Sync failed: {e}", exc_info=True)
            finally:
                if db:
                    await db.close()
                    
        except Exception as e:
            logger.error(f"[SCHEDULER] Critical error in scheduled sync: {e}", exc_info=True)
    
    async def start(self):
        """Start the scheduler with 3x daily sync jobs"""
        if self.is_running:
            logger.warning("[SCHEDULER] Already running")
            return
        
        try:
            # Add sync job with cron trigger (8 AM, 1 PM, 6 PM EST)
            self.scheduler.add_job(
                self._run_scheduled_sync,
                trigger=CronTrigger(
                    hour='8,13,18',  # 8 AM, 1 PM, 6 PM
                    minute='0',
                    timezone=EST
                ),
                id=self.job_id,
                name="QuickBooks Sync (3x daily)",
                replace_existing=True,
                max_instances=1  # Prevent concurrent runs
            )
            
            self.scheduler.start()
            self.is_running = True
            
            # Log next run times
            job = self.scheduler.get_job(self.job_id)
            if job:
                next_run = job.next_run_time
                logger.info(
                    f"[SCHEDULER] Started. Next sync: {next_run.strftime('%Y-%m-%d %I:%M %p %Z')}"
                )
            
        except Exception as e:
            logger.error(f"[SCHEDULER] Failed to start: {e}", exc_info=True)
            raise
    
    async def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            logger.warning("[SCHEDULER] Not running")
            return
        
        try:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("[SCHEDULER] Stopped")
        except Exception as e:
            logger.error(f"[SCHEDULER] Failed to stop: {e}", exc_info=True)
            raise
    
    async def pause(self):
        """Pause the scheduler (jobs won't run but scheduler stays alive)"""
        if not self.is_running:
            logger.warning("[SCHEDULER] Not running")
            return
        
        try:
            self.scheduler.pause()
            logger.info("[SCHEDULER] Paused")
        except Exception as e:
            logger.error(f"[SCHEDULER] Failed to pause: {e}", exc_info=True)
            raise
    
    async def resume(self):
        """Resume the scheduler after pause"""
        if not self.is_running:
            logger.warning("[SCHEDULER] Not running")
            return
        
        try:
            self.scheduler.resume()
            logger.info("[SCHEDULER] Resumed")
        except Exception as e:
            logger.error(f"[SCHEDULER] Failed to resume: {e}", exc_info=True)
            raise
    
    async def trigger_now(self):
        """Manually trigger sync job immediately (outside schedule)"""
        logger.info("[SCHEDULER] Manually triggering sync job...")
        await self._run_scheduled_sync()
    
    def get_status(self) -> dict:
        """Get current scheduler status"""
        if not self.is_running:
            return {
                "is_running": False,
                "message": "Scheduler is not running"
            }
        
        try:
            job = self.scheduler.get_job(self.job_id)
            
            if not job:
                return {
                    "is_running": True,
                    "message": "Scheduler running but job not found"
                }
            
            next_run = job.next_run_time
            
            return {
                "is_running": True,
                "is_paused": self.scheduler.state == 2,  # STATE_PAUSED = 2
                "job_name": job.name,
                "job_id": job.id,
                "trigger": str(job.trigger),
                "next_run_time": next_run.isoformat() if next_run else None,
                "next_run_time_formatted": next_run.strftime('%Y-%m-%d %I:%M %p %Z') if next_run else None,
                "timezone": "US/Eastern (EST/EDT)",
                "schedule": "3x daily at 8:00 AM, 1:00 PM, 6:00 PM EST"
            }
        except Exception as e:
            logger.error(f"[SCHEDULER] Failed to get status: {e}", exc_info=True)
            return {
                "is_running": self.is_running,
                "error": str(e)
            }


# Global scheduler instance
scheduler_service = SchedulerService()
