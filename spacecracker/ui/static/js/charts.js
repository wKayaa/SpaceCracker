// Simple Chart Implementation for SpaceCracker
// Lightweight replacement for Chart.js to avoid external dependencies

class SimpleChart {
    constructor(ctx, config) {
        this.canvas = ctx;
        this.config = config;
        this.draw();
    }

    draw() {
        const canvas = this.canvas;
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        if (this.config.type === 'doughnut') {
            this.drawDoughnut(ctx, width, height);
        } else if (this.config.type === 'bar') {
            this.drawBar(ctx, width, height);
        }
    }
    
    drawDoughnut(ctx, width, height) {
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) / 3;
        const data = this.config.data.datasets[0].data;
        const labels = this.config.data.labels;
        const colors = this.config.data.datasets[0].backgroundColor;
        
        let total = data.reduce((sum, value) => sum + value, 0);
        if (total === 0) total = 1; // Avoid division by zero
        
        let currentAngle = -Math.PI / 2; // Start from top
        
        // Draw segments
        data.forEach((value, index) => {
            const sliceAngle = (value / total) * 2 * Math.PI;
            
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            ctx.arc(centerX, centerY, radius * 0.6, currentAngle + sliceAngle, currentAngle, true);
            ctx.closePath();
            ctx.fillStyle = colors[index];
            ctx.fill();
            
            currentAngle += sliceAngle;
        });
        
        // Draw center text
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Total', centerX, centerY - 5);
        ctx.fillText(data.reduce((sum, value) => sum + value, 0), centerX, centerY + 15);
    }
    
    drawBar(ctx, width, height) {
        const data = this.config.data.datasets[0].data;
        const labels = this.config.data.labels;
        const colors = this.config.data.datasets[0].backgroundColor;
        
        const margin = 40;
        const chartWidth = width - 2 * margin;
        const chartHeight = height - 2 * margin;
        
        const maxValue = Math.max(...data, 1);
        const barWidth = chartWidth / data.length * 0.8;
        const barSpacing = chartWidth / data.length * 0.2;
        
        data.forEach((value, index) => {
            const barHeight = (value / maxValue) * chartHeight;
            const x = margin + index * (barWidth + barSpacing);
            const y = height - margin - barHeight;
            
            ctx.fillStyle = colors[index];
            ctx.fillRect(x, y, barWidth, barHeight);
            
            // Draw label
            ctx.fillStyle = '#ffffff';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(labels[index], x + barWidth / 2, height - margin + 15);
            ctx.fillText(value, x + barWidth / 2, y - 5);
        });
    }
}

// Global Chart object to replace Chart.js
window.Chart = SimpleChart;