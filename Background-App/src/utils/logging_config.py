import logging
import logging.handlers
import os
import sys
from datetime import datetime

def get_base_directory():
    """Get the base directory where the executable or script is located."""
    if getattr(sys, 'frozen', False):
        # If running as executable
        return os.path.dirname(sys.executable)
    else:
        # If running as script, go up to the project root
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_logging(base_dir: str = None, log_level: int = logging.INFO):
    """Configure logging with both file and console handlers."""
    if base_dir is None:
        base_dir = get_base_directory()

    # Create logs directory
    logs_dir = os.path.join(base_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create handlers
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    # File handlers
    # Main log file - contains all logs
    main_log_file = os.path.join(logs_dir, 'workmatrix.log')
    file_handler = logging.handlers.RotatingFileHandler(
        main_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.DEBUG)

    # Error log file - contains only ERROR and CRITICAL
    error_log_file = os.path.join(logs_dir, 'error.log')
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setFormatter(detailed_formatter)
    error_handler.setLevel(logging.ERROR)

    # Performance log file - for monitoring performance metrics
    perf_log_file = os.path.join(logs_dir, 'performance.log')
    perf_handler = logging.handlers.RotatingFileHandler(
        perf_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    perf_handler.setFormatter(detailed_formatter)
    perf_handler.setLevel(logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers
    root_logger.handlers = []
    
    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)

    # Create performance logger
    perf_logger = logging.getLogger('performance')
    perf_logger.addHandler(perf_handler)
    perf_logger.setLevel(logging.INFO)
    perf_logger.propagate = False  # Don't propagate to root logger

    return root_logger, perf_logger