// ========================================
// GESTION DES ONGLETS
// ========================================

function initializeTabs() {
  // Restaurer l'onglet actif depuis localStorage
  const activeTab = localStorage.getItem('inventory_config_active_tab');
  if (activeTab) {
    const tab = document.querySelector(`[data-bs-target="${activeTab}"]`);
    if (tab) {
      const tabInstance = new bootstrap.Tab(tab);
      tabInstance.show();
    }
  }

  // Sauvegarder l'onglet actif quand il change
  const tabElements = document.querySelectorAll('[data-bs-toggle="tab"]');
  tabElements.forEach(tab => {
    tab.addEventListener('shown.bs.tab', function(e) {
      localStorage.setItem('inventory_config_active_tab', e.target.getAttribute('data-bs-target'));
    });
  });
}

// ========================================
// FONCTIONS GLOBALES
// ========================================

// Fonction de recherche accessible globalement
function performSearch(entity, query, tbodyId) {
  const url = new URL(`/inventory/${entity}/search/`, window.location.origin);
  url.searchParams.set('q', query);

  fetch(url)
  .then(response => response.text())
  .then(html => {
      const tbody = document.getElementById(tbodyId);
      if (tbody) {
        tbody.innerHTML = html;
        // Réattacher les événements après mise à jour du contenu
        if (window.attachEventListeners) {
          window.attachEventListeners();
        }
      }
  })
  .catch(error => {
      Swal.fire({
        icon: 'error',
        title: 'Erreur de recherche',
        text: 'Impossible de charger les résultats de recherche.',
        confirmButtonColor: '#dc3545',
        confirmButtonText: 'OK'
      });
  });
}

// ========================================
// INITIALISATION PRINCIPALE
// ========================================

const entityDisplayNames = {
  'uom': "une Unité de Mesure",
  'category': "une Catégorie",
  'product_type': "un Type de Produit",
  'operation_type': "un Type d'Opération",
  'location_type': "un Type d'Emplacement",
  'location': "un Emplacement"
};

