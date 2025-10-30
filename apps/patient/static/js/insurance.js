// JavaScript spécifique pour le module d'assurance

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation du module d'assurance
    initializeInsuranceModule();
});

function initializeInsuranceModule() {
    // Initialisation des formulaires d'assurance
    initializeInsuranceForms();
    
    // Initialisation des tables d'assurance
    initializeInsuranceTables();
    
    // Initialisation des événements
    initializeInsuranceEvents();
}

function initializeInsuranceForms() {
    // Gestion du formulaire d'édition d'assurance
    const insuranceEditForm = document.getElementById('mutuelle-edit-form');
    if (insuranceEditForm) {
        insuranceEditForm.addEventListener('submit', handleInsuranceFormSubmit);
    }
    
    // Gestion du bouton d'annulation
    const cancelInsuranceEditBtn = document.getElementById('cancel-mutuelle-edit');
    if (cancelInsuranceEditBtn) {
        cancelInsuranceEditBtn.addEventListener('click', handleCancelInsuranceEdit);
    }
}

function initializeInsuranceTables() {
    // Initialisation des tables d'assurance si nécessaire
    // Cette fonction peut être étendue pour gérer la pagination, le tri, etc.
}

function initializeInsuranceEvents() {
    // Initialisation des événements spécifiques à l'assurance
    // Cette fonction peut être étendue pour gérer d'autres interactions
}

function handleInsuranceFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    // Supprimer insurance_name des données du formulaire si présent
    if (formData.has('insurance_name')) {
        formData.delete('insurance_name');
    }
    
    // Envoyer les données via AJAX
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Afficher un message de succès
            Swal.fire({
                icon: 'success',
                title: 'Assurance mise à jour',
                text: 'Les informations d\'assurance ont été mises à jour avec succès.',
                timer: 3000,
                showConfirmButton: false
            });
            
            // Fermer le modal si présent
            const modal = bootstrap.Modal.getInstance(document.getElementById('insuranceModal'));
            if (modal) {
                modal.hide();
            }
            
            // Recharger les données si nécessaire
            // reloadInsuranceData();
        } else {
            // Afficher les erreurs
            Swal.fire({
                icon: 'error',
                title: 'Erreur',
                text: data.error || 'Une erreur est survenue lors de la mise à jour de l\'assurance.'
            });
        }
    })
    .catch(error => {
        console.error('Erreur lors de la soumission du formulaire:', error);
        Swal.fire({
            icon: 'error',
            title: 'Erreur',
            text: 'Une erreur est survenue lors de la mise à jour de l\'assurance.'
        });
    });
}

function handleCancelInsuranceEdit() {
    // Fermer le modal d'édition d'assurance
    const modal = bootstrap.Modal.getInstance(document.getElementById('insuranceModal'));
    if (modal) {
        modal.hide();
    }
}

// Fonction utilitaire pour obtenir un cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Fonction pour recharger les données d'assurance (à implémenter si nécessaire)
// function reloadInsuranceData() {
//     // Implémentation pour recharger les données
// }
