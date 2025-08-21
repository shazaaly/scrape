# Playwright Web Scraper

A comprehensive, feature-rich web scraping tool built with Playwright for automated data extraction. This project provides both command-line and web interface options for scraping websites with advanced configuration, multiple export formats, and anti-bot measures.

## 🚀 Features

### Core Functionality
- **Playwright Integration**: Automated browser control using Playwright (Chromium, Firefox, Webkit)
- **Multiple Interfaces**: Both command-line and web-based user interfaces
- **Advanced Configuration**: YAML/JSON configuration files with template support
- **Export Formats**: JSON, CSV, and Excel output formats
- **Anti-Detection**: User agent rotation, random delays, and realistic browsing behavior

### Web Interface
- **Modern UI**: Responsive Bootstrap-based interface with dark/light themes
- **Real-time Monitoring**: Live task progress tracking and status updates
- **Results Preview**: View scraped data directly in the browser
- **Task History**: Keep track of recent scraping tasks
- **Configuration Templates**: Pre-built templates for common scraping scenarios

### Scraping Capabilities
- **CSS Selectors**: Extract data using flexible CSS selectors
- **Dynamic Content**: Handle JavaScript-rendered pages
- **Cookie Handling**: Automatic cookie banner dismissal
- **Content Loading**: Smart waiting for dynamic content
- **Multiple Pages**: Support for scraping multiple pages in sequence
- **Error Handling**: Robust error handling with detailed logging

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Configuration](#configuration)
- [Examples](#examples)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## 🛠 Installation

### Prerequisites

- **Python 3.8+**: Make sure you have Python 3.8 or higher installed
- **Node.js** (for Playwright browsers): Required for Playwright browser installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/playwright-web-scraper.git
cd playwright-web-scraper
```

### Step 2: Install Python Dependencies

Using pip:
```bash
pip install -r requirements.txt
```

Or using uv (recommended for faster installation):
```bash
uv sync
```

### Step 3: Install Playwright Browsers

```bash
playwright install
```

For system dependencies (Linux):
```bash
playwright install-deps
```

### Step 4: Verify Installation

Test the web interface:
```bash
python run_server.py
```

Visit `http://localhost:5000` to access the web interface.

## 🚀 Quick Start

### Using the Web Interface

1. **Start the server**:
   ```bash
   python run_server.py
   ```

2. **Open your browser** and navigate to `http://localhost:5000`

3. **Enter a URL** to scrape (e.g., `https://quotes.toscrape.com`)

4. **Add CSS selectors** (e.g., `.quote .text, .quote .author`)

5. **Click "Start Scraping"** and monitor the progress

6. **Download results** when complete

### Using the Command Line

Basic scraping:
```bash
python main.py --url "https://quotes.toscrape.com" --selectors ".quote .text,.quote .author"
```

Advanced configuration:
```bash
python main.py --url "https://news.ycombinator.com" \
                --selectors ".storylink,.subtext" \
                --format csv \
                --delay 2 \
                --max-pages 3
```

Using a configuration file:
```bash
python main.py --config config.yaml
```

## 📖 Usage

### Web Interface

The web interface provides an intuitive way to configure and run scraping tasks:

#### Main Features:
- **URL Validation**: Real-time URL validation with helpful feedback
- **Selector Assistant**: Dropdown suggestions for common CSS selectors
- **Advanced Settings**: Browser configuration, timing settings, and viewport options
- **Progress Tracking**: Real-time task monitoring with progress bars
- **Results Management**: Preview, download, and manage scraping results

#### Configuration Options:
- **Target URL**: The website you want to scrape
- **CSS Selectors**: Elements to extract data from
- **Browser Settings**: Headless mode, viewport size
- **Timing**: Delays, timeouts, and wait conditions
- **Output**: Export format and filename

### Command Line Interface

#### Basic Usage

```bash
python main.py [OPTIONS]
```

#### Available Options:

| Option | Description | Default |
|--------|-------------|---------|
| `--url` | Target URL to scrape | Required* |
| `--config` | Configuration file path | Required* |
| `--selectors` | CSS selectors (comma-separated) | body |
| `--output` | Output filename (without extension) | scraped_data |
| `--format` | Output format (json, csv) | json |
| `--headless` | Run in headless mode (true/false) | true |
| `--delay` | Delay between requests (seconds) | 1.0 |
| `--timeout` | Page load timeout (milliseconds) | 30000 |
| `--max-pages` | Maximum pages to scrape | 1 |
| `--user-agent` | Custom user agent string | Auto |
| `--viewport-width` | Browser viewport width | 1280 |
| `--viewport-height` | Browser viewport height | 720 |
| `--wait-for-selector` | Wait for specific selector | None |
| `--log-level` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |

*Either `--url` or `--config` is required.

## ⚙️ Configuration

### Configuration Files

Create YAML or JSON configuration files for reusable scraping setups:

```yaml
# config.yaml
url: "https://example.com"
selectors:
  - "h1"
  - "p"
  - ".article-title"
  - "[data-testid='content']"

# Browser settings
headless: true
delay: 1.0
timeout: 30000

# Viewport settings
viewport:
  width: 1280
  height: 720

# Advanced options
javascript_enabled: true
images_enabled: false
css_enabled: true
follow_redirects: true

# Anti-bot measures
random_delay: true
rotate_user_agent: true

# Export settings
export_format: "json"
output_file: "scraped_data"
max_pages: 1
```

### Pre-built Templates

The project includes templates for common scraping scenarios:

#### News Scraper Template
```yaml
selectors:
  - "h1"
  - "h2"
  - ".article-title"
  - ".article-content"
  - ".byline"
  - ".publish-date"
wait_for_selector: "h1"
delay: 2.0
max_pages: 10
```

#### E-commerce Scraper Template
```yaml
selectors:
  - ".product-title"
  - ".price"
  - ".description"
  - ".rating"
  - ".availability"
wait_for_selector: ".product-title"
delay: 1.5
javascript_enabled: true
max_pages: 20
```

### Creating Custom Templates

```bash
python -c "
from config import create_config_template
create_config_template('news_scraper', 'my-news-config.yaml')
"
```

## 💡 Examples

### Example 1: Scraping Quotes

```bash
python main.py \
  --url "https://quotes.toscrape.com" \
  --selectors ".quote .text, .quote .author, .quote .tags" \
  --format csv \
  --output quotes_data
```

### Example 2: Scraping News Headlines

```yaml
# news_config.yaml
url: "https://news.ycombinator.com"
selectors:
  - ".storylink"
  - ".subtext"
  - ".score"
delay: 2.0
max_pages: 5
export_format: "json"
output_file: "hn_headlines"
```

```bash
python main.py --config news_config.yaml
```

### Example 3: E-commerce Product Scraping

```bash
python main.py \
  --url "https://books.toscrape.com" \
  --selectors ".product_pod h3 a, .price_color, .star-rating" \
  --delay 1.5 \
  --max-pages 3 \
  --format excel \
  --wait-for-selector ".product_pod"
```

### Example 4: Using the Web Interface Programmatically

```python
import requests

# Start a scraping task
response = requests.post('http://localhost:5000/api/scrape', json={
    'url': 'https://quotes.toscrape.com',
    'selectors': ['.quote .text', '.quote .author'],
    'delay': 1.0,
    'max_pages': 2
})

task_id = response.json()['task_id']

# Check task status
status = requests.get(f'http://localhost:5000/api/status/{task_id}')
print(status.json())

# Download results when complete
results = requests.get(f'http://localhost:5000/api/download/{task_id}')
```

## 🔧 API Reference

### REST API Endpoints

When running the web server (`python run_server.py`), the following endpoints are available:

#### Start Scraping Task
```
POST /api/scrape
Content-Type: application/json

{
  "url": "https://example.com",
  "selectors": ["h1", "p"],
  "headless": true,
  "delay": 1.0,
  "timeout": 30000,
  "max_pages": 1
}
```

#### Get Task Status
```
GET /api/status/{task_id}
```

#### Get Task Results
```
GET /api/results/{task_id}
```

#### Download Results File
```
GET /api/download/{task_id}
```

#### List All Tasks
```
GET /api/tasks
```

#### Validate URL
```
POST /api/validate-url
Content-Type: application/json

{
  "url": "https://example.com"
}
```

### Python API

```python
from scraper import PlaywrightScraper
from config import ScrapingConfig
from exporters import DataExporter

# Create configuration
config = ScrapingConfig(
    url="https://quotes.toscrape.com",
    selectors=[".quote .text", ".quote .author"],
    headless=True,
    delay=1.0
)

# Initialize scraper
scraper = PlaywrightScraper(config)

# Perform scraping
async def scrape_data():
    data = await scraper.scrape()
    
    # Export results
    exporter = DataExporter()
    output_file = exporter.export(data, "quotes", "json")
    
    print(f"Data exported to: {output_file}")

# Run the scraper
import asyncio
asyncio.run(scrape_data())
```

## 📁 Project Structure

```
playwright-web-scraper/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project configuration
├── config.yaml              # Sample configuration
├── main.py                  # CLI entry point
├── run_server.py            # Web server entry point
├── scraper.py               # Core scraping logic
├── config.py                # Configuration management
├── exporters.py             # Data export utilities
├── utils.py                 # Utility functions
├── web_interface.py         # Additional web interface helpers
├── static/                  # Web interface assets
│   ├── style.css           # Custom styles
│   └── app.js              # Frontend JavaScript
├── templates/               # HTML templates
│   └── index.html          # Main web interface
└── logs/                   # Application logs (auto-created)
```

## 🔒 Best Practices & Security

### Responsible Scraping
- **Respect robots.txt**: Always check the website's robots.txt file
- **Rate Limiting**: Use appropriate delays between requests
- **Terms of Service**: Comply with website terms and conditions
- **Data Privacy**: Handle scraped data responsibly

### Anti-Detection Measures
- **User Agent Rotation**: Automatic rotation of user agents
- **Random Delays**: Variable delays between requests
- **Realistic Behavior**: Human-like browsing patterns
- **Session Management**: Proper cookie and session handling

### Performance Optimization
- **Headless Mode**: Use headless browsers for better performance
- **Selective Loading**: Disable images/CSS when not needed
- **Efficient Selectors**: Use specific, efficient CSS selectors
- **Memory Management**: Proper cleanup of resources

## 🐛 Troubleshooting

### Common Issues

#### 1. Playwright Installation Issues
```bash
# Reinstall Playwright browsers
playwright install --force

# Install system dependencies (Linux)
playwright install-deps
```

#### 2. Selector Not Finding Elements
- Use browser developer tools to inspect elements
- Test selectors in the browser console
- Wait for dynamic content with `wait_for_selector`
- Try different selector strategies

#### 3. Timeout Errors
- Increase the timeout value
- Check if the website requires JavaScript
- Verify the website is accessible
- Use non-headless mode for debugging

#### 4. Memory Issues
- Reduce the number of concurrent pages
- Implement proper cleanup in custom scripts
- Monitor resource usage
- Use smaller viewport sizes

### Debug Mode

Enable debug logging for detailed information:

```bash
python main.py --url "https://example.com" --log-level DEBUG
```

Or in the web interface, check the browser console for detailed logs.

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Development Setup

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/playwright-web-scraper.git
   cd playwright-web-scraper
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e .
   pip install pytest black flake8 mypy
   ```

4. **Run tests**:
   ```bash
   pytest tests/
   ```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions
- Format code with Black: `black .`
- Check linting with Flake8: `flake8 .`

### Submitting Changes

1. Create a feature branch: `git checkout -b feature-name`
2. Make your changes
3. Add tests for new functionality
4. Run the test suite
5. Submit a pull request

### Reporting Issues

When reporting issues, please include:
- Python version
- Operating system
- Detailed error messages
- Steps to reproduce
- Sample URLs (if applicable)

## 📋 Roadmap

### Planned Features

- [ ] **Database Integration**: Support for saving results to databases
- [ ] **Scheduled Scraping**: Cron-like scheduling for automated scraping
- [ ] **Proxy Support**: Proxy rotation and management
- [ ] **Data Validation**: Schema validation for scraped data
- [ ] **API Rate Limiting**: Built-in rate limiting for API-like scraping
- [ ] **Cloud Deployment**: Easy deployment to cloud platforms
- [ ] **Machine Learning**: Automatic selector generation using ML
- [ ] **Real-time Monitoring**: Advanced monitoring and alerting


**Happy Scraping!** 🕷️

Made with ❤️ by Shaza Aly
