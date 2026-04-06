/**
 * Ігрофікс ПК - Main JavaScript v2.0
 * Головний файл JavaScript з sound effects та анімаціями
 */

// ============================================
// Глобальні змінні та стан
// ============================================

let cartCount = parseInt(sessionStorage.getItem('cartCount')) || 0;
let audioContext = null;
let soundEnabled = false;

const sounds = {
    hover: null,
    click: null,
    lightning: null,
    success: null,
    error: null
};

// ============================================
// Ініціалізація при завантаженні + Premium Features
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    initNavbar();
    initEffects();
    initParticles();
    initAnimations();
    updateCartBadge();
    initFlashMessages();
    initCustomCursor();
    initParallax();
    initLazyLoading();
    initThemeToggle();
    initStaggerLoad();
    initLanguageToggle();
});

// ============================================
// Audio System
// ============================================

function initAudio() {
    // Створюємо AudioContext при першій взаємодії користувача
    document.addEventListener('click', function initAudioContext() {
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        
        // Генеруємо синтетичні звуки
        generateSounds();
        
        // Видаляємо цей listener після ініціалізації
        document.removeEventListener('click', initAudioContext);
    }, { once: true });
}

function generateSounds() {
    if (!audioContext) return;
    
    // Звук наведення (короткий блиск)
    sounds.hover = createLightningSound(0.08, 800, 0.1);
    
    // Звук кліку (середній блиск)
    sounds.click = createLightningSound(0.15, 600, 0.2);
    
    // Звук блискавки (великий)
    sounds.lightning = createLightningSound(0.3, 400, 0.5);
    
    // Звук успіху
    sounds.success = createSuccessSound();
    
    // Звук помилки
    sounds.error = createErrorSound();
}

function createLightningSound(volume, frequency, duration) {
    return function() {
        if (!audioContext || !soundEnabled) return;
        
        try {
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            const filter = audioContext.createBiquadFilter();
            
            // Налаштування осцилятора
            oscillator.type = 'sawtooth';
            oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(frequency * 2, audioContext.currentTime + duration * 0.1);
            oscillator.frequency.exponentialRampToValueAtTime(frequency * 0.5, audioContext.currentTime + duration);
            
            // Фільтр для більш "електричного" звуку
            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(2000, audioContext.currentTime);
            filter.frequency.exponentialRampToValueAtTime(500, audioContext.currentTime + duration);
            
            // Гучність
            gainNode.gain.setValueAtTime(0, audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(volume, audioContext.currentTime + 0.01);
            gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + duration);
            
            // З'єднання
            oscillator.connect(filter);
            filter.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            // Запуск та зупинка
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + duration);
        } catch (e) {
            console.log('Audio error:', e);
        }
    };
}

function createSuccessSound() {
    return function() {
        if (!audioContext || !soundEnabled) return;
        
        try {
            const notes = [523.25, 659.25, 783.99]; // C5, E5, G5
            
            notes.forEach((freq, i) => {
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.type = 'sine';
                oscillator.frequency.value = freq;
                
                gainNode.gain.setValueAtTime(0, audioContext.currentTime + i * 0.1);
                gainNode.gain.linearRampToValueAtTime(0.15, audioContext.currentTime + i * 0.1 + 0.05);
                gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + i * 0.1 + 0.3);
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.start(audioContext.currentTime + i * 0.1);
                oscillator.stop(audioContext.currentTime + i * 0.1 + 0.3);
            });
        } catch (e) {
            console.log('Audio error:', e);
        }
    };
}

function createErrorSound() {
    return function() {
        if (!audioContext || !soundEnabled) return;
        
        try {
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.type = 'square';
            oscillator.frequency.setValueAtTime(200, audioContext.currentTime);
            oscillator.frequency.linearRampToValueAtTime(100, audioContext.currentTime + 0.2);
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.2);
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.2);
        } catch (e) {
            console.log('Audio error:', e);
        }
    };
}

// ============================================
// Кастомний курсор
// ============================================

