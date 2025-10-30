// ========================================
// INITIALISATION DES DONNÉES
// ========================================

function initializeProductLocations() {
  // Initialiser les données des emplacements
  const locationsElement = document.getElementById('locations-data');
  if (locationsElement) {
    try {
      window.locationsData = JSON.parse(locationsElement.textContent);
    } catch (e) {
      window.locationsData = [];
    }
  } else {
    window.locationsData = [];
  }
  
  // Initialiser les données des emplacements de produits
  const productLocationsElement = document.getElementById('product-locations-data');
  if (productLocationsElement) {
    try {
      window.productLocations = JSON.parse(productLocationsElement.textContent);
    } catch (e) {
      window.productLocations = [];
    }
  } else {
    window.productLocations = [];
  }
}

// ========================================
// GESTION DE L'INTERFACE
// ========================================

function scrollToProductForm() {
  const formCard = document.getElementById('product-form-card');
  if (formCard) {
    formCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

// ========================================
// GESTION DES ALERTES
// ========================================

function showSuccessAlert(message) {
  if (typeof Swal !== 'undefined') {
    Swal.fire({
      icon: 'success',
      title: 'Opération réussie',
      text: message,
      confirmButtonColor: '#28a745',
      confirmButtonText: 'OK'
    });
  } else {
    // Fallback si SweetAlert2 n'est pas disponible
    alert('Succès: ' + message);
  }
}

function showErrorAlert(message) {
  if (typeof Swal !== 'undefined') {
    Swal.fire({
      icon: 'error',
      title: 'Erreur',
      text: message,
      confirmButtonColor: '#dc3545',
      confirmButtonText: 'OK'
    });
  } else {
    // Fallback si SweetAlert2 n'est pas disponible
    alert('Erreur: ' + message);
  }
}

// ========================================
// RECHERCHE AUTOMATIQUE
// ========================================

function initializeAutoSearch() {
  const searchInput = document.getElementById('product-search');
  if (searchInput) {
    let searchTimeout;
    searchInput.addEventListener('input', function() {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        if (this.form) {
          this.form.submit();
        }
      }, 500);
    });
  }
}

// ========================================
// GESTION DES MESSAGES DE SESSION
// ========================================

function handleSessionMessages() {
  // Vérifier si on a déjà affiché un message pour cette session
  const sessionKey = 'pharmacy_products_success_shown';
  const currentUrl = window.location.href;
  const lastShownUrl = sessionStorage.getItem(sessionKey);
  
  // Vérifier si on a des messages de session à afficher
  if (window.swalSuccess && window.swalSuccess.trim() !== '') {
    // Ne montrer le message que si on n'a pas déjà montré pour cette URL
    if (lastShownUrl !== currentUrl) {
      showSuccessAlert(window.swalSuccess);
      sessionStorage.setItem(sessionKey, currentUrl);
    }
    // Nettoyer le message pour éviter les répétitions
    window.swalSuccess = null;
  }
  
  if (window.swalError && window.swalError.trim() !== '') {
    // Ne montrer le message que si on n'a pas déjà montré pour cette URL
    if (lastShownUrl !== currentUrl) {
      showErrorAlert(window.swalError);
      sessionStorage.setItem(sessionKey, currentUrl);
    }
    // Nettoyer le message pour éviter les répétitions
    window.swalError = null;
  }
  
  // Traiter les messages Django
  handleDjangoMessages();
}

function handleDjangoMessages() {
  const messagesContainer = document.getElementById('django-messages');
  console.log('Messages container:', messagesContainer); // Debug log
  
  if (messagesContainer) {
    const messages = messagesContainer.querySelectorAll('.message');
    console.log('Found messages:', messages.length); // Debug log
    
    messages.forEach(message => {
      const level = message.getAttribute('data-level');
      const text = message.getAttribute('data-text');
      
      if (level === 'success' || level === 'info') {
        showSuccessAlert(text);
      } else if (level === 'error' || level === 'danger') {
        showErrorAlert(text);
      } else if (level === 'warning') {
        if (typeof Swal !== 'undefined') {
          Swal.fire({
            icon: 'warning',
            title: 'Attention',
            text: text,
            confirmButtonColor: '#ffc107',
            confirmButtonText: 'OK'
          });
        } else {
          alert('Attention: ' + text);
        }
      }
    });
    
    // Supprimer les messages après les avoir affichés
    messagesContainer.remove();
  }
}

// ========================================
// TRI & BOUTON IMPORT/EXPORT
// ========================================

