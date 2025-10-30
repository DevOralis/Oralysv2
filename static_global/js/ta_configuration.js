// Configuration des activités thérapeutiques
document.addEventListener('DOMContentLoaded', function() {
    // Variables globales
    let currentEditingId = null;
    let currentEditingType = null; // 'activity_type' ou 'location'

    // Gestion des types d'activités
    const activityTypeForm = document.getElementById('activity-type-form');
    const activityTypeFormCard = document.getElementById('activity-type-form-card');
    const activityTypeFormTitle = document.getElementById('activity-type-form-title');
    const btnAddActivityType = document.getElementById('btn-add-activity-type');

    // Gestion des salles
    const locationForm = document.getElementById('location-form');
    const locationFormCard = document.getElementById('location-form-card');
    const locationFormTitle = document.getElementById('location-form-title');
    const btnAddLocation = document.getElementById('btn-add-location');

    // Event listeners pour les types d'activités
    if (btnAddActivityType) {
        btnAddActivityType.addEventListener('click', function() {
            showActivityTypeForm();
        });
    }

    if (activityTypeForm) {
        activityTypeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitActivityTypeForm();
        });
    }

    // Event listeners pour les salles
    if (btnAddLocation) {
        btnAddLocation.addEventListener('click', function() {
            showLocationForm();
        });
    }

    if (locationForm) {
        locationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitLocationForm();
        });
    }

    // Event listeners pour les boutons d'édition des types d'activités
    document.addEventListener('click', function(e) {
        if (e.target.closest('.edit-activity-type-btn')) {
            const btn = e.target.closest('.edit-activity-type-btn');
            const id = btn.dataset.id;
            const name = btn.dataset.name;
            const description = btn.dataset.description;
            const isActive = btn.dataset.isActive === 'true';
            
            editActivityType(id, name, description, isActive);
        }

        if (e.target.closest('.edit-location-btn')) {
            const btn = e.target.closest('.edit-location-btn');
            const id = btn.dataset.id;
            const name = btn.dataset.name;
            const address = btn.dataset.address;
            const capacity = btn.dataset.capacity;
            const isActive = btn.dataset.isActive === 'true';
            
            editLocation(id, name, address, capacity, isActive);
        }

        if (e.target.closest('.btn-cancel-form')) {
            hideAllForms();
        }
    });

    // Fonctions pour les types d'activités
    function showActivityTypeForm(id = null, name = '', description = '', isActive = true) {
        currentEditingType = 'activity_type';
        currentEditingId = id;
        
        // Remplir le formulaire
        const form = activityTypeForm;
        form.querySelector('input[name="id"]').value = id || '';
        form.querySelector('input[name="name"]').value = name;
        form.querySelector('textarea[name="description"]').value = description;
        form.querySelector('input[name="is_active"]').checked = isActive;
        
        // Mettre à jour le titre
        activityTypeFormTitle.textContent = id ? 'Modifier le type d\'activité' : 'Ajouter un type d\'activité';
        
        // Afficher le formulaire
        hideAllForms();
        activityTypeFormCard.classList.remove('d-none');
        activityTypeFormCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Focus sur le premier champ
        form.querySelector('input[name="name"]').focus();
    }

    function editActivityType(id, name, description, isActive) {
        showActivityTypeForm(id, name, description, isActive);
    }

    function submitActivityTypeForm() {
        const form = activityTypeForm;
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            if (key === 'is_active') {
                data[key] = form.querySelector('input[name="is_active"]').checked;
            } else {
                data[key] = value;
            }
        }
        
        // Récupérer l'ID depuis le champ hidden ou currentEditingId
        const editingId = form.querySelector('input[name="id"]').value || currentEditingId;
        
        // S'assurer que l'ID est inclus pour les modifications
        if (editingId) {
            data['id'] = editingId;
            currentEditingId = editingId; // S'assurer que currentEditingId est défini
        }

        const url = editingId ? 
            `/therapeutic_activities/api/activity-types/${editingId}/update/` :
            '/therapeutic_activities/api/activity-types/create/';

        // Debug: log l'URL qui sera appelée
        console.log('URL appelée:', url, 'EditingId:', editingId);

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Succès',
                    text: data.message,
                    timer: 2000,
                    showConfirmButton: false
                });
                hideAllForms();
                setTimeout(() => location.reload(), 1000);
            } else {
                let errorMessage = data.message || 'Une erreur est survenue';
                if (data.errors) {
                    errorMessage += '\n' + Object.values(data.errors).flat().join('\n');
                }
                Swal.fire({
                    icon: 'error',
                    title: 'Erreur',
                    text: errorMessage
                });
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            Swal.fire({
                icon: 'error',
                title: 'Erreur',
                text: 'Une erreur est survenue lors de l\'enregistrement.'
            });
        });
    }

    // Fonctions pour les salles
    function showLocationForm(id = null, name = '', address = '', capacity = '', isActive = true) {
        currentEditingType = 'location';
        currentEditingId = id;
        
        // Remplir le formulaire
        const form = locationForm;
        form.querySelector('input[name="id"]').value = id || '';
        form.querySelector('input[name="name"]').value = name;
        form.querySelector('input[name="address"]').value = address;
        form.querySelector('input[name="capacity"]').value = capacity;
        form.querySelector('input[name="is_active"]').checked = isActive;
        
        // Mettre à jour le titre
        locationFormTitle.textContent = id ? 'Modifier la salle' : 'Ajouter une salle';
        
        // Afficher le formulaire
        hideAllForms();
        locationFormCard.classList.remove('d-none');
        locationFormCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Focus sur le premier champ
        form.querySelector('input[name="name"]').focus();
    }

    function editLocation(id, name, address, capacity, isActive) {
        showLocationForm(id, name, address, capacity, isActive);
    }

    function submitLocationForm() {
        const form = locationForm;
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            if (key === 'is_active') {
                data[key] = form.querySelector('input[name="is_active"]').checked;
            } else if (key === 'capacity' && value) {
                data[key] = parseInt(value);
            } else {
                data[key] = value;
            }
        }
        
        // Récupérer l'ID depuis le champ hidden ou currentEditingId
        const editingId = form.querySelector('input[name="id"]').value || currentEditingId;
        
        // S'assurer que l'ID est inclus pour les modifications
        if (editingId) {
            data['id'] = editingId;
            currentEditingId = editingId; // S'assurer que currentEditingId est défini
        }

        const url = editingId ? 
            `/therapeutic_activities/api/activity-locations/${editingId}/update/` :
            '/therapeutic_activities/api/activity-locations/create/';

        // Debug: log l'URL qui sera appelée
        console.log('URL appelée (location):', url, 'EditingId:', editingId);

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Succès',
                    text: data.message,
                    timer: 2000,
                    showConfirmButton: false
                });
                hideAllForms();
                setTimeout(() => location.reload(), 1000);
            } else {
                let errorMessage = data.message || 'Une erreur est survenue';
                if (data.errors) {
                    errorMessage += '\n' + Object.values(data.errors).flat().join('\n');
                }
                Swal.fire({
                    icon: 'error',
                    title: 'Erreur',
                    text: errorMessage
                });
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            Swal.fire({
                icon: 'error',
                title: 'Erreur',
                text: 'Une erreur est survenue lors de l\'enregistrement.'
            });
        });
    }

    // Fonction pour mettre à jour une ligne du tableau
    function updateTableRow(data, type) {
        if (currentEditingId) {
            // Mode modification - mettre à jour la ligne existante
            const tableId = type === 'activity_type' ? 'activity-types-table' : 'locations-table';
            const table = document.getElementById(tableId);
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const editBtn = row.querySelector('.edit-' + (type === 'activity_type' ? 'activity-type' : 'location') + '-btn');
                if (editBtn && editBtn.dataset.id == currentEditingId) {
                    // Mettre à jour les données de la ligne
                    if (type === 'activity_type') {
                        row.cells[0].textContent = data.name;
                        row.cells[1].textContent = data.description || '';
                        row.cells[2].innerHTML = data.is_active ? '<span class="badge bg-success">Actif</span>' : '<span class="badge bg-danger">Inactif</span>';
                        
                        // Mettre à jour les attributs du bouton d'édition
                        editBtn.dataset.name = data.name;
                        editBtn.dataset.description = data.description || '';
                        editBtn.dataset.isActive = data.is_active ? 'true' : 'false';
                    } else {
                        row.cells[0].textContent = data.name;
                        row.cells[1].textContent = data.address || 'Non spécifiée';
                        row.cells[2].textContent = data.capacity || 'Non définie';
                        row.cells[3].innerHTML = data.is_active ? '<span class="badge bg-success">Actif</span>' : '<span class="badge bg-danger">Inactif</span>';
                        
                        // Mettre à jour les attributs du bouton d'édition
                        editBtn.dataset.name = data.name;
                        editBtn.dataset.address = data.address || '';
                        editBtn.dataset.capacity = data.capacity || '';
                        editBtn.dataset.isActive = data.is_active ? 'true' : 'false';
                    }
                }
            });
        } else {
            // Mode création - recharger la page pour afficher le nouvel élément
            location.reload();
        }
    }

    // Fonctions utilitaires
    function hideAllForms() {
        if (activityTypeFormCard) {
            activityTypeFormCard.classList.add('d-none');
        }
        if (locationFormCard) {
            locationFormCard.classList.add('d-none');
        }
        currentEditingId = null;
        currentEditingType = null;
    }

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
});

// Fonctions globales pour les suppressions
function deleteActivityType(id, name) {
    Swal.fire({
        title: 'Confirmer la suppression',
        text: `Êtes-vous sûr de vouloir supprimer le type d'activité "${name}" ?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Oui, supprimer',
        cancelButtonText: 'Annuler'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/therapeutic_activities/api/activity-types/${id}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Supprimé',
                        text: data.message,
                        timer: 2000,
                        showConfirmButton: false
                    });
                    location.reload();
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erreur',
                        text: data.message
                    });
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Erreur',
                    text: 'Une erreur est survenue lors de la suppression.'
                });
            });
        }
    });
}

function deleteActivityLocation(id, name) {
    Swal.fire({
        title: 'Confirmer la suppression',
        text: `Êtes-vous sûr de vouloir supprimer la salle "${name}" ?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Oui, supprimer',
        cancelButtonText: 'Annuler'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/therapeutic_activities/api/activity-locations/${id}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Supprimé',
                        text: data.message,
                        timer: 2000,
                        showConfirmButton: false
                    });
                    location.reload();
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erreur',
                        text: data.message
                    });
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Erreur',
                    text: 'Une erreur est survenue lors de la suppression.'
                });
            });
        }
    });
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}