function initCustomCursor() {
    // Створюємо елемент курсора
    const cursor = document.createElement('div');
    cursor.className = 'custom-cursor';
    document.body.appendChild(cursor);
    
    // Відстежуємо рух миші
    document.addEventListener('mousemove', function(e) {
        cursor.style.left = e.clientX - 10 + 'px';
        cursor.style.top = e.clientY - 10 + 'px';
    });
    
    // Змінюємо курсор при наведенні на інтерактивні елементи
    const interactiveElements = document.querySelectorAll('a, button, .btn, .card, .product-card, .category-card, input, select');
    
    interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', function() {
            cursor.classList.add('hover');
        });
        
        el.addEventListener('mouseleave', function() {
            cursor.classList.remove('hover');
        });
    });
}

function playSound(soundName) {
    if (sounds[soundName]) {
        sounds[soundName]();
    }
}

// ============================================
// Навігація
// ============================================

function initNavbar() {
    const navbar = document.getElementById('navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// ============================================
// Ефекти
// ============================================

function initEffects() {
    // Блискавка при натисканні на кнопки
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            triggerLightningEffect(e.clientX, e.clientY);
            playSound('click');
        });
    });
    
    // Ефект для карток товарів
    document.querySelectorAll('.product-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            // Hover ефект без звуку
        });
    });
    
    // Магнітний ефект для карток
    document.querySelectorAll('.card-hover-glow').forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = card.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;
            card.style.setProperty('--mouse-x', x + '%');
            card.style.setProperty('--mouse-y', y + '%');
        });
    });
}

function triggerLightningEffect(x, y) {
    const overlay = document.getElementById('lightningOverlay');
    if (overlay) {
        overlay.style.setProperty('--x', x + 'px');
        overlay.style.setProperty('--y', y + 'px');
        
        // Додаємо кілька спалахів для більш реалістичного ефекту
        setTimeout(() => {
            overlay.classList.add('active');
            setTimeout(() => overlay.classList.remove('active'), 200);
        }, 0);
        
        setTimeout(() => {
            overlay.classList.add('active');
            setTimeout(() => overlay.classList.remove('active'), 150);
        }, 100);
    }
}

// Глобальна функція для тригера блискавки
window.triggerLightning = function(x, y) {
    triggerLightningEffect(x, y);
    playSound('lightning');
};

// ============================================
// Частинки на фоні
// ============================================

function initParticles() {
    const container = document.getElementById('particlesContainer');
    if (!container) return;
    
    for (let i = 0; i < 30; i++) {
        createParticle(container);
    }
}

function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    particle.style.left = Math.random() * 100 + '%';
    particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
    particle.style.animationDelay = Math.random() * 10 + 's';
    particle.style.opacity = Math.random() * 0.5 + 0.2;
    particle.style.width = (Math.random() * 4 + 2) + 'px';
    particle.style.height = particle.style.width;
    
    // Випадковий колір
    const colors = ['var(--primary)', 'var(--secondary)', 'var(--accent)'];
    particle.style.background = colors[Math.floor(Math.random() * colors.length)];
    particle.style.boxShadow = `0 0 10px ${particle.style.background}`;
    
    container.appendChild(particle);
    
    particle.addEventListener('animationend', function() {
        particle.remove();
        createParticle(container);
    });
}

// ============================================
// Анімації при скролі
// ============================================

function initAnimations() {
    const reveals = document.querySelectorAll('.reveal');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });
    
    reveals.forEach(el => observer.observe(el));
    
    // Stagger-анімація для сіток
    const staggerContainers = document.querySelectorAll('[data-stagger]');
    staggerContainers.forEach(container => {
        const children = container.children;
        Array.from(children).forEach((child, index) => {
            child.style.animationDelay = (index * 0.1) + 's';
            child.classList.add('fade-in');
        });
    });
}

// ============================================
// Flash-повідомлення
// ============================================

function initFlashMessages() {
    const messages = document.querySelectorAll('.flash-message');
    
    messages.forEach((msg, index) => {
        setTimeout(() => {
            msg.style.animation = 'slideIn 0.3s ease-out';
        }, index * 100);
        
        setTimeout(() => {
            msg.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(() => msg.remove(), 300);
        }, 5000);
    });
}

// ============================================
// Функції кошика
// ============================================

