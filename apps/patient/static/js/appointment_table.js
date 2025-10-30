// Appointment Table Management - Style Patient
document.addEventListener('DOMContentLoaded', function() {
    initializeAppointmentTable();
});

// Protection contre les initialisations multiples
let appointmentTableInitialized = false;

function initializeAppointmentTable() {
    if (appointmentTableInitialized) return;
    appointmentTableInitialized = true;
    
    console.log('Initializing Appointment Table...');
    
    // Initialiser toutes les fonctionnalités
    initializeAppointmentSearch();
    initializeAppointmentCheckboxes();
    initializeAppointmentExport();
    initializeAppointmentSorting();
    initializeAppointmentModal();
    initializeAppointmentPagination();
}

// Recherche côté client - Style Patient
function initializeAppointmentSearch() {
    const searchInput = document.getElementById('searchAppointment');
    const table = document.getElementById('tableAppointments');
    
    if (searchInput && table) {
        searchInput.addEventListener('input', function () {
            const filter = searchInput.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr:not(.empty-row):not(#appointments-no-results)');
            let visibleCount = 0;
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                const isVisible = text.includes(filter);
                row.style.display = isVisible ? '' : 'none';
                if (isVisible) visibleCount++;
            });
            
            // Afficher/masquer le message "Aucun rendez-vous"
            const noResults = document.getElementById('appointments-no-results');
            if (noResults) {
                noResults.style.display = visibleCount === 0 ? '' : 'none';
            }
            
            updateAppointmentCheckboxState();
        });
    }
    
    // Filtre par médecin
    const filterMedecin = document.getElementById('filterMedecin');
    if (filterMedecin && table) {
        filterMedecin.addEventListener('change', function() {
            const filter = this.options[this.selectedIndex].text.toLowerCase();
            const rows = table.querySelectorAll('tbody tr:not(.empty-row):not(#appointments-no-results)');
            let visibleCount = 0;
            
            rows.forEach(row => {
                if (!this.value || this.value === '') {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    const medecinCell = row.querySelector('td[data-label="Médecin"]');
                    const medecinText = medecinCell ? medecinCell.textContent.toLowerCase().trim() : '';
                    const isVisible = medecinText.includes(filter);
                    row.style.display = isVisible ? '' : 'none';
                    if (isVisible) visibleCount++;
                }
            });
            
            // Afficher/masquer le message "Aucun rendez-vous"
            const noResults = document.getElementById('appointments-no-results');
            if (noResults) {
                noResults.style.display = visibleCount === 0 ? '' : 'none';
            }
            
            updateAppointmentCheckboxState();
        });
    }
    
    // Filtre par statut
    const filterStatut = document.getElementById('filterStatut');
    if (filterStatut && table) {
        filterStatut.addEventListener('change', function() {
            const filter = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr:not(.empty-row):not(#appointments-no-results)');
            let visibleCount = 0;
            
            rows.forEach(row => {
                if (!filter) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    const statutCell = row.querySelector('[data-label="Statut"]');
                    const statutText = statutCell ? statutCell.textContent.toLowerCase().trim() : '';
                    const isVisible = statutText.includes(filter);
                    row.style.display = isVisible ? '' : 'none';
                    if (isVisible) visibleCount++;
                }
            });
            
            // Afficher/masquer le message "Aucun rendez-vous"
            const noResults = document.getElementById('appointments-no-results');
            if (noResults) {
                noResults.style.display = visibleCount === 0 ? '' : 'none';
            }
            
            updateAppointmentCheckboxState();
        });
    }
}

function updateAppointmentCheckboxState() {
    const selectAll = document.getElementById('selectAllAppointments');
    const rowChecks = document.querySelectorAll('.row-check');
    const visibleChecks = Array.from(rowChecks).filter(cb => cb.closest('tr').style.display !== 'none');
    
    if (!selectAll || visibleChecks.length === 0) return;
    
    const checkedCount = visibleChecks.filter(cb => cb.checked).length;
    
    if (checkedCount === 0) {
        selectAll.checked = false;
        selectAll.indeterminate = false;
    } else if (checkedCount === visibleChecks.length) {
        selectAll.checked = true;
        selectAll.indeterminate = false;
    } else {
        selectAll.checked = false;
        selectAll.indeterminate = true;
    }
}

// Gestion des checkboxes
function initializeAppointmentCheckboxes() {
    const selectAll = document.getElementById('selectAllAppointments');
    const rowChecks = document.querySelectorAll('.row-check');
    
    if (!selectAll) return;
    
    // Supprimer les anciens listeners
    selectAll.removeEventListener('change', handleSelectAllAppointments);
    
    // Ajouter le listener pour "Tout sélectionner"
    selectAll.addEventListener('change', handleSelectAllAppointments);
    
    // Ajouter les listeners pour les checkboxes individuelles
    rowChecks.forEach(checkbox => {
        checkbox.removeEventListener('change', handleRowCheckAppointments);
        checkbox.addEventListener('change', handleRowCheckAppointments);
    });
    
    // Mettre à jour l'état initial
    updateSelectAllStateAppointments();
}

