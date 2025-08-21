"""
Utility functions for the Playwright Web Scraper.
"""

import logging
import re
from urllib.parse import urlparse
from typing import Optional, Dict, Any
import sys
from pathlib import Path


def setup_logging(log_level: str = 'INFO'):
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / 'scraper.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific log levels for external libraries
    logging.getLogger('playwright').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    if not url:
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL.
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Domain name or None if invalid URL
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return None


def is_valid_selector(selector: str) -> bool:
    """
    Validate CSS selector syntax.
    
    Args:
        selector: CSS selector to validate
        
    Returns:
        True if selector appears valid, False otherwise
    """
    if not selector or not isinstance(selector, str):
        return False
    
    # Basic validation for common CSS selector patterns
    invalid_chars = ['<', '>', '{', '}', '(', ')']
    if any(char in selector for char in invalid_chars):
        return False
    
    # Check for empty selector
    if selector.strip() == '':
        return False
    
    return True


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes = int(size_bytes / 1024.0)
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def safe_filename(filename: str) -> str:
    """
    Make filename safe for filesystem.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    # Remove or replace invalid characters
    safe_chars = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple underscores
    safe_chars = re.sub(r'_+', '_', safe_chars)
    
    # Trim and remove leading/trailing dots and spaces
    safe_chars = safe_chars.strip('. ')
    
    # Ensure filename is not empty
    if not safe_chars:
        safe_chars = "scraped_data"
    
    return safe_chars


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries.
    
    Args:
        base_config: Base configuration
        override_config: Configuration to override base with
        
    Returns:
        Merged configuration
    """
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    
    return merged


def get_user_agent_info(user_agent: str) -> Dict[str, str]:
    """
    Parse user agent string to extract browser info.
    
    Args:
        user_agent: User agent string
        
    Returns:
        Dictionary with browser info
    """
    info = {
        'browser': 'Unknown',
        'version': 'Unknown',
        'os': 'Unknown'
    }
    
    if not user_agent:
        return info
    
    # Browser detection
    if 'Chrome' in user_agent:
        info['browser'] = 'Chrome'
        chrome_match = re.search(r'Chrome/(\d+\.\d+)', user_agent)
        if chrome_match:
            info['version'] = chrome_match.group(1)
    elif 'Firefox' in user_agent:
        info['browser'] = 'Firefox'
        firefox_match = re.search(r'Firefox/(\d+\.\d+)', user_agent)
        if firefox_match:
            info['version'] = firefox_match.group(1)
    elif 'Safari' in user_agent and 'Chrome' not in user_agent:
        info['browser'] = 'Safari'
        safari_match = re.search(r'Safari/(\d+\.\d+)', user_agent)
        if safari_match:
            info['version'] = safari_match.group(1)
    
    # OS detection
    if 'Windows' in user_agent:
        info['os'] = 'Windows'
    elif 'Macintosh' in user_agent or 'Mac OS' in user_agent:
        info['os'] = 'macOS'
    elif 'Linux' in user_agent:
        info['os'] = 'Linux'
    elif 'Android' in user_agent:
        info['os'] = 'Android'
    elif 'iPhone' in user_agent or 'iPad' in user_agent:
        info['os'] = 'iOS'
    
    return info


class ProgressTracker:
    """
    Simple progress tracking utility.
    """
    
    def __init__(self, total: int, description: str = "Progress"):
        self.total = total
        self.current = 0
        self.description = description
        self.logger = logging.getLogger(__name__)
    
    def update(self, increment: int = 1):
        """Update progress counter."""
        self.current += increment
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        self.logger.info(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%)")
    
    def finish(self):
        """Mark progress as complete."""
        self.logger.info(f"{self.description}: Complete ({self.total}/{self.total})")