// Initialiser le tri serveur sur les en-têtes de colonnes
function initializeTableSorting() {
  const productTable = document.getElementById('searchableTable');
  if (!productTable) return;

  const headers = productTable.querySelectorAll('th[data-sort-field]');
  const urlParams = new URLSearchParams(window.location.search);
  const currentSortBy = urlParams.get('sort_by');
  const currentSortOrder = urlParams.get('sort_order');

  // Mettre à jour les icônes selon l'état courant
  if (currentSortBy && currentSortOrder) {
    headers.forEach(header => {
      const sortField = header.getAttribute('data-sort-field');
      const sortIcon  = header.querySelector('.fas');
      if (!sortIcon) return;
      if (sortField === currentSortBy) {
        header.setAttribute('data-sort-direction', currentSortOrder);
        sortIcon.className = currentSortOrder === 'asc'
          ? 'fas fa-sort-up ms-1 text-primary'
          : 'fas fa-sort-down ms-1 text-primary';
      } else {
        header.setAttribute('data-sort-direction', 'none');
        sortIcon.className = 'fas fa-sort ms-1 text-muted';
      }
    });
  }

  headers.forEach(header => {
    const sortIcon = header.querySelector('.fas');
    if (!sortIcon) return;
    header.style.cursor = 'pointer';
    if (!header.getAttribute('data-sort-direction')) header.setAttribute('data-sort-direction', 'none');

    header.addEventListener('click', e => {
      e.preventDefault();
      const sortField = header.getAttribute('data-sort-field');
      const curParams = new URLSearchParams(window.location.search);
      const curSortBy = curParams.get('sort_by');
      const curSortOrder = curParams.get('sort_order');
      let newDir = 'asc';
      if (curSortBy === sortField) newDir = curSortOrder === 'asc' ? 'desc' : 'asc';

      const newUrl = new URL(window.location);
      newUrl.searchParams.set('sort_by', sortField);
      newUrl.searchParams.set('sort_order', newDir);
      newUrl.searchParams.set('page', '1');
      newUrl.hash = '';
      window.location.href = newUrl.toString();
    });
  });
}

