// Fonction pour récupérer un cookie par son nom
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

// Fonction pour obtenir le libellé du statut
function getStatusLabel(status) {
    const labels = {
        'draft': 'Brouillon',
        'submitted': 'Soumise',
        'approved': 'Approuvée',
        'refused': 'Refusée',
        'cancelled': 'Annulée'
    };
    return labels[status] || status;
}

// Fonction pour obtenir la classe CSS du statut
function getStatusClass(status) {
    const classes = {
        'draft': 'bg-secondary',
        'submitted': 'bg-info',
        'approved': 'bg-success',
        'refused': 'bg-danger',
        'cancelled': 'bg-warning'
    };
    return classes[status] || 'bg-secondary';
}

// Fonction utilitaire pour normaliser les chaînes
function normalize(str) {
    return str.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim();
}

// Consolidated DOMContentLoaded handler
document.addEventListener('DOMContentLoaded', function() {
    // Prevent multiple executions
    if (document.body.hasAttribute('data-leave-management-initialized')) return;
    document.body.setAttribute('data-leave-management-initialized', 'true');

    // Leave type search
    const searchTypeInput = document.getElementById('searchLeaveTypeConfig');
    const typeTable = document.getElementById('leaveTypeConfigTable');
    if (searchTypeInput && typeTable) {
        searchTypeInput.addEventListener('input', function() {
            const value = normalize(searchTypeInput.value);
            Array.from(typeTable.tBodies[0].rows).forEach(row => {
                const text = normalize(row.textContent);
                row.style.display = text.includes(value) ? '' : 'none';
            });
        });
    } else {
        console.warn('searchLeaveTypeConfig or leaveTypeConfigTable not found');
    }

    // Protection globale contre la soumission multiple
    let isSubmitting = false;
    
    // Form submission for new leave request
    const newForm = document.getElementById('leaveRequestForm');
    if (newForm && !newForm.hasAttribute('data-submit-listener-added')) {
        newForm.setAttribute('data-submit-listener-added', 'true');
        
        // Supprimer tous les anciens event listeners
        const clonedForm = newForm.cloneNode(true);
        newForm.parentNode.replaceChild(clonedForm, newForm);
        
        const form = document.getElementById('leaveRequestForm');
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Protection globale
            if (isSubmitting) {
                console.log('Soumission déjà en cours, ignorée');
                return false;
            }
            
            isSubmitting = true;
            console.log('Début de soumission');
            
            // Désactiver tous les boutons de soumission
            const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"]');
            const originalButtonTexts = [];
            
            submitButtons.forEach((btn, index) => {
                originalButtonTexts[index] = btn.innerHTML;
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Traitement...';
            });
            
            const formData = new FormData(form);
            
            fetch('/hr/leaves/submit/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(async response => {
                // Essayer de parser la réponse JSON (même en cas d'erreur 400)
                let data = {};
                try {
                    data = await response.clone().json();
                } catch (e) {
                    // Ce n'est pas du JSON ; on laissera le gestionnaire d'erreurs générique faire son travail
                }

                if (!response.ok) {
                    // Les erreurs de validation (400) renvoient un JSON avec status "error" ou "overlap".
                    if (response.status === 400 && data && (data.status === 'error' || data.status === 'overlap')) {
                        return data; // Laisser le then suivant gérer l'affichage de l'erreur
                    }
                    // Autres erreurs => lancer exception pour catch()
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return data;
            })
            .then(data => {
                console.log('Réponse reçue:', data);
                
                if (data.status === 'success') {
                    console.log('Succès - fermeture modal et rechargement');
                    
                    // Fermer le modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('newLeaveRequestModal'));
                    if (modal) modal.hide();
                    
                    // Afficher SweetAlert de succès
                    Swal.fire({
                        icon: 'success',
                        title: 'Succès !',
                        text: 'Votre demande de congé a été soumise avec succès.',
                        showConfirmButton: false,
                        timer: 2000,
                        timerProgressBar: true
                    }).then(() => {
                        // Recharger la page après la SweetAlert
                        window.location.reload();
                    });
                    
                    return; // Sortir ici pour éviter la suite
                }
                
                // Gérer les autres cas
                if (data.status === 'overlap') {
                    Swal.fire({
                        icon: 'warning',
                        title: 'Chevauchement de congé',
                        text: data.message || 'Vous avez déjà une demande sur cette période.',
                        confirmButtonText: 'OK'
                    });
                } else if (data.status === 'error') {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erreur',
                        text: data.message || 'Une erreur est survenue.'
                    });
                }
                
                // Réactiver les boutons
                submitButtons.forEach((btn, index) => {
                    btn.disabled = false;
                    btn.innerHTML = originalButtonTexts[index];
                });
                
                isSubmitting = false;
            })
            .catch(error => {
                console.error('Erreur de soumission:', error);
                
                // Fermer le modal en cas d'erreur
                const modal = bootstrap.Modal.getInstance(document.getElementById('newLeaveRequestModal'));
                if (modal) modal.hide();
                
                Swal.fire({
                    icon: 'error',
                    title: 'Erreur de communication',
                    text: 'Impossible de soumettre la demande. Vérifiez votre connexion.'
                });
                
                // Réactiver les boutons
                submitButtons.forEach((btn, index) => {
                    btn.disabled = false;
                    btn.innerHTML = originalButtonTexts[index];
                });
                
                isSubmitting = false;
            });
            
            return false;
        });
    }

    // Form submission for editing leave request
    const editForm = document.getElementById('editLeaveRequestForm');
    if (editForm && !editForm.hasAttribute('data-submit-listener-added')) {
        editForm.setAttribute('data-submit-listener-added', 'true');
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const requestId = document.getElementById('editRequestId').value;
            const formData = new FormData(this);
            fetch(`/hr/leaves/edit/${requestId}/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
                return response.json();
            })
            .then(data => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('editLeaveRequestModal'));
                if (modal) modal.hide();
                if (data.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Succès',
                        text: 'La demande a été modifiée avec succès.',
                        showConfirmButton: false,
                        timer: 1500
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erreur',
                        text: data.message || 'Une erreur est survenue lors de la modification de la demande.'
                    });
                }
            })
            .catch(error => {
                console.error('Erreur lors de l\'édition:', error);
                const modal = bootstrap.Modal.getInstance(document.getElementById('editLeaveRequestModal'));
                if (modal) modal.hide();
                Swal.fire({
                    icon: 'error',
                    title: 'Erreur',
                    text: 'Impossible de modifier la demande. Vérifiez votre connexion.'
                });
            });
        });
    }

    // Cancel request handler
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.cancelRequest');
        if (btn) {
            e.preventDefault();
            const requestId = btn.getAttribute('data-id');
            Swal.fire({
                title: 'Annuler la demande ?',
                text: 'Voulez-vous vraiment annuler cette demande de congé ?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Oui, annuler',
                cancelButtonText: 'Non'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/hr/leaves/cancel/${requestId}/`, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    })
                    .then(response => {
                        if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
                        return response.json();
                    })
                    .then(data => {
                        if (data.status === 'success') {
                            Swal.fire({
                                icon: 'success',
                                title: 'Succès !',
                                text: 'La demande a été annulée avec succès.',
                                showConfirmButton: false,
                                timer: 2000,
                                timerProgressBar: true
                            }).then(() => {
                                window.location.reload();
                            });
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: 'Erreur',
                                text: data.message || 'Une erreur est survenue lors de l\'annulation.'
                            });
                        }
                    })
                    .catch(error => {
                        console.error('Erreur lors de l\'annulation:', error);
                        Swal.fire({
                            icon: 'error',
                            title: 'Erreur',
                            text: 'Une erreur est survenue lors de la communication avec le serveur.'
                        });
                    });
                }
            });
        }
    });

    // Leave request table search and pagination
    function setupLeaveRequestTableSearchAndPagination() {
        const table = document.getElementById('leaveRequestTable');
        if (!table) {
            console.warn('leaveRequestTable not found');
            return;
        }
        const tbody = table.querySelector('tbody');
        if (!tbody) {
            console.warn('leaveRequestTable tbody not found');
            return;
        }
        const searchInput = document.getElementById('searchLeaveRequest');
        const pagination = document.getElementById('leaveRequestPagination');
        const rowsPerPage = 5;
        let filteredRows = [];
        let currentPage = 1;

        function getAllRows() {
            return Array.from(tbody.querySelectorAll('tr:not(.empty-row)'));
        }

        function filterRows() {
            const searchTerm = searchInput ? normalize(searchInput.value) : '';
            let rows = getAllRows();
            if (searchTerm) {
                rows = rows.filter(row => {
                    let concat = '';
                    for (let i = 0; i < row.cells.length; i++) {
                        concat += ' ' + normalize(row.cells[i].textContent);
                    }
                    return concat.includes(searchTerm);
                });
            }
            filteredRows = rows;
            currentPage = 1;
            displayRows();
            updatePagination();
        }

        function displayRows() {
            getAllRows().forEach(row => row.style.display = 'none');
            const start = (currentPage - 1) * rowsPerPage;
            const end = start + rowsPerPage;
            const pageRows = filteredRows.slice(start, end);
            pageRows.forEach(row => row.style.display = '');
            let noResultsRow = tbody.querySelector('.empty-row');
            if (filteredRows.length === 0) {
                if (!noResultsRow) {
                    noResultsRow = document.createElement('tr');
                    noResultsRow.className = 'empty-row';
                    noResultsRow.innerHTML = `<td colspan="9" class="text-center py-3">Aucun résultat trouvé pour votre recherche</td>`;
                    tbody.appendChild(noResultsRow);
                }
                noResultsRow.style.display = '';
            } else if (noResultsRow) {
                noResultsRow.style.display = 'none';
            }
        }

        function updatePagination() {
            const totalPages = Math.max(1, Math.ceil(filteredRows.length / rowsPerPage));
            pagination.innerHTML = '';
            if (totalPages <= 1) return;
            
            const prev = document.createElement('li');
            prev.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
            prev.innerHTML = `<a class="page-link" href="#" aria-label="Précédent">
                <i class="fas fa-chevron-left d-block d-sm-none"></i>
                <span class="d-none d-sm-block">&laquo; Préc</span>
            </a>`;
            prev.onclick = e => {
                e.preventDefault();
                if (currentPage > 1) {
                    currentPage--;
                    displayRows();
                    updatePagination();
                }
            };
            pagination.appendChild(prev);
            
            for (let i = 1; i <= totalPages; i++) {
                const li = document.createElement('li');
                li.className = `page-item ${i === currentPage ? 'active' : ''}`;
                li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
                li.onclick = e => {
                    e.preventDefault();
                    currentPage = i;
                    displayRows();
                    updatePagination();
                };
                pagination.appendChild(li);
            }
            
            const next = document.createElement('li');
            next.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
            next.innerHTML = `<a class="page-link" href="#" aria-label="Suivant">
                <i class="fas fa-chevron-right d-block d-sm-none"></i>
                <span class="d-none d-sm-block">Suiv &raquo;</span>
            </a>`;
            next.onclick = e => {
                e.preventDefault();
                if (currentPage < totalPages) {
                    currentPage++;
                    displayRows();
                    updatePagination();
                }
            };
            pagination.appendChild(next);
        }

        if (searchInput) {
            searchInput.addEventListener('input', filterRows);
        } else {
            console.warn('searchLeaveRequest not found for pagination');
        }
        
        // Ajouter la fonctionnalité de tri
        setupLeaveRequestSorting();
        
        // Ajouter la gestion des checkboxes
        setupLeaveRequestCheckboxes();
        
        filteredRows = getAllRows();
        displayRows();
        updatePagination();
    }

    // Fonction pour gérer les checkboxes des demandes de congés
    function setupLeaveRequestCheckboxes() {
        const selectAllCheckbox = document.getElementById('selectAllLeaveRequests');
        const rowCheckboxes = document.querySelectorAll('#leaveRequestTable .row-check');
        
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function() {
                const isChecked = this.checked;
                rowCheckboxes.forEach(checkbox => {
                    checkbox.checked = isChecked;
                });
            });
        }
        
        // Gérer les checkboxes individuelles
        rowCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                updateSelectAllState();
            });
        });
        
        function updateSelectAllState() {
            if (!selectAllCheckbox) return;
            
            const visibleCheckboxes = Array.from(document.querySelectorAll('#leaveRequestTable tbody tr:not([style*="display: none"]) .row-check'));
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
        }
    }

    // Fonction de tri pour le tableau des demandes de congés
    function setupLeaveRequestSorting() {
        const sortableHeaders = document.querySelectorAll('#leaveRequestTable .sortable');
        
        sortableHeaders.forEach(header => {
            header.addEventListener('click', function() {
                const sortField = this.dataset.sort;
                const currentDirection = this.dataset.direction || 'asc';
                const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
                
                // Mettre à jour l'icône de tri
                updateLeaveRequestSortIcons(this, newDirection);
                
                // Trier toutes les lignes (pas seulement la page actuelle)
                sortLeaveRequestTable(sortField, newDirection);
                
                // Réappliquer le filtrage et la pagination
                filterRows();
                
                // Sauvegarder la direction pour ce header
                this.dataset.direction = newDirection;
            });
        });
    }

    function sortLeaveRequestTable(sortField, direction) {
        const table = document.getElementById('leaveRequestTable');
        const tbody = table.querySelector('tbody');
        const allRows = Array.from(tbody.querySelectorAll('tr:not(.empty-row)'));
        
        allRows.sort((a, b) => {
            let aValue, bValue;
            
            switch(sortField) {
                case 'leave_type':
                    // Chercher dans la première cellule visible (type de congé)
                    aValue = a.querySelector('td:first-child span')?.textContent.trim() || 
                             a.querySelector('td:first-child')?.textContent.trim() || '';
                    bValue = b.querySelector('td:first-child span')?.textContent.trim() || 
                             b.querySelector('td:first-child')?.textContent.trim() || '';
                    break;
                case 'start_date':
                    aValue = a.querySelector('td[data-label="Date de début"]')?.textContent.trim() || '';
                    bValue = b.querySelector('td[data-label="Date de début"]')?.textContent.trim() || '';
                    break;
                case 'end_date':
                    aValue = a.querySelector('td[data-label="Date de fin"]')?.textContent.trim() || '';
                    bValue = b.querySelector('td[data-label="Date de fin"]')?.textContent.trim() || '';
                    break;
                case 'duration':
                    aValue = a.querySelector('td[data-label="Durée"]')?.textContent.trim() || '';
                    bValue = b.querySelector('td[data-label="Durée"]')?.textContent.trim() || '';
                    break;
                case 'status':
                    aValue = a.querySelector('td[data-label="Statut"] .badge')?.textContent.trim() || '';
                    bValue = b.querySelector('td[data-label="Statut"] .badge')?.textContent.trim() || '';
                    break;
                case 'request_date':
                    aValue = a.querySelector('td[data-label="Date de demande"]')?.textContent.trim() || '';
                    bValue = b.querySelector('td[data-label="Date de demande"]')?.textContent.trim() || '';
                    break;
                default:
                    return 0;
            }
            
            const comparison = aValue.localeCompare(bValue, 'fr', { numeric: true });
            return direction === 'asc' ? comparison : -comparison;
        });
        
        // Réorganiser toutes les lignes dans le tbody
        allRows.forEach(row => tbody.appendChild(row));
        
        // Mettre à jour les variables globales pour la pagination
        if (typeof filteredRows !== 'undefined') {
            filteredRows = allRows;
            if (typeof displayRows === 'function') {
                displayRows();
            }
            if (typeof updatePagination === 'function') {
                updatePagination();
            }
        }
    }

    function updateLeaveRequestSortIcons(activeHeader, direction) {
        // Réinitialiser toutes les icônes
        document.querySelectorAll('#leaveRequestTable .sort-icon').forEach(icon => {
            icon.className = 'fas fa-sort sort-icon text-muted';
        });
        
        // Mettre à jour l'icône active
        const activeIcon = activeHeader.querySelector('.sort-icon');
        if (activeIcon) {
            if (direction === 'asc') {
                activeIcon.className = 'fas fa-sort-up sort-icon text-white';
            } else {
                activeIcon.className = 'fas fa-sort-down sort-icon text-white';
            }
        }
    }

    // Fonction de tri pour les types de congés
    function setupLeaveTypeSorting() {
        const sortableHeaders = document.querySelectorAll('#leaveTypeConfigTable .sortable');
        
        sortableHeaders.forEach(header => {
            header.addEventListener('click', function() {
                const sortField = this.dataset.sort;
                const currentDirection = this.dataset.direction || 'asc';
                const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
                
                // Mettre à jour l'icône de tri
                updateLeaveTypeSortIcons(this, newDirection);
                
                // Trier le tableau côté client
                sortLeaveTypeTable(sortField, newDirection);
                
                // Sauvegarder la direction pour ce header
                this.dataset.direction = newDirection;
            });
        });
    }

    function sortLeaveTypeTable(sortField, direction) {
        const table = document.getElementById('leaveTypeConfigTable');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr:not(.empty-row)'));
        
        rows.sort((a, b) => {
            let aValue, bValue;
            
            switch(sortField) {
                case 'leave_type':
                    aValue = a.querySelector('td:nth-child(2)')?.textContent.trim() || '';
                    bValue = b.querySelector('td:nth-child(2)')?.textContent.trim() || '';
                    break;
                case 'default_days':
                    aValue = a.querySelector('td:nth-child(3) .badge')?.textContent.replace(/[^\d]/g, '') || '0';
                    bValue = b.querySelector('td:nth-child(3) .badge')?.textContent.replace(/[^\d]/g, '') || '0';
                    aValue = parseInt(aValue);
                    bValue = parseInt(bValue);
                    return direction === 'asc' ? aValue - bValue : bValue - aValue;
                case 'status':
                    aValue = a.querySelector('td:nth-child(4) .badge')?.textContent.trim() || '';
                    bValue = b.querySelector('td:nth-child(4) .badge')?.textContent.trim() || '';
                    break;
                default:
                    return 0;
            }
            
            if (typeof aValue === 'string') {
                const comparison = aValue.localeCompare(bValue, 'fr', { numeric: true });
                return direction === 'asc' ? comparison : -comparison;
            }
            return 0;
        });
        
        // Réorganiser les lignes
        rows.forEach(row => tbody.appendChild(row));
    }

    function updateLeaveTypeSortIcons(activeHeader, direction) {
        // Réinitialiser toutes les icônes
        document.querySelectorAll('#leaveTypeConfigTable .sort-icon').forEach(icon => {
            icon.className = 'fas fa-sort sort-icon text-muted';
        });
        
        // Mettre à jour l'icône active
        const activeIcon = activeHeader.querySelector('.sort-icon');
        if (activeIcon) {
            if (direction === 'asc') {
                activeIcon.className = 'fas fa-sort-up sort-icon text-primary';
            } else {
                activeIcon.className = 'fas fa-sort-down sort-icon text-primary';
            }
        }
    }

    // AJAX search for leave requests (optional, with debounce)
    const searchInput = document.getElementById('searchLeaveRequest');
    const tableBlock = document.getElementById('leaveRequestTableBlock');
    if (searchInput && tableBlock) {
        let debounceTimeout;
        function fetchLeaveRequestsAJAX() {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => {
                const params = new URLSearchParams({ search: searchInput.value }).toString();
                fetch(`?${params}`, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => {
                    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    tableBlock.innerHTML = data.html;
                    // Reinitialize pagination after AJAX update
                    setupLeaveRequestTableSearchAndPagination();
                })
                .catch(error => {
                    console.error('Fetch error:', error);
                });
            }, 300); // Debounce for 300ms
        }
        searchInput.addEventListener('input', fetchLeaveRequestsAJAX);
    } else {
        console.warn('searchLeaveRequest or leaveRequestTableBlock not found for AJAX');
    }
    // Initialize table search and pagination
    if (document.getElementById('leaveRequestTable') && searchInput) {
        setupLeaveRequestTableSearchAndPagination();
    }
    
    // Fonction pour charger les données d'une demande de congé dans le modal d'édition
    function loadLeaveRequestData(requestId) {
        console.log('Chargement des données pour la demande:', requestId);
        
        // Afficher un loading
        Swal.fire({
            title: 'Chargement...',
            text: 'Récupération des données',
            allowOutsideClick: false,
            showConfirmButton: false,
            willOpen: () => {
                Swal.showLoading();
            }
        });
        
        fetch(`/hr/leaves/get/${requestId}/`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            console.log('Réponse reçue, status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Données complètes reçues:', data);
            Swal.close(); // Fermer le loading
            
            if (data.status === 'success' && data.request) {
                const request = data.request;
                console.log('Structure de la demande:', {
                    request_id: request.request_id,
                    leave_type: request.leave_type,
                    start_date: request.start_date,
                    end_date: request.end_date,
                    notes: request.notes,
                    certificate: request.certificate,
                    certificate_url: request.certificate_url,
                    certificate_name: request.certificate_name
                });
                
                // Remplir les champs du formulaire avec vérification
                const editRequestId = document.getElementById('editRequestId');
                const editLeaveType = document.getElementById('editLeaveType');
                const editStartDate = document.getElementById('editStartDate');
                const editEndDate = document.getElementById('editEndDate');
                const editNotes = document.getElementById('editNotes');
                
                if (editRequestId) {
                    editRequestId.value = request.request_id;
                    console.log('Request ID set:', request.request_id);
                }
                
                if (editLeaveType && request.leave_type && request.leave_type.type_id) {
                    editLeaveType.value = request.leave_type.type_id;
                    console.log('Leave type set:', request.leave_type.type_id, 'Options disponibles:', Array.from(editLeaveType.options).map(o => o.value));
                    
                    // Vérifier si la valeur a été correctement assignée
                    setTimeout(() => {
                        if (editLeaveType.value !== request.leave_type.type_id) {
                            console.warn('La valeur du type de conge n\'a pas ete assignee correctement');
                            // Essayer de trouver par nom
                            for (let option of editLeaveType.options) {
                                if (option.textContent.trim() === request.leave_type.name) {
                                    option.selected = true;
                                    console.log('Type de conge trouve par nom:', option.value);
                                    break;
                                }
                            }
                        }
                    }, 100);
                } else {
                    console.warn('Probleme avec le type de conge:', { editLeaveType, leave_type: request.leave_type });
                }
                
                if (editStartDate) {
                    editStartDate.value = request.start_date;
                    console.log('Start date set:', request.start_date);
                }
                
                if (editEndDate) {
                    editEndDate.value = request.end_date;
                    console.log('End date set:', request.end_date);
                }
                
                if (editNotes) {
                    editNotes.value = request.notes || '';
                    console.log('Notes set:', request.notes);
                }
                
                // Gérer l'affichage du certificat existant
                const currentCertificateDiv = document.getElementById('currentCertificate');
                if (currentCertificateDiv) {
                    if (request.certificate && request.certificate_url) {
                        console.log('Certificat détecté:', request.certificate_url);
                        currentCertificateDiv.innerHTML = `
                            <div class="alert alert-info">
                                <i class="fas fa-file"></i> 
                                <strong>Certificat actuel :</strong> 
                                <a href="${request.certificate_url}" target="_blank" class="text-decoration-none">
                                    ${request.certificate_name || 'Voir le document'}
                                </a>
                                <br><small class="text-muted">Vous pouvez télécharger un nouveau fichier pour le remplacer.</small>
                            </div>
                        `;
                    } else {
                        console.log('Aucun certificat détecté');
                        currentCertificateDiv.innerHTML = '<small class="text-muted">Aucun certificat médical.</small>';
                    }
                }
                
                // Ouvrir le modal
                const modal = new bootstrap.Modal(document.getElementById('editLeaveRequestModal'));
                modal.show();
                
                console.log('Modal ouvert avec succès');
            } else {
                console.error('Erreur dans la réponse:', data);
                Swal.fire({
                    icon: 'error',
                    title: 'Erreur',
                    text: data.message || 'Impossible de charger les données de la demande.'
                });
            }
        })
        .catch(error => {
            console.error('Erreur lors du chargement:', error);
            Swal.close(); // Fermer le loading
            Swal.fire({
                icon: 'error',
                title: 'Erreur de communication',
                text: `Impossible de charger les données: ${error.message}`
            });
        });
    }
    
    // Gérer les clics sur les boutons d'édition