function addToCart(productId, buttonElement) {
    if (!buttonElement) return;
    const originalText = buttonElement.innerHTML;
    buttonElement.innerHTML = '<span class="spinner"></span>';
    buttonElement.disabled = true;

    flyToCart(buttonElement);

    fetch('/api/cart/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cartCount = data.cart_count;
            updateCartBadge();
            
            // Успішна анімація
            buttonElement.innerHTML = '<span>✓</span> Додано!';
            buttonElement.classList.add('btn-success', 'added');
            buttonElement.classList.remove('btn-primary');
            
            // Ефект блискавки
            const rect = buttonElement.getBoundingClientRect();
            triggerLightningEffect(rect.left + rect.width / 2, rect.top + rect.height / 2);
            playSound('success');
            
            showToast('Товар додано до кошика!', 'success');
            
            // Анімація кошика в навбарі
            const cartBtn = document.getElementById('cartBtn');
            if (cartBtn) {
                cartBtn.style.animation = 'cart-bounce 0.5s ease';
                setTimeout(() => cartBtn.style.animation = '', 500);
            }
            
            setTimeout(() => {
                buttonElement.innerHTML = '<span>🛒</span> В кошик';
                buttonElement.classList.remove('btn-success', 'added');
                buttonElement.classList.add('btn-primary');
                buttonElement.disabled = false;
            }, 1500);
        } else {
            throw new Error(data.message || 'Помилка');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        buttonElement.innerHTML = originalText;
        buttonElement.disabled = false;
        showToast('Помилка додавання товару', 'danger');
        playSound('error');
    });
}

function updateCartQuantity(productId, quantity) {
    fetch('/api/cart/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (quantity <= 0) {
                const item = document.querySelector(`.cart-item[data-product-id="${productId}"]`);
                if (item) {
                    item.style.animation = 'slideOut 0.3s ease-out forwards';
                    setTimeout(() => item.remove(), 300);
                }
            }
            
            cartCount = data.cart_count;
            updateCartBadge();
            updateCartTotal(data.total);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Помилка оновлення', 'danger');
    });
}

function removeFromCart(productId) {
    if (!confirm('Видалити товар з кошика?')) return;
    
    fetch('/api/cart/remove', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const item = document.querySelector(`.cart-item[data-product-id="${productId}"]`);
            if (item) {
                item.style.animation = 'slideOut 0.3s ease-out forwards';
                setTimeout(() => {
                    item.remove();
                    if (document.querySelectorAll('.cart-item').length === 0) {
                        location.reload();
                    }
                }, 300);
            }
            
            cartCount = data.cart_count;
            updateCartBadge();
            showToast('Товар видалено', 'info');
            playSound('click');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Помилка видалення', 'danger');
    });
}

function clearCart() {
    if (!confirm('Очистити весь кошик?')) return;
    
    fetch('/api/cart/clear', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Помилка', 'danger');
    });
}

function updateCartBadge() {
    const badge = document.getElementById('cartBadge');
    if (badge) {
        if (cartCount > 0) {
            badge.textContent = cartCount;
            badge.style.display = 'flex';
            badge.style.animation = 'badge-pop 0.3s ease';
        } else {
            badge.style.display = 'none';
        }
    }
    sessionStorage.setItem('cartCount', cartCount);
}

function updateCartTotal(total) {
    const totalElement = document.getElementById('cartTotal');
    if (totalElement) {
        totalElement.textContent = formatPrice(total);
    }
}

// ============================================
// Toast-повідомлення
// ============================================

