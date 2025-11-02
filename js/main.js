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

    // Mobile navigation
    const initMobileNav = () => {
        const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
        const nav = document.querySelector('nav');
        
        if (mobileNavToggle && nav) {
            // Remove any existing listeners first
            const newToggle = mobileNavToggle.cloneNode(true);
            mobileNavToggle.parentNode.replaceChild(newToggle, mobileNavToggle);
            
            // Toggle menu function
            const toggleMenu = (e) => {
                if (e) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                const isOpen = nav.classList.contains('active');
                
                if (isOpen) {
                    nav.classList.remove('active');
                    document.body.classList.remove('nav-open');
                    newToggle.classList.remove('active');
                    // Enable scrolling
                    document.body.style.overflow = '';
                } else {
                    nav.classList.add('active');
                    document.body.classList.add('nav-open');
                    newToggle.classList.add('active');
                    // Prevent background scrolling
                    document.body.style.overflow = 'hidden';
                }
            };

            // Toggle on button click
            newToggle.addEventListener('click', toggleMenu);

            // Close menu when clicking outside
            document.addEventListener('click', (e) => {
                const isOpen = nav.classList.contains('active');
                if (isOpen && !nav.contains(e.target) && !newToggle.contains(e.target)) {
                    toggleMenu();
                }
            });

            // Close menu when pressing Escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && nav.classList.contains('active')) {
                    toggleMenu();
                }
            });

            // Close menu when clicking a link
            nav.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    if (nav.classList.contains('active')) {
                        toggleMenu();
                    }
                });
            });
        }
    };

    // Initialize mobile nav
    initMobileNav();

    // Re-initialize mobile nav after each page load
    document.addEventListener('pageshow', initMobileNav);

    // Handle page transitions
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            const nav = document.querySelector('nav');
            const toggle = document.querySelector('.mobile-nav-toggle');
            if (nav.classList.contains('active')) {
                nav.classList.remove('active');
                document.body.classList.remove('nav-open');
                toggle.classList.remove('active');
            }
        });
    });

    // Close mobile nav when clicking outside
    document.addEventListener('click', (e) => {
        const nav = document.querySelector('nav.active');
        const toggle = document.querySelector('.mobile-nav-toggle');
        if (nav && toggle && !nav.contains(e.target) && !toggle.contains(e.target)) {
            nav.classList.remove('active');
            document.body.classList.remove('nav-open');
        }
    });
});