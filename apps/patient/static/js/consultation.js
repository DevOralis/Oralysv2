// JavaScript spécifique pour le module de consultation

// Fonctions pour gérer le formulaire d'ajout de consultation - définies globalement
window.showAddConsultationForm = function() {
    const form = document.getElementById('add-consultation-form');
    if (form) {
        form.style.display = 'block';
        // Faire défiler vers le formulaire
        form.scrollIntoView({ behavior: 'smooth', block: 'start' });
        // Focus sur le premier champ
        const firstInput = form.querySelector('select[name="patient_id"]');
        if (firstInput) {
            firstInput.focus();
        }
    }
};

window.hideAddConsultationForm = function() {
    const form = document.getElementById('add-consultation-form');
    if (form) {
        form.style.display = 'none';
        // Réinitialiser le formulaire
        const consultationForm = document.getElementById('consultationForm');
        if (consultationForm) {
            consultationForm.reset();
        }
    }
};

// Initialisation lorsque le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
    // --- NOUVELLE LOGIQUE POUR LA MODALE UNIQUE ---
    const detailsModalElement = document.getElementById('detailsModal');
    if (detailsModalElement) {
        const detailsModal = new bootstrap.Modal(detailsModalElement);
        const detailsModalContent = document.getElementById('detailsModalContent');

        // Utiliser la délégation d'événements sur le body pour les éléments chargés dynamiquement
        document.body.addEventListener('click', function(event) {
            const consultationBtn = event.target.closest('.view-consultation-details');
            const appointmentBtn = event.target.closest('.view-appointment-details');
            let url = null;

            if (consultationBtn) {
                const consultationId = consultationBtn.dataset.id;
                url = `/patient/ajax/consultation/${consultationId}/`;
            }

            if (appointmentBtn) {
                const appointmentId = appointmentBtn.dataset.id;
                url = `/patient/ajax/appointment/${appointmentId}/`;
            }

            if (url) {
                // Afficher un spinner de chargement
                detailsModalContent.innerHTML = '<div class="modal-body text-center"><i class="fas fa-spinner fa-spin fa-3x"></i></div>';
                detailsModal.show();

                // Charger le contenu
                fetch(url)
                    .then(response => {
                        if (!response.ok) throw new Error('Erreur réseau');
                        return response.text();
                    })
                    .then(html => {
                        detailsModalContent.innerHTML = html;
                    })
                    .catch(error => {
                        detailsModalContent.innerHTML = '<div class="modal-body text-center"><p class="text-danger">Erreur lors du chargement des détails.</p></div>';
                        console.error('Erreur fetch modale:', error);
                    });
            }
        });
    }
    // --- FIN DE LA NOUVELLE LOGIQUE ---

    // Initialiser les fonctionnalités de consultation
    initConsultationFeatures();
    
    // Initialiser les SweetAlert pour les consultations
    initConsultationAlerts();
});

// Fonction pour initialiser les fonctionnalités de consultation
function initConsultationFeatures() {
    // Empêcher le submit du formulaire de recherche/filtre s'il existe
    const todoForm = document.getElementById('consultations-a-completer-block');
    if (todoForm) {
        const form = todoForm.querySelector('form');
        if (form) {
            form.addEventListener('submit', function(e) { e.preventDefault(); });
        }
    }
    
    const doneForm = document.getElementById('consultations-validees-block');
    if (doneForm) {
        const form = doneForm.querySelector('form');
        if (form) {
            form.addEventListener('submit', function(e) { e.preventDefault(); });
        }
    }
    
    
    // Initialiser la pagination
    bindConsultationPagination();
    
    // Initialiser les filtres
    bindTodoFilters();
    bindDoneFilters();
}

// Fonction pour initialiser les SweetAlert pour les consultations
function initConsultationAlerts() {
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.get('success') === 'consultation') {
        Swal.fire({
            icon: 'success',
            title: 'Succès',
            text: 'Consultation enregistrée avec succès !',
            timer: 2000,
            showConfirmButton: false
        });
        urlParams.delete('success');
        window.history.replaceState({}, document.title, window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : ''));
    } else if (urlParams.get('error')) {
        Swal.fire({
            icon: 'error',
            title: 'Erreur',
            text: urlParams.get('error'),
            showConfirmButton: true
        });
        urlParams.delete('error');
        window.history.replaceState({}, document.title, window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : ''));
    } else if (urlParams.get('success') === 'rdv_created') {
        Swal.fire({
            icon: 'success',
            title: 'Rendez-vous créé !',
            text: 'Le rendez-vous a été créé avec succès.',
            timer: 3000,
            showConfirmButton: false
        });
        urlParams.delete('success');
        window.history.replaceState({}, document.title, window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : ''));
    }
}

