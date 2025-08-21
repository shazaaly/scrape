#!/usr/bin/env python3
"""
Web Interface Server for Playwright Scraper
Provides a simple web interface to configure and run scraping tasks.
"""

import asyncio
import json
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import threading
import queue
import time

from scraper import PlaywrightScraper
from config import ScrapingConfig
from exporters import DataExporter
from utils import setup_logging, validate_url


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

# Global variables for task management
scraping_tasks = {}
task_queue = queue.Queue()
results_storage = {}

# Setup logging
setup_logging('INFO')
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    """Main page with scraping interface."""
    return render_template('index.html')


@app.route('/api/scrape', methods=['POST'])
def start_scraping():
    """Start a new scraping task."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('url'):
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        if not validate_url(url):
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # Create configuration from request data
        config_data = {
            'url': url,
            'selectors': data.get('selectors', ['body']),
            'headless': data.get('headless', True),
            'delay': float(data.get('delay', 1.0)),
            'timeout': int(data.get('timeout', 30000)),
            'max_pages': int(data.get('max_pages', 1)),
            'wait_for_selector': data.get('wait_for_selector'),
            'viewport': {
                'width': int(data.get('viewport_width', 1280)),
                'height': int(data.get('viewport_height', 720))
            }
        }
        
        config = ScrapingConfig(**config_data)
        
        # Generate task ID
        task_id = f"task_{int(time.time() * 1000)}"
        
        # Store task info
        scraping_tasks[task_id] = {
            'status': 'queued',
            'config': config,
            'created_at': time.time(),
            'progress': 0
        }
        
        # Start scraping in background
        thread = threading.Thread(target=run_scraping_task, args=(task_id, config))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'status': 'started',
            'message': 'Scraping task started successfully'
        })
        
    except Exception as e:
        logger.error(f"Error starting scraping task: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<task_id>')
def get_task_status(task_id):
    """Get status of a scraping task."""
    if task_id not in scraping_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task_info = scraping_tasks[task_id]
    
    response = {
        'task_id': task_id,
        'status': task_info['status'],
        'progress': task_info['progress'],
        'created_at': task_info['created_at']
    }
    
    # Add results if completed
    if task_info['status'] == 'completed' and task_id in results_storage:
        result_info = results_storage[task_id]
        response.update({
            'total_items': result_info.get('total_items', 0),
            'export_file': result_info.get('export_file'),
            'summary': result_info.get('summary', {})
        })
    
    # Add error message if failed
    if task_info['status'] == 'failed':
        response['error_message'] = task_info.get('error_message')
    
    return jsonify(response)


@app.route('/api/results/<task_id>')
def get_task_results(task_id):
    """Get results of a completed scraping task."""
    if task_id not in scraping_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    if scraping_tasks[task_id]['status'] != 'completed':
        return jsonify({'error': 'Task not completed yet'}), 400
    
    if task_id not in results_storage:
        return jsonify({'error': 'Results not found'}), 404
    
    return jsonify(results_storage[task_id]['data'])


@app.route('/api/download/<task_id>')
def download_results(task_id):
    """Download results file."""
    if task_id not in scraping_tasks or task_id not in results_storage:
        return jsonify({'error': 'Task not found or no results available'}), 404
    
    result_info = results_storage[task_id]
    export_file = result_info.get('export_file')
    
    if not export_file or not Path(export_file).exists():
        return jsonify({'error': 'Export file not found'}), 404
    
    return send_file(export_file, as_attachment=True)


@app.route('/api/tasks')
def list_tasks():
    """List all scraping tasks."""
    tasks_list = []
    for task_id, task_info in scraping_tasks.items():
        task_summary = {
            'task_id': task_id,
            'status': task_info['status'],
            'url': task_info['config'].url,
            'created_at': task_info['created_at'],
            'progress': task_info['progress']
        }
        
        if task_info['status'] == 'completed' and task_id in results_storage:
            task_summary['total_items'] = results_storage[task_id].get('total_items', 0)
        
        tasks_list.append(task_summary)
    
    # Sort by creation time (newest first)
    tasks_list.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify(tasks_list)


@app.route('/api/validate-url', methods=['POST'])
def validate_url_endpoint():
    """Validate URL format."""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'valid': False, 'message': 'URL is required'})
    
    is_valid = validate_url(url)
    message = 'URL is valid' if is_valid else 'Invalid URL format'
    
    return jsonify({'valid': is_valid, 'message': message})


def run_scraping_task(task_id: str, config: ScrapingConfig):
    """Run scraping task in background thread."""
    try:
        # Update task status
        scraping_tasks[task_id]['status'] = 'running'
        scraping_tasks[task_id]['progress'] = 10
        
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run scraping
            scraper = PlaywrightScraper(config)
            scraped_data = loop.run_until_complete(scraper.scrape())
            
            scraping_tasks[task_id]['progress'] = 70
            
            if not scraped_data:
                raise Exception("No data was scraped from the target URL")
            
            # Export data
            exporter = DataExporter()
            export_file = exporter.export(scraped_data, f"web_scrape_{task_id}", 'json')
            
            scraping_tasks[task_id]['progress'] = 90
            
            # Generate summary stats
            summary_stats = exporter.get_summary_stats(scraped_data)
            
            # Store results
            results_storage[task_id] = {
                'data': scraped_data[:100],  # Store first 100 items for preview
                'total_items': len(scraped_data),
                'export_file': export_file,
                'summary': summary_stats
            }
            
            # Mark as completed
            scraping_tasks[task_id]['status'] = 'completed'
            scraping_tasks[task_id]['progress'] = 100
            
            logger.info(f"Task {task_id} completed successfully. Scraped {len(scraped_data)} items.")
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        scraping_tasks[task_id]['status'] = 'failed'
        scraping_tasks[task_id]['error_message'] = str(e)


if __name__ == '__main__':
    logger.info("Starting Playwright Scraper Web Interface...")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
