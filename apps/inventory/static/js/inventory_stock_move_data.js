// ========================================
// INITIALISATION DES DONNÉES
// ========================================

function initializeStockMoveData() {
  // Initialiser les données de stock par produit/emplacement
  const stockElement = document.getElementById('stock-by-product-location');
  if (stockElement) {
    try {
      window.stockByProductLocation = JSON.parse(stockElement.textContent);
    } catch (e) {
      window.stockByProductLocation = {};
    }
  } else {
    // Retry after a short delay
    setTimeout(() => {
      const retryElement = document.getElementById('stock-by-product-location');
      if (retryElement) {
        try {
          window.stockByProductLocation = JSON.parse(retryElement.textContent);
        } catch (e) {
          window.stockByProductLocation = {};
        }
      } else {
        window.stockByProductLocation = {};
      }
    }, 100);
  }
  
  // Initialiser les données des produits
  const productsElement = document.getElementById('products-data');
  if (productsElement) {
    try {
      window.productsData = JSON.parse(productsElement.textContent);
    } catch (e) {
      window.productsData = [];
    }
  }
  
  // Initialiser les lignes de mouvement si elles existent
  const moveLinesElement = document.getElementById('move-lines-data');
  if (moveLinesElement) {
    try {
      window.moveLinesData = JSON.parse(moveLinesElement.textContent);
    } catch (e) {
      window.moveLinesData = [];
    }
  }
}

// ========================================
// GESTION DES ERREURS
// ========================================

function showFormErrors(errors) {
  Swal.fire({
    icon: 'error',
    title: 'Erreur de formulaire',
    text: errors,
    confirmButtonColor: '#dc3545',
    confirmButtonText: 'OK'
  });
}

function handleJavaScriptError(error) {
  Swal.fire({
    icon: 'error',
    title: 'Erreur JavaScript',
    text: error && error.message ? error.message : 'Une erreur inattendue s\'est produite.',
    confirmButtonColor: '#dc3545',
    confirmButtonText: 'OK'
  });
}

// ========================================
// CONFIGURATION SELECT2
// ========================================

function initializeSelect2() {
  if (window.jQuery && $.fn.select2) {
    $('#id_operation_type, #department-select, #supplier-select, #order-select')
      .select2({ 
        allowClear: true, 
        placeholder: 'Sélectionner' 
      });
  }
}

// ========================================
// GESTION DES CHAMPS CONDITIONNELS
// ========================================

function toggleFieldsByOperationType() {
  const opType = document.getElementById('id_operation_type');
  const srcCol = document.getElementById('source-location-col');
  const dstCol = document.getElementById('dest-location-col');
  const deptF = document.getElementById('department-field');
  const suppF = document.getElementById('supplier-field');
  const ordF = document.getElementById('order-field');
  const moveForm = document.getElementById('move-form');
  
  if (!opType) return;
  
  // Détection édition ou création
  const isEdit = !!(moveForm && moveForm.getAttribute('data-state') && 
                   moveForm.getAttribute('data-state') !== 'draft');
  
  function normalizeString(str) {
    return str
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/\s+/g, ' ')
      .trim();
  }
  
  function toggle() {
    const label = normalizeString(opType.options[opType.selectedIndex].text.toLowerCase());
    const isReception = label.includes('reception') || label.includes('réception');
    const isCons = label.includes('consommation');
    const isTransfert = label.includes('transfert');

    // Affichage conditionnel
    if (srcCol) srcCol.style.setProperty('display', isReception ? 'none' : 'block', 'important');
    if (dstCol) dstCol.style.setProperty('display', isCons ? 'none' : 'block', 'important');
    if (deptF) deptF.style.setProperty('display', isCons ? 'block' : 'none', 'important');
    if (suppF) suppF.style.setProperty('display', isReception ? 'block' : 'none', 'important');
    if (ordF) ordF.style.setProperty('display', (isReception && !isEdit) ? 'block' : 'none', 'important');
  }
  
  // Initialiser et écouter les changements
  toggle();
  opType.addEventListener('change', toggle);
}

// ========================================
// GESTION DES MESSAGES
// ========================================

function showMessages() {
  // Messages de succès
  if (window.swalSuccess && window.swalSuccess.trim() !== '') {
    Swal.fire({
      icon: 'success',
      title: 'Succès !',
      text: window.swalSuccess,
      confirmButtonColor: '#28a745',
      confirmButtonText: 'OK'
    });
    window.swalSuccess = null;
  }
  
  // Messages d'erreur
  if (window.swalError && window.swalError.trim() !== '') {
    Swal.fire({
      icon: 'error',
      title: 'Erreur !',
      text: window.swalError,
      confirmButtonColor: '#dc3545',
      confirmButtonText: 'OK'
    });
    window.swalError = null;
  }
}

// Fonction pour afficher les messages immédiatement si SweetAlert est disponible
function showMessagesImmediately() {
  if (typeof Swal !== 'undefined') {
    showMessages();
  } else {
    // Si SweetAlert n'est pas encore chargé, attendre un peu
    setTimeout(showMessagesImmediately, 100);
  }
}

