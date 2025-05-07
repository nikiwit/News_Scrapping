#!/usr/bin/env python3
# logging_setup.py - Configure logging with separate files for each run

import os
import logging
import pytz
from datetime import datetime
from pathlib import Path

def setup_logging(level=logging.INFO):
    """
    Set up logging with date-based folder organization.
    
    Args:
        level: Logging level (default: INFO)
        
    Returns:
        logger: Configured logger
    """
    # Get current time in Kuala Lumpur timezone
    kuala_lumpur_tz = pytz.timezone('Asia/Kuala_Lumpur')
    now = datetime.now(pytz.UTC).astimezone(kuala_lumpur_tz)
    
    # Format date and time
    date_str = now.strftime("%Y%m%d")  # YYYYMMDD format
    time_str = now.strftime("%H%M%S")  # HHMMSS format
    
    # Create logs directory with date-based subfolder
    logs_dir = Path("logs") / date_str
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log filename with time: logs/20250507/092315.log
    log_filename = f"{time_str}.log"
    log_path = logs_dir / log_filename
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()  # Also output to console
        ]
    )
    
    logger = logging.getLogger("NewsSystem")
    logger.info(f"Logging started. Log file: {log_path}")
    
    return logger