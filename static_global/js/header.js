/**
 * Header functionality - Language selector, user menu, and submenu handling
 */

// Check screen width and set initial state
function checkScreenWidth() {
  const sidebar = document.querySelector('.sidebar');
  const mainContent = document.querySelector('.main');
  const header = document.querySelector('.header');
  const footer = document.querySelector('.main-footer');
  
  if (!sidebar) return;
  
  if (window.innerWidth < 992) {
    // If screen is small, set default collapsed state only on initial load
    // Don't override if user has manually expanded
    if (!sidebar.hasAttribute('data-user-toggled')) {
      sidebar.classList.add('collapsed');
    }
    
    // Apply current state width
    const isCollapsed = sidebar.classList.contains('collapsed');
    const currentWidth = isCollapsed ? '80px' : '270px';
    sidebar.style.width = currentWidth;
    
    if (mainContent) {
      mainContent.style.marginLeft = currentWidth;
      mainContent.style.width = `calc(100% - ${currentWidth})`;
    }
    
    if (header) {
      header.style.left = currentWidth;
      header.style.width = `calc(100% - ${currentWidth})`;
    }
    
    // Update footer positioning in responsive mode
    if (footer) {
      footer.style.marginLeft = currentWidth;
      footer.style.width = `calc(100% - ${currentWidth})`;
    }
    
    document.documentElement.style.setProperty('--sidebar-width', currentWidth);
    
    // Update toggle button icon
    const toggleBtn = document.getElementById('toggleSidebar');
    if (toggleBtn) {
      toggleBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
    }
    
    // Update logo icon size
    const logoIcon = document.querySelector('.logo-toggle i');
    if (logoIcon) {
      logoIcon.style.fontSize = '1.5rem';
    }
  } else {
    // If screen is large enough, ensure sidebar is expanded
    sidebar.classList.remove('collapsed');
    const expandedWidth = '270px';
    sidebar.style.width = expandedWidth;
    
    if (mainContent) {
      mainContent.style.marginLeft = expandedWidth;
      mainContent.style.width = `calc(100% - ${expandedWidth})`;
    }
    
    if (header) {
      header.style.left = expandedWidth;
      header.style.width = `calc(100% - ${expandedWidth})`;
    }
    
    // Reset footer positioning in desktop mode
    if (footer) {
      footer.style.marginLeft = '';
      footer.style.width = '';
    }
    
    document.documentElement.style.setProperty('--sidebar-width', expandedWidth);
    
    // Remove user toggle marker when in desktop mode
    sidebar.removeAttribute('data-user-toggled');
    
    // Update toggle button icon
    const toggleBtn = document.getElementById('toggleSidebar');
    if (toggleBtn) {
      toggleBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
    }
    
    // Update logo icon size
    const logoIcon = document.querySelector('.logo-toggle i');
    if (logoIcon) {
      logoIcon.style.fontSize = '1.5rem';
    }
  }
}

// Run checkScreenWidth on initial load
// Add small delay to ensure DOM is ready
setTimeout(checkScreenWidth, 50);

