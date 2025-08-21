"""
Configuration management for the Playwright Web Scraper.
"""

import yaml
import json
from typing import Dict, Any, List, Union, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ScrapingConfig:
    """
    Configuration class for scraping parameters.
    """
    url: Union[str, List[str]]
    selectors: List[str] = field(default_factory=lambda: ['body'])
    headless: bool = True
    delay: float = 1.0
    timeout: int = 30000
    user_agent: Optional[str] = None
    viewport: Dict[str, int] = field(default_factory=lambda: {'width': 1280, 'height': 720})
    max_pages: int = 1
    wait_for_selector: Optional[str] = None
    export_format: str = 'json'
    output_file: str = 'scraped_data'
    
    # Advanced options
    javascript_enabled: bool = True
    images_enabled: bool = False
    css_enabled: bool = True
    follow_redirects: bool = True
    
    # Anti-bot measures
    random_delay: bool = True
    rotate_user_agent: bool = True
    
    @classmethod
    def from_file(cls, config_path: str) -> 'ScrapingConfig':
        """
        Load configuration from YAML or JSON file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            ScrapingConfig instance
        """
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.suffix.lower() in ['.yaml', '.yml']:
                config_data = yaml.safe_load(f)
            elif config_file.suffix.lower() == '.json':
                config_data = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {config_file.suffix}")
        
        return cls(**config_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            'url': self.url,
            'selectors': self.selectors,
            'headless': self.headless,
            'delay': self.delay,
            'timeout': self.timeout,
            'user_agent': self.user_agent,
            'viewport': self.viewport,
            'max_pages': self.max_pages,
            'wait_for_selector': self.wait_for_selector,
            'export_format': self.export_format,
            'output_file': self.output_file,
            'javascript_enabled': self.javascript_enabled,
            'images_enabled': self.images_enabled,
            'css_enabled': self.css_enabled,
            'follow_redirects': self.follow_redirects,
            'random_delay': self.random_delay,
            'rotate_user_agent': self.rotate_user_agent
        }
    
    def save_to_file(self, config_path: str):
        """
        Save configuration to file.
        
        Args:
            config_path: Path to save configuration file
        """
        config_file = Path(config_path)
        config_data = self.to_dict()
        
        with open(config_file, 'w', encoding='utf-8') as f:
            if config_file.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            elif config_file.suffix.lower() == '.json':
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported configuration file format: {config_file.suffix}")
    
    def validate(self):
        """
        Validate configuration parameters.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.url:
            raise ValueError("URL is required")
        
        if not self.selectors:
            raise ValueError("At least one selector is required")
        
        if self.delay < 0:
            raise ValueError("Delay must be non-negative")
        
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        
        if self.max_pages <= 0:
            raise ValueError("Max pages must be positive")
        
        if 'width' not in self.viewport or 'height' not in self.viewport:
            raise ValueError("Viewport must contain width and height")
        
        if self.viewport['width'] <= 0 or self.viewport['height'] <= 0:
            raise ValueError("Viewport dimensions must be positive")


# Default configuration templates
DEFAULT_CONFIGS = {
    'news_scraper': {
        'selectors': ['h1', 'h2', '.article-title', '.headline', 'p'],
        'wait_for_selector': 'h1',
        'delay': 2.0,
        'max_pages': 5
    },
    'ecommerce_scraper': {
        'selectors': ['.product-title', '.price', '.description', '.rating'],
        'wait_for_selector': '.product-title',
        'delay': 1.5,
        'javascript_enabled': True
    },
    'social_media_scraper': {
        'selectors': ['.post-content', '.username', '.timestamp', '.likes'],
        'delay': 3.0,
        'headless': False,
        'javascript_enabled': True
    }
}


def create_config_template(template_name: str, output_path: str = 'config.yaml'):
    """
    Create a configuration template file.
    
    Args:
        template_name: Name of the template to use
        output_path: Path to save the configuration file
    """
    if template_name not in DEFAULT_CONFIGS:
        raise ValueError(f"Unknown template: {template_name}. Available: {list(DEFAULT_CONFIGS.keys())}")
    
    base_config = {
        'url': 'https://example.com',  # User needs to replace this
        **DEFAULT_CONFIGS[template_name]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(base_config, f, default_flow_style=False, indent=2)
    
    print(f"Configuration template '{template_name}' saved to {output_path}")
    print("Please edit the 'url' field and other parameters as needed.")