function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        background: var(--card-bg);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        box-shadow: var(--shadow-lg);
        animation: slideIn 0.3s ease-out;
        min-width: 250px;
    `;
    
    const icons = {
        success: '✅',
        danger: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    const colors = {
        success: 'var(--success)',
        danger: 'var(--danger)',
        warning: 'var(--warning)',
        info: 'var(--info)'
    };
    
    toast.innerHTML = `
        <span style="font-size: 1.25rem;">${icons[type] || icons.info}</span>
        <span style="color: ${colors[type] || colors.info};">${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Блискавка при toast
    const rect = toast.getBoundingClientRect();
    triggerLightningEffect(rect.left + rect.width / 2, rect.top);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================
// Паралакс при скролі
// ============================================

function initParallax() {
    const parallaxElements = document.querySelectorAll('.hero-image, .bg-gradient, .grid-lightning');
    const heroContent = document.querySelector('.hero-content');
    const sections = document.querySelectorAll('.section');

    window.addEventListener('scroll', function() {
        const scrollY = window.scrollY;

        parallaxElements.forEach(el => {
            const speed = el.classList.contains('hero-image') ? 0.4 : 0.15;
            el.style.transform = el.classList.contains('hero-image')
                ? `translateY(calc(-50% + ${scrollY * speed}px))`
                : `translateY(${scrollY * speed}px)`;
        });

        if (heroContent) {
            heroContent.style.transform = `translateY(${scrollY * 0.2}px)`;
            heroContent.style.opacity = Math.max(0, 1 - scrollY / 600);
        }

        sections.forEach(section => {
            const rect = section.getBoundingClientRect();
            const centerY = rect.top + rect.height / 2;
            const windowCenter = window.innerHeight / 2;
            const offset = (centerY - windowCenter) * 0.03;
            const children = section.querySelectorAll('.section-header');
            children.forEach(child => {
                child.style.transform = `translateY(${offset}px)`;
            });
        });
    });
}

// ============================================
// Lazy Loading зображень
// ============================================

function initLazyLoading() {
    const lazyImages = document.querySelectorAll('img[data-src], svg');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    if (el.tagName === 'IMG' && el.dataset.src) {
                        el.src = el.dataset.src;
                        el.removeAttribute('data-src');
                        el.classList.add('lazy-loaded');
                    }
                    if (el.tagName === 'svg' || el.closest('.card-img')) {
                        el.classList.add('lazy-loaded');
                    }
                    imageObserver.unobserve(el);
                }
            });
        }, { rootMargin: '200px' });

        lazyImages.forEach(img => imageObserver.observe(img));

        document.querySelectorAll('.card-img').forEach(el => imageObserver.observe(el));
    }
}

// ============================================
// Fly-to-Cart анімація
// ============================================

function flyToCart(buttonElement) {
    const cartBtn = document.getElementById('cartBtn');
    if (!cartBtn || !buttonElement) return;

    const card = buttonElement.closest('.product-card') || buttonElement.closest('.card');
    const sourceEl = card ? (card.querySelector('.card-img') || card) : buttonElement;

    const sourceRect = sourceEl.getBoundingClientRect();
    const cartRect = cartBtn.getBoundingClientRect();

    // Main cart fly animation
    const flyEl = document.createElement('div');
    flyEl.className = 'fly-to-cart';
    flyEl.style.cssText = `
        position: fixed;
        z-index: 10000;
        pointer-events: none;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: var(--gradient-1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        box-shadow: 0 0 20px rgba(108, 92, 231, 0.8);
        left: ${sourceRect.left + sourceRect.width / 2 - 30}px;
        top: ${sourceRect.top + sourceRect.height / 2 - 30}px;
        opacity: 1;
        transform: scale(1);
    `;
    flyEl.innerHTML = '<span style="filter: brightness(2);">🛒</span>';
    document.body.appendChild(flyEl);

    requestAnimationFrame(() => {
        flyEl.style.transition = 'all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
        flyEl.style.left = `${cartRect.left + cartRect.width / 2 - 15}px`;
        flyEl.style.top = `${cartRect.top + cartRect.height / 2 - 15}px`;
        flyEl.style.width = '30px';
        flyEl.style.height = '30px';
        flyEl.style.opacity = '0.3';
        flyEl.style.transform = 'scale(0.3)';
    });

    setTimeout(() => {
        flyEl.remove();
        cartBtn.style.animation = 'cart-bounce 0.5s ease';
        setTimeout(() => cartBtn.style.animation = '', 500);
        
        // PREMIUM: Cart particles explosion
        cartParticles(cartRect.left + cartRect.width / 2, cartRect.top + cartRect.height / 2);
    }, 850);
}

// ============================================
// PREMIUM FEATURES
// ============================================

// 1. Dark/Light Theme Toggle
function initThemeToggle() {
    const toggleBtn = document.getElementById('themeToggle');
    if (!toggleBtn) return;
    
    const html = document.documentElement;
    const currentTheme = localStorage.getItem('theme') || 'dark';
    
    // Apply saved theme (optimized - no lag)
    html.setAttribute('theme', currentTheme);
    const icon = toggleBtn.querySelector('.theme-icon');
    icon.textContent = currentTheme === 'dark' ? '☀️' : '🌙';
    
    // Debounced toggle for unlimited switches
    let toggleTimeout;
    toggleBtn.addEventListener('click', () => {
        clearTimeout(toggleTimeout);
        toggleTimeout = setTimeout(() => {
            const newTheme = html.getAttribute('theme') === 'dark' ? 'light' : 'dark';
            html.setAttribute('theme', newTheme);
            localStorage.setItem('theme', newTheme);
            icon.textContent = newTheme === 'dark' ? '☀️' : '🌙';
            triggerLightningEffect(toggleBtn.getBoundingClientRect().left + 20, toggleBtn.getBoundingClientRect().top + 20);
            playSound('click');
        }, 50); // 50ms debounce - super smooth
    });
}

