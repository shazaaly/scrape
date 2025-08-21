// Playwright Web Scraper - Frontend JavaScript
class ScraperApp {
    constructor() {
        this.currentTaskId = null;
        this.pollInterval = null;
        this.initializeEventListeners();
        this.loadRecentTasks();
    }

    initializeEventListeners() {
        // Form submission
        document.getElementById('scraping-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.startScraping();
        });

        // URL validation
        document.getElementById('validate-url').addEventListener('click', () => {
            this.validateUrl();
        });

        // Selector suggestions
        document.getElementById('selector-suggestions').addEventListener('click', (e) => {
            if (e.target.matches('.dropdown-item')) {
                e.preventDefault();
                const selector = e.target.getAttribute('data-selector');
                this.addSelector(selector);
            }
        });

        // Preview config
        document.getElementById('preview-config').addEventListener('click', () => {
            this.previewConfig();
        });

        // Download results
        document.getElementById('download-results').addEventListener('click', () => {
            this.downloadResults();
        });

        // View results
        document.getElementById('view-results').addEventListener('click', () => {
            this.viewResults();
        });

        // Modal download
        document.getElementById('download-from-modal').addEventListener('click', () => {
            this.downloadResults();
        });

        // Load template
        document.getElementById('load-template').addEventListener('click', () => {
            this.showTemplateSelector();
        });

        // Save config
        document.getElementById('save-config').addEventListener('click', () => {
            this.saveConfig();
        });