function updateFormTitle(entity, isEdit) {
  const formCard = document.getElementById(`${entity}-form-card`);
  if (formCard) {
    const titleSpan = document.getElementById(`${entity}-form-title`);
    const displayName = entityDisplayNames[entity] || "un élément";
    if (titleSpan) {
      titleSpan.textContent = isEdit ? `Modifier ${displayName}` : `Ajouter ${displayName}`;
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // ========================================
  // FONCTIONS UTILITAIRES
  // ========================================

  function showForm(formId, reset = false) {
    const formCard = document.getElementById(formId);
    if (formCard) {
      formCard.classList.remove('d-none');
      if (reset) {
        formCard.querySelectorAll('input, select, textarea').forEach(el => {
          el.value = '';
        });
      }
    }
  }

  function hideForm(formId) {
    const formCard = document.getElementById(formId);
    if (formCard) {
      formCard.classList.add('d-none');
    }
  }

  function scrollToForm(formId) {
    const formCard = document.getElementById(formId);
    if (formCard) {
      formCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setTimeout(() => {
        const firstInput = formCard.querySelector('input, select, textarea');
        if (firstInput) {
          firstInput.focus();
        }
      }, 500);
    }
}

// ========================================
  // GESTIONNAIRES D'ÉVÉNEMENTS
// ========================================

function attachEventListeners() {
    // Boutons Éditer
    document.querySelectorAll('.btn-edit-config').forEach(btn => {
      btn.addEventListener('click', function() {
        const row = this.closest('tr');
        const entity = row.closest('tbody').getAttribute('data-entity');
        const id = row.getAttribute('data-id');
        const name = row.getAttribute('data-name') || row.getAttribute('data-label'); // Support both data-name and data-label
        const symbole = row.getAttribute('data-symbole');
        const description = row.getAttribute('data-description');
        const type = row.getAttribute('data-type');
        const parent = row.getAttribute('data-parent');

        fillForm(entity, { id, name, description, symbole, type, parent });
        updateFormTitle(entity, true); // Mettre à jour le titre pour la modification
        showForm(`${entity}-form-card`);
        scrollToForm(`${entity}-form-card`);
      });
    });

    // Boutons Supprimer spécifiques
    document.querySelectorAll('.btn-uom-delete').forEach(btn => {
      btn.addEventListener('click', function() {
      const row = this.closest('tr');
      const id = row.getAttribute('data-id');
        const name = row.getAttribute('data-name') || row.getAttribute('data-label'); 
        deleteEntity('uom', id, name);
      });
    });

    document.querySelectorAll('.btn-category-delete').forEach(btn => {
      btn.addEventListener('click', function() {
        const row = this.closest('tr');
        const id = row.getAttribute('data-id');
        const name = row.getAttribute('data-name') || row.getAttribute('data-label'); 
        deleteEntity('category', id, name);
      });
    });

    document.querySelectorAll('.btn-product-type-delete').forEach(btn => {
      btn.addEventListener('click', function() {
        const row = this.closest('tr');
        const id = row.getAttribute('data-id');
        const name = row.getAttribute('data-name') || row.getAttribute('data-label'); 
        deleteEntity('product_type', id, name);
    });
  });

    document.querySelectorAll('.btn-operation-type-delete').forEach(btn => {
      btn.addEventListener('click', function() {
      const row = this.closest('tr');
      const id = row.getAttribute('data-id');
        const name = row.getAttribute('data-name') || row.getAttribute('data-label'); 
        deleteEntity('operation_type', id, name);
      });
    });

    document.querySelectorAll('.btn-location-type-delete').forEach(btn => {
      btn.addEventListener('click', function() {
        const row = this.closest('tr');
        const id = row.getAttribute('data-id');
        const name = row.getAttribute('data-name') || row.getAttribute('data-label'); 
        deleteEntity('location_type', id, name);
      });
    });

    document.querySelectorAll('.btn-location-delete').forEach(btn => {
      btn.addEventListener('click', function() {
        const row = this.closest('tr');
        const id = row.getAttribute('data-id');
        const name = row.getAttribute('data-name') || row.getAttribute('data-label'); 
        deleteEntity('location', id, name);
    });
  });
}

  // Rendre la fonction accessible globalement
  window.attachEventListeners = attachEventListeners;

// ========================================
  // REMPLISSAGE DES FORMULAIRES
// ========================================

  function fillForm(entity, data) {
    const formId = `${entity}-form`;
  const form = document.getElementById(formId);
  if (!form) {
      return;
  }

    // Remplir les champs selon l'entité
    if (data.id) {
      const idField = form.querySelector('[name="id"]');
      if (idField) {
        idField.value = data.id;
      } else {
        console.error('Champ ID non trouvé dans le formulaire');
      }
    }
    
    // Gestion spécifique pour les emplacements
    if (entity === 'location') {
      // Nom
      if (data.name) {
        const nameField = form.querySelector('[name="name"]');
        if (nameField) {
          nameField.value = data.name;
        }
      }
      
      // Type d'emplacement
      if (data.type) {
        const typeField = form.querySelector('[name="location_type"]');
        if (typeField) {
          typeField.value = data.type;
        }
      }
      
      // Parent
      if (data.parent) {
        const parentField = form.querySelector('[name="parent_location"]');
        if (parentField) {
          parentField.value = data.parent;
        }
      }
      
      // Gérer la case à cocher "Est un emplacement racine"
      const isParentCheckbox = form.querySelector('[name="is_parent"]');
      const parentGroup = document.getElementById('parent-location-group');
      if (isParentCheckbox && parentGroup) {
        // Si pas de parent, c'est un emplacement racine
        const isRoot = !data.parent || data.parent === '';
        isParentCheckbox.checked = isRoot;
        parentGroup.style.display = isRoot ? 'none' : 'block';
      }
    } else {
      // Gestion générique pour les autres entités
      if (data.name) {
        const nameField = form.querySelector('[name="label"], [name="name"]');
        if (nameField) {
          nameField.value = data.name;
        }
      }
      
      if (data.description) {
        const descField = form.querySelector('[name="description"]');
        if (descField) {
          descField.value = data.description;
        }
      }
      
      if (data.symbole) {
        const symboleField = form.querySelector('[name="symbole"]');
        if (symboleField) {
          symboleField.value = data.symbole;
        }
  }
}
}

// ========================================
  // SUPPRESSION D'ENTITÉS
// ========================================

  function deleteEntity(entity, id, name) {
  Swal.fire({
    title: 'Confirmer la suppression',
    text: `Êtes-vous sûr de vouloir supprimer "${name}" ?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Oui, supprimer',
      cancelButtonText: 'Annuler',
      confirmButtonColor: '#dc3545',
      cancelButtonColor: '#6c757d'
  }).then((result) => {
    if (result.isConfirmed) {
        const url = `/inventory/${entity}/${id}/delete/`;
  
        // Sauvegarder l'onglet actif avant le rechargement
        const activeTab = document.querySelector('.tab-pane.active');
        if (activeTab) {
          const tabId = activeTab.id;
          localStorage.setItem('inventory_config_active_tab', `#${tabId}`);
        }
  
  fetch(url, {
    method: 'POST',
    headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
            Swal.fire({
              icon: 'success',
              title: 'Suppression réussie',
              text: `${name} supprimé avec succès.`,
              confirmButtonColor: '#28a745',
              confirmButtonText: 'OK'
            }).then(() => {
              location.reload();
            });
    } else {
            Swal.fire({
              icon: 'error',
              title: 'Erreur de suppression',
              text: data.error || 'Impossible de supprimer cet élément.',
              confirmButtonColor: '#dc3545',
              confirmButtonText: 'OK'
            });
    }
  })
  .catch(error => {
          Swal.fire({
            icon: 'error',
            title: 'Erreur de suppression',
            text: 'Une erreur est survenue lors de la suppression.',
            confirmButtonColor: '#dc3545',
            confirmButtonText: 'OK'
          });
        });
      }
  });
}

