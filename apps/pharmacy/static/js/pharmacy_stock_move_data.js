// ========================================
// INITIALISATION DES DONNÉES
// ========================================

function initializeStockMoveData() {
    // Initialiser les données de stock par produit/poste
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
            form.action = `/pharmacy/stock-moves/${moveId}/delete/`;
            form.innerHTML = `<input type="hidden" name="csrfmiddlewaretoken" value="${document.querySelector('[name=csrfmiddlewaretoken]').value}">`;
            document.body.appendChild(form);
            form.submit();
          }
        });
      });
    });
  }
  
  // ========================================
  // RECHERCHE AUTOMATIQUE
  // ========================================
  
  function initializeAutoSearch() {
    const searchInput = document.getElementById('move-search');
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
  // INITIALISATION PRINCIPALE
  // ========================================
  
  document.addEventListener('DOMContentLoaded', function() {
    try {
      initializeStockMoveData();
      toggleFieldsByOperationType();
      showMessages();
      initializeDeleteConfirmations();
      initializeAutoSearch();
    } catch (error) {
      handleJavaScriptError(error);
    }
  });  