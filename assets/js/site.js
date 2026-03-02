// Mobile menu functionality
document.addEventListener('DOMContentLoaded', function() {
  const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
  const mainNav = document.querySelector('.main-nav');
  const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
  
  // Mobile menu toggle
  if (mobileMenuToggle && mainNav) {
    mobileMenuToggle.addEventListener('click', function() {
      const isExpanded = this.getAttribute('aria-expanded') === 'true';
      this.setAttribute('aria-expanded', !isExpanded);
      mainNav.classList.toggle('active');
      
      // Animate hamburger to X
      const lines = this.querySelectorAll('.hamburger-line');
      if (mainNav.classList.contains('active')) {
        lines[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
        lines[1].style.opacity = '0';
        lines[2].style.transform = 'rotate(-45deg) translate(7px, -6px)';
      } else {
        lines[0].style.transform = 'none';
        lines[1].style.opacity = '1';
        lines[2].style.transform = 'none';
      }
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
      if (!mainNav.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
        mainNav.classList.remove('active');
        mobileMenuToggle.setAttribute('aria-expanded', 'false');
        const lines = mobileMenuToggle.querySelectorAll('.hamburger-line');
        lines[0].style.transform = 'none';
        lines[1].style.opacity = '1';
        lines[2].style.transform = 'none';
      }
    });
  }
  
  // Dropdown functionality
  dropdownToggles.forEach(toggle => {
    toggle.addEventListener('click', function(e) {
      e.preventDefault();
      const isExpanded = this.getAttribute('aria-expanded') === 'true';
      const dropdownMenu = this.nextElementSibling;
      
      // Close other dropdowns
      dropdownToggles.forEach(otherToggle => {
        if (otherToggle !== this) {
          otherToggle.setAttribute('aria-expanded', 'false');
          const otherMenu = otherToggle.nextElementSibling;
          if (otherMenu) {
            otherMenu.classList.remove('active');
          }
        }
      });
      
      // Toggle current dropdown
      this.setAttribute('aria-expanded', !isExpanded);
      if (dropdownMenu) {
        dropdownMenu.classList.toggle('active');
      }
    });
  });
  
  // Close dropdowns when clicking outside
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.dropdown-container')) {
      dropdownToggles.forEach(toggle => {
        toggle.setAttribute('aria-expanded', 'false');
        const dropdownMenu = toggle.nextElementSibling;
        if (dropdownMenu) {
          dropdownMenu.classList.remove('active');
        }
      });
    }
  });
  
  // Keyboard navigation
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      // Close mobile menu
      if (mainNav && mainNav.classList.contains('active')) {
        mainNav.classList.remove('active');
        mobileMenuToggle.setAttribute('aria-expanded', 'false');
        const lines = mobileMenuToggle.querySelectorAll('.hamburger-line');
        lines[0].style.transform = 'none';
        lines[1].style.opacity = '1';
        lines[2].style.transform = 'none';
      }
      
      // Close dropdowns
      dropdownToggles.forEach(toggle => {
        toggle.setAttribute('aria-expanded', 'false');
        const dropdownMenu = toggle.nextElementSibling;
        if (dropdownMenu) {
          dropdownMenu.classList.remove('active');
        }
      });
    }
  });
  
  // Image Slideshow functionality (supports multiple slideshows)
  const slideshowContainers = document.querySelectorAll('.slideshow-container');
  slideshowContainers.forEach((slideshowContainer) => {
    const slides = slideshowContainer.querySelectorAll('.slide');
    const dots = slideshowContainer.querySelectorAll('.dot');
    const prevBtn = slideshowContainer.querySelector('.prev');
    const nextBtn = slideshowContainer.querySelector('.next');

    if (!slides.length) {
      return;
    }

    let currentSlide = 0;
    let slideInterval;

    function showSlide(index) {
      if (!slides.length) {
        return;
      }
      if (index < 0 || index >= slides.length) {
        return;
      }

      slides.forEach(slide => slide.classList.remove('active'));
      dots.forEach(dot => dot.classList.remove('active'));

      slides[index].classList.add('active');
      if (dots[index]) {
        dots[index].classList.add('active');
      }

      currentSlide = index;
    }

    function nextSlide() {
      const next = (currentSlide + 1) % slides.length;
      showSlide(next);
    }

    function prevSlide() {
      const prev = (currentSlide - 1 + slides.length) % slides.length;
      showSlide(prev);
    }

    function startAutoPlay() {
      slideInterval = setInterval(nextSlide, 5000); // Change slide every 5 seconds
    }

    function stopAutoPlay() {
      if (slideInterval) {
        clearInterval(slideInterval);
      }
    }

    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        prevSlide();
        stopAutoPlay();
        startAutoPlay();
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        nextSlide();
        stopAutoPlay();
        startAutoPlay();
      });
    }

    dots.forEach((dot, index) => {
      dot.addEventListener('click', () => {
        showSlide(index);
        stopAutoPlay();
        startAutoPlay();
      });
    });

    slideshowContainer.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') {
        prevSlide();
        stopAutoPlay();
        startAutoPlay();
      } else if (e.key === 'ArrowRight') {
        nextSlide();
        stopAutoPlay();
        startAutoPlay();
      }
    });

    slideshowContainer.addEventListener('mouseenter', stopAutoPlay);
    slideshowContainer.addEventListener('mouseleave', startAutoPlay);

    let touchStartX = 0;
    let touchEndX = 0;

    slideshowContainer.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
    });

    slideshowContainer.addEventListener('touchend', (e) => {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
    });

    function handleSwipe() {
      const swipeThreshold = 50;
      const diff = touchStartX - touchEndX;

      if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
          nextSlide();
        } else {
          prevSlide();
        }
        stopAutoPlay();
        startAutoPlay();
      }
    }

    showSlide(0);
    startAutoPlay();
    slideshowContainer.setAttribute('tabindex', '0');
  });
});
