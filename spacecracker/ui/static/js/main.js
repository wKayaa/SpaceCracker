// SpaceCracker Pro - Main JavaScript
// Real-time dashboard updates and interactive features

class SpaceCrackerUI {
    constructor() {
        this.wsConnection = null;
        this.scanInProgress = false;
        this.updateInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startStatsUpdates();
        this.setupFileUploads();
        this.setupFormValidation();
    }

    setupEventListeners() {
        // Navigation
        const navLinks = document.querySelectorAll('.sidebar-nav a');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            });
        });

        // Scan controls
        const startScanBtn = document.getElementById('startScan');
        const stopScanBtn = document.getElementById('stopScan');
        
        if (startScanBtn) {
            startScanBtn.addEventListener('click', () => this.startScan());
        }
        
        if (stopScanBtn) {
            stopScanBtn.addEventListener('click', () => this.stopScan());
        }

        // Module selection
        const moduleCheckboxes = document.querySelectorAll('input[name="modules"]');
        const selectAllBtn = document.getElementById('selectAllModules');
        const selectNoneBtn = document.getElementById('selectNoneModules');
        
        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', () => {
                moduleCheckboxes.forEach(cb => cb.checked = true);
            });
        }
        
        if (selectNoneBtn) {
            selectNoneBtn.addEventListener('click', () => {
                moduleCheckboxes.forEach(cb => cb.checked = false);
            });
        }

        // Export buttons
        const exportBtns = document.querySelectorAll('[data-export]');
        exportBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const format = btn.getAttribute('data-export');
                this.exportResults(format);
            });
        });
    }

    setupFileUploads() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    const label = e.target.nextElementSibling;
                    if (label) {
                        label.textContent = `Selected: ${file.name}`;
                    }
                }
            });
        });

        // Drag and drop for target files
        const dropZone = document.getElementById('targetDropZone');
        if (dropZone) {
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('drag-over');
            });

            dropZone.addEventListener('dragleave', () => {
                dropZone.classList.remove('drag-over');
            });

            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.uploadTargetFile(files[0]);
                }
            });
        }
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    return false;
                }
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });

        return isValid;
    }

    showFieldError(field, message) {
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.textContent = message;
        } else {
            const error = document.createElement('div');
            error.className = 'field-error text-danger';
            error.textContent = message;
            field.parentNode.appendChild(error);
        }
        field.classList.add('is-invalid');
    }

    clearFieldError(field) {
        const error = field.parentNode.querySelector('.field-error');
        if (error) {
            error.remove();
        }
        field.classList.remove('is-invalid');
    }

    async startScan() {
        try {
            const targets = this.getTargets();
            const modules = this.getSelectedModules();

            if (!targets.length) {
                this.showAlert('Please provide at least one target', 'warning');
                return;
            }

            if (!modules.length) {
                this.showAlert('Please select at least one module', 'warning');
                return;
            }

            const response = await fetch('/api/scan/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    targets: targets,
                    modules: modules
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.scanInProgress = true;
                this.showAlert('Scan started successfully!', 'success');
                this.updateScanUI(true);
                this.startScanProgress();
            } else {
                this.showAlert(result.error || 'Failed to start scan', 'danger');
            }

        } catch (error) {
            this.showAlert('Error starting scan: ' + error.message, 'danger');
        }
    }

    async stopScan() {
        try {
            const response = await fetch('/api/scan/stop', {
                method: 'POST'
            });

            const result = await response.json();

            if (response.ok) {
                this.scanInProgress = false;
                this.showAlert('Scan stopped', 'info');
                this.updateScanUI(false);
                this.stopScanProgress();
            } else {
                this.showAlert(result.error || 'Failed to stop scan', 'danger');
            }

        } catch (error) {
            this.showAlert('Error stopping scan: ' + error.message, 'danger');
        }
    }

    getTargets() {
        const targetInput = document.getElementById('targets');
        const targetList = document.getElementById('targetList');
        
        let targets = [];
        
        if (targetInput && targetInput.value.trim()) {
            targets = targetInput.value.split('\n')
                .map(t => t.trim())
                .filter(t => t && !t.startsWith('#'));
        }
        
        if (targetList) {
            const listTargets = Array.from(targetList.children)
                .map(item => item.textContent.trim());
            targets = targets.concat(listTargets);
        }
        
        return [...new Set(targets)]; // Remove duplicates
    }

    getSelectedModules() {
        const checkboxes = document.querySelectorAll('input[name="modules"]:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    updateScanUI(scanning) {
        const startBtn = document.getElementById('startScan');
        const stopBtn = document.getElementById('stopScan');
        const progressContainer = document.getElementById('scanProgress');
        
        if (startBtn) {
            startBtn.disabled = scanning;
            startBtn.innerHTML = scanning ? 
                '<i class="fas fa-spinner fa-spin"></i> Scanning...' :
                '<i class="fas fa-play"></i> Start Scan';
        }
        
        if (stopBtn) {
            stopBtn.disabled = !scanning;
        }
        
        if (progressContainer) {
            progressContainer.style.display = scanning ? 'block' : 'none';
        }
    }

    startScanProgress() {
        this.updateInterval = setInterval(() => {
            this.updateScanStatus();
        }, 2000);
    }

    stopScanProgress() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    async updateScanStatus() {
        try {
            const response = await fetch('/api/scan/status');
            const status = await response.json();
            
            if (status.status === 'no_scan') {
                this.scanInProgress = false;
                this.updateScanUI(false);
                this.stopScanProgress();
                return;
            }
            
            // Update progress bar
            const progressBar = document.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = status.progress + '%';
                progressBar.textContent = Math.round(status.progress) + '%';
            }
            
            // Update status text
            const statusText = document.getElementById('scanStatusText');
            if (statusText) {
                statusText.textContent = `Status: ${status.status} | Progress: ${Math.round(status.progress)}%`;
            }
            
            if (status.finished) {
                this.scanInProgress = false;
                this.updateScanUI(false);
                this.stopScanProgress();
                this.showAlert('Scan completed!', 'success');
                
                // Refresh results if on results page
                if (window.location.pathname.includes('/results')) {
                    setTimeout(() => window.location.reload(), 1000);
                }
            }
            
        } catch (error) {
            console.error('Error updating scan status:', error);
        }
    }

    startStatsUpdates() {
        // Update stats every 10 seconds
        setInterval(() => {
            this.updateStats();
        }, 10000);
        
        // Initial update
        this.updateStats();
    }

    async updateStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            // Update dashboard stats
            this.updateStatCards(stats);
            this.updateCharts(stats);
            
        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }

    updateStatCards(stats) {
        const elements = {
            'totalFindings': stats.total_findings,
            'criticalFindings': stats.findings_by_severity.Critical || 0,
            'highFindings': stats.findings_by_severity.High || 0,
            'scanProgress': stats.scan_progress
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                this.animateCounter(element, parseInt(value) || 0);
            }
        });
    }

    updateCharts(stats) {
        // Update severity chart
        if (window.severityChart && stats.findings_by_severity) {
            const data = Object.values(stats.findings_by_severity);
            const labels = Object.keys(stats.findings_by_severity);
            
            window.severityChart.data.datasets[0].data = data;
            window.severityChart.data.labels = labels;
            window.severityChart.update();
        }
        
        // Update module chart
        if (window.moduleChart && stats.findings_by_module) {
            const data = Object.values(stats.findings_by_module);
            const labels = Object.keys(stats.findings_by_module);
            
            window.moduleChart.data.datasets[0].data = data;
            window.moduleChart.data.labels = labels;
            window.moduleChart.update();
        }
    }

    animateCounter(element, targetValue) {
        const currentValue = parseInt(element.textContent) || 0;
        const increment = Math.ceil((targetValue - currentValue) / 20);
        
        if (currentValue !== targetValue) {
            element.textContent = Math.min(currentValue + increment, targetValue);
            setTimeout(() => this.animateCounter(element, targetValue), 50);
        }
    }

    async uploadTargetFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/upload/targets', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showAlert(`Uploaded ${result.targets.length} targets`, 'success');
                this.displayTargets(result.targets);
            } else {
                this.showAlert(result.error || 'Upload failed', 'danger');
            }
            
        } catch (error) {
            this.showAlert('Error uploading file: ' + error.message, 'danger');
        }
    }

    displayTargets(targets) {
        const targetList = document.getElementById('targetList');
        if (targetList) {
            targetList.innerHTML = '';
            targets.forEach(target => {
                const item = document.createElement('div');
                item.className = 'target-item';
                item.innerHTML = `
                    <span>${target}</span>
                    <button type="button" class="btn btn-sm btn-danger" onclick="this.parentNode.remove()">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                targetList.appendChild(item);
            });
        }
    }

    async exportResults(format) {
        try {
            const response = await fetch(`/api/results/export/${format}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `spacecracker_results.${format}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showAlert(`Results exported as ${format.toUpperCase()}`, 'success');
            } else {
                const result = await response.json();
                this.showAlert(result.error || 'Export failed', 'danger');
            }
            
        } catch (error) {
            this.showAlert('Error exporting results: ' + error.message, 'danger');
        }
    }

    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alertContainer') || document.body;
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade-in`;
        alert.innerHTML = `
            <strong>${type.charAt(0).toUpperCase() + type.slice(1)}!</strong> ${message}
            <button type="button" class="btn-close" onclick="this.parentNode.remove()">×</button>
        `;
        
        alertContainer.appendChild(alert);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

// Initialize UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.spaceCrackerUI = new SpaceCrackerUI();
});

// Utility functions
function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('open');
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}