function handleSelectAllAppointments() {
    const selectAll = document.getElementById('selectAllAppointments');
    const rowChecks = document.querySelectorAll('.row-check');
    
    rowChecks.forEach(checkbox => {
        checkbox.checked = selectAll.checked;
    });
}

function handleRowCheckAppointments() {
    updateSelectAllStateAppointments();
}

function updateSelectAllStateAppointments() {
    const selectAll = document.getElementById('selectAllAppointments');
    const rowChecks = document.querySelectorAll('.row-check');
    
    if (!selectAll || rowChecks.length === 0) return;
    
    const checkedCount = Array.from(rowChecks).filter(cb => cb.checked).length;
    
    if (checkedCount === 0) {
        selectAll.checked = false;
        selectAll.indeterminate = false;
    } else if (checkedCount === rowChecks.length) {
        selectAll.checked = true;
        selectAll.indeterminate = false;
    } else {
        selectAll.checked = false;
        selectAll.indeterminate = true;
    }
}

// Export Excel
function initializeAppointmentExport() {
    const exportBtn = document.getElementById('export-appointments');
    if (!exportBtn) return;
    
    exportBtn.addEventListener('click', function() {
        exportAppointmentsToExcel();
    });
}

function exportAppointmentsToExcel() {
    // Notification que l'export n'est pas encore implémenté
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: 'Export non disponible',
            text: 'La fonctionnalité d\'export n\'est pas encore implémentée.',
            icon: 'info',
            confirmButtonText: 'OK'
        });
    } else {
        alert('La fonctionnalité d\'export n\'est pas encore implémentée.');
    }
}

// Tri des colonnes
function initializeAppointmentSorting() {
    const sortIcons = document.querySelectorAll('#tableAppointments .sort-icon');
    
    sortIcons.forEach(icon => {
        const th = icon.closest('th');
        if (th) {
            th.style.cursor = 'pointer';
            th.removeEventListener('click', handleAppointmentSort);
            th.addEventListener('click', handleAppointmentSort);
        }
    });
}

