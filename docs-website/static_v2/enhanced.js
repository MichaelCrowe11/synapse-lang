// Synapse Advanced Enhancement System
// Cutting-edge interactions and visualizations

class SynapseEnhancer {
    constructor() {
        this.init();
        this.particles = [];
        this.connections = [];
        this.mousePosition = { x: 0, y: 0 };
    }

    init() {
        // Initialize canvas for particle system
        this.createParticleCanvas();
        
        // Advanced scroll effects
        this.initScrollEffects();
        
        // Interactive code blocks
        this.enhanceCodeBlocks();
        
        // Dynamic data visualization
        this.initDataViz();
        
        // Gesture recognition
        this.initGestures();
        
        // Performance monitoring
        this.initPerformanceMonitor();
        
        // Start animation loop
        this.animate();
    }

    createParticleCanvas() {
        const canvas = document.createElement('canvas');
        canvas.id = 'particle-canvas';
        canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
            opacity: 0.3;
        `;
        document.body.appendChild(canvas);
        
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.resize();
        
        // Create quantum particles
        for (let i = 0; i < 50; i++) {
            this.particles.push({
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                radius: Math.random() * 2 + 1,
                phase: Math.random() * Math.PI * 2,
                frequency: Math.random() * 0.02 + 0.01
            });
        }
        
        window.addEventListener('resize', () => this.resize());
        window.addEventListener('mousemove', (e) => {
            this.mousePosition = { x: e.clientX, y: e.clientY };
        });
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Update particles
        this.particles.forEach(particle => {
            // Quantum behavior
            particle.x += particle.vx + Math.sin(particle.phase) * 0.5;
            particle.y += particle.vy + Math.cos(particle.phase) * 0.5;
            particle.phase += particle.frequency;
            
            // Wrap around screen
            if (particle.x < 0) particle.x = this.canvas.width;
            if (particle.x > this.canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = this.canvas.height;
            if (particle.y > this.canvas.height) particle.y = 0;
            
            // Mouse interaction
            const dx = this.mousePosition.x - particle.x;
            const dy = this.mousePosition.y - particle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < 100) {
                particle.vx -= dx * 0.0001;
                particle.vy -= dy * 0.0001;
            }
        });
        
        // Draw connections
        this.ctx.strokeStyle = 'rgba(91, 71, 224, 0.1)';
        this.ctx.lineWidth = 1;
        
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 150) {
                    this.ctx.globalAlpha = 1 - distance / 150;
                    this.ctx.beginPath();
                    this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                    this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                    this.ctx.stroke();
                }
            }
        }
        
        // Draw particles
        this.ctx.globalAlpha = 1;
        this.ctx.fillStyle = '#5B47E0';
        
        this.particles.forEach(particle => {
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
            this.ctx.fill();
        });
    }

    initScrollEffects() {
        // Parallax scrolling
        const elements = document.querySelectorAll('[data-parallax]');
        
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            
            elements.forEach(element => {
                const speed = element.dataset.parallax || 0.5;
                element.style.transform = `translateY(${scrolled * speed}px)`;
            });
            
            // Reveal animations
            document.querySelectorAll('.reveal-on-scroll').forEach(element => {
                const rect = element.getBoundingClientRect();
                if (rect.top < window.innerHeight && rect.bottom > 0) {
                    element.classList.add('revealed');
                }
            });
        });
    }

    enhanceCodeBlocks() {
        document.querySelectorAll('pre code').forEach(block => {
            // Add line numbers
            const lines = block.textContent.split('\n');
            const numbered = lines.map((line, i) => 
                `<span class="line-number">${i + 1}</span>${line}`
            ).join('\n');
            
            block.innerHTML = numbered;
            
            // Add copy button with animation
            const copyBtn = document.createElement('button');
            copyBtn.className = 'code-copy-btn';
            copyBtn.innerHTML = 'COPY';
            
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(block.textContent);
                copyBtn.innerHTML = 'COPIED';
                copyBtn.classList.add('success');
                
                setTimeout(() => {
                    copyBtn.innerHTML = 'COPY';
                    copyBtn.classList.remove('success');
                }, 2000);
            };
            
            block.parentElement.style.position = 'relative';
            block.parentElement.appendChild(copyBtn);
        });
    }

    initDataViz() {
        // Create live data visualization for metrics
        const metricsElement = document.querySelector('.metrics-live');
        if (!metricsElement) return;
        
        const data = [];
        const maxPoints = 50;
        
        // Generate random data stream
        setInterval(() => {
            data.push({
                time: Date.now(),
                value: Math.random() * 100 + 50,
                quantum: Math.sin(Date.now() * 0.001) * 30 + 70
            });
            
            if (data.length > maxPoints) {
                data.shift();
            }
            
            this.renderChart(metricsElement, data);
        }, 500);
    }

    renderChart(container, data) {
        if (!container) return;
        
        container.innerHTML = '';
        
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '200');
        
        const width = container.offsetWidth;
        const height = 200;
        
        // Create path
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        
        const points = data.map((d, i) => {
            const x = (i / (data.length - 1)) * width;
            const y = height - (d.value / 150) * height;
            return `${x},${y}`;
        });
        
        path.setAttribute('d', `M ${points.join(' L ')}`);
        path.setAttribute('stroke', '#5B47E0');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('fill', 'none');
        
        // Add glow effect
        const filter = document.createElementNS('http://www.w3.org/2000/svg', 'filter');
        filter.id = 'glow';
        
        const feGaussianBlur = document.createElementNS('http://www.w3.org/2000/svg', 'feGaussianBlur');
        feGaussianBlur.setAttribute('stdDeviation', '4');
        filter.appendChild(feGaussianBlur);
        
        svg.appendChild(filter);
        path.style.filter = 'url(#glow)';
        
        svg.appendChild(path);
        container.appendChild(svg);
    }

    initGestures() {
        let touchStartX = 0;
        let touchStartY = 0;
        
        document.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        });
        
        document.addEventListener('touchend', (e) => {
            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;
            
            const dx = touchEndX - touchStartX;
            const dy = touchEndY - touchStartY;
            
            // Swipe detection
            if (Math.abs(dx) > 50) {
                if (dx > 0) {
                    this.onSwipeRight();
                } else {
                    this.onSwipeLeft();
                }
            }
            
            if (Math.abs(dy) > 50) {
                if (dy > 0) {
                    this.onSwipeDown();
                } else {
                    this.onSwipeUp();
                }
            }
        });
    }

    onSwipeLeft() {
        // Navigate to next section
        const sections = document.querySelectorAll('section');
        const current = document.querySelector('section.active') || sections[0];
        const next = current.nextElementSibling;
        
        if (next && next.tagName === 'SECTION') {
            next.scrollIntoView({ behavior: 'smooth' });
            sections.forEach(s => s.classList.remove('active'));
            next.classList.add('active');
        }
    }

    onSwipeRight() {
        // Navigate to previous section
        const sections = document.querySelectorAll('section');
        const current = document.querySelector('section.active') || sections[0];
        const prev = current.previousElementSibling;
        
        if (prev && prev.tagName === 'SECTION') {
            prev.scrollIntoView({ behavior: 'smooth' });
            sections.forEach(s => s.classList.remove('active'));
            prev.classList.add('active');
        }
    }

    onSwipeUp() {
        // Trigger command palette
        this.showCommandPalette();
    }

    onSwipeDown() {
        // Show quick actions
        this.showQuickActions();
    }

    showCommandPalette() {
        const palette = document.createElement('div');
        palette.className = 'command-palette';
        palette.innerHTML = `
            <input type="text" placeholder="Type a command..." autofocus>
            <div class="commands">
                <div class="command" data-action="playground">Open Playground</div>
                <div class="command" data-action="docs">View Documentation</div>
                <div class="command" data-action="dashboard">Analytics Dashboard</div>
                <div class="command" data-action="theme">Toggle Theme</div>
            </div>
        `;
        
        document.body.appendChild(palette);
        
        const input = palette.querySelector('input');
        input.focus();
        
        input.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            palette.querySelectorAll('.command').forEach(cmd => {
                const text = cmd.textContent.toLowerCase();
                cmd.style.display = text.includes(query) ? 'block' : 'none';
            });
        });
        
        palette.addEventListener('click', (e) => {
            if (e.target.classList.contains('command')) {
                const action = e.target.dataset.action;
                this.executeCommand(action);
                document.body.removeChild(palette);
            }
        });
        
        // Close on escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && document.body.contains(palette)) {
                document.body.removeChild(palette);
            }
        });
    }

    executeCommand(action) {
        switch(action) {
            case 'playground':
                window.location.href = '/playground';
                break;
            case 'docs':
                window.location.href = '/docs';
                break;
            case 'dashboard':
                window.location.href = '/dashboard';
                break;
            case 'theme':
                document.body.dataset.theme = 
                    document.body.dataset.theme === 'dark' ? 'light' : 'dark';
                break;
        }
    }

    showQuickActions() {
        const actions = document.createElement('div');
        actions.className = 'quick-actions';
        actions.innerHTML = `
            <button class="quick-action" data-action="copy-install">
                Copy Install Command
            </button>
            <button class="quick-action" data-action="star-github">
                Star on GitHub
            </button>
            <button class="quick-action" data-action="share">
                Share
            </button>
        `;
        
        document.body.appendChild(actions);
        
        setTimeout(() => {
            actions.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            actions.classList.remove('show');
            setTimeout(() => {
                if (document.body.contains(actions)) {
                    document.body.removeChild(actions);
                }
            }, 300);
        }, 3000);
    }

    initPerformanceMonitor() {
        const monitor = document.createElement('div');
        monitor.className = 'performance-monitor';
        monitor.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.8);
            color: #00FF00;
            font-family: monospace;
            font-size: 10px;
            padding: 10px;
            border-radius: 4px;
            z-index: 10000;
            display: none;
        `;
        
        document.body.appendChild(monitor);
        
        // Toggle with Ctrl+Shift+P
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'P') {
                monitor.style.display = 
                    monitor.style.display === 'none' ? 'block' : 'none';
            }
        });
        
        // Update metrics
        setInterval(() => {
            if (monitor.style.display === 'none') return;
            
            const memory = performance.memory ? 
                `Memory: ${Math.round(performance.memory.usedJSHeapSize / 1048576)}MB` : '';
            
            const fps = this.calculateFPS();
            
            monitor.innerHTML = `
                FPS: ${fps}<br>
                Particles: ${this.particles.length}<br>
                ${memory}<br>
                DOM Nodes: ${document.querySelectorAll('*').length}
            `;
        }, 100);
    }

    calculateFPS() {
        const now = performance.now();
        if (!this.lastFrame) {
            this.lastFrame = now;
            return 60;
        }
        
        const delta = now - this.lastFrame;
        this.lastFrame = now;
        
        return Math.round(1000 / delta);
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.synapseEnhancer = new SynapseEnhancer();
    });
} else {
    window.synapseEnhancer = new SynapseEnhancer();
}
