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
        this.loadModules();
    }

    async loadModules() {
        const modulesList = document.getElementById('modulesList');
        if (!modulesList) return;

        try {
            const response = await fetch('/api/modules');
            const data = await response.json();
            
            if (data.modules) {
                modulesList.innerHTML = this.renderModules(data.modules);
                this.setupModuleEventListeners();
            }
        } catch (error) {
            console.error('Error loading modules:', error);
            modulesList.innerHTML = '<p class="text-danger">Error loading modules</p>';
        }
    }

    renderModules(modules) {
        return modules.map(module => `
            <div class="form-group">
                <label class="module-option ${module.enabled ? 'enabled' : 'disabled'}">
                    <input type="checkbox" name="modules" value="${module.name}" 
                           class="form-check-input" ${module.enabled ? 'checked' : ''}>
                    <div class="module-info">
                        <div class="module-header">
                            <strong>${module.name}</strong>
                            <span class="badge badge-${this.getSeverityClass(module.severity)}">${module.severity}</span>
                        </div>
                        <small class="text-muted d-block">${module.description}</small>
                        <small class="text-info">${module.category}</small>
                    </div>
                </label>
            </div>
        `).join('');
    }

    getSeverityClass(severity) {
        const map = {
            'Critical': 'danger',
            'High': 'warning',
            'Medium': 'info',
            'Low': 'secondary'
        };
        return map[severity] || 'secondary';
    }

    setupModuleEventListeners() {
        const selectAllBtn = document.getElementById('selectAllModules');
        const selectNoneBtn = document.getElementById('selectNoneModules');
        
        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', () => {
                document.querySelectorAll('input[name="modules"]').forEach(cb => cb.checked = true);
            });
        }
        
        if (selectNoneBtn) {
            selectNoneBtn.addEventListener('click', () => {
                document.querySelectorAll('input[name="modules"]').forEach(cb => cb.checked = false);
            });
        }
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
            const options = this.getScanOptions();

            if (!targets.length) {
                this.showAlert('Please provide at least one target', 'warning');
                return;
            }

            if (!modules.length) {
                this.showAlert('Please select at least one module', 'warning');
                return;
            }

            // Use CLI backend for better performance
            const response = await fetch('/api/cli/scan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    targets: targets,
                    options: {
                        modules: modules,
                        ...options
                    }
                })
            });

            const result = await response.json();

            if (result.success) {
                this.scanInProgress = true;
                this.showAlert(`Scan started successfully! Scan ID: ${result.scan_id}`, 'success');
                this.updateScanUI(true);
                this.startScanProgress();
                
                // Store scan ID for status tracking
                this.currentScanId = result.scan_id;
                
                // Show CLI command for reference
                if (result.command) {
                    console.log('CLI Command:', result.command);
                }
            } else {
                this.showAlert(result.error || 'Failed to start scan', 'danger');
            }

        } catch (error) {
            this.showAlert('Error starting scan: ' + error.message, 'danger');
        }
    }

    getScanOptions() {
        const form = document.getElementById('scanForm');
        if (!form) return {};

        return {
            threads: parseInt(form.querySelector('input[name="threads"]')?.value || 50),
            timeout: parseInt(form.querySelector('input[name="timeout"]')?.value || 30),
            rate_limit: parseFloat(form.querySelector('input[name="rate_limit"]')?.value || 10),
            recursive: form.querySelector('input[name="recursive"]')?.checked || false,
            auto_exploit: form.querySelector('input[name="auto_exploit"]')?.checked || false
        };
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

// New enhanced functions
function showAnalytics() {
    // Show analytics modal or navigate to analytics page
    window.spaceCrackerUI.showAlert('Analytics feature coming soon!', 'info');
}

function showDownloads() {
    // Show downloads modal
    window.spaceCrackerUI.showAlert('Downloads feature available in Results page', 'info');
}

// Enhanced CLI integration functions
async function startCliScan(targets, options = {}) {
    try {
        const response = await fetch('/api/cli/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                targets: targets,
                options: options
            })
        });
        
        const result = await response.json();
        if (result.success) {
            window.spaceCrackerUI.showAlert('Scan started successfully!', 'success');
            return result.scan_id;
        } else {
            throw new Error(result.error || 'Unknown error');
        }
    } catch (error) {
        window.spaceCrackerUI.showAlert('Error starting scan: ' + error.message, 'danger');
        throw error;
    }
}

// Enhanced theme and visual effects
function initializeVisualEffects() {
    // Add particle background effect
    createParticleBackground();
    
    // Add smooth scrolling
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Add intersection observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe all cards and main elements
    document.querySelectorAll('.card, .stats-grid > div').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });
}

function createParticleBackground() {
    const canvas = document.createElement('canvas');
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '-1';
    canvas.style.opacity = '0.1';
    document.body.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const particles = [];
    const particleCount = 50;
    
    for (let i = 0; i < particleCount; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            size: Math.random() * 2 + 1
        });
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'rgba(195, 7, 63, 0.5)';
        
        particles.forEach(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
            if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;
            
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            ctx.fill();
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
    
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

// Initialize visual effects when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initializeVisualEffects, 100);
});