function bindConsultationPagination() {
    // Utiliser la délégation d'événements sur le document pour les liens de pagination
    document.querySelectorAll('.pagination-container .page-ajax').forEach(link => {
        // Éviter d'ajouter plusieurs écouteurs au même élément
        if (link.hasAttribute('data-listener-added')) return;
        link.setAttribute('data-listener-added', 'true');

        link.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('href');
            const container = this.closest('#consultations-a-completer-block, #consultations-validees-block');
            
            if (!container) return;

            fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(response => {
                    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    container.innerHTML = data.html;
                    // Re-lier les événements sur le nouveau contenu
                    initConsultationFeatures();
                })
                .catch(error => {
                    console.error('Erreur lors de la pagination AJAX:', error);
                });
        });
    });
}

// Recherche et filtres AJAX consultations à compléter
function triggerTodoAjax() {
    const searchInput = document.getElementById('search-todo');
    const filterInput = document.getElementById('filter-todo-medecin');
    
    if (!searchInput || !filterInput) return;
    
    const val = searchInput.value;
    const med = filterInput.value;
    const params = new URLSearchParams({search_todo: val, filter_todo_medecin: med});
    
    fetch('?' + params.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const container = document.getElementById('consultations-a-completer-block');
            container.innerHTML = data.html;
            bindConsultationPagination();
            bindTodoFilters();
        })
        .catch(error => {
            console.error('Erreur lors de la recherche:', error);
        });
}

function bindTodoFilters() {
    const searchTodo = document.getElementById('search-todo');
    const filterTodoMedecin = document.getElementById('filter-todo-medecin');
    
    if (searchTodo && !searchTodo.hasAttribute('data-listener-added')) {
        searchTodo.setAttribute('data-listener-added', 'true');
        searchTodo.addEventListener('input', triggerTodoAjax);
    }
    
    if (filterTodoMedecin && !filterTodoMedecin.hasAttribute('data-listener-added')) {
        filterTodoMedecin.setAttribute('data-listener-added', 'true');
        filterTodoMedecin.addEventListener('change', triggerTodoAjax);
    }
}

// Recherche et filtres AJAX consultations validées
function triggerDoneAjax() {
    const searchInput = document.getElementById('search-done');
    const filterInput = document.getElementById('filter-done-medecin');
    
    if (!searchInput || !filterInput) return;
    
    const val = searchInput.value;
    const med = filterInput.value;
    const params = new URLSearchParams({search_done: val, filter_done_medecin: med});
    
    fetch('?' + params.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const container = document.getElementById('consultations-validees-block');
            container.innerHTML = data.html;
            bindConsultationPagination();
            bindDoneFilters();
        })
        .catch(error => {
            console.error('Erreur lors de la recherche:', error);
        });
}

function bindDoneFilters() {
    const searchDone = document.getElementById('search-done');
    const filterDoneMedecin = document.getElementById('filter-done-medecin');
    
    if (searchDone && !searchDone.hasAttribute('data-listener-added')) {
        searchDone.setAttribute('data-listener-added', 'true');
        searchDone.addEventListener('input', triggerDoneAjax);
    }
    
    if (filterDoneMedecin && !filterDoneMedecin.hasAttribute('data-listener-added')) {
        filterDoneMedecin.setAttribute('data-listener-added', 'true');
        filterDoneMedecin.addEventListener('change', triggerDoneAjax);
    }
}

// Gestion du changement automatique du bouton Exporter/Importer
function updateExportImportButton() {
    const exportImportIcon = document.getElementById('export-import-icon');
    const exportImportText = document.getElementById('export-import-text');
    const exportImportBtn = document.getElementById('export-import-btn');
    const checkedBoxes = document.querySelectorAll('#tableConsultations .row-check:checked');
    const hasCheckedItems = checkedBoxes.length > 0;
    
    if (exportImportIcon && exportImportText && exportImportBtn) {
        if (hasCheckedItems) {
            // Changer en mode "Exporter" quand des cases sont cochées
            exportImportIcon.className = 'fas fa-file-export';
            exportImportText.textContent = 'Exporter';
            exportImportBtn.title = 'Exporter';
        } else {
            // Mode par défaut "Importer" quand aucune case n'est cochée
            exportImportIcon.className = 'fas fa-file-import';
            exportImportText.textContent = 'Importer';
            exportImportBtn.title = 'Importer';
        }
    }
}

