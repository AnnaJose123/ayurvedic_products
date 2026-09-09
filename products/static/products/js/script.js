/**
 * HerbaCare - Interactive Motion & Animation System
 * Features:
 * 1. Preloader: Counting percentage that tears away on load
 * 2. Custom Cursor: Lerped dot following pointer via requestAnimationFrame
 * 3. Split-Text Hero: Word-level staggered cascading animation
 * 4. IntersectionObserver: Orchestrated scroll reveals
 * 5. Magnetic Buttons: CTA mouse-following spring motion
 */

document.addEventListener('DOMContentLoaded', () => {

  /* -------------------------------------------------------------------------- */
  /* 1. PRELOADER COUNTDOWN & TEAR-AWAY (ONLY ON INITIAL LOAD OR REFRESH)       */
  /* -------------------------------------------------------------------------- */
  const preloader = document.getElementById('preloader');
  const preloaderCount = document.getElementById('preloaderCount');

  // Detect browser refresh vs internal navigation
  const navEntries = performance.getEntriesByType('navigation');
  const navType = navEntries.length > 0 ? navEntries[0].type : '';
  const isReload = navType === 'reload';
  const isInternalNav = sessionStorage.getItem('is_internal_navigation') === 'true';

  // Reset internal navigation flag
  sessionStorage.removeItem('is_internal_navigation');

  // Track clicks on internal links to mark internal navigation
  document.addEventListener('click', (e) => {
    const link = e.target.closest('a');
    if (link && link.href && link.origin === window.location.origin) {
      if (link.pathname !== window.location.pathname || link.search !== window.location.search) {
        sessionStorage.setItem('is_internal_navigation', 'true');
      }
    }
  });

  // Track form submissions
  document.addEventListener('submit', () => {
    sessionStorage.setItem('is_internal_navigation', 'true');
  });

  if (preloader && preloaderCount) {
    // Show counting preloader animation ONLY on initial site visit or browser refresh (F5)
    if (!isInternalNav || isReload) {
      let count = 0;
      const interval = setInterval(() => {
        count += Math.floor(Math.random() * 12) + 5;
        if (count >= 100) {
          count = 100;
          clearInterval(interval);
          setTimeout(() => {
            preloader.classList.add('loaded');
            initSplitTextHero();
          }, 300);
        }
        preloaderCount.textContent = count + '%';
      }, 45);
    } else {
      // Skip preloader instantly for smooth internal page navigation
      preloader.style.display = 'none';
      preloader.classList.add('loaded');
      initSplitTextHero();
    }
  } else {
    initSplitTextHero();
  }

  /* -------------------------------------------------------------------------- */
  /* 2. LERPED CUSTOM CURSOR                                                    */
  /* -------------------------------------------------------------------------- */
  const dot = document.getElementById('cursorDot');
  const ring = document.getElementById('cursorRing');

  if (dot && ring && matchMedia('(pointer: fine)').matches) {
    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;
    let ringX = mouseX;
    let ringY = mouseY;
    let dotX = mouseX;
    let dotY = mouseY;

    window.addEventListener('mousemove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    });

    function renderCursor() {
      // Lerp ring position (smooth delay)
      ringX += (mouseX - ringX) * 0.15;
      ringY += (mouseY - ringY) * 0.15;
      
      // Faster lerp for dot
      dotX += (mouseX - dotX) * 0.45;
      dotY += (mouseY - dotY) * 0.45;

      ring.style.transform = `translate3d(${ringX}px, ${ringY}px, 0) translate(-50%, -50%)`;
      dot.style.transform = `translate3d(${dotX}px, ${dotY}px, 0) translate(-50%, -50%)`;

      requestAnimationFrame(renderCursor);
    }
    requestAnimationFrame(renderCursor);

    // Expand ring over interactive elements
    const hoverSelectors = 'a, button, .btn, .product-card, .dosha-card, .feature-card, .magnetic-btn, input, select, textarea';
    document.querySelectorAll(hoverSelectors).forEach(el => {
      el.addEventListener('mouseenter', () => document.body.classList.add('cursor-hover'));
      el.addEventListener('mouseleave', () => document.body.classList.remove('cursor-hover'));
    });
  }

  /* -------------------------------------------------------------------------- */
  /* 3. SPLIT-TEXT HERO ANIMATION                                               */
  /* -------------------------------------------------------------------------- */
  function initSplitTextHero() {
    const heroTitle = document.querySelector('.split-hero-title');
    if (!heroTitle) return;

    const rawText = heroTitle.textContent.trim();
    heroTitle.innerHTML = '';
    const words = rawText.split(' ');

    words.forEach((word, idx) => {
      const span = document.createElement('span');
      span.className = 'split-word';
      span.textContent = word + (idx < words.length - 1 ? '\u00A0' : '');
      span.style.animationDelay = `${0.1 + idx * 0.08}s`;
      heroTitle.appendChild(span);
    });
  }

  /* -------------------------------------------------------------------------- */
  /* 4. SINGLE INTERSECTION OBSERVER SCROLL REVEALS                             */
  /* -------------------------------------------------------------------------- */
  const reveals = document.querySelectorAll('.reveal');
  if (reveals.length > 0) {
    const observerOptions = {
      threshold: 0.12,
      rootMargin: '0px 0px -40px 0px'
    };

    const revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const index = Array.from(reveals).indexOf(el) % 6;
          el.style.transitionDelay = `${index * 0.08}s`;
          el.classList.add('revealed');
          observer.unobserve(el);
        }
      });
    }, observerOptions);

    reveals.forEach(el => revealObserver.observe(el));
  }

  /* -------------------------------------------------------------------------- */
  /* 5. MAGNETIC BUTTON MOTION                                                  */
  /* -------------------------------------------------------------------------- */
  const magneticBtns = document.querySelectorAll('.magnetic-btn, .btn-brass, .btn-primary');
  magneticBtns.forEach(btn => {
    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      btn.style.transform = `translate3d(${x * 0.28}px, ${y * 0.28}px, 0)`;
    });

    btn.addEventListener('mouseleave', () => {
      btn.style.transform = `translate3d(0px, 0px, 0)`;
    });
  });

  /* -------------------------------------------------------------------------- */
  /* 6. MOBILE NAVIGATION DRAWER TOGGLE                                         */
  /* -------------------------------------------------------------------------- */
  const mobileToggle = document.getElementById('mobileToggle');
  const navLinks = document.getElementById('navLinks');

  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      navLinks.classList.toggle('active');
      const isExpanded = navLinks.classList.contains('active');
      mobileToggle.setAttribute('aria-expanded', isExpanded);
      
      const icon = mobileToggle.querySelector('i');
      if (icon) {
        icon.className = isExpanded ? 'fas fa-times' : 'fas fa-bars';
      }
    });

    document.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('active');
        const icon = mobileToggle.querySelector('i');
        if (icon) icon.className = 'fas fa-bars';
      });
    });
  }

});
