document.addEventListener('DOMContentLoaded', () => {
    console.log("Portfolio loaded successfully.");

    // Detect if device is mobile/tablet
    const isTouchDevice = () => {
        return (('ontouchstart' in window) ||
                (navigator.maxTouchPoints > 0) ||
                (navigator.msMaxTouchPoints > 0));
    };

    const isMobile = isTouchDevice();

    // Header scroll behavior
    let lastScroll = 0;
    const header = document.querySelector('header');
    
    if (header) {
        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;
            
            if (currentScroll <= 0) {
                header.classList.remove('header-hidden');
                return;
            }
            
            if (currentScroll > lastScroll && !header.classList.contains('header-hidden')) {
                // Scrolling down
                header.classList.add('header-hidden');
            } else if (currentScroll < lastScroll && header.classList.contains('header-hidden')) {
                // Scrolling up
                header.classList.remove('header-hidden');
            }
            
            lastScroll = currentScroll;
        }, { passive: true });
    }

    // Animate elements on scroll
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Add animation classes to elements
    document.querySelectorAll('section').forEach(section => {
        section.classList.add('animate-on-scroll');
        observer.observe(section);
    });

    document.querySelectorAll('.card').forEach(card => {
        card.classList.add('animate-on-scroll');
        observer.observe(card);
    });

    // Card hover effects - ONLY on non-touch devices
    if (!isMobile) {
        document.querySelectorAll('.card').forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = (y - centerY) / 20;
                const rotateY = (centerX - x) / 20;
                
                card.style.transform = `
                    perspective(1000px)
                    rotateX(${rotateX}deg)
                    rotateY(${rotateY}deg)
                    scale3d(1.02, 1.02, 1.02)
                `;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
            });
        });
    }

    // Add loading animation to images
    document.querySelectorAll('img').forEach(img => {
        if (!img.complete) {
            img.classList.add('loading');
            img.addEventListener('load', () => {
                img.classList.remove('loading');
            }, { once: true });
        }
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                
                // Close mobile nav if open
                const nav = document.querySelector('nav');
                const toggle = document.querySelector('.mobile-nav-toggle');
                if (nav && nav.classList.contains('active')) {
                    nav.classList.remove('active');
                    if (toggle) toggle.classList.remove('active');
                }
                
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Mobile navigation - only initialize once
    let mobileNavInitialized = false;
    
    const initMobileNav = () => {
        if (mobileNavInitialized) return;
        
        const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
        const nav = document.querySelector('nav');
        
        if (!mobileNavToggle || !nav) return;
        
        mobileNavToggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const isActive = nav.classList.toggle('active');
            mobileNavToggle.classList.toggle('active');
            
            // Prevent body scroll when nav is open
            if (isActive) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });
        
        mobileNavInitialized = true;
    };

    // Initialize mobile nav
    initMobileNav();

    // Close mobile nav when clicking on nav links
    document.querySelectorAll('nav a').forEach(link => {
        link.addEventListener('click', () => {
            const nav = document.querySelector('nav');
            const toggle = document.querySelector('.mobile-nav-toggle');
            
            if (nav && nav.classList.contains('active')) {
                nav.classList.remove('active');
                if (toggle) toggle.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });

    // Close mobile nav when clicking outside
    document.addEventListener('click', (e) => {
        const nav = document.querySelector('nav');
        const toggle = document.querySelector('.mobile-nav-toggle');
        
        if (!nav || !toggle) return;
        
        if (nav.classList.contains('active') && 
            !nav.contains(e.target) && 
            !toggle.contains(e.target)) {
            nav.classList.remove('active');
            toggle.classList.remove('active');
            document.body.style.overflow = '';
        }
    });

    // Handle browser back/forward
    window.addEventListener('pageshow', (event) => {
        if (event.persisted) {
            // Page was loaded from cache
            const nav = document.querySelector('nav');
            const toggle = document.querySelector('.mobile-nav-toggle');
            
            if (nav) nav.classList.remove('active');
            if (toggle) toggle.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
});
