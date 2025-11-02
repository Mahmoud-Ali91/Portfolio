document.addEventListener('DOMContentLoaded', () => {
    console.log("Portfolio loaded successfully.");

    // Remove any existing mobile navigation elements from previous page
    const existingNav = document.querySelector('.mobile-nav-toggle');
    if (existingNav) {
        existingNav.remove();
    }

    // Header scroll behavior
    let lastScroll = 0;
    const header = document.querySelector('header');
    
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
    });

    // Animate elements on scroll
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
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

    // Card hover effects
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

    // Add loading animation to images
    document.querySelectorAll('img').forEach(img => {
        if (!img.complete) {
            img.classList.add('loading');
            img.addEventListener('load', () => {
                img.classList.remove('loading');
            });
        }
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Mobile navigation (clean, targeted to .site-nav)
    const initMobileNav = () => {
        const toggle = document.querySelector('.mobile-nav-toggle');
        const nav = document.querySelector('#site-nav') || document.querySelector('.site-nav');

        if (!toggle || !nav) return;

        // Ensure a single backdrop element exists
        let backdrop = document.querySelector('.site-nav-backdrop');
        if (!backdrop) {
            backdrop = document.createElement('div');
            backdrop.className = 'site-nav-backdrop';
            document.body.appendChild(backdrop);
        }

        // Focus handling for accessibility
        const focusableSelectors = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
        let previousActive = null;
        let keydownHandler = null;

        const openNav = () => {
            nav.classList.add('active');
            toggle.classList.add('active');
            document.body.classList.add('nav-open');
            toggle.setAttribute('aria-expanded', 'true');
            backdrop.classList.add('visible');
            // Prevent background scroll
            document.body.style.overflow = 'hidden';

            // Save focus and move focus into nav
            previousActive = document.activeElement;
            const first = nav.querySelector(focusableSelectors);
            if (first) first.focus();

            // Trap tab key inside nav
            keydownHandler = (e) => {
                if (e.key !== 'Tab') return;
                const focusable = Array.from(nav.querySelectorAll(focusableSelectors)).filter(el => el.offsetWidth > 0 || el.offsetHeight > 0 || el === document.activeElement);
                if (focusable.length === 0) return;
                const firstEl = focusable[0];
                const lastEl = focusable[focusable.length - 1];
                if (e.shiftKey && document.activeElement === firstEl) {
                    e.preventDefault();
                    lastEl.focus();
                } else if (!e.shiftKey && document.activeElement === lastEl) {
                    e.preventDefault();
                    firstEl.focus();
                }
            };
            document.addEventListener('keydown', keydownHandler);
        };

        const closeNav = () => {
            nav.classList.remove('active');
            toggle.classList.remove('active');
            document.body.classList.remove('nav-open');
            toggle.setAttribute('aria-expanded', 'false');
            backdrop.classList.remove('visible');
            document.body.style.overflow = '';

            // Restore focus and remove trap
            try { if (previousActive && typeof previousActive.focus === 'function') previousActive.focus(); } catch (err) {}
            if (keydownHandler) document.removeEventListener('keydown', keydownHandler);
            keydownHandler = null;
        };

        const onToggle = (e) => {
            e.stopPropagation();
            if (nav.classList.contains('active')) closeNav(); else openNav();
        };

        // Remove duplicate listeners by cloning if needed
        const newToggle = toggle.cloneNode(true);
        toggle.parentNode.replaceChild(newToggle, toggle);

        // Re-assign reference to the new node
        const boundToggle = document.querySelector('.mobile-nav-toggle');
        boundToggle.addEventListener('click', onToggle);

        // Backdrop click closes nav
        backdrop.addEventListener('click', closeNav);

        // Close when a nav link is clicked
        nav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                closeNav();
            });
        });

        // Close on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && nav.classList.contains('active')) {
                closeNav();
            }
        });

        // Close on visibility/orientation/resize changes
        document.addEventListener('visibilitychange', () => { if (document.hidden) closeNav(); });
        window.addEventListener('orientationchange', closeNav);
        window.addEventListener('resize', () => { if (window.innerWidth > 900) closeNav(); });
    };
            
    // Initialize mobile nav
    initMobileNav();

    // Re-initialize mobile nav after pageshow (history navigation)
    document.addEventListener('pageshow', initMobileNav);
});