// 2. Cart Particles Explosion
function cartParticles(x, y) {
    const canvas = document.createElement('canvas');
    canvas.width = 400;
    canvas.height = 400;
    canvas.style.cssText = 'position: fixed; left: ' + (x - 200) + 'px; top: ' + (y - 200) + 'px; z-index: 10001; pointer-events: none;';
    canvas.style.background = 'transparent';
    document.body.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    const particles = [];
    
    // Create 30 particles
    for (let i = 0; i < 30; i++) {
        particles.push({
            x: 200,
            y: 200,
            vx: (Math.random() - 0.5) * 10,
            vy: (Math.random() - 0.5) * 10,
            size: Math.random() * 4 + 2,
            color: ['#6c5ce7', '#00cec9', '#fd79a8'][Math.floor(Math.random() * 3)],
            life: 1
        });
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.1; // gravity
            p.life -= 0.02;
            
            ctx.save();
            ctx.globalAlpha = p.life;
            ctx.fillStyle = p.color;
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 10;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        });
        
        if (particles.some(p => p.life > 0)) {
            requestAnimationFrame(animate);
        } else {
            canvas.remove();
        }
    }
    
    animate();
    playSound('lightning');
}

// 3. Order Success Fireworks
window.orderFireworks = function() {
    const canvas = document.createElement('canvas');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    canvas.style.cssText = 'position: fixed; top: 0; left: 0; z-index: 10001; pointer-events: none;';
    document.body.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    const fireworks = [];
    
    // Create 5 fireworks rockets
    for (let i = 0; i < 5; i++) {
        fireworks.push({
            x: Math.random() * canvas.width,
            y: canvas.height,
            vy: -Math.random() * 15 - 10,
            exploded: false,
            particles: []
        });
    }
    
    function animate() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        fireworks.forEach(fw => {
            if (!fw.exploded) {
                fw.y += fw.vy;
                fw.vy += 0.1;
                
                // Rocket trail
                ctx.fillStyle = '#6c5ce7';
                ctx.shadowColor = '#6c5ce7';
                ctx.shadowBlur = 15;
                ctx.beginPath();
                ctx.arc(fw.x, fw.y, 3, 0, Math.PI * 2);
                ctx.fill();
                
                if (fw.y < canvas.height * 0.3) {
                    fw.exploded = true;
                    // Create explosion particles
                    for (let j = 0; j < 50; j++) {
                        fw.particles.push({
                            x: fw.x,
                            y: fw.y,
                            vx: (Math.random() - 0.5) * 12,
                            vy: (Math.random() - 0.5) * 12,
                            size: Math.random() * 3 + 1,
                            color: ['#6c5ce7', '#00cec9', '#fd79a8', '#fdcb6e', '#00b894'][Math.floor(Math.random() * 5)],
                            life: 1
                        });
                    }
                }
            }
            
            // Animate particles
            fw.particles.forEach(p => {
                p.x += p.vx;
                p.y += p.vy;
                p.vy += 0.05;
                p.life -= 0.015;
                
                ctx.save();
                ctx.globalAlpha = p.life;
                ctx.fillStyle = p.color;
                ctx.shadowColor = p.color;
                ctx.shadowBlur = 20;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            });
            
            // Remove dead particles
            fw.particles = fw.particles.filter(p => p.life > 0);
        });
        
        if (fireworks.some(fw => !fw.exploded || fw.particles.length > 0)) {
            requestAnimationFrame(animate);
        } else {
            canvas.remove();
        }
    }
    
    animate();
    playSound('success');
};

// 4. Stagger Page Load Animation
function initStaggerLoad() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                entry.target.style.animationDelay = `${index * 0.1}s`;
                entry.target.classList.add('stagger-reveal');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    // Apply to all .reveal + stagger class
    document.querySelectorAll('.reveal, .card, .section').forEach((el, index) => {
        el.style.animationDelay = `${index * 0.05}s`;
        observer.observe(el);
    });
}

// ============================================
 // Language Toggle System (UA/EN)
 // ============================================