// Gérer le bouton dynamique Import/Export
function initializeDynamicExportButton() {
  const importBtn = document.getElementById('importBtn');
  const exportLink = document.getElementById('exportLink');
  const selectAllCheckbox = document.getElementById('selectAll');
  if (!importBtn || !exportLink) return;

  function updateExportUrl(checkedBoxes) {
    const baseUrl = exportLink.href.split('?')[0];
    const url = new URL(baseUrl, window.location.origin);

    if (checkedBoxes.length) {
      const ids = Array.from(checkedBoxes)
        .map(cb => cb.closest('tr').getAttribute('data-product-id'))
        .filter(Boolean);
      url.searchParams.set('ids', ids.join(','));
    }

    const searchInput = document.getElementById('product-search');
    const formSelect  = document.querySelector('select[name="pharmaceutical_form"]');
    if (searchInput && searchInput.value) url.searchParams.set('q', searchInput.value);
    if (formSelect && formSelect.value)   url.searchParams.set('pharmaceutical_form', formSelect.value);

    const curParams = new URLSearchParams(window.location.search);
    const sortBy = curParams.get('sort_by');
    const sortOrder = curParams.get('sort_order');
    if (sortBy)   url.searchParams.set('sort_by', sortBy);
    if (sortOrder) url.searchParams.set('sort_order', sortOrder);

    exportLink.href = url.toString();
  }

  function updateButtonState() {
    const checked = document.querySelectorAll('.row-check:checked');
    if (checked.length) {
      importBtn.style.display = 'none';
      exportLink.style.display = 'inline-block';
      const span = exportLink.querySelector('span');
      if (span) span.textContent = `Exporter (${checked.length})`;
      updateExportUrl(checked);
    } else {
      importBtn.style.display = 'inline-block';
      exportLink.style.display = 'none';
      const span = exportLink.querySelector('span');
      if (span) span.textContent = 'Exporter';
    }
  }

  // Listeners
  document.querySelectorAll('.row-check').forEach(cb => {
    cb.addEventListener('change', updateButtonState);
  });

  if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener('change', () => {
      document.querySelectorAll('.row-check').forEach(cb => { cb.checked = selectAllCheckbox.checked; });
      updateButtonState();
    });
  }

  // Init
  updateButtonState();

  // ========================================
  // GESTION DU SELECT ALL ET CONFIRMATION
  // ========================================
  const rowCheckboxes = document.querySelectorAll('.row-check');
  // Function to reset to import mode (used on cancel)
  function resetToImportMode() {
    rowCheckboxes.forEach(cb => { cb.checked = false; });
    if (selectAllCheckbox) selectAllCheckbox.checked = false;
    clearSelectAllState();
    updateButtonState();
  }

  // Confirmation when user checks selectAll
  if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener('change', function() {
      if (this.checked) {
        Swal.fire({
          title: 'Sélectionner tous les éléments ?',
          text: 'Voulez-vous sélectionner tous les éléments filtrés (sur toutes les pages) ou seulement ceux de cette page ?',
          icon: 'question',
          showCancelButton: true,
          showDenyButton: true,
          confirmButtonText: 'Tous les éléments',
          denyButtonText: 'Cette page seulement',
          cancelButtonText: 'Annuler',
          confirmButtonColor: '#3085d6',
          denyButtonColor: '#1e90ff'
        }).then(result => {
          if (result.isConfirmed) {
            selectAllFilteredItems();
          } else if (result.isDenied) {
            rowCheckboxes.forEach(cb => { cb.checked = true; });
            updateButtonState();
          } else {
            this.checked = false;
          }
        });
      } else {
        rowCheckboxes.forEach(cb => { cb.checked = false; });
        clearSelectAllState();
        updateButtonState();
      }
    });
  }

  // Update selectAll indeterminate state on individual checkbox change
  rowCheckboxes.forEach(cb => {
    cb.addEventListener('change', function() {
      if (!selectAllCheckbox) return;
      const allChecked = Array.from(rowCheckboxes).every(box => box.checked);
      const noneChecked = Array.from(rowCheckboxes).every(box => !box.checked);
      if (allChecked) {
        selectAllCheckbox.checked = true;
        selectAllCheckbox.indeterminate = false;
      } else if (noneChecked) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
      } else {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = true;
      }
    });
  });

  // ================= Helper functions for select all ================
  function selectAllFilteredItems() {
    const searchInput = document.getElementById('product-search');
    const formSelect  = document.querySelector('select[name="pharmaceutical_form"]');
    const q  = searchInput ? searchInput.value : '';
    const form = formSelect ? formSelect.value : '';
    sessionStorage.setItem('ph_selectAll', 'true');
    sessionStorage.setItem('ph_q', q);
    sessionStorage.setItem('ph_form', form);
    rowCheckboxes.forEach(cb => { cb.checked = true; });
    updateButtonStateForSelectAll();
    Swal.fire({ icon:'success', title:'Sélection totale', text:'Tous les éléments filtrés seront exportés', timer:2000, showConfirmButton:false });
  }

  function clearSelectAllState() {
    sessionStorage.removeItem('ph_selectAll');
    sessionStorage.removeItem('ph_q');
    sessionStorage.removeItem('ph_form');
  }
  function isSelectAllMode() {
    return sessionStorage.getItem('ph_selectAll') === 'true';
  }
  function updateExportUrlForSelectAll() {
    const baseUrl = exportLink.href.split('?')[0];
    const url = new URL(baseUrl, window.location.origin);
    url.searchParams.set('select_all', 'true');
    const searchInput = document.getElementById('product-search');
    const formSelect  = document.querySelector('select[name="pharmaceutical_form"]');
    if (searchInput && searchInput.value) url.searchParams.set('q', searchInput.value);
    if (formSelect && formSelect.value)   url.searchParams.set('pharmaceutical_form', formSelect.value);
    const curParams = new URLSearchParams(window.location.search);
    const sb = curParams.get('sort_by');
    const so = curParams.get('sort_order');
    if (sb) url.searchParams.set('sort_by', sb);
    if (so) url.searchParams.set('sort_order', so);
    exportLink.href = url.toString();
  }
  function updateButtonStateForSelectAll() {
    importBtn.style.display = 'none';
    exportLink.style.display = 'inline-block';
    const span = exportLink.querySelector('span');
    if (span) span.textContent = 'Exporter (Tous)';
    updateExportUrlForSelectAll();
  }

  // Maintain state on load
  if (isSelectAllMode()) {
    const searchInput = document.getElementById('product-search');
    const formSelect = document.querySelector('select[name="pharmaceutical_form"]');
    const storedQ = sessionStorage.getItem('ph_q') || '';
    const storedForm = sessionStorage.getItem('ph_form') || '';
    if ((searchInput && searchInput.value !== storedQ) || (formSelect && formSelect.value !== storedForm)) {
      clearSelectAllState();
    } else {
      updateButtonStateForSelectAll();
    }
  }
}


// ========================================
// INITIALISATION PRINCIPALE
// ========================================

// Fonction pour vérifier si SweetAlert2 est disponible
function waitForSweetAlert(callback, maxAttempts = 50) {
  let attempts = 0;
  const checkInterval = setInterval(() => {
    attempts++;
    if (typeof Swal !== 'undefined') {
      clearInterval(checkInterval);
      callback();
    } else if (attempts >= maxAttempts) {
      clearInterval(checkInterval);
      console.warn('SweetAlert2 non disponible après 5 secondes');
      callback(); // Exécuter quand même avec fallback
    }
  }, 100);
}

document.addEventListener('DOMContentLoaded', function() {
  try {
    initializeProductLocations();
    
    // Scroll vers le formulaire si en mode édition
    if (window.location.hash === '#product-form-card') {
      scrollToProductForm();
    }
    
    // Initialiser la recherche automatique
    initializeAutoSearch();
    // Initialiser le tri et les actions Import/Export
    initializeTableSorting();
    initializeDynamicExportButton();
    
    // Attendre que SweetAlert2 soit chargé, puis gérer les messages
    waitForSweetAlert(() => {
      handleSessionMessages();
    });
    
  } catch (error) {
    console.error('Erreur lors de l\'initialisation:', error);
  }
}); 