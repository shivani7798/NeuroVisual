/**
 * Visualization rendering engine
 * Renders audio-reactive visualizations on canvas based on parameters
 */

class VisualizationRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.animationId = null;
        this.params = this.getDefaultParams();
        this.time = 0;
        
        // Set canvas size
        this.resize();
        window.addEventListener('resize', () => this.resize());
    }
    
    resize() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
    }
    
    getDefaultParams() {
        return {
            color_hue: 200,
            color_saturation: 0.5,
            color_brightness: 0.7,
            pattern_complexity: 0.3,
            motion_speed: 0.4,
            pattern_size: 0.6,
            contrast: 0.4,
            flash_intensity: 0.0,
            rotation_speed: 0.2
        };
    }
    
    updateParams(newParams) {
        this.params = { ...this.params, ...newParams };
    }
    
    start() {
        if (!this.animationId) {
            this.animate();
        }
    }
    
    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }
    
    animate() {
        this.time += this.params.motion_speed * 0.02;
        this.render();
        this.animationId = requestAnimationFrame(() => this.animate());
    }
    
    render() {
        const { width, height } = this.canvas;
        const centerX = width / 2;
        const centerY = height / 2;
        
        // Clear with smooth background
        this.ctx.fillStyle = this.hslToRgb(
            this.params.color_hue,
            0.1,
            0.1 + this.params.flash_intensity * 0.2
        );
        this.ctx.fillRect(0, 0, width, height);
        
        // Draw calming patterns
        this.drawCalmingPatterns(centerX, centerY);
    }
    
    drawCalmingPatterns(centerX, centerY) {
        const { width, height } = this.canvas;
        const complexity = Math.floor(this.params.pattern_complexity * 20) + 3;
        const size = this.params.pattern_size * Math.min(width, height) / 3;
        const rotation = this.time * this.params.rotation_speed;
        
        // Draw multiple layers of patterns
        for (let layer = 0; layer < 3; layer++) {
            const layerSize = size * (1 - layer * 0.25);
            const layerAlpha = 0.3 - layer * 0.08;
            
            this.ctx.save();
            this.ctx.translate(centerX, centerY);
            this.ctx.rotate(rotation * (layer % 2 === 0 ? 1 : -1));
            
            // Draw circular patterns
            for (let i = 0; i < complexity; i++) {
                const angle = (i / complexity) * Math.PI * 2;
                const x = Math.cos(angle) * layerSize;
                const y = Math.sin(angle) * layerSize;
                
                // Gradient circles
                const gradient = this.ctx.createRadialGradient(x, y, 0, x, y, 30);
                
                const hue = (this.params.color_hue + i * 10) % 360;
                const color1 = this.hslToRgb(
                    hue,
                    this.params.color_saturation,
                    this.params.color_brightness,
                    layerAlpha
                );
                const color2 = this.hslToRgb(
                    hue,
                    this.params.color_saturation * 0.8,
                    this.params.color_brightness * 0.6,
                    0
                );
                
                gradient.addColorStop(0, color1);
                gradient.addColorStop(1, color2);
                
                this.ctx.fillStyle = gradient;
                this.ctx.beginPath();
                this.ctx.arc(x, y, 30, 0, Math.PI * 2);
                this.ctx.fill();
            }
            
            // Draw connecting lines for low contrast
            if (this.params.contrast > 0.2) {
                this.ctx.strokeStyle = this.hslToRgb(
                    this.params.color_hue,
                    this.params.color_saturation * 0.5,
                    this.params.color_brightness,
                    this.params.contrast * 0.3
                );
                this.ctx.lineWidth = 2;
                this.ctx.beginPath();
                
                for (let i = 0; i < complexity; i++) {
                    const angle = (i / complexity) * Math.PI * 2;
                    const x = Math.cos(angle) * layerSize;
                    const y = Math.sin(angle) * layerSize;
                    
                    if (i === 0) {
                        this.ctx.moveTo(x, y);
                    } else {
                        this.ctx.lineTo(x, y);
                    }
                }
                this.ctx.closePath();
                this.ctx.stroke();
            }
            
            this.ctx.restore();
        }
        
        // Draw center glow
        const centerGradient = this.ctx.createRadialGradient(
            centerX, centerY, 0,
            centerX, centerY, 100
        );
        centerGradient.addColorStop(0, this.hslToRgb(
            this.params.color_hue,
            this.params.color_saturation * 0.8,
            this.params.color_brightness * 1.2,
            0.4
        ));
        centerGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
        
        this.ctx.fillStyle = centerGradient;
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, 100, 0, Math.PI * 2);
        this.ctx.fill();
    }
    
    hslToRgb(h, s, l, a = 1) {
        h = h / 360;
        const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
        const p = 2 * l - q;
        
        const hue2rgb = (p, q, t) => {
            if (t < 0) t += 1;
            if (t > 1) t -= 1;
            if (t < 1/6) return p + (q - p) * 6 * t;
            if (t < 1/2) return q;
            if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
            return p;
        };
        
        const r = Math.round(hue2rgb(p, q, h + 1/3) * 255);
        const g = Math.round(hue2rgb(p, q, h) * 255);
        const b = Math.round(hue2rgb(p, q, h - 1/3) * 255);
        
        return `rgba(${r}, ${g}, ${b}, ${a})`;
    }
}
