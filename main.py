#!/usr/bin/env python3
"""
Playwright Web Scraper - Command Line Interface
A comprehensive web scraping tool using Playwright for automated data extraction.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any

from scraper import PlaywrightScraper
from config import ScrapingConfig
from exporters import DataExporter
from utils import setup_logging, validate_url


async def main():
    """Main entry point for the scraper application."""
    parser = argparse.ArgumentParser(
        description="Playwright Web Scraper - Extract data from websites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --url https://example.com --selectors "h1,p,.class-name"
  python main.py --config config.yaml --output data.csv --format csv
  python main.py --url https://news.com --headless false --delay 2
        """
    )
    
    # Required arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', type=str, help='Target URL to scrape')
    group.add_argument('--config', type=str, help='Configuration file path')
    
    # Optional arguments
    parser.add_argument('--selectors', type=str, 
                       help='Comma-separated CSS selectors to extract')
    parser.add_argument('--output', type=str, default='scraped_data',
                       help='Output file name (without extension)')
    parser.add_argument('--format', choices=['json', 'csv'], default='json',
                       help='Output format')
    parser.add_argument('--headless', type=str, choices=['true', 'false'], 
                       default='true', help='Run in headless mode')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between requests in seconds')
    parser.add_argument('--timeout', type=int, default=30000,
                       help='Page load timeout in milliseconds')
    parser.add_argument('--user-agent', type=str,
                       help='Custom user agent string')
    parser.add_argument('--viewport-width', type=int, default=1280,
                       help='Browser viewport width')
    parser.add_argument('--viewport-height', type=int, default=720,
                       help='Browser viewport height')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level')
    parser.add_argument('--max-pages', type=int, default=1,
                       help='Maximum number of pages to scrape')
    parser.add_argument('--wait-for-selector', type=str,
                       help='Wait for specific selector before scraping')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        if args.config:
            config = ScrapingConfig.from_file(args.config)
            logger.info(f"Loaded configuration from {args.config}")
        else:
            # Validate URL
            if not validate_url(args.url):
                logger.error(f"Invalid URL: {args.url}")
                sys.exit(1)
            
            # Create config from command line arguments
            config_dict = {
                'url': args.url,
                'selectors': args.selectors.split(',') if args.selectors else ['body'],
                'headless': args.headless.lower() == 'true',
                'delay': args.delay,
                'timeout': args.timeout,
                'user_agent': args.user_agent,
                'viewport': {
                    'width': args.viewport_width,
                    'height': args.viewport_height
                },
                'max_pages': args.max_pages,
                'wait_for_selector': args.wait_for_selector
            }
            config = ScrapingConfig(**config_dict)
        
        logger.info("Starting web scraping process...")
        logger.info(f"Target URL: {config.url}")
        logger.info(f"Selectors: {', '.join(config.selectors)}")
        logger.info(f"Output format: {args.format}")
        
        # Initialize scraper
        scraper = PlaywrightScraper(config)
        
        # Perform scraping
        scraped_data = await scraper.scrape()
        
        if not scraped_data:
            logger.warning("No data was scraped from the target URL")
            sys.exit(1)
        
        logger.info(f"Successfully scraped {len(scraped_data)} data points")
        
        # Export data
        exporter = DataExporter()
        output_file = exporter.export(scraped_data, args.output, args.format)
        
        logger.info(f"Data exported to: {output_file}")
        logger.info("Scraping completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