const translations = {
    uk: {
        'home': 'Головна',
        'catalog': 'Каталог',
        'builder': 'Конструктор ПК',
        'profile': 'Профіль',
        'admin': 'Адмінка',
        'cart': 'Кошик',
        'login': 'Вхід',
        'register': 'Реєстрація',
        'logout': 'Вихід',
        'toggle-theme': 'Перемкнути тему',
        'ua-en': '🇺🇦 Українська / 🇺🇸 English'
    },
    en: {
        'home': 'Home',
        'catalog': 'Catalog',
        'builder': 'PC Builder',
        'profile': 'Profile',
        'admin': 'Admin',
        'cart': 'Cart',
        'login': 'Login',
        'register': 'Register',
        'logout': 'Logout',
        'toggle-theme': 'Toggle theme',
        'ua-en': '🇺🇸 English / 🇺🇦 Ukrainian'
    }
};

function initLanguageToggle() {
    const langBtn = document.getElementById('langToggle');
    if (!langBtn) return;
    
    const currentLang = localStorage.getItem('lang') || 'uk';
    document.documentElement.setAttribute('lang', currentLang);
    document.getElementById('langIcon').textContent = currentLang === 'uk' ? '🇺🇦' : '🇺🇸';
    
    langBtn.title = translations[currentLang]['ua-en'];
    
    langBtn.addEventListener('click', () => {
        const newLang = currentLang === 'uk' ? 'en' : 'uk';
        document.documentElement.setAttribute('lang', newLang);
        localStorage.setItem('lang', newLang);
        document.getElementById('langIcon').textContent = newLang === 'uk' ? '🇺🇦' : '🇺🇸';
        langBtn.title = translations[newLang]['ua-en'];
        
        // Update all translated elements
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.dataset.i18n;
            if (translations[newLang][key]) {
                el.textContent = translations[newLang][key];
            }
        });
        
        // Update theme button title
        const themeBtn = document.getElementById('themeToggle');
        if (themeBtn) {
            themeBtn.title = translations[newLang]['toggle-theme'];
        }
        
        triggerLightningEffect(langBtn.getBoundingClientRect().left + 20, langBtn.getBoundingClientRect().top + 20);
        playSound('click');
    });
}

// Theme button styles (optimized)
const themeStyle = document.createElement('style');
themeStyle.textContent = `
    .theme-btn, .lang-btn {
        position: relative;
        min-width: 44px;
        background: var(--card-bg);
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
    }
    .theme-btn:hover, .lang-btn:hover {
        box-shadow: var(--glow-primary);
        transform: scale(1.05);
    }
    [theme="light"] .theme-btn, [theme="light"] .lang-btn { 
        border-color: rgba(0,0,0,0.1); 
    }
`;
document.head.appendChild(themeStyle);

window.flyToCart = flyToCart;
window.orderFireworks = orderFireworks;

// ============================================
// Утиліти
// ============================================

function formatPrice(price) {
    return price.toLocaleString('uk-UA').replace(',', ' ') + ' ₴';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============================================
// Compatibility Check (для конструктора)
// ============================================

window.checkCompatibility = async function(components) {
    try {
        const response = await fetch('/api/compatibility', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ components })
        });
        return await response.json();
    } catch (error) {
        console.error('Compatibility check failed:', error);
        return { compatible: true, issues: [] };
    }
};

// Експорт функцій
window.addToCart = addToCart;
window.updateQuantity = updateCartQuantity;
window.removeFromCart = removeFromCart;
window.clearCart = clearCart;
window.showToast = showToast;
window.formatPrice = formatPrice;
window.triggerLightningEffect = triggerLightningEffect;
window.playSound = playSound;
window.flyToCart = flyToCart;

// Додаткові CSS анімації
const additionalStyles = document.createElement('style');
additionalStyles.textContent = `
    @keyframes slideOut {
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @keyframes cart-bounce {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.2); }
    }
    
    @keyframes badge-pop {
        0% { transform: scale(0); }
        50% { transform: scale(1.3); }
        100% { transform: scale(1); }
    }
    
    /* Sound toggle button */
    .sound-toggle {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        background: var(--card-bg);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .sound-toggle:hover {
        background: var(--card-bg-hover);
        box-shadow: var(--glow-primary);
    }
    
    .sound-toggle.muted {
        opacity: 0.5;
    }
`;
document.head.appendChild(additionalStyles);


