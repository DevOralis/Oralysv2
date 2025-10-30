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
  }
  
  // Initialiser les données des emplacements de produits
  const productLocationsElement = document.getElementById('product-locations-data');
  if (productLocationsElement) {
    try {
      const content = productLocationsElement.textContent.trim();
      window.productLocations = content ? JSON.parse(content) : [];
    } catch (e) {
      console.warn('Erreur lors du parsing des données product-locations:', e);
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
  Swal.fire({
    icon: 'success',
    title: 'Opération réussie',
    text: message,
    confirmButtonColor: '#28a745',
    confirmButtonText: 'OK'
  }).then(() => {
    // Après fermeture du SweetAlert, rester en haut de la page
    window.scrollTo(0, 0);
    // Supprimer le hash pour éviter le défilement automatique
    if (window.location.hash === '#product-form-card') {
      history.replaceState(null, '', window.location.pathname + window.location.search);
    }
  });
}

function showErrorAlert(message) {
  Swal.fire({
    icon: 'error',
    title: 'Erreur',
    text: message,
    confirmButtonColor: '#dc3545',
    confirmButtonText: 'OK'
  });
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
  // Vérifier si on a des messages de session à afficher
  if (window.swalSuccess && window.swalSuccess.trim() !== '') {
    showSuccessAlert(window.swalSuccess);
    // Nettoyer le message pour éviter les répétitions
    window.swalSuccess = null;
  }
  
  if (window.swalError && window.swalError.trim() !== '') {
    showErrorAlert(window.swalError);
    // Nettoyer le message pour éviter les répétitions
    window.swalError = null;
  }
}

// ========================================
// INITIALISATION PRINCIPALE
// ========================================

document.addEventListener('DOMContentLoaded', function() {
  try {
    initializeProductLocations();
    
    // Défilement conditionnel : uniquement sur les routes d'ajout/édition
    const shouldAutoScroll = () => {
      if (window.location.hash !== '#product-form-card') return false;
      const path = window.location.pathname;
      return /\/products\/add\/$/.test(path) || /\/products\/\d+\/edit\//.test(path);
    };
    // Si hash présent mais page liste (pas d'ajout/édition), on l'enlève et revient en haut
    if (window.location.hash === '#product-form-card' && !shouldAutoScroll()) {
      history.replaceState(null, '', window.location.pathname + window.location.search);
      window.scrollTo(0, 0);
    }
    
    // Si l'URL contient le hash du formulaire lors du chargement initial,
    // faire défiler vers la carte du formulaire après que le DOM est prêt.
    if (shouldAutoScroll()) {
      setTimeout(scrollToProductForm, 50);
    } else {
      // S'assurer que la page liste reste en haut
      window.scrollTo(0, 0);
    }

    // Réagir aux changements de hash (ex. nouvel appui sur "Nouveau produit")
    window.addEventListener('hashchange', function () {
      if (window.location.hash === '#product-form-card') {
        if (shouldAutoScroll()) {
          scrollToProductForm();
        } else {
          history.replaceState(null, '', window.location.pathname + window.location.search);
        }
      }
    });
    
    initializeAutoSearch();
    handleSessionMessages();
    
  } catch (error) {
    console.error('Erreur lors de l\'initialisation:', error);
  }
}); 