document.addEventListener('DOMContentLoaded', function() {
  // Initialize submenu functionality
  $('.sub-menu ul').hide();
  $(".sub-menu > a").click(function (e) {
    e.preventDefault();
    const sidebar = document.querySelector('.sidebar');

    if (sidebar.classList.contains('collapsed')) {
      // En mode collapsed, ne rien afficher pour TOUS les sous-menus
      return false;
    } else {
      // In expanded mode, we use the slide toggle functionality
      // Close other submenus
      $('.sub-menu').not($(this).parent()).removeClass('active').children('ul').slideUp('100');
      $('.sub-menu').not($(this).parent()).find('.right').removeClass('fa-caret-up').addClass('fa-caret-down');
      
      // Toggle current submenu
      $(this).siblings('ul').slideToggle("100");
      $(this).parent(".sub-menu").toggleClass("active");
      $(this).find(".right").toggleClass("fa-caret-up fa-caret-down");
    }
  });
  
  // Close submenus when clicking outside
  $(document).click(function(e) {
    if (!$(e.target).closest('.sub-menu').length) {
      // Close slide-down submenus
      $('.sub-menu').removeClass('active').children('ul').slideUp('100');
      $('.sub-menu .right').removeClass('fa-caret-up').addClass('fa-caret-down');
      // Close pop-out submenus
      $('.sub-menu.show-submenu').removeClass('show-submenu');
    }
  });
  

  
  // Run on window resize with debouncing
  let resizeTimer;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(checkScreenWidth, 150);
  });

  // Toggle sidebar functionality
  const toggleSidebar = document.getElementById('toggleSidebar');
  const logoToggle = document.getElementById('logoToggle');
  const sidebar = document.querySelector('.sidebar');
  const mainContent = document.querySelector('.main');
  
  if ((toggleSidebar || logoToggle) && sidebar) {
    // Always start with expanded sidebar (no localStorage persistence)
    sidebar.classList.remove('collapsed');
    if (toggleSidebar) {
      toggleSidebar.innerHTML = '<i class="fas fa-chevron-left"></i>';
    }
    
    // Toggle sidebar on button click
    function toggleSidebarState() {
      const header = document.querySelector('.header');
      const footer = document.querySelector('.main-footer');
      const isCurrentlyCollapsed = sidebar.classList.contains('collapsed');
      
      // Close all header dropdowns and submenus when toggling sidebar
      closeAllDropdowns();
      closeAllSubmenus();
      
      // Mark that user has manually toggled the sidebar
      sidebar.setAttribute('data-user-toggled', 'true');
      
      // In responsive mode (small screens), allow full expansion
      if (window.innerWidth < 992) {
        if (isCurrentlyCollapsed) {
          // Expand to full width in responsive mode
          sidebar.classList.remove('collapsed');
          const newWidth = '270px';
          sidebar.style.width = newWidth;
          document.documentElement.style.setProperty('--sidebar-width', newWidth);
          
          if (mainContent) {
            mainContent.style.marginLeft = newWidth;
            mainContent.style.width = `calc(100% - ${newWidth})`;
          }
          
          if (header) {
            header.style.left = newWidth;
            header.style.width = `calc(100% - ${newWidth})`;
          }
          
          // Update footer in responsive mode
          if (footer) {
            footer.style.marginLeft = newWidth;
            footer.style.width = `calc(100% - ${newWidth})`;
          }
          
          if (toggleSidebar) {
            toggleSidebar.innerHTML = '<i class="fas fa-chevron-left"></i>';
          }
        } else {
          // Collapse to icon-only in responsive mode
          sidebar.classList.add('collapsed');
          const newWidth = '80px';
          sidebar.style.width = newWidth;
          document.documentElement.style.setProperty('--sidebar-width', newWidth);
          
          if (mainContent) {
            mainContent.style.marginLeft = newWidth;
            mainContent.style.width = `calc(100% - ${newWidth})`;
          }
          
          if (header) {
            header.style.left = newWidth;
            header.style.width = `calc(100% - ${newWidth})`;
          }
          
          // Update footer in responsive mode
          if (footer) {
            footer.style.marginLeft = newWidth;
            footer.style.width = `calc(100% - ${newWidth})`;
          }
          
          if (toggleSidebar) {
            toggleSidebar.innerHTML = '<i class="fas fa-chevron-right"></i>';
          }
        }
      } else {
        // Normal desktop behavior
        sidebar.classList.toggle('collapsed');
        const isNowCollapsed = sidebar.classList.contains('collapsed');
        
        // Remove user toggle marker when in desktop mode
        if (window.innerWidth >= 992) {
          sidebar.removeAttribute('data-user-toggled');
        }
        
        // Update toggle button icon
        if (toggleSidebar) {
          toggleSidebar.innerHTML = isNowCollapsed ? 
            '<i class="fas fa-chevron-right"></i>' : 
            '<i class="fas fa-chevron-left"></i>';
        }
        
        // Set sidebar width
        const newWidth = isNowCollapsed ? '80px' : '270px';
        sidebar.style.width = newWidth;
        document.documentElement.style.setProperty('--sidebar-width', newWidth);
        
        // Update main content
        if (mainContent) {
          mainContent.style.marginLeft = newWidth;
          mainContent.style.width = `calc(100% - ${newWidth})`;
        }
        
        // Update header position and width
        if (header) {
          header.style.left = newWidth;
          header.style.width = `calc(100% - ${newWidth})`;
        }
        
        // Reset footer positioning in desktop mode
        if (footer) {
          footer.style.marginLeft = '';
          footer.style.width = '';
        }
      }
      
      // Toggle logo size
      const logo = document.querySelector('.logo-toggle i');
      if (logo) {
        logo.style.fontSize = '1.5rem';
      }
    }
    
    // Function to close all header dropdowns
    function closeAllDropdowns() {
      const userDropdown = document.querySelector('.user-dropdown');
      if (userDropdown) {
        userDropdown.classList.remove('show');
      }
      
      const languageDropdown = document.querySelector('.language-selector');
      if (languageDropdown) {
        languageDropdown.classList.remove('show');
      }
      
      const allDropdowns = document.querySelectorAll('.dropdown.show');
      allDropdowns.forEach(dropdown => {
        dropdown.classList.remove('show');
      });
    }
    
    // Function to close all submenus
    function closeAllSubmenus() {
      // Use jQuery to leverage existing slideUp functionality and selectors
      $('.sub-menu.active').removeClass('active').children('ul').slideUp('100');
      $('.sub-menu.active .right').removeClass('fa-caret-up').addClass('fa-caret-down');
      
      // Close pop-out submenus in collapsed mode
      $('.sub-menu.show-submenu').removeClass('show-submenu');
    }
    
    // Add event listeners
    if (toggleSidebar) {
      toggleSidebar.addEventListener('click', toggleSidebarState);
    }
    
    if (logoToggle) {
      logoToggle.addEventListener('click', toggleSidebarState);
    }
    
    // Set initial state - always expanded
    if (sidebar.classList.contains('collapsed')) {
      sidebar.classList.remove('collapsed');
      if (toggleSidebar) {
        toggleSidebar.innerHTML = '<i class="fas fa-chevron-left"></i>';
      }
      
      if (mainContent) {
        mainContent.style.marginLeft = '250px';
      }
    }
    
    const existingMobileMenuBtn = document.querySelector('.toggle-mobile-menu');
    if (existingMobileMenuBtn) {
      existingMobileMenuBtn.remove();
    }
    
    // Set initial state - always expanded on large screens
    if (window.innerWidth >= 992 && sidebar.classList.contains('collapsed')) {
      sidebar.classList.remove('collapsed');
      if (toggleSidebar) {
        toggleSidebar.innerHTML = '<i class="fas fa-chevron-left"></i>';
      }
      
      if (mainContent) {
        mainContent.style.marginLeft = '270px';
      }
    }
  }
  
  // Toggle dropdown arrow animation
  const userDropdown = document.getElementById('userDropdown');
  if (userDropdown) {
    userDropdown.addEventListener('show.bs.dropdown', function () {
      this.querySelector('.fa-chevron-up').classList.add('rotate-180');
    });
    userDropdown.addEventListener('hide.bs.dropdown', function () {
      this.querySelector('.fa-chevron-up').classList.remove('rotate-180');
    });
  }
  
  // Language selector functionality
  const languageItems = document.querySelectorAll('.language-selector .dropdown-item');
  const currentLanguageSpan = document.getElementById('currentLanguage');
  
  const languages = {
    'fr': { code: 'FR', name: 'Français', display: 'Français' },
    'en': { code: 'EN', name: 'English', display: 'English' },
    'es': { code: 'ES', name: 'Español', display: 'Español' }
  };
  
  let currentLang = localStorage.getItem('selectedLanguage') || 'fr';
  let currentDisplay = localStorage.getItem('selectedLanguageDisplay') || 'Français';
  updateLanguageDisplay(currentLang, currentDisplay);
  
  languageItems.forEach(item => {
    item.addEventListener('click', function(e) {
      e.preventDefault();
      const selectedLang = this.getAttribute('data-lang');
      const selectedDisplay = this.getAttribute('data-display');
      
      if (selectedLang && languages[selectedLang]) {
        currentLang = selectedLang;
        localStorage.setItem('selectedLanguage', selectedLang);
        localStorage.setItem('selectedLanguageDisplay', selectedDisplay);
        updateLanguageDisplay(selectedLang, selectedDisplay);
        showLanguageChangeMessage(languages[selectedLang].name);
        console.log('Language changed to:', languages[selectedLang].name);
      }
    });
  });
  
  function updateLanguageDisplay(langCode, displayName) {
    if (currentLanguageSpan) {
      if (displayName) {
        currentLanguageSpan.textContent = displayName;
      } else if (languages[langCode]) {
        currentLanguageSpan.textContent = languages[langCode].display;
      }
    }
  }
  
  function showLanguageChangeMessage(languageName) {
    const notification = document.createElement('div');
    notification.className = 'language-notification';
    notification.innerHTML = `<i class="fas fa-check-circle"></i> Langue changée vers ${languageName}`;
    notification.style.cssText = `
      position: fixed;
      top: 80px;
      right: 20px;
      background: #28a745;
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 9999;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
      animation: slideIn 0.3s ease-out;
    `;
    
    if (!document.getElementById('language-notification-styles')) {
      const style = document.createElement('style');
      style.id = 'language-notification-styles';
      style.textContent = `
        @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
      `;
      document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => { if (notification.parentNode) notification.parentNode.removeChild(notification); }, 300);
    }, 3000);
  }
  
  const userMenuItems = document.querySelectorAll('.user-dropdown .dropdown-item');
  userMenuItems.forEach(item => {
    if (!item.getAttribute('href') || item.getAttribute('href') === '#') {
      item.addEventListener('click', function(e) {
        e.preventDefault();
        const itemText = this.textContent.trim();
        switch(true) {
          case itemText.includes('Mon Profil'): console.log('Navigating to profile...'); break;
          case itemText.includes('Paramètres'): console.log('Opening settings...'); break;
          case itemText.includes('Notifications'): console.log('Opening notifications...'); break;
          case itemText.includes('Aide'): console.log('Opening help...'); break;
          case itemText.includes('Mode Sombre'): toggleDarkMode(); break;
          default: console.log('Menu item clicked:', itemText);
        }
      });
    }
  });
  
  function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);
    const darkModeItem = document.querySelector('.dropdown-item:has(.fa-moon)');
    if (darkModeItem) {
      const icon = darkModeItem.querySelector('i');
      const text = darkModeItem.childNodes[darkModeItem.childNodes.length - 1];
      if (isDark) {
        icon.className = 'fas fa-sun me-2';
        text.textContent = ' Mode Clair';
      } else {
        icon.className = 'fas fa-moon me-2';
        text.textContent = ' Mode Sombre';
      }
    }
    console.log('Dark mode:', isDark ? 'enabled' : 'disabled');
  }
  
  if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
    toggleDarkMode();
  }

  // Initialisation forcée des dropdowns Bootstrap pour le responsive
  let dropdownsInitialized = false;
  let bootstrapDropdowns = [];

  function destroyExistingDropdowns() {
    // Détruire les instances Bootstrap existantes pour éviter les conflits
    bootstrapDropdowns.forEach(dropdown => {
      try {
        dropdown.dispose();
      } catch (e) {
        // Ignorer les erreurs de disposal
      }
    });
    bootstrapDropdowns = [];

    // Supprimer tous les event listeners personnalisés
    const dropdownElements = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    dropdownElements.forEach(element => {
      element.removeEventListener('click', handleDropdownClick);
      element.removeEventListener('show.bs.dropdown', handleDropdownShow);
    });
  }

  function handleDropdownClick(e) {
    e.preventDefault();
    e.stopPropagation();
    console.log('Dropdown cliqué:', this.id);

    const currentDropdownMenu = this.nextElementSibling;
    const isCurrentlyOpen = currentDropdownMenu && currentDropdownMenu.classList.contains('show');

    // TOUJOURS fermer tous les dropdowns d'abord
    console.log('Fermeture de tous les dropdowns...');
    closeAllDropdowns();

    // Si le dropdown cliqué n'était pas ouvert, l'ouvrir après un délai
    if (!isCurrentlyOpen) {
      setTimeout(() => {
        if (currentDropdownMenu) {
          console.log('Ouverture du dropdown:', this.id);
          currentDropdownMenu.classList.add('show');
          this.setAttribute('aria-expanded', 'true');

          // Ajouter la classe show au parent dropdown aussi
          const parentDropdown = this.closest('.dropdown');
          if (parentDropdown) {
            parentDropdown.classList.add('show');
          }
        }
      }, 50);
    }
  }

  function handleDropdownShow(e) {
    console.log('Bootstrap show event pour:', this.id);
    // Fermer tous les autres dropdowns avant d'ouvrir celui-ci
    const otherDropdowns = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    otherDropdowns.forEach(other => {
      if (other !== this) {
        const otherMenu = other.nextElementSibling;
        if (otherMenu && otherMenu.classList.contains('show')) {
          otherMenu.classList.remove('show');
          other.setAttribute('aria-expanded', 'false');
          const otherParent = other.closest('.dropdown');
          if (otherParent) {
            otherParent.classList.remove('show');
          }
        }
      }
    });
  }

  function closeAllDropdowns() {
    const allDropdowns = document.querySelectorAll('.dropdown-menu.show');
    const allDropdownToggles = document.querySelectorAll('[data-bs-toggle="dropdown"][aria-expanded="true"]');
    const allDropdownContainers = document.querySelectorAll('.dropdown.show');

    allDropdowns.forEach(menu => {
      menu.classList.remove('show');
    });

    allDropdownToggles.forEach(toggle => {
      toggle.setAttribute('aria-expanded', 'false');
    });

    allDropdownContainers.forEach(container => {
      container.classList.remove('show');
    });
  }

  function initializeBootstrapDropdowns() {
    console.log('Initialisation des dropdowns Bootstrap...');

    // Détruire les instances existantes d'abord
    if (dropdownsInitialized) {
      destroyExistingDropdowns();
    }

    // Initialiser tous les dropdowns
    const dropdownElementList = document.querySelectorAll('[data-bs-toggle="dropdown"]');

    dropdownElementList.forEach(dropdownToggleEl => {
      try {
        const dropdown = new bootstrap.Dropdown(dropdownToggleEl, {
          autoClose: true,
          boundary: 'viewport'
        });
        bootstrapDropdowns.push(dropdown);

        // Ajouter les event listeners
        dropdownToggleEl.addEventListener('click', handleDropdownClick);
        dropdownToggleEl.addEventListener('show.bs.dropdown', handleDropdownShow);

      } catch (e) {
        console.log('Erreur lors de l\'initialisation du dropdown:', e);
      }
    });

    console.log('Dropdowns initialisés:', bootstrapDropdowns.length);
    dropdownsInitialized = true;

    // Fermer tous les dropdowns quand on clique ailleurs (une seule fois)
    if (!document.body.hasAttribute('data-dropdown-outside-listener')) {
      document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
          console.log('Clic à l\'extérieur - fermeture de tous les dropdowns');
          closeAllDropdowns();
        }
      });
      document.body.setAttribute('data-dropdown-outside-listener', 'true');
    }
  }

  // Initialiser les dropdowns une seule fois avec un délai raisonnable
  setTimeout(initializeBootstrapDropdowns, 100);
  
  // Variable pour éviter les appels multiples lors du redimensionnement
  let resizeTimeout;

  // Réinitialiser les dropdowns lors du redimensionnement
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      console.log('Redimensionnement détecté - réinitialisation des dropdowns');
      initializeBootstrapDropdowns();
    }, 250);
  });

});