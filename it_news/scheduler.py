## scheduler.py
import time
import schedule
import logging
import threading
from datetime import datetime

from config import SCRAPING_INTERVAL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("it_scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NewsScheduler:
    def __init__(self, job_function):
        """Initialize the scheduler with the job function to run"""
        self.job_function = job_function
        self.stop_event = threading.Event()
        self.running = False
        
    def run_job(self):
        """Wrapper for the job function that logs execution"""
        try:
            logger.info(f"Running scheduled job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.job_function()
        except Exception as e:
            logger.error(f"Error running scheduled job: {str(e)}")
        
    def start_scheduler(self):
        """Start the scheduler to run every SCRAPING_INTERVAL minutes"""
        if self.running:
            logger.warning("Scheduler is already running")
            return False
            
        # Schedule the job to run at regular intervals
        schedule.every(SCRAPING_INTERVAL).minutes.do(self.run_job)
        
        # Run once immediately
        self.run_job()
        
        self.running = True
        self.stop_event.clear()
        
        # Start the scheduler in a separate thread
        scheduler_thread = threading.Thread(target=self._run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        logger.info(f"Scheduler started, running every {SCRAPING_INTERVAL} minutes")
        return True
        
    def _run_scheduler(self):
        """Run the scheduler until stopped"""
        while not self.stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)
            
    def stop_scheduler(self):
        """Stop the scheduler"""
        if not self.running:
            logger.warning("Scheduler is not running")
            return False
            
        self.stop_event.set()
        schedule.clear()
        self.running = False
        
        logger.info("Scheduler stopped")
        return True
        
    def run_once(self):
        """Run the job once without scheduling"""
        self.run_job()
        return True