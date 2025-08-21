# Architecture Documentation

## Overview

This document provides a comprehensive guide to the architecture of the Playwright Web Scraper project. It's designed to help you understand the codebase structure, make modifications, and scale the application effectively.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Code Organization](#code-organization)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Design Patterns](#design-patterns)
6. [Extension Points](#extension-points)
7. [Scaling Strategies](#scaling-strategies)
8. [Development Guidelines](#development-guidelines)

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT INTERFACES                        │
├─────────────────────────┬───────────────────────────────────┤
│    Web Interface        │      Command Line Interface      │
│   (Flask + Bootstrap)   │         (Argparse)              │
└─────────────┬───────────┴───────────────────┬───────────────┘
              │                               │
              └───────────────┬───────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────┐
│                   APPLICATION LAYER                          │
├───────────────────┬─────────────────────┬─────────────────────┤
│   Configuration   │   Task Management   │   Data Processing   │
│   Management      │   & Orchestration   │   & Export          │
└─────────┬─────────┴─────────────────────┴─────────────┬───────┘
          │                                             │
          └─────────────────┬───────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                    SCRAPING ENGINE                            │
├─────────────────────────────┬─────────────────────────────────┤
│      Playwright Core        │      Browser Automation        │
│   (Browser Management)      │    (Page Interaction)          │
└─────────────────────────────┴─────────────────────────────────┘
```

### Technology Stack

- **Backend**: Python 3.8+
- **Web Framework**: Flask
- **Browser Automation**: Playwright
- **Data Processing**: Pandas
- **Configuration**: YAML/JSON
- **Frontend**: Bootstrap 5, JavaScript (ES6+)
- **Package Management**: uv (recommended) or pip
- **Async Support**: asyncio

## Code Organization

### Directory Structure

```
playwright-web-scraper/
├── 📁 static/                    # Frontend assets
│   ├── 🎨 style.css             # Custom CSS styles
│   └── ⚡ app.js                # Frontend JavaScript
├── 📁 templates/                 # HTML templates
│   └── 🌐 index.html            # Main web interface
├── 📁 logs/                      # Application logs (auto-created)
├── 🐍 main.py                   # CLI entry point
├── 🌐 run_server.py             # Web server entry point
├── 🕷️ scraper.py                # Core scraping engine
├── ⚙️ config.py                 # Configuration management
├── 📊 exporters.py              # Data export utilities
├── 🛠️ utils.py                  # Utility functions
├── 🌐 web_interface.py          # Additional web helpers
├── 📋 config.yaml               # Sample configuration
├── 📄 pyproject.toml            # Project configuration
└── 📚 replit.md                 # Project documentation
```

### File Responsibilities

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `main.py` | CLI interface and argument parsing | `main()` |
| `run_server.py` | Flask web server and API endpoints | Flask app, API routes |
| `scraper.py` | Core scraping logic and browser automation | `PlaywrightScraper` |
| `config.py` | Configuration management and validation | `ScrapingConfig` |
| `exporters.py` | Data export and formatting | `DataExporter` |
| `utils.py` | Utility functions and helpers | Various utility functions |
| `web_interface.py` | Additional web interface functionality | Flask blueprints |

## Component Details

### 1. Configuration Management (`config.py`)

**Purpose**: Centralized configuration handling with validation and templating.

**Key Components**:
```python
@dataclass
class ScrapingConfig:
    """Main configuration class with validation"""
    url: Union[str, List[str]]
    selectors: List[str]
    headless: bool = True
    delay: float = 1.0
    # ... other fields
```

**Extension Points**:
- Add new configuration fields to `ScrapingConfig`
- Create new template configurations in `DEFAULT_CONFIGS`
- Add validation logic in the `validate()` method

### 2. Scraping Engine (`scraper.py`)

**Purpose**: Browser automation and data extraction using Playwright.

**Key Components**:
```python
class PlaywrightScraper:
    """Main scraper class with async context management"""
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping orchestration"""
        
    async def scrape_page(self, url: str) -> List[Dict[str, Any]]:
        """Single page scraping logic"""
        
    async def extract_element_data(self, element, selector, index, url):
        """Individual element data extraction"""
```

**Architecture Decisions**:
- **Async Context Manager**: Ensures proper resource cleanup
- **User Agent Rotation**: Built-in anti-detection measures
- **Modular Extraction**: Separate methods for different data types

### 3. Data Export System (`exporters.py`)

**Purpose**: Multi-format data export with cleaning and validation.

**Key Components**:
```python
class DataExporter:
    """Handles multiple export formats"""
    
    def export(self, data, filename, format_type) -> str:
        """Main export interface"""
        
    def clean_data(self, data) -> List[Dict[str, Any]]:
        """Data cleaning and validation"""
```

**Supported Formats**:
- JSON: Preserves data structure and metadata
- CSV: Flattened tabular format
- Excel: Multi-sheet with metadata

### 4. Web Interface (`run_server.py`, `web_interface.py`)

**Purpose**: REST API and web-based user interface.

**API Architecture**:
```python
# Main endpoints
@app.route('/api/scrape', methods=['POST'])     # Start scraping task
@app.route('/api/status/<task_id>')             # Get task status
@app.route('/api/results/<task_id>')            # Get results
@app.route('/api/download/<task_id>')           # Download file
```

**Task Management**:
- Background threading for non-blocking scraping
- In-memory task storage (can be extended to database)
- Real-time progress tracking

## Data Flow

### 1. Configuration Flow

```
User Input → Validation → ScrapingConfig → Scraper Initialization
     ↓
CLI Args/Web Form → config.py → scraper.py
```

### 2. Scraping Flow

```
URL(s) → Browser Launch → Page Navigation → Element Selection → Data Extraction → Cleanup
   ↓           ↓              ↓               ↓               ↓            ↓
Config → Playwright → Page Load → CSS Selectors → JSON Data → Export
```

### 3. Web Interface Flow

```
Frontend Request → Flask Route → Background Task → Progress Updates → Results
       ↓              ↓              ↓               ↓              ↓
   app.js → run_server.py → Threading → WebSocket/Polling → Download
```

## Design Patterns

### 1. **Strategy Pattern** (Export Formats)
```python
# Different export strategies
def export_json(self, data, filename): ...
def export_csv(self, data, filename): ...  
def export_excel(self, data, filename): ...
```

### 2. **Template Method** (Scraping Process)
```python
async def scrape(self):
    """Template method defining scraping steps"""
    await self.initialize_browser()  # Step 1
    for url in urls:
        data = await self.scrape_page(url)  # Step 2
    await self.close()  # Step 3
```

### 3. **Builder Pattern** (Configuration)
```python
config = ScrapingConfig.from_file('config.yaml')
# or
config = ScrapingConfig(url="...", selectors=[...])
```

### 4. **Facade Pattern** (Main Interfaces)
```python
# Simple interface hiding complex implementation
async def scrape_website(url, selectors):
    config = ScrapingConfig(url=url, selectors=selectors)
    scraper = PlaywrightScraper(config)
    return await scraper.scrape()
```

## Extension Points

### 1. Adding New Export Formats

```python
# In exporters.py
class DataExporter:
    def export_xml(self, data: List[Dict[str, Any]], filename: str) -> str:
        """Add XML export functionality"""
        # Implementation here
        
    def export(self, data, filename, format_type):
        # Add new format to the dispatcher
        if format_type.lower() == 'xml':
            return self.export_xml(data, filename)
```

### 2. Custom Data Extraction

```python
# In scraper.py
class PlaywrightScraper:
    async def extract_custom_data(self, element):
        """Add custom extraction logic"""
        # Your custom extraction logic
        
    async def extract_element_data(self, element, selector, index, url):
        # Extend existing extraction
        data_item = await self.extract_custom_data(element)
```

### 3. New API Endpoints

```python
# In run_server.py or web_interface.py
@app.route('/api/custom-endpoint', methods=['POST'])
def custom_functionality():
    """Add new API functionality"""
    # Implementation here
```

### 4. Database Integration

```python
# New file: database.py
class DatabaseManager:
    def save_results(self, task_id, data):
        """Save scraping results to database"""
        
    def get_task_history(self, user_id):
        """Retrieve task history from database"""
```

## Scaling Strategies

### 1. Horizontal Scaling

**Current State**: Single-process, single-machine
**Scale Options**:

```python
# Option 1: Multi-processing
from multiprocessing import Pool

async def scrape_multiple_urls(urls):
    with Pool() as pool:
        results = pool.map(scrape_single_url, urls)
    return results

# Option 2: Distributed task queue (Celery)
from celery import Celery

app = Celery('scraper')

@app.task
def scrape_task(config_dict):
    """Celery task for distributed scraping"""
    # Scraping logic here
```

### 2. Database Integration

**Current State**: In-memory storage
**Recommended Approach**:

```python
# database.py
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ScrapingTask(Base):
    __tablename__ = 'scraping_tasks'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(String, unique=True)
    config = Column(JSON)
    status = Column(String)
    results = Column(JSON)
    created_at = Column(DateTime)
```

### 3. Caching Layer

```python
# caching.py
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_results(expiration=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"scraper:{hash(str(args))}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### 4. Rate Limiting & Throttling

```python
# rate_limiting.py
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=100, window_minutes=1):
        self.max_requests = max_requests
        self.window = timedelta(minutes=window_minutes)
        self.requests = defaultdict(list)
    
    def allow_request(self, identifier):
        now = datetime.now()
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.window
        ]
        
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True
        return False
```

## Development Guidelines

### 1. Code Organization Principles

- **Separation of Concerns**: Each module has a single responsibility
- **Dependency Injection**: Configuration is passed to components
- **Interface Segregation**: Small, focused interfaces
- **Open/Closed Principle**: Open for extension, closed for modification

### 2. Adding New Features

#### Step 1: Define the Interface
```python
# In appropriate module
class NewFeature:
    def process(self, data):
        raise NotImplementedError
```

#### Step 2: Implement the Feature
```python
class ConcreteFeature(NewFeature):
    def process(self, data):
        # Implementation
        return processed_data
```

#### Step 3: Integrate with Configuration
```python
# In config.py
@dataclass
class ScrapingConfig:
    # ... existing fields
    enable_new_feature: bool = False
    new_feature_options: Dict = field(default_factory=dict)
```

#### Step 4: Wire Everything Together
```python
# In main scraping logic
if config.enable_new_feature:
    feature = ConcreteFeature(**config.new_feature_options)
    data = feature.process(data)
```

### 3. Testing Strategy

```python
# tests/test_scraper.py
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
async def mock_scraper():
    scraper = PlaywrightScraper(mock_config)
    scraper.browser = AsyncMock()
    return scraper

async def test_scrape_page(mock_scraper):
    # Test implementation
    result = await mock_scraper.scrape_page("http://example.com")
    assert len(result) > 0
```

### 4. Configuration Management

#### Environment-specific Configs
```yaml
# config/development.yaml
debug: true
headless: false
delay: 0.5

# config/production.yaml  
debug: false
headless: true
delay: 2.0
```

#### Feature Flags
```python
# feature_flags.py
class FeatureFlags:
    ENABLE_CACHING = True
    ENABLE_RATE_LIMITING = True
    ENABLE_ADVANCED_SELECTORS = False
```

### 5. Monitoring & Logging

```python
# monitoring.py
import logging
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logging.info(f"{func.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            logging.error(f"{func.__name__} failed: {str(e)}")
            raise
    return wrapper
```

## Common Modification Scenarios

### 1. Adding a New Browser Engine

```python
# In scraper.py
class PlaywrightScraper:
    def __init__(self, config):
        self.browser_engines = {
            'chromium': self.playwright.chromium,
            'firefox': self.playwright.firefox,
            'webkit': self.playwright.webkit,
            # Add new engine here
        }
    
    async def initialize_browser(self):
        engine = self.browser_engines[self.config.browser_engine]
        self.browser = await engine.launch(...)
```

### 2. Custom Authentication

```python
# auth.py
class AuthenticationManager:
    async def login(self, page, auth_config):
        if auth_config.type == 'basic':
            await self.basic_auth(page, auth_config)
        elif auth_config.type == 'oauth':
            await self.oauth_auth(page, auth_config)
            
    async def basic_auth(self, page, config):
        await page.fill('#username', config.username)
        await page.fill('#password', config.password)
        await page.click('#login')
```

### 3. Data Validation

```python
# validators.py
from pydantic import BaseModel, validator

class ScrapedDataModel(BaseModel):
    url: str
    title: str
    content: str
    
    @validator('url')
    def validate_url(cls, v):
        # URL validation logic
        return v
```

## Performance Considerations

### 1. Memory Management
- Use async context managers for proper cleanup
- Limit concurrent page instances
- Implement data streaming for large datasets

### 2. Browser Optimization
```python
# Optimized browser launch
await browser.new_context(
    viewport={'width': 1280, 'height': 720},
    java_script_enabled=False,  # Disable if not needed
    images_enabled=False,       # Skip images for speed
)
```

### 3. Selective Loading
```python
# Route blocking for faster loading
await page.route('**/*', lambda route: (
    route.abort() if route.request.resource_type in ['image', 'stylesheet']
    else route.continue_()
))
```

This architecture documentation should give you a solid foundation for understanding, modifying, and scaling the project. Each section provides both theoretical understanding and practical code examples to help you implement changes effectively.