// Utiliser la délégation d'événements pour gérer les checkboxes dynamiques
document.addEventListener('change', function(e) {
    if (e.target.id === 'selectAllConsultations') {
        // Gestion de la case "Sélectionner tout"
        const isChecked = e.target.checked;
        const visibleCheckboxes = document.querySelectorAll('#tableConsultations tbody tr:not([style*="display: none"]) .row-check');
        visibleCheckboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
        });
        updateExportImportButton();
    } else if (e.target.classList.contains('row-check')) {
        // Gestion des cases individuelles
        updateConsultationCheckboxState();
        updateExportImportButton();
    }
});

// Mettre à jour l'état des checkboxes
function updateConsultationCheckboxState() {
    const selectAllCheckbox = document.getElementById('selectAllConsultations');
    if (!selectAllCheckbox) return;
    
    const visibleCheckboxes = Array.from(document.querySelectorAll('#tableConsultations tbody tr:not([style*="display: none"]) .row-check'));
    const checkedCount = visibleCheckboxes.filter(cb => cb.checked).length;
    
    if (checkedCount === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
    } else if (checkedCount === visibleCheckboxes.length) {
        selectAllCheckbox.checked = true;
        selectAllCheckbox.indeterminate = false;
    } else {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = true;
    }
    
    // Mettre à jour le bouton export/import
    updateExportImportButton();
}

// Gestion du changement automatique du bouton Exporter/Importer pour les consultations à compléter
function updateExportImportButtonTodo() {
    const exportImportIcon = document.getElementById('export-import-icon-todo');
    const exportImportText = document.getElementById('export-import-text-todo');
    const exportImportBtn = document.getElementById('export-import-btn-todo');
    const checkedBoxes = document.querySelectorAll('#tableConsultationsTodo .row-check:checked');
    const hasCheckedItems = checkedBoxes.length > 0;
    
    if (exportImportIcon && exportImportText && exportImportBtn) {
        if (hasCheckedItems) {
            // Changer en mode "Exporter" quand des cases sont cochées
            exportImportIcon.className = 'fas fa-file-export';
            exportImportText.textContent = 'Exporter';
            exportImportBtn.title = 'Exporter';
        } else {
            // Mode par défaut "Importer" quand aucune case n'est cochée
            exportImportIcon.className = 'fas fa-file-import';
            exportImportText.textContent = 'Importer';
            exportImportBtn.title = 'Importer';
        }
    }
}

// Gestion supplémentaire pour les consultations à compléter
document.addEventListener('change', function(e) {
    if (e.target.id === 'selectAllConsultationsTodo') {
        // Gestion de la case "Sélectionner tout" pour les consultations à compléter
        const isChecked = e.target.checked;
        const visibleCheckboxes = document.querySelectorAll('#tableConsultationsTodo tbody tr:not([style*="display: none"]) .row-check');
        visibleCheckboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
        });
        updateExportImportButtonTodo();
    } else if (e.target.classList.contains('row-check') && e.target.closest('#tableConsultationsTodo')) {
        // Gestion des cases individuelles pour les consultations à compléter
        updateConsultationTodoCheckboxState();
        updateExportImportButtonTodo();
    }
});

// Mettre à jour l'état des checkboxes pour les consultations à compléter
function updateConsultationTodoCheckboxState() {
    const selectAllCheckbox = document.getElementById('selectAllConsultationsTodo');
    if (!selectAllCheckbox) return;
    
    const visibleCheckboxes = Array.from(document.querySelectorAll('#tableConsultationsTodo tbody tr:not([style*="display: none"]) .row-check'));
    const checkedCount = visibleCheckboxes.filter(cb => cb.checked).length;
    
    if (checkedCount === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
    } else if (checkedCount === visibleCheckboxes.length) {
        selectAllCheckbox.checked = true;
        selectAllCheckbox.indeterminate = false;
    } else {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = true;
    }
    
    // Mettre à jour le bouton export/import
    updateExportImportButtonTodo();
}