// ========================================
// UTILITAIRES
// ========================================

function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// ========================================
  // INITIALISATION DES BOUTONS AJOUTER
// ========================================

function initializeAddButtons() {
  const addButtons = {
    'btn-add-uom': 'uom-form-card',
    'btn-add-category': 'category-form-card',
    'btn-add-product-type': 'product-type-form-card',
    'btn-add-operation-type': 'operation-type-form-card',
    'btn-add-location-type': 'location-type-form-card',
    'btn-add-location': 'location-form-card'
  };

  Object.entries(addButtons).forEach(([buttonId, formId]) => {
    const button = document.getElementById(buttonId);
    if (button) {
      button.addEventListener('click', () => {
        const entity = formId.replace('-form-card', '');
        updateFormTitle(entity, false); // Mettre à jour le titre pour l'ajout
        showForm(formId, true); // true to reset form
        scrollToForm(formId);
      });
    }
  });
  }

  // ========================================
  // INITIALISATION DES BOUTONS ANNULER
  // ========================================

  function initializeCancelButtons() {
  document.querySelectorAll('.btn-cancel-form').forEach(button => {
    button.addEventListener('click', () => {
        const formCard = button.closest('.form-card');
        if (formCard) {
          hideForm(formCard.id);
        }
    });
  });
}

// ========================================
  // SOUMISSION DES FORMULAIRES
// ========================================

function initializeFormSubmissions() {
    const forms = [
      'uom-form', 'category-form', 'product-type-form',
      'operation-type-form', 'location-type-form', 'location-form'
    ];

    forms.forEach(formId => {
      const form = document.getElementById(formId);
      if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const formData = new FormData(this);
          const id = formData.get('id');
          const isEdit = id && id.trim() !== '';
          const entity = getEntityFromForm(formId);
      
          // Construire l'URL correcte selon l'entité
      let url;
      if (isEdit) {
            url = `/inventory/${entity}/${id}/edit/`;
      } else {
        url = `/inventory/${entity}/add/`;
      }

      fetch(url, {
        method: 'POST',
            body: formData
          })
          .then(response => {
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
          })
      .then(data => {
        if (data.success) {
              // Sauvegarder l'onglet actif avant le rechargement
              const activeTab = document.querySelector('.tab-pane.active');
              if (activeTab) {
                const tabId = activeTab.id;
                localStorage.setItem('inventory_config_active_tab', `#${tabId}`);
              }
              
              Swal.fire({
                icon: 'success',
                title: isEdit ? 'Modification réussie' : 'Ajout réussi',
                text: data.message || 'Opération effectuée avec succès.',
                confirmButtonColor: '#28a745',
                confirmButtonText: 'OK'
              }).then(() => {
                location.reload();
              });
        } else {
              Swal.fire({
                icon: 'error',
                title: 'Erreur',
                text: data.error || 'Une erreur est survenue.',
                confirmButtonColor: '#dc3545',
                confirmButtonText: 'OK'
              });
        }
      })
      .catch(error => {
            Swal.fire({
              icon: 'error',
              title: 'Erreur',
              text: 'Une erreur est survenue lors de l\'opération.',
              confirmButtonColor: '#dc3545',
              confirmButtonText: 'OK'
      });
    });
  });
}
    });
  }

  function getEntityFromForm(formId) {
    const entityMap = {
      'uom-form': 'uom',
      'category-form': 'category',
      'product-type-form': 'product_type',
      'operation-type-form': 'operation_type',
      'location-type-form': 'location_type',
      'location-form': 'location'
    };
    return entityMap[formId] || 'uom';
  }

  // ========================================
  // GESTION DE LA CASE À COCHER "EST UN EMPLACEMENT RACINE"
  // ========================================

  function initializeLocationCheckbox() {
    const isParentCheckbox = document.getElementById('is-parent-toggle');
    const parentGroup = document.getElementById('parent-location-group');
    
    if (isParentCheckbox && parentGroup) {
      
      isParentCheckbox.addEventListener('change', function() {
        
        if (this.checked) {
          // Si cochée, cacher le groupe parent et vider le champ
          parentGroup.style.display = 'none';
          const parentSelect = document.getElementById('parent-location-select');
          if (parentSelect) {
            parentSelect.value = '';
          }
        } else {
          // Si décochée, afficher le groupe parent
          parentGroup.style.display = 'block';
        }
      });
    }
  }

  // ========================================
  // INITIALISATION PRINCIPALE
  // ========================================

  try {
    initializeAddButtons();
    initializeCancelButtons();
    initializeFormSubmissions();
    attachEventListeners();
    initializeTabs(); // Initialiser les onglets
    initializeLocationCheckbox(); // Initialiser la case à cocher
  } catch (error) {
    Swal.fire({
      icon: 'error',
      title: 'Erreur d\'initialisation',
      text: 'Une erreur est survenue lors du chargement de la page.',
      confirmButtonColor: '#dc3545',
      confirmButtonText: 'OK'
    });
  }
});