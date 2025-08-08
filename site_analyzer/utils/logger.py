import logging
import sys
from datetime import datetime
from pathlib import Path


class SiteAnalyzerLogger:
    """Centralized logging system for site analyzer"""
    
    def __init__(self, log_level=logging.INFO, log_file=None):
        self.logger = logging.getLogger('site_analyzer')
        self.logger.setLevel(log_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def success(self, message):
        self.logger.info(f"✅ {message}")
    
    def failure(self, message):
        self.logger.error(f"❌ {message}")


# Global logger instance
logger = SiteAnalyzerLogger(
    log_level=logging.INFO,
    log_file=f'site_analyzer_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
)