        // Auto-update URL validation on input
        document.getElementById('url').addEventListener('input', () => {
            this.clearUrlValidation();
        });
    }

    async startScraping() {
        const config = this.getFormConfig();
        
        if (!this.validateConfig(config)) {
            return;
        }

        try {
            this.setLoadingState(true);
            
            const response = await fetch('/api/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to start scraping');
            }

            this.currentTaskId = result.task_id;
            this.showStatusCard();
            this.startPolling();
            this.showAlert('Scraping started successfully!', 'success');

        } catch (error) {
            console.error('Error starting scraping:', error);
            this.showAlert(`Error: ${error.message}`, 'error');
        } finally {
            this.setLoadingState(false);
        }
    }

    getFormConfig() {
        const selectors = document.getElementById('selectors').value
            .split(',')
            .map(s => s.trim())
            .filter(s => s.length > 0);

        return {
            url: document.getElementById('url').value.trim(),
            selectors: selectors.length > 0 ? selectors : ['body'],
            headless: document.getElementById('headless').checked,
            delay: parseFloat(document.getElementById('delay').value) || 1.0,
            timeout: parseInt(document.getElementById('timeout').value) || 30000,
            viewport_width: parseInt(document.getElementById('viewport-width').value) || 1280,
            viewport_height: parseInt(document.getElementById('viewport-height').value) || 720,
            max_pages: parseInt(document.getElementById('max-pages').value) || 1,
            wait_for_selector: document.getElementById('wait-selector').value.trim() || null
        };
    }

    validateConfig(config) {
        let isValid = true;
        
        // Validate URL
        if (!config.url) {
            this.showFieldError('url', 'URL is required');
            isValid = false;
        } else if (!this.isValidUrl(config.url)) {
            this.showFieldError('url', 'Please enter a valid URL');
            isValid = false;
        }

        // Validate selectors
        if (config.selectors.length === 0) {
            this.showFieldError('selectors', 'At least one selector is required');
            isValid = false;
        }

        // Validate numeric values
        if (config.delay < 0) {
            this.showFieldError('delay', 'Delay must be non-negative');
            isValid = false;
        }

        if (config.timeout <= 0) {
            this.showFieldError('timeout', 'Timeout must be positive');
            isValid = false;
        }

        if (config.max_pages <= 0) {
            this.showFieldError('max-pages', 'Max pages must be positive');
            isValid = false;
        }

        return isValid;
    }

    async validateUrl() {
        const url = document.getElementById('url').value.trim();
        
        if (!url) {
            this.showFieldError('url', 'Please enter a URL');
            return;
        }

        try {
            this.setFieldLoading('validate-url', true);

            const response = await fetch('/api/validate-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url })
            });

            const result = await response.json();

            if (result.valid) {
                this.showFieldSuccess('url', result.message);
            } else {
                this.showFieldError('url', result.message);
            }

        } catch (error) {
            console.error('Error validating URL:', error);
            this.showFieldError('url', 'Failed to validate URL');
        } finally {
            this.setFieldLoading('validate-url', false);
        }
    }

    addSelector(selector) {
        const selectorsInput = document.getElementById('selectors');
        const currentSelectors = selectorsInput.value.trim();
        
        if (currentSelectors) {
            selectorsInput.value = currentSelectors + ', ' + selector;
        } else {
            selectorsInput.value = selector;
        }
        
        selectorsInput.focus();
    }

    async previewConfig() {
        const config = this.getFormConfig();
        
        const configJson = JSON.stringify(config, null, 2);
        
        // Create a modal to show the config
        const modal = this.createConfigModal(configJson);
        document.body.appendChild(modal);
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Clean up modal when hidden
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    createConfigModal(configJson) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Configuration Preview</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <pre><code>${configJson}</code></pre>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="navigator.clipboard.writeText('${configJson.replace(/'/g, "\\'")}'); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy to Clipboard', 2000)">Copy to Clipboard</button>
                    </div>
                </div>
            </div>
        `;
        return modal;
    }

    showStatusCard() {
        document.getElementById('status-card').style.display = 'block';
        this.updateTaskStatus('queued', 0, 'Task queued...');
    }

    startPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }

        this.pollInterval = setInterval(() => {
            this.pollTaskStatus();
        }, 2000);
    }

    async pollTaskStatus() {
        if (!this.currentTaskId) {
            return;
        }

        try {
            const response = await fetch(`/api/status/${this.currentTaskId}`);
            const status = await response.json();

            if (!response.ok) {
                throw new Error(status.error || 'Failed to get task status');
            }

            this.updateTaskStatus(
                status.status,
                status.progress,
                this.getStatusMessage(status)
            );

            if (status.status === 'completed') {
                this.onTaskCompleted(status);
            } else if (status.status === 'failed') {
                this.onTaskFailed(status);
            }

        } catch (error) {
            console.error('Error polling task status:', error);
        }
    }

    updateTaskStatus(status, progress, message) {
        const statusBadge = document.getElementById('current-status');
        const progressBar = document.getElementById('progress-bar');
        const taskDetails = document.getElementById('task-details');

        statusBadge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        statusBadge.className = `badge status-${status}`;

        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);

        taskDetails.innerHTML = `<small class="text-muted">${message}</small>`;
    }

    getStatusMessage(status) {
        switch (status.status) {
            case 'queued':
                return 'Task is queued for processing...';
            case 'running':
                return `Scraping in progress... (${status.progress}%)`;
            case 'completed':
                return `Completed! Scraped ${status.total_items} items.`;
            case 'failed':
                return `Failed: ${status.error_message}`;
            default:
                return 'Unknown status';
        }
    }

    onTaskCompleted(status) {
        clearInterval(this.pollInterval);
        this.showAlert(`Scraping completed! Found ${status.total_items} items.`, 'success');
        this.showResultsCard(status);
        this.loadRecentTasks();
    }

    onTaskFailed(status) {
        clearInterval(this.pollInterval);
        this.showAlert(`Scraping failed: ${status.error_message}`, 'error');
        this.loadRecentTasks();
    }

    showResultsCard(status) {
        const resultsCard = document.getElementById('results-card');
        const itemsCount = document.getElementById('items-count');
        
        itemsCount.textContent = status.total_items;
        resultsCard.style.display = 'block';
    }

    async downloadResults() {
        if (!this.currentTaskId) {
            this.showAlert('No results to download', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/download/${this.currentTaskId}`);
            
            if (!response.ok) {
                throw new Error('Failed to download results');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `scraping_results_${this.currentTaskId}.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.showAlert('Results downloaded successfully!', 'success');

        } catch (error) {
            console.error('Error downloading results:', error);
            this.showAlert(`Error downloading results: ${error.message}`, 'error');
        }
    }

    async viewResults() {
        if (!this.currentTaskId) {
            this.showAlert('No results to view', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/results/${this.currentTaskId}`);
            const results = await response.json();

            if (!response.ok) {
                throw new Error(results.error || 'Failed to get results');
            }

            this.showResultsModal(results);

        } catch (error) {
            console.error('Error viewing results:', error);
            this.showAlert(`Error viewing results: ${error.message}`, 'error');
        }
    }

    showResultsModal(results) {
        const modal = document.getElementById('results-modal');
        const tableHeader = document.getElementById('results-table-header');
        const tableBody = document.getElementById('results-table-body');

        // Clear previous content
        tableHeader.innerHTML = '';
        tableBody.innerHTML = '';

        if (!results || results.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="100%">No results to display</td></tr>';
        } else {
            // Create table headers from first result
            const firstResult = results[0];
            Object.keys(firstResult).forEach(key => {
                const th = document.createElement('th');
                th.textContent = key.replace(/_/g, ' ').toUpperCase();
                tableHeader.appendChild(th);
            });

            // Create table rows (limit to first 50 for performance)
            results.slice(0, 50).forEach(result => {
                const row = document.createElement('tr');
                Object.keys(firstResult).forEach(key => {
                    const td = document.createElement('td');
                    let value = result[key];
                    
                    // Format different types of values
                    if (typeof value === 'object' && value !== null) {
                        value = JSON.stringify(value);
                    } else if (typeof value === 'string' && value.length > 100) {
                        value = value.substring(0, 100) + '...';
                    }
                    
                    td.textContent = value || '';
                    row.appendChild(td);
                });
                tableBody.appendChild(row);
            });

            if (results.length > 50) {
                const row = document.createElement('tr');
                row.innerHTML = `<td colspan="${Object.keys(firstResult).length}" class="text-center text-muted">... and ${results.length - 50} more results</td>`;
                tableBody.appendChild(row);
            }
        }

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    async loadRecentTasks() {
        try {
            const response = await fetch('/api/tasks');
            const tasks = await response.json();

            const recentTasksContainer = document.getElementById('recent-tasks');
            
            if (!response.ok || tasks.length === 0) {
                recentTasksContainer.innerHTML = '<p class="text-muted">No recent tasks</p>';
                return;
            }

            const tasksHtml = tasks.slice(0, 5).map(task => {
                const timeAgo = this.timeAgo(new Date(task.created_at * 1000));
                const statusClass = `status-${task.status}`;
                
                return `
                    <div class="task-item">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <a href="${task.url}" class="task-url" target="_blank" title="${task.url}">
                                    ${this.truncateUrl(task.url, 40)}
                                </a>
                                <div class="task-meta mt-1">
                                    <small class="text-muted">${timeAgo}</small>
                                    ${task.status === 'completed' ? 
                                        `<small class="text-muted">• ${task.total_items} items</small>` : 
                                        ''
                                    }
                                </div>
                            </div>
                            <span class="badge ${statusClass}">${task.status}</span>
                        </div>
                    </div>
                `;
            }).join('');

            recentTasksContainer.innerHTML = tasksHtml;

        } catch (error) {
            console.error('Error loading recent tasks:', error);
        }
    }

    // Utility methods
    setLoadingState(loading) {
        const button = document.getElementById('start-scraping');
        if (loading) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Starting...';
        } else {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-play me-1"></i>Start Scraping';
        }
    }

    setFieldLoading(fieldId, loading) {
        const button = document.getElementById(fieldId);
        if (loading) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        } else {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-check"></i> Validate';
        }
    }

    showFieldError(fieldId, message) {
        const field = document.getElementById(fieldId);
        const feedback = document.getElementById(fieldId + '-feedback') || this.createFeedback(fieldId);
        
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        feedback.textContent = message;
        feedback.className = 'invalid-feedback';
        feedback.style.display = 'block';
    }

    showFieldSuccess(fieldId, message) {
        const field = document.getElementById(fieldId);
        const feedback = document.getElementById(fieldId + '-feedback') || this.createFeedback(fieldId);
        
        field.classList.add('is-valid');
        field.classList.remove('is-invalid');
        feedback.textContent = message;
        feedback.className = 'valid-feedback';
        feedback.style.display = 'block';
    }

    clearUrlValidation() {
        const field = document.getElementById('url');
        const feedback = document.getElementById('url-feedback');
        
        field.classList.remove('is-valid', 'is-invalid');
        if (feedback) {
            feedback.style.display = 'none';
        }
    }

    createFeedback(fieldId) {
        const feedback = document.createElement('div');
        feedback.id = fieldId + '-feedback';
        feedback.style.display = 'none';
        
        const field = document.getElementById(fieldId);
        field.parentNode.appendChild(feedback);
        
        return feedback;
    }

    isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }

    truncateUrl(url, maxLength) {
        if (url.length <= maxLength) return url;
        
        try {
            const urlObj = new URL(url);
            const domain = urlObj.hostname;
            const path = urlObj.pathname;
            
            if (domain.length + 10 >= maxLength) {
                return domain.substring(0, maxLength - 3) + '...';
            }
            
            const availableLength = maxLength - domain.length - 3;
            const truncatedPath = path.length > availableLength ? 
                path.substring(0, availableLength) + '...' : path;
            
            return domain + truncatedPath;
        } catch {
            return url.substring(0, maxLength - 3) + '...';
        }
    }

    timeAgo(date) {
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);
        
        const intervals = [
            { label: 'year', seconds: 31536000 },
            { label: 'month', seconds: 2592000 },
            { label: 'day', seconds: 86400 },
            { label: 'hour', seconds: 3600 },
            { label: 'minute', seconds: 60 }
        ];
        
        for (const interval of intervals) {
            const count = Math.floor(seconds / interval.seconds);
            if (count >= 1) {
                return `${count} ${interval.label}${count !== 1 ? 's' : ''} ago`;
            }
        }
        
        return 'just now';
    }

    showAlert(message, type = 'info') {
        const alertContainer = this.getOrCreateAlertContainer();
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        alertContainer.appendChild(alert);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    getOrCreateAlertContainer() {
        let container = document.getElementById('alert-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'alert-container';
            container.className = 'position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        return container;
    }

    async showTemplateSelector() {
        // This would show a modal with template options
        // For now, just show a simple alert
        this.showAlert('Template feature coming soon!', 'info');
    }

    saveConfig() {
        const config = this.getFormConfig();
        const configJson = JSON.stringify(config, null, 2);
        
        const blob = new Blob([configJson], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'scraper_config.json';
        document.body.appendChild(a);
        a.click();
        URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        this.showAlert('Configuration saved successfully!', 'success');
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ScraperApp();
});

// Global utility functions
window.copyToClipboard = function(text) {
    navigator.clipboard.writeText(text).then(() => {
        console.log('Copied to clipboard');
    }).catch(err => {
        console.error('Failed to copy: ', err);
    });
};
