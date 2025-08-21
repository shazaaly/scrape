# Overview

This is a Playwright Web Scraper application that provides both command-line and web interfaces for extracting data from websites. The system uses Playwright for browser automation to scrape web content with configurable selectors, export options, and anti-bot measures. It supports multiple output formats (JSON, CSV, Excel) and includes a Flask-based web interface for easier interaction.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Components

The application follows a modular architecture with clear separation of concerns:

**Scraper Engine**: The `PlaywrightScraper` class handles browser automation using Playwright's async API. It supports headless browsing, user agent rotation, and configurable delays to avoid detection. The scraper can handle single URLs or multiple pages with customizable selectors for data extraction.

**Configuration Management**: The `ScrapingConfig` dataclass provides a centralized configuration system supporting both programmatic configuration and file-based config (YAML/JSON). This includes browser settings, scraping parameters, and anti-bot measures.

**Data Export System**: The `DataExporter` class handles multiple output formats with automatic data cleaning and timestamp-based file naming. Supports JSON, CSV, and Excel formats with validation and error handling.

**Web Interface**: Flask-based web server provides a user-friendly interface for configuring scraping tasks, monitoring progress, and downloading results. Uses Bootstrap for responsive design and includes real-time task monitoring.

## Design Patterns

**Async Context Manager**: The scraper uses async context managers for proper resource management, ensuring browsers and contexts are properly initialized and cleaned up.

**Strategy Pattern**: Multiple export formats are handled through a unified interface with format-specific implementations.

**Configuration-First Approach**: All scraping parameters are externalized into configuration objects, making the system highly configurable without code changes.

## Browser Automation

The system uses Playwright for robust browser automation with features like:
- Configurable viewport and browser settings
- User agent rotation for anti-detection
- JavaScript execution control
- Image and CSS loading optimization
- Timeout and retry mechanisms

## Data Processing Pipeline

Data flows through a clean pipeline: URL validation → Browser initialization → Page scraping → Data extraction → Cleaning → Export. Each stage includes error handling and logging for debugging and monitoring.

# External Dependencies

**Playwright**: Primary browser automation framework for headless Chrome/Firefox/Safari control and web scraping functionality.

**Flask**: Web framework providing the HTTP server and templating system for the web interface.

**Pandas**: Data manipulation library used for advanced data processing and Excel export capabilities.

**PyYAML**: Configuration file parsing for YAML-based scraping configurations.

**Bootstrap & Font Awesome**: Frontend CSS frameworks for responsive web interface design and icons.

**Logging**: Built-in Python logging for comprehensive application monitoring and debugging.

The application is designed to be self-contained with minimal external service dependencies, focusing on local processing and file-based outputs.