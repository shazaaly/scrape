"""
Playwright Web Scraper Core Module
Handles the main scraping logic using Playwright browser automation.
"""

import asyncio
import logging
import random
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from config import ScrapingConfig


class PlaywrightScraper:
    """
    Main scraper class using Playwright for browser automation.
    """
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def initialize_browser(self):
        """Initialize Playwright browser and context."""
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Create browser context with configuration
            user_agent = self.config.user_agent or random.choice(self.user_agents)
            
            self.context = await self.browser.new_context(
                user_agent=user_agent,
                viewport={
                    'width': self.config.viewport.get('width', 1280),
                    'height': self.config.viewport.get('height', 720)
                }
            )
            
            self.logger.info("Browser initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {str(e)}")
            raise
    
    async def close(self):
        """Close browser and cleanup resources."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            self.logger.info("Browser closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing browser: {str(e)}")
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method that orchestrates the entire process.
        
        Returns:
            List of dictionaries containing scraped data
        """
        if not self.browser:
            await self.initialize_browser()
        
        try:
            # Handle single URL or multiple URLs
            urls = [self.config.url] if isinstance(self.config.url, str) else self.config.url
            all_scraped_data = []
            
            for url in urls[:self.config.max_pages]:
                self.logger.info(f"Scraping URL: {url}")
                page_data = await self.scrape_page(url)
                
                if page_data:
                    all_scraped_data.extend(page_data)
                    self.logger.info(f"Scraped {len(page_data)} items from {url}")
                
                # Add delay between pages
                if len(urls) > 1:
                    await asyncio.sleep(self.config.delay)
            
            return all_scraped_data
            
        except Exception as e:
            self.logger.error(f"Scraping failed: {str(e)}")
            raise
        finally:
            await self.close()
    
    async def scrape_page(self, url: str) -> List[Dict[str, Any]]:
        """
        Scrape a single page using configured selectors.
        
        Args:
            url: Target URL to scrape
            
        Returns:
            List of dictionaries containing scraped data from the page
        """
        if not self.context:
            raise RuntimeError("Browser context not initialized")
        page = await self.context.new_page()
        scraped_data = []
        
        try:
            # Navigate to page
            self.logger.info(f"Navigating to: {url}")
            await page.goto(url, timeout=self.config.timeout)
            
            # Wait for specific selector if configured
            if self.config.wait_for_selector:
                self.logger.info(f"Waiting for selector: {self.config.wait_for_selector}")
                await page.wait_for_selector(self.config.wait_for_selector, timeout=self.config.timeout)
            
            # Wait for page to load
            await page.wait_for_load_state('networkidle')
            
            # Handle basic interactions if needed
            await self.handle_page_interactions(page)
            
            # Extract data using selectors
            for selector in self.config.selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    
                    for i, element in enumerate(elements):
                        data_item = await self.extract_element_data(element, selector, i, url)
                        if data_item:
                            scraped_data.append(data_item)
                            
                except Exception as e:
                    self.logger.warning(f"Failed to extract data for selector '{selector}': {str(e)}")
                    continue
            
            # Add delay to avoid being blocked
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            self.logger.error(f"Failed to scrape page {url}: {str(e)}")
            raise
        finally:
            await page.close()
        
        return scraped_data
    
    async def handle_page_interactions(self, page: Page):
        """
        Handle basic page interactions like clicking, scrolling.
        
        Args:
            page: Playwright page object
        """
        try:
            # Check for cookie banners and dismiss them
            cookie_selectors = [
                '[id*="cookie"]',
                '[class*="cookie"]',
                '[id*="consent"]',
                '[class*="consent"]',
                'button[aria-label*="Accept"]',
                'button[aria-label*="Close"]'
            ]
            
            for selector in cookie_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        await element.click()
                        await asyncio.sleep(0.5)
                        break
                except:
                    continue
            
            # Scroll to load dynamic content
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
            await asyncio.sleep(1)
            await page.evaluate("window.scrollTo(0, 0)")
            
        except Exception as e:
            self.logger.debug(f"Page interaction warning: {str(e)}")
    
    async def extract_element_data(self, element, selector: str, index: int, url: str) -> Dict[str, Any]:
        """
        Extract data from a single element.
        
        Args:
            element: Playwright element handle
            selector: CSS selector used to find the element
            index: Index of the element in the selector results
            url: Source URL
            
        Returns:
            Dictionary containing extracted data
        """
        try:
            data_item = {
                'url': url,
                'selector': selector,
                'index': index,
                'timestamp': asyncio.get_event_loop().time()
            }
            
            # Extract text content
            text_content = await element.text_content()
            if text_content:
                data_item['text'] = text_content.strip()
            
            # Extract inner HTML
            inner_html = await element.inner_html()
            if inner_html:
                data_item['html'] = inner_html.strip()
            
            # Extract attributes
            attributes = await element.evaluate('''
                element => {
                    const attrs = {};
                    for (let attr of element.attributes) {
                        attrs[attr.name] = attr.value;
                    }
                    return attrs;
                }
            ''')
            if attributes:
                data_item['attributes'] = attributes
            
            # Extract links if present
            href = await element.get_attribute('href')
            if href:
                # Convert relative URLs to absolute
                absolute_url = urljoin(url, href)
                data_item['link'] = absolute_url
            
            # Extract image sources
            src = await element.get_attribute('src')
            if src:
                absolute_src = urljoin(url, src)
                data_item['image_src'] = absolute_src
            
            # Extract data attributes
            data_attrs = await element.evaluate('''
                element => {
                    const dataAttrs = {};
                    for (let attr of element.attributes) {
                        if (attr.name.startsWith('data-')) {
                            dataAttrs[attr.name] = attr.value;
                        }
                    }
                    return dataAttrs;
                }
            ''')
            if data_attrs:
                data_item['data_attributes'] = data_attrs
            
            return data_item
            
        except Exception as e:
            self.logger.warning(f"Failed to extract data from element: {str(e)}")
            return {}