// ========================================
// CONFIRMATIONS DE SUPPRESSION
// ========================================

function initializeDeleteConfirmations() {
  document.querySelectorAll('.btn-delete-move').forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const moveId = this.getAttribute('data-id');
      const moveRef = this.getAttribute('data-ref');
      
      Swal.fire({
        title: 'Confirmer la suppression',
        text: `Êtes-vous sûr de vouloir supprimer le mouvement "${moveRef}" ?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Oui, supprimer',
        cancelButtonText: 'Annuler',
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d'
      }).then((result) => {
        if (result.isConfirmed) {
          const form = document.createElement('form');
          form.method = 'POST';
          form.action = `/inventory/stock-moves/${moveId}/delete/`;
          form.innerHTML = `<input type="hidden" name="csrfmiddlewaretoken" value="${document.querySelector('[name=csrfmiddlewaretoken]').value}">`;
          document.body.appendChild(form);
          form.submit();
        }
      });
    });
  });
}

// RECHERCHE AUTOMATIQUE
// ========================================

function initializeAutoSearch() {
  const searchInput = document.getElementById('search-input');
  const searchForm = document.getElementById('search-form');
  
  if (searchInput && searchForm) {
    let searchTimeout;
    
    // Ajouter la classe de chargement
    function setLoading(isLoading) {
      const searchContainer = searchInput.closest('.input-group');
      if (searchContainer) {
        if (isLoading) {
          searchContainer.classList.add('search-loading', 'active');
        } else {
          searchContainer.classList.remove('active');
          // Laisser la classe search-loading pour le style
        }
      }
    }
    
    // Fonction pour effectuer la recherche via AJAX
    function performSearch(query) {
      if (query === undefined || query === '') {
        // Si la recherche est vide, recharger la page sans paramètres
        window.location.href = window.location.pathname;
        return;
      }
      
      setLoading(true);
      
      // Récupérer les paramètres actuels
      const urlParams = new URLSearchParams(window.location.search);
      const state = document.getElementById('state_filter')?.value || '';
      const operationType = document.getElementById('operation-type-filter')?.value || '';
      
      // Construire l'URL de la requête
      let searchUrl = `${window.location.pathname}?search=${encodeURIComponent(query)}`;
      if (state) searchUrl += `&state=${state}`;
      if (operationType) searchUrl += `&operation_type=${encodeURIComponent(operationType)}`;
      
      // Effectuer la requête AJAX
      fetch(searchUrl, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'text/html'
        }
      })
      .then(response => response.text())
      .then(html => {
        // Mettre à jour le contenu de la page avec les résultats
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // Mettre à jour le tableau
        const newTable = doc.querySelector('.table-responsive');
        if (newTable) {
          const currentTable = document.querySelector('.table-responsive');
          if (currentTable) {
            currentTable.innerHTML = newTable.innerHTML;
          }
        }
        
        // Mettre à jour la pagination
        const newPagination = doc.querySelector('.pagination');
        const paginationContainer = document.querySelector('.pagination-container') || 
                                 document.createElement('div');
        
        if (newPagination) {
          if (!paginationContainer.parentNode) {
            // Si le conteneur de pagination n'existe pas, l'ajouter après le tableau
            const tableContainer = document.querySelector('.table-responsive').parentNode;
            tableContainer.appendChild(paginationContainer);
          }
          paginationContainer.innerHTML = newPagination.outerHTML;
        } else {
          // Si pas de pagination, vider le conteneur
          if (paginationContainer) {
            paginationContainer.innerHTML = '';
          }
        }
        
        // Mettre à jour l'URL sans recharger la page
        window.history.pushState({}, '', searchUrl);
      })
      .catch(error => {
        console.error('Erreur lors de la recherche:', error);
        // En cas d'erreur, soumettre le formulaire normalement
        searchForm.submit();
      })
      .finally(() => {
        setLoading(false);
      });
    }
    
    // Gestionnaire d'événements pour la saisie
    searchInput.addEventListener('input', function() {
      clearTimeout(searchTimeout);
      const query = this.value;
      
      // Si le champ est vide, recharger immédiatement
      if (!query || query.trim() === '') {
        performSearch('');
        return;
      }
      
      // Sinon, attendre un peu avant de lancer la recherche
      searchTimeout = setTimeout(() => {
        performSearch(query);
      }, 300);
    });
    
    // Gestion du bouton de réinitialisation de la recherche
    const resetButton = searchInput.nextElementSibling;
    if (resetButton && resetButton.classList.contains('input-group-text') && resetButton.querySelector('i')) {
      resetButton.addEventListener('click', function() {
        searchInput.value = '';
        performSearch('');
      });
    }
  }
}

// ========================================
// INITIALISATION PRINCIPALE
// ========================================

document.addEventListener('DOMContentLoaded', function() {
  try {
    initializeStockMoveData();
    initializeSelect2();
    toggleFieldsByOperationType();
    showMessages();
    initializeDeleteConfirmations();
    initializeAutoSearch();
  } catch (error) {
    handleJavaScriptError(error);
  }
});