function handleAppointmentSort(e) {
    const th = e.currentTarget;
    const table = document.getElementById('tableAppointments');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr:not(#appointments-no-results)'));
    
    if (rows.length === 0) return;
    
    const columnIndex = Array.from(th.parentNode.children).indexOf(th);
    const sortIcon = th.querySelector('.sort-icon');
    
    // Déterminer la direction du tri
    let ascending = true;
    if (sortIcon.classList.contains('fa-sort-up')) {
        ascending = false;
        sortIcon.className = 'fas fa-sort-down sort-icon ms-1 text-white-50';
    } else {
        ascending = true;
        sortIcon.className = 'fas fa-sort-up sort-icon ms-1 text-white-50';
    }
    
    // Réinitialiser les autres icônes
    document.querySelectorAll('#tableAppointments .sort-icon').forEach(icon => {
        if (icon !== sortIcon) {
            icon.className = 'fas fa-sort sort-icon ms-1 text-white-50';
        }
    });
    
    // Trier les lignes
    rows.sort((a, b) => {
        const aText = a.children[columnIndex].textContent.trim();
        const bText = b.children[columnIndex].textContent.trim();
        
        // Tri spécial pour les dates
        if (columnIndex === 1) { // Colonne Date/Heure
            const aDate = new Date(aText.split(' ')[0].split('/').reverse().join('-') + ' ' + aText.split(' ')[1]);
            const bDate = new Date(bText.split(' ')[0].split('/').reverse().join('-') + ' ' + bText.split(' ')[1]);
            return ascending ? aDate - bDate : bDate - aDate;
        }
        
        // Tri alphabétique pour les autres colonnes
        return ascending ? aText.localeCompare(bText) : bText.localeCompare(aText);
    });
    
    // Réorganiser les lignes dans le tableau
    rows.forEach(row => tbody.appendChild(row));
}

// Modal pour afficher les détails du rendez-vous
function initializeAppointmentModal() {
    document.addEventListener('click', function(e) {
        if (e.target.closest('.voir-plus-btn')) {
            const btn = e.target.closest('.voir-plus-btn');
            
            // Récupérer les données du bouton
            const date = btn.getAttribute('data-date');
            const patient = btn.getAttribute('data-patient');
            const medecin = btn.getAttribute('data-medecin');
            const motif = btn.getAttribute('data-motif');
            const statut = btn.getAttribute('data-statut');
            
            // Remplir le modal
            document.getElementById('modal-date').textContent = date;
            document.getElementById('modal-patient').textContent = patient;
            document.getElementById('modal-medecin').textContent = medecin;
            document.getElementById('modal-motif').textContent = motif;
            
            // Formater le statut avec badge
            const modalStatut = document.getElementById('modal-statut');
            let statutBadge = '';
            if (statut === 'à venir') {
                statutBadge = '<span class="badge bg-primary">À venir</span>';
            } else if (statut === 'effectué') {
                statutBadge = '<span class="badge bg-success">Effectué</span>';
            } else if (statut === 'annulé') {
                statutBadge = '<span class="badge bg-danger">Annulé</span>';
            } else {
                statutBadge = `<span class="badge bg-secondary">${statut}</span>`;
            }
            modalStatut.innerHTML = statutBadge;
        }
    });
}

// Pagination 2 par page - Style Patient exact
function initializeAppointmentPagination() {
    const table = document.getElementById('tableAppointments');
    const pagination = document.getElementById('appointmentPagination');
    
    if (!table || !pagination) return;
    
    const rowsPerPage = 2;
    const rows = Array.from(table.querySelectorAll('tbody tr:not(.empty-row):not(#appointments-no-results)'));
    
    // Forcer la pagination JavaScript même s'il y a peu de lignes
    if (rows.length > 0) {
        let currentPage = 1;
        const pageCount = Math.ceil(rows.length / rowsPerPage);

        function showPage(page) {
            currentPage = page;
            rows.forEach((row, i) => {
                const shouldShow = (i >= (page - 1) * rowsPerPage && i < page * rowsPerPage);
                row.style.display = shouldShow ? '' : 'none';
            });
            updatePagination(page);
            updateAppointmentCheckboxState(); // Mettre à jour les checkboxes après changement de page
        }

        function updatePagination(page) {
            pagination.innerHTML = '';
            
            // Container pour la pagination - style hr.html
            const paginationNav = document.createElement('nav');
            paginationNav.setAttribute('aria-label', 'Pagination rendez-vous');
            paginationNav.className = 'mt-3';
            
            const paginationUl = document.createElement('ul');
            paginationUl.className = 'pagination justify-content-center flex-wrap';
            
            // Bouton Précédent - style hr.html
            const prev = document.createElement('li');
            prev.className = 'page-item' + (page === 1 ? ' disabled' : '');
            
            if (page === 1) {
                prev.innerHTML = `<span class="page-link">
                    <i class="fas fa-chevron-left d-block d-sm-none"></i>
                    <span class="d-none d-sm-block">&laquo; Préc</span>
                </span>`;
            } else {
                prev.innerHTML = `<a class="page-link" href="#" aria-label="Précédent">
                    <i class="fas fa-chevron-left d-block d-sm-none"></i>
                    <span class="d-none d-sm-block">&laquo; Préc</span>
                </a>`;
                prev.onclick = function(e) { e.preventDefault(); showPage(page - 1); };
            }
            paginationUl.appendChild(prev);
            
            // Pages numérotées - style hr.html
            for (let p = 1; p <= pageCount; p++) {
                const li = document.createElement('li');
                li.className = 'page-item' + (p === page ? ' active' : '');
                
                if (p === page) {
                    li.innerHTML = `<span class="page-link">${p}</span>`;
                } else {
                    li.innerHTML = `<a class="page-link" href="#">${p}</a>`;
                    li.onclick = function(e) { e.preventDefault(); showPage(p); };
                }
                paginationUl.appendChild(li);
            }
            
            // Bouton Suivant - style hr.html
            const next = document.createElement('li');
            next.className = 'page-item' + (page === pageCount ? ' disabled' : '');
            
            if (page === pageCount) {
                next.innerHTML = `<span class="page-link">
                    <i class="fas fa-chevron-right d-block d-sm-none"></i>
                    <span class="d-none d-sm-block">Suiv &raquo;</span>
                </span>`;
            } else {
                next.innerHTML = `<a class="page-link" href="#" aria-label="Suivant">
                    <i class="fas fa-chevron-right d-block d-sm-none"></i>
                    <span class="d-none d-sm-block">Suiv &raquo;</span>
                </a>`;
                next.onclick = function(e) { e.preventDefault(); showPage(page + 1); };
            }
            paginationUl.appendChild(next);
            
            paginationNav.appendChild(paginationUl);
            pagination.appendChild(paginationNav);
        }

        showPage(1);
    }
}

// Gestion du changement automatique du bouton Exporter/Importer
function updateExportImportButton() {
    const exportImportIcon = document.getElementById('export-import-icon');
    const exportImportText = document.getElementById('export-import-text');
    const exportImportBtn = document.getElementById('export-import-btn');
    const checkedBoxes = document.querySelectorAll('#tableAppointments .row-check:checked');
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
    if (e.target.id === 'selectAllAppointments') {
        // Gestion de la case "Sélectionner tout"
        const isChecked = e.target.checked;
        const visibleCheckboxes = document.querySelectorAll('#tableAppointments tbody tr:not([style*="display: none"]) .row-check');
        visibleCheckboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
        });
        updateExportImportButton();
    } else if (e.target.classList.contains('row-check')) {
        // Gestion des cases individuelles
        updateAppointmentCheckboxState();
        updateExportImportButton();
    }
});

// Mettre à jour la fonction updateAppointmentCheckboxState existante
function updateAppointmentCheckboxState() {
    const selectAllCheckbox = document.getElementById('selectAllAppointments');
    if (!selectAllCheckbox) return;
    
    const visibleCheckboxes = Array.from(document.querySelectorAll('#tableAppointments tbody tr:not([style*="display: none"]) .row-check'));
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
