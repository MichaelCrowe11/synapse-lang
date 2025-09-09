// Synapse Language Website - Main JavaScript

// Animated counter for stats
function animateCounter() {
    const counters = document.querySelectorAll('.stat-number');
    const speed = 200;
    
    counters.forEach(counter => {
        const target = +counter.getAttribute('data-target');
        const increment = target / speed;
        
        const updateCount = () => {
            const count = +counter.innerText;
            
            if (count < target) {
                counter.innerText = Math.ceil(count + increment);
                setTimeout(updateCount, 1);
            } else {
                counter.innerText = target.toLocaleString();
            }
        };
        
        updateCount();
    });
}

// Observe stats section for animation trigger
const observerOptions = {
    threshold: 0.5,
    rootMargin: '0px'
};

const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateCounter();
            statsObserver.unobserve(entry.target);
        }
    });
}, observerOptions);

// Start observing when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const statsSection = document.querySelector('.stats');
    if (statsSection) {
        statsObserver.observe(statsSection);
    }
    
    // Initialize canvas animation
    initCanvasAnimation();
    
    // Smooth scroll for navigation links
    initSmoothScroll();
});

// Canvas neural network animation
function initCanvasAnimation() {
    const canvas = document.getElementById('synapseCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const particles = [];
    const connections = [];
    const particleCount = 50;
    
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.radius = Math.random() * 2 + 1;
        }
        
        update() {
            this.x += this.vx;
            this.y += this.vy;
            
            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
        }
        
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(147, 51, 234, 0.5)';
            ctx.fill();
        }
    }
    
    // Create particles
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
    
    // Animation loop
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Update and draw particles
        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });
        
        // Draw connections
        particles.forEach((p1, i) => {
            particles.slice(i + 1).forEach(p2 => {
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 150) {
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = `rgba(147, 51, 234, ${0.2 * (1 - distance / 150)})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            });
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
    
    // Resize handler
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

// Smooth scroll
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Modal functions
function showInstallModal() {
    document.getElementById('installModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeInstallModal() {
    document.getElementById('installModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show success feedback
        const button = event.target;
        const originalText = button.innerText;
        button.innerText = 'Copied!';
        button.style.background = '#10B981';
        
        setTimeout(() => {
            button.innerText = originalText;
            button.style.background = '';
        }, 2000);
    });
}

// Purchase functions
function downloadCommunity() {
    // Track download
    gtag('event', 'download', {
        'event_category': 'engagement',
        'event_label': 'community_edition'
    });
    
    // Redirect to PyPI
    window.open('https://pypi.org/project/synapse-lang/', '_blank');
}

function purchaseProfessional() {
    // Track conversion intent
    gtag('event', 'begin_checkout', {
        'value': 499,
        'currency': 'USD',
        'items': [{
            'name': 'Synapse Professional',
            'category': 'License',
            'quantity': 1,
            'price': 499
        }]
    });
    
    // Redirect to payment processor
    window.location.href = '/checkout.html?product=professional';
}

function contactSales() {
    // Track enterprise interest
    gtag('event', 'contact_sales', {
        'event_category': 'engagement',
        'event_label': 'enterprise'
    });
    
    // Open contact form
    window.location.href = '/contact.html?interest=enterprise';
}

// Navbar scroll effect
let lastScroll = 0;
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        navbar.style.background = 'rgba(10, 0, 20, 0.98)';
        navbar.style.boxShadow = '0 5px 20px rgba(0, 0, 0, 0.3)';
    } else {
        navbar.style.background = 'rgba(10, 0, 20, 0.95)';
        navbar.style.boxShadow = '';
    }
    
    lastScroll = currentScroll;
});

// Feature cards hover effect
document.querySelectorAll('.feature-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-10px) scale(1.02)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = '';
    });
});

// Typing animation for hero
function typeWriter(element, text, speed = 50) {
    let i = 0;
    element.innerHTML = '';
    
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

// Initialize typing effect on load
window.addEventListener('load', () => {
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        const text = heroTitle.innerText;
        typeWriter(heroTitle, text, 30);
    }
});

// Particle mouse interaction
document.addEventListener('mousemove', (e) => {
    const particles = document.querySelectorAll('.particle');
    const x = e.clientX;
    const y = e.clientY;
    
    particles.forEach(particle => {
        const rect = particle.getBoundingClientRect();
        const dx = rect.left - x;
        const dy = rect.top - y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < 100) {
            particle.style.transform = `translate(${dx * 0.1}px, ${dy * 0.1}px)`;
        }
    });
});

// Load animation for sections
const sections = document.querySelectorAll('section');
const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, {
    threshold: 0.1
});

sections.forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(30px)';
    section.style.transition = 'all 0.6s ease-out';
    sectionObserver.observe(section);
});

// Console Easter egg
console.log('%c🧬 Welcome to Synapse Language! 🧬', 
    'font-size: 20px; font-weight: bold; color: #9333EA; text-shadow: 2px 2px 4px rgba(147, 51, 234, 0.5);');
console.log('%cRevolutionizing scientific computing, one synapse at a time.', 
    'font-size: 14px; color: #EC4899;');
console.log('%cJoin us: https://github.com/synapse-lang/synapse', 
    'font-size: 12px; color: #C084FC;');