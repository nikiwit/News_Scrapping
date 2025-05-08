#!/usr/bin/env python3
# logging_setup.py - Configure logging with separate files for each run

import os
import logging
import pytz
from datetime import datetime
from pathlib import Path

def setup_logging(level=logging.INFO, module_name=None):
    """
    Set up logging with date-based folder organization.
    
    Args:
        level: Logging level (default: INFO)
        module_name: Specific module name (optional)
        
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
    
    # Reset root logger handlers to prevent duplicate logging
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    # Configure root logger
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    
    # File handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Get the specific logger requested
    if module_name:
        logger = logging.getLogger(module_name)
    else:
        logger = logging.getLogger("NewsSystem")
    
    logger.info(f"Logging started. Log file: {log_path}")
    
    return logger, log_path