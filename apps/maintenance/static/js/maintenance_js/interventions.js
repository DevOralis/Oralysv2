/**
 * Gestion des interventions - Maintenance
 * Gère l'édition, l'ajout et la suppression des interventions
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeInterventionModals();
    initializeSearch();
    initializeDeleteModal();
});

/**
 * Initialise les modals d'édition des interventions
 */
function initializeInterventionModals() {
    const modalEdit = document.getElementById('modalInterventionEdit');
    if (modalEdit) {
        modalEdit.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            loadInterventionData(button);
        });
    }
}

/**
 * Charge les données d'une intervention dans le modal d'édition
 */
function loadInterventionData(button) {
    try {
        // Récupérer les données de l'intervention
        const interventionData = {
            id: button.getAttribute('data-intervention-id'),
            equipement: button.getAttribute('data-equipement-id'),
            prestataire: button.getAttribute('data-prestataire-id'),
            date: button.getAttribute('data-date-intervention'),
            type: button.getAttribute('data-type-intervention'),
            criticite: button.getAttribute('data-criticite'),
            statut: button.getAttribute('data-statut'),
            description: button.getAttribute('data-description')
        };
        
        // Vérifier que l'ID est présent
        if (!interventionData.id) {
            console.error('ID de l\'intervention manquant');
            showAlert('Erreur: ID de l\'intervention manquant', 'danger');
            return;
        }
        
        // Remplir le formulaire avec les données
        fillEditForm(interventionData);
        
        // Log des données pour debug
        console.log('Données de l\'intervention chargées:', interventionData);
        
    } catch (error) {
        console.error('Erreur lors du chargement des données:', error);
        showAlert('Erreur lors du chargement des données', 'danger');
    }
}

/**
 * Remplit le formulaire d'édition avec les données de l'intervention
 */
function fillEditForm(data) {
    const formFields = {
        'edit_intervention_id': data.id,
        'edit_equipement': data.equipement || '',
        'edit_prestataire': data.prestataire || '',
        'edit_date_intervention': data.date || '',
        'edit_type_intervention': data.type || '',
        'edit_criticite': data.criticite || '',
        'edit_statut': data.statut || '',
        'edit_description': data.description || ''
    };
    
    // Remplir chaque champ
    Object.keys(formFields).forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.value = formFields[fieldId];
        } else {
            console.warn(`Champ non trouvé: ${fieldId}`);
        }
    });
}

/**
 * Initialise la recherche
 */
function initializeSearch() {
    const searchInput = document.getElementById('intervention-search');
    if (searchInput) {
        // Soumettre le formulaire en appuyant sur Entrée
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                submitSearchForm(this);
            }
        });

        // Soumettre automatiquement après un délai (recherche en temps réel)
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.length >= 2 || this.value.length === 0) {
                    submitSearchForm(this);
                }
            }, 500);
        });
    }
}

/**
 * Soumet le formulaire de recherche
 */
function submitSearchForm(searchInput) {
    const form = searchInput.closest('form');
    if (form) {
        form.submit();
    }
}

/**
 * Initialise le modal de suppression
 */
function initializeDeleteModal() {
    const modalDelete = document.getElementById('modalDeleteIntervention');
    if (modalDelete) {
        modalDelete.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            loadDeleteData(button);
        });
    }
}

/**
 * Charge les données pour la suppression
 */
function loadDeleteData(button) {
    try {
        const interventionId = button.getAttribute('data-intervention-id');
        const equipementNom = button.getAttribute('data-intervention-equipement');
        
        if (!interventionId) {
            console.error('ID de l\'intervention manquant pour la suppression');
            showAlert('Erreur: ID de l\'intervention manquant', 'danger');
            return;
        }
        
        // Remplir les champs du modal de suppression
        const idField = document.getElementById('delete_intervention_id');
        const equipementField = document.getElementById('delete_intervention_equipement');
        
        if (idField) idField.value = interventionId;
        if (equipementField) equipementField.textContent = equipementNom || 'cet équipement';
        
    } catch (error) {
        console.error('Erreur lors du chargement des données de suppression:', error);
        showAlert('Erreur lors du chargement des données', 'danger');
    }
}

/**
 * Affiche une alerte
 */
function showAlert(message, type = 'info') {
    // Créer l'alerte
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insérer l'alerte au début du contenu
    const container = document.querySelector('.container-fluid');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-fermer après 5 secondes
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

/**
 * Valide le formulaire d'édition
 */
function validateEditForm() {
    const requiredFields = [
        'edit_intervention_id',
        'edit_equipement',
        'edit_date_intervention',
        'edit_type_intervention',
        'edit_criticite',
        'edit_statut'
    ];
    
    let isValid = true;
    const errors = [];
    
    requiredFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field && !field.value.trim()) {
            isValid = false;
            errors.push(`Le champ ${field.previousElementSibling?.textContent || fieldId} est requis`);
        }
    });
    
    if (!isValid) {
        showAlert('Veuillez remplir tous les champs obligatoires', 'warning');
        console.error('Erreurs de validation:', errors);
    }
    
    return isValid;
}

/**
 * Soumet le formulaire d'édition avec validation
 */
function submitEditForm() {
    if (validateEditForm()) {
        const form = document.querySelector('#modalInterventionEdit form');
        if (form) {
            form.submit();
        }
    }
}