document.addEventListener('click', function(e) {
        if (e.target && e.target.matches('.editRequest, .editRequest *')) {
            e.preventDefault();
            
            // Trouver le bouton parent si on a cliqué sur une icône
            const button = e.target.closest('.editRequest');
            if (button) {
                const requestId = button.getAttribute('data-id');
                if (requestId) {
                    loadLeaveRequestData(requestId);
                }
            }
        }
    });
    
    // Gérer les clics sur les boutons de visualisation
document.addEventListener('click', function(e) {
        if (e.target && e.target.matches('.viewRequest, .viewRequest *')) {
            e.preventDefault();
            
            const button = e.target.closest('.viewRequest');
            if (button) {
                const requestId = button.getAttribute('data-id');
                if (requestId) {
                    loadLeaveRequestForView(requestId);
                }
            }
        }
    });
    
    // Fonction pour charger les données dans le modal de visualisation
    function loadLeaveRequestForView(requestId) {
        fetch(`/hr/leaves/get/${requestId}/`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' && data.request) {
                const request = data.request;
                
                // Remplir les champs du modal de visualisation
                document.getElementById('viewLeaveType').textContent = request.leave_type.name;
                document.getElementById('viewStartDate').textContent = new Date(request.start_date).toLocaleDateString('fr-FR');
                document.getElementById('viewEndDate').textContent = new Date(request.end_date).toLocaleDateString('fr-FR');
                document.getElementById('viewDuration').textContent = request.duration;
                document.getElementById('viewRequestDate').textContent = new Date(request.request_date).toLocaleDateString('fr-FR');
                document.getElementById('viewNotes').textContent = request.notes || '-';
                
                // Gérer le statut
                const statusElement = document.getElementById('viewStatus');
                statusElement.textContent = getStatusLabel(request.status);
                statusElement.className = `badge ${getStatusClass(request.status)}`;
                
                // Gérer le certificat
                const certificateSection = document.getElementById('viewCertificateSection');
                if (request.certificate && request.certificate_url) {
                    document.getElementById('viewCertificateLink').href = request.certificate_url;
                    certificateSection.style.display = 'block';
                } else {
                    certificateSection.style.display = 'none';
                }
                
                // Ouvrir le modal
                const modal = new bootstrap.Modal(document.getElementById('viewLeaveRequestModal'));
                modal.show();
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            Swal.fire({
                icon: 'error',
                title: 'Erreur',
                text: 'Impossible de charger les détails de la demande.'
            });
        });
    }
});

