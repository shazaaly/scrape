"""
Additional web interface utilities and helpers.
"""

from flask import Blueprint, request, jsonify
import json
from typing import Dict, Any, List
from config import ScrapingConfig, DEFAULT_CONFIGS, create_config_template
from utils import validate_url, is_valid_selector
import logging

# Create blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


@api_bp.route('/config/templates')
def get_config_templates():
    """Get available configuration templates."""
    templates = {}
    for name, config in DEFAULT_CONFIGS.items():
        templates[name] = {
            'name': name.replace('_', ' ').title(),
            'description': f"Pre-configured settings for {name.replace('_', ' ')} scraping",
            'config': config
        }
    
    return jsonify(templates)


@api_bp.route('/config/validate', methods=['POST'])
def validate_config():
    """Validate scraping configuration."""
    try:
        data = request.get_json()
        
        errors = []
        warnings = []
        
        # Validate URL
        url = data.get('url')
        if not url:
            errors.append("URL is required")
        elif not validate_url(url):
            errors.append("Invalid URL format")
        
        # Validate selectors
        selectors = data.get('selectors', [])
        if not selectors:
            warnings.append("No selectors specified, will use 'body' by default")
        else:
            for selector in selectors:
                if not is_valid_selector(selector):
                    errors.append(f"Invalid selector: '{selector}'")
        
        # Validate numeric values
        try:
            delay = float(data.get('delay', 1.0))
            if delay < 0:
                errors.append("Delay must be non-negative")
        except (ValueError, TypeError):
            errors.append("Delay must be a valid number")
        
        try:
            timeout = int(data.get('timeout', 30000))
            if timeout <= 0:
                errors.append("Timeout must be positive")
        except (ValueError, TypeError):
            errors.append("Timeout must be a valid integer")
        
        try:
            max_pages = int(data.get('max_pages', 1))
            if max_pages <= 0:
                errors.append("Max pages must be positive")
        except (ValueError, TypeError):
            errors.append("Max pages must be a valid integer")
        
        # Validate viewport
        viewport = data.get('viewport', {})
        try:
            width = int(viewport.get('width', 1280))
            height = int(viewport.get('height', 720))
            if width <= 0 or height <= 0:
                errors.append("Viewport dimensions must be positive")
        except (ValueError, TypeError):
            errors.append("Viewport dimensions must be valid integers")
        
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        })
        
    except Exception as e:
        logger.error(f"Config validation error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/selectors/suggestions')
def get_selector_suggestions():
    """Get common CSS selector suggestions."""
    suggestions = {
        'content': [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'span', 'div',
            'article', 'section', 'main'
        ],
        'links': [
            'a', 'a[href]',
            'nav a', '.menu a', '.navigation a'
        ],
        'lists': [
            'ul', 'ol', 'li',
            '.list-item', '.item'
        ],
        'forms': [
            'form', 'input', 'textarea', 'select', 'button',
            'input[type="text"]', 'input[type="email"]'
        ],
        'media': [
            'img', 'video', 'audio',
            'img[src]', 'img[alt]'
        ],
        'data': [
            '[data-*]', '[data-id]', '[data-value]',
            '.price', '.title', '.description', '.rating'
        ],
        'common_classes': [
            '.content', '.article', '.post', '.item',
            '.title', '.heading', '.description', '.summary',
            '.price', '.cost', '.amount', '.value',
            '.date', '.time', '.timestamp',
            '.author', '.by', '.byline',
            '.rating', '.score', '.stars',
            '.tag', '.category', '.label'
        ],
        'ecommerce': [
            '.product-title', '.product-name', '.item-name',
            '.price', '.cost', '.amount', '.sale-price',
            '.description', '.details', '.specs',
            '.rating', '.reviews', '.stars',
            '.availability', '.stock', '.in-stock',
            '.add-to-cart', '.buy-now'
        ],
        'news': [
            '.headline', '.title', '.article-title',
            '.byline', '.author', '.journalist',
            '.publish-date', '.date', '.timestamp',
            '.article-content', '.story', '.content',
            '.summary', '.excerpt', '.lead'
        ]
    }
    
    return jsonify(suggestions)


@api_bp.route('/export/formats')
def get_export_formats():
    """Get available export formats."""
    formats = {
        'json': {
            'name': 'JSON',
            'description': 'JavaScript Object Notation - preserves data structure',
            'extension': '.json',
            'features': ['Nested data', 'Data types', 'Metadata']
        },
        'csv': {
            'name': 'CSV',
            'description': 'Comma-Separated Values - spreadsheet compatible',
            'extension': '.csv',
            'features': ['Tabular format', 'Excel compatible', 'Flattened data']
        },
        'excel': {
            'name': 'Excel',
            'description': 'Microsoft Excel format with metadata',
            'extension': '.xlsx',
            'features': ['Multiple sheets', 'Metadata', 'Formatting']
        }
    }
    
    return jsonify(formats)


def get_scraping_tips() -> Dict[str, List[str]]:
    """Get helpful scraping tips for users."""
    return {
        'general': [
            "Start with simple selectors like 'h1', 'p', or '.class-name'",
            "Use browser developer tools to inspect elements and find selectors",
            "Test selectors on a single page before scraping multiple pages",
            "Be respectful of websites and don't overload them with requests",
            "Check robots.txt file before scraping a website"
        ],
        'selectors': [
            "Use specific selectors to get exactly what you need",
            "Combine selectors with commas to extract multiple elements",
            "Use attribute selectors like '[data-testid=\"value\"]' for dynamic content",
            "Try different selector strategies if the first one doesn't work",
            "Use descendant selectors like '.article h2' for more precision"
        ],
        'performance': [
            "Increase delay between requests if you encounter rate limiting",
            "Disable image loading to speed up scraping",
            "Use headless mode for better performance",
            "Limit the number of pages to scrape initially",
            "Monitor memory usage for large scraping tasks"
        ],
        'troubleshooting': [
            "If elements don't load, try increasing the timeout",
            "Use 'wait_for_selector' for dynamic content that loads after page load",
            "Check the browser console for JavaScript errors",
            "Try non-headless mode if headless fails",
            "Verify that the website structure hasn't changed"
        ]
    }


@api_bp.route('/help/tips')
def get_tips():
    """Get scraping tips and best practices."""
    return jsonify(get_scraping_tips())


@api_bp.route('/stats/summary')
def get_scraping_stats():
    """Get overall scraping statistics."""
    # This would typically pull from a database
    # For now, return mock stats
    stats = {
        'total_tasks': 0,
        'completed_tasks': 0,
        'failed_tasks': 0,
        'total_items_scraped': 0,
        'most_common_domains': [],
        'average_items_per_task': 0
    }
    
    return jsonify(stats)