// Initialiser le tri pour les types de congés au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Attendre que les autres scripts se chargent
    setTimeout(() => {
        if (document.getElementById('leaveTypeConfigTable')) {
            setupLeaveTypeSorting();
        }
        if (document.getElementById('leaveRequestTable')) {
            setupLeaveRequestSorting();
        }
    }, 100);

    // Gestion du changement automatique des boutons Exporter/Importer
    
    // Pour la section "Types de congés configurés"
    const exportImportBtnTypes = document.getElementById('export-import-btn-types');
    const exportImportIconTypes = document.getElementById('export-import-icon-types');
    const exportImportTextTypes = document.getElementById('export-import-text-types');
    const selectAllLeaveTypes = document.getElementById('selectAllLeaveTypes');
    
    function updateExportImportButtonTypes() {
        const checkedBoxes = document.querySelectorAll('#leaveTypeConfigTable .row-check:checked');
        const hasCheckedItems = checkedBoxes.length > 0;
        
        if (hasCheckedItems) {
            // Changer en mode "Exporter" quand des cases sont cochées
            exportImportIconTypes.className = 'fas fa-file-export';
            exportImportTextTypes.textContent = 'Exporter';
        } else {
            // Mode par défaut "Importer" quand aucune case n'est cochée
            exportImportIconTypes.className = 'fas fa-file-import';
            exportImportTextTypes.textContent = 'Importer';
        }
    }
    
    // Event listener pour la case "Sélectionner tout" des types de congés
    if (selectAllLeaveTypes) {
        selectAllLeaveTypes.addEventListener('change', function() {
            const rowCheckboxes = document.querySelectorAll('#leaveTypeConfigTable .row-check');
            rowCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateExportImportButtonTypes();
        });
    }
    
    // Pour la section "Statut de mes demandes"
    const exportImportBtnRequests = document.getElementById('export-import-btn-requests');
    const exportImportIconRequests = document.getElementById('export-import-icon-requests');
    const exportImportTextRequests = document.getElementById('export-import-text-requests');
    const selectAllLeaveRequests = document.getElementById('selectAllLeaveRequests');
    
    function updateExportImportButtonRequests() {
        const checkedBoxes = document.querySelectorAll('#leaveRequestTable .row-check:checked');
        const hasCheckedItems = checkedBoxes.length > 0;
        
        if (hasCheckedItems) {
            // Changer en mode "Exporter" quand des cases sont cochées
            exportImportIconRequests.className = 'fas fa-file-export';
            exportImportTextRequests.textContent = 'Exporter';
        } else {
            // Mode par défaut "Importer" quand aucune case n'est cochée
            exportImportIconRequests.className = 'fas fa-file-import';
            exportImportTextRequests.textContent = 'Importer';
        }
    }
    
    // Event listener pour la case "Sélectionner tout" des demandes
    if (selectAllLeaveRequests) {
        selectAllLeaveRequests.addEventListener('change', function() {
            const rowCheckboxes = document.querySelectorAll('#leaveRequestTable .row-check');
            rowCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateExportImportButtonRequests();
        });
    }
    
    // Event listeners pour les cases individuelles
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('row-check')) {
            // Déterminer dans quelle table se trouve la case cochée
            const table = e.target.closest('table');
            if (table) {
                if (table.id === 'leaveTypeConfigTable') {
                    updateExportImportButtonTypes();
                    
                    // Mettre à jour la case "Sélectionner tout" des types
                    const allCheckboxes = document.querySelectorAll('#leaveTypeConfigTable .row-check');
                    const checkedCheckboxes = document.querySelectorAll('#leaveTypeConfigTable .row-check:checked');
                    
                    if (selectAllLeaveTypes) {
                        selectAllLeaveTypes.checked = allCheckboxes.length === checkedCheckboxes.length;
                        selectAllLeaveTypes.indeterminate = checkedCheckboxes.length > 0 && checkedCheckboxes.length < allCheckboxes.length;
                    }
                } else if (table.id === 'leaveRequestTable') {
                    updateExportImportButtonRequests();
                    
                    // Mettre à jour la case "Sélectionner tout" des demandes
                    const allCheckboxes = document.querySelectorAll('#leaveRequestTable .row-check');
                    const checkedCheckboxes = document.querySelectorAll('#leaveRequestTable .row-check:checked');
                    
                    if (selectAllLeaveRequests) {
                        selectAllLeaveRequests.checked = allCheckboxes.length === checkedCheckboxes.length;
                        selectAllLeaveRequests.indeterminate = checkedCheckboxes.length > 0 && checkedCheckboxes.length < allCheckboxes.length;
                    }
                }
            }
        }
    });
    
    // Gestionnaire pour les boutons de soumission des demandes en brouillon
    document.addEventListener('click', function(e) {
        if (e.target && e.target.matches('.submitRequest, .submitRequest *')) {
            e.preventDefault();
            
            const button = e.target.closest('.submitRequest');
            if (button) {
                const requestId = button.getAttribute('data-id');
                if (requestId) {
                    submitDraftRequest(requestId);
                }
            }
        }
    });
    
    // Fonction pour soumettre une demande en brouillon
    function submitDraftRequest(requestId) {
        Swal.fire({
            title: 'Confirmer la soumission',
            text: 'Êtes-vous sûr de vouloir soumettre cette demande ? Une fois soumise, vous ne pourrez plus la modifier.',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#28a745',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Oui, soumettre',
            cancelButtonText: 'Annuler'
        }).then((result) => {
            if (result.isConfirmed) {
                // Afficher un indicateur de chargement
                Swal.fire({
                    title: 'Soumission en cours...',
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    showConfirmButton: false,
                    didOpen: () => {
                        Swal.showLoading();
                    }
                });
                
                const formData = new FormData();
                formData.append('request_id', requestId);
                
                fetch(`/hr/leaves/submit/${requestId}/`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        Swal.fire({
                            icon: 'success',
                            title: 'Succès',
                            text: data.message,
                            timer: 1500,
                            showConfirmButton: false
                        }).then(() => {
                            window.location.reload();
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Erreur',
                            text: data.message || 'Une erreur est survenue lors de la soumission'
                        });
                    }
                })
                .catch(error => {
                    console.error('Erreur lors de la soumission:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Erreur de communication',
                        text: 'Impossible de soumettre la demande. Vérifiez votre connexion.'
                    });
                });
            }
        });
    }
    
    // Initialiser l'état des boutons au chargement
    updateExportImportButtonTypes();
    updateExportImportButtonRequests();
});
