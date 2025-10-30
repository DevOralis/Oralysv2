// JavaScript spécifique pour les dossiers d'assurance

// Variable pour éviter les initialisations multiples
let insuranceModuleInitialized = false;

document.addEventListener('DOMContentLoaded', function() {
    // Éviter les initialisations multiples
    if (insuranceModuleInitialized) {
        return;
    }
    
    // Initialisation du module d'assurance
    initializeInsuranceRecordsModule();
    insuranceModuleInitialized = true;
});

function initializeInsuranceRecordsModule() {
    // Gestion des messages de succès
    handleSuccessMessages();
    
    // Initialisation de la recherche
    initializeSearch();
    
    // Liaison des boutons d'édition
    bindMutuelleEditButtons();
    
    // Initialisation de la pagination 2 par page
    initializePagination();
    
    // Initialisation du tri des colonnes
    initializeTableSorting();
    
    // Initialisation des checkboxes
    initializeCheckboxes();
    
    // Initialisation du modal détails
    initializeDetailsModal();
    
    // Initialisation de l'export
    initializeExport();
}

function handleSuccessMessages() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Message de succès pour la modification d'assurance
    if (urlParams.get('mutuelle_success') === '1') {
        Swal.fire({
            icon: 'success',
            title: 'Succès',
            text: 'Modification réussie !',
            timer: 2500,
            showConfirmButton: false
        });
        // Retirer le paramètre de l'URL sans recharger
        urlParams.delete('mutuelle_success');
        const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
        window.history.replaceState({}, document.title, newUrl);
    }
    
    // Message de succès pour la mise à jour d'assurance
    if (urlParams.get('success') === 'insurance_updated') {
        Swal.fire({
            icon: 'success',
            title: 'Succès',
            text: 'Les informations d\'assurance ont été mises à jour avec succès.',
            timer: 3000,
            showConfirmButton: false
        });
        // Nettoyer l'URL
        urlParams.delete('success');
        window.history.replaceState({}, document.title, window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : ''));
    }
}

function triggerMutuelleAjax() {
    const search = document.getElementById('search-mutuelle').value;
    const params = new URLSearchParams({ search_mutuelle: search });
    fetch('?' + params.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(response => response.json())
        .then(data => {
            document.getElementById('dossier-mutuelle-table-block').innerHTML = data.html;
            bindMutuelleEditButtons(); // Re-bind buttons after AJAX update
        });
}

function bindMutuelleEditButtons() {
    document.querySelectorAll('.edit-mutuelle-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const patientId = this.getAttribute('data-id');
            const editUrl = `/patient/mutuelle-edit-form/${patientId}/`;
            fetch(editUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(response => response.text())
                .then(html => {
                    document.getElementById('mutuelle-edit-form-container').innerHTML = html;
                    document.getElementById('mutuelle-edit-form-container').style.display = 'block';
                    
                    // Ajouter le listener pour le bouton annuler
                    const cancelBtn = document.getElementById('cancel-mutuelle-edit');
                    if (cancelBtn) {
                        cancelBtn.addEventListener('click', function() {
                            // Masquer la section d'édition
                            document.getElementById('mutuelle-edit-form-container').style.display = 'none';
                            // Remonter vers le haut de la page
                            window.scrollTo({ top: 0, behavior: 'smooth' });
                        });
                    }
                }).catch(error => {
                    console.error('Error loading mutuelle edit form:', error);
                });
        });
    });
}

function initializeSearch() {
    const searchInput = document.getElementById('search-mutuelle');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                triggerMutuelleAjax();
            }, 300);
        });
        
        // Recherche au clic sur Entrée
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                clearTimeout(searchTimeout);
                triggerMutuelleAjax();
            }
        });
        
        // Recherche automatique au chargement si une valeur existe
        if (searchInput.value.trim() !== '') {
            triggerMutuelleAjax();
        }
    }
}

// Pagination 5 par page - Style HR exact
function initializePagination() {
    const table = document.getElementById('tableInsurance');
    if (!table) return;
    
    const rowsPerPage = 5;
    const rows = Array.from(table.querySelectorAll('tbody tr:not(.empty-row):not(#insurance-no-results)'));
    const totalRows = rows.length;
    const totalPages = Math.ceil(totalRows / rowsPerPage);
    let currentPage = 1;
    
    function showPage(page) {
        const startIndex = (page - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;
        
        rows.forEach((row, index) => {
            if (index >= startIndex && index < endIndex) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
        
        updatePaginationButtons(page, totalPages);
    }
    
    function updatePaginationButtons(currentPage, totalPages) {
        const pagination = document.getElementById('mutuellePagination');
        if (!pagination) return;
        
        pagination.innerHTML = '';
        
        // Bouton Précédent - Style HR exact
        const prevLi = document.createElement('li');
        prevLi.className = currentPage === 1 ? 'page-item disabled' : 'page-item';
        if (currentPage === 1) {
            prevLi.innerHTML = '<span class="page-link" aria-label="Précédent">Préc</span>';
        } else {
            prevLi.innerHTML = '<a class="page-link" href="#" data-page="' + (currentPage - 1) + '" aria-label="Précédent">Préc</a>';
        }
        pagination.appendChild(prevLi);
        
        // Boutons de pages - Style HR exact
        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement('li');
            li.className = i === currentPage ? 'page-item active' : 'page-item';
            if (i === currentPage) {
                li.innerHTML = '<span class="page-link">' + i + '</span>';
            } else {
                li.innerHTML = '<a class="page-link" href="#" data-page="' + i + '">' + i + '</a>';
            }
            
            // Masquer certaines pages sur mobile comme dans HR
            if (i > 3 && i !== currentPage && i !== totalPages) {
                li.classList.add('d-none', 'd-sm-block');
            }
            
            pagination.appendChild(li);
        }
        
        // Bouton Suivant - Style HR exact
        const nextLi = document.createElement('li');
        nextLi.className = currentPage === totalPages ? 'page-item disabled' : 'page-item';
        if (currentPage === totalPages) {
            nextLi.innerHTML = '<span class="page-link" aria-label="Suivant">Suiv</span>';
        } else {
            nextLi.innerHTML = '<a class="page-link" href="#" data-page="' + (currentPage + 1) + '" aria-label="Suivant">Suiv</a>';
        }
        pagination.appendChild(nextLi);
        
        // Ajouter les event listeners
        pagination.querySelectorAll('a.page-link').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const page = parseInt(this.dataset.page);
                currentPage = page;
                showPage(page);
            });
        });
    }
    
    // Initialiser la première page
    if (totalRows > 0) {
        showPage(1);
    }
}

// Tri des colonnes
function initializeTableSorting() {
    const sortableHeaders = document.querySelectorAll('.sortable');
    
    sortableHeaders.forEach((header, index) => {
        header.addEventListener('click', function() {
            const sortType = this.dataset.sort;
            const currentDirection = this.dataset.direction || 'asc';
            const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
            
            // Réinitialiser tous les headers
            sortableHeaders.forEach(h => {
                h.dataset.direction = '';
                const icon = h.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-sort text-muted';
                }
            });
            
            // Mettre à jour le header actuel
            this.dataset.direction = newDirection;
            const icon = this.querySelector('i');
            if (icon) {
                icon.className = newDirection === 'asc' 
                    ? 'fas fa-sort-up text-primary' 
                    : 'fas fa-sort-down text-primary';
            }
            
            sortTable(index + 1, sortType, newDirection); // +1 car première colonne est checkbox
            initializePagination(); // Réinitialiser la pagination après tri
        });
    });
}

function sortTable(columnIndex, sortType, direction) {
    const table = document.getElementById('tableInsurance');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr:not(.empty-row)'));
    
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();
        
        let comparison = 0;
        if (sortType === 'number') {
            comparison = parseFloat(aText) - parseFloat(bText);
        } else {
            comparison = aText.localeCompare(bText);
        }
        
        return direction === 'asc' ? comparison : -comparison;
    });
    
    // Réorganiser les lignes
    rows.forEach(row => tbody.appendChild(row));
}

// Gestion des checkboxes
function initializeCheckboxes() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const rowCheckboxes = document.querySelectorAll('.row-check');
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            rowCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }
    
    rowCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const checkedCount = document.querySelectorAll('.row-check:checked').length;
            const totalCount = rowCheckboxes.length;
            
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = checkedCount === totalCount;
                selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < totalCount;
            }
        });
    });
}

// Modal détails - Version corrigée pour récupérer les données
function initializeDetailsModal() {
    const modalElement = document.getElementById('insuranceDetailsModal');
    if (!modalElement) return;
    
    // Utiliser la délégation d'événements pour capturer tous les boutons modal, même après AJAX
    document.addEventListener('click', function(e) {
        // Chercher le bouton modal dans les éléments cliqués
        const modalButton = e.target.closest('.btn[data-nom]');
        
        if (modalButton && modalButton.classList.contains('d-lg-none')) {
            e.preventDefault();
            e.stopPropagation();
            
            // Vérifier que c'est bien un clic intentionnel
            if (e.isTrusted && e.type === 'click') {
                openInsuranceModal(modalButton);
            }
        }
    });
}

// Fonction pour ouvrir le modal de manière contrôlée
function openInsuranceModal(button) {
    if (!button) return;
    
    const modalElement = document.getElementById('insuranceDetailsModal');
    if (!modalElement) return;
    
    // Remplir le modal avec les données
    const modalData = {
        'modal-nom': button.dataset.nom || '-',
        'modal-prenom': button.dataset.prenom || '-',
        'modal-insurance': button.dataset.insurance || '-',
        'modal-affiliation': button.dataset.affiliation || '-',
        'modal-adherent': button.dataset.adherent || '-',
        'modal-relation': button.dataset.relation || '-',
        'modal-telephone': button.dataset.telephone || '-'
    };
    
    // Mettre à jour le contenu
    Object.entries(modalData).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
    
    // Ouvrir le modal manuellement avec configuration normale
    const modal = new bootstrap.Modal(modalElement, {
        backdrop: true,     // Permet la fermeture en cliquant à l'extérieur
        keyboard: true      // Permet la fermeture avec Escape
    });
    
    modal.show();
    
    // S'assurer que le modal se ferme proprement
    modalElement.addEventListener('hidden.bs.modal', function() {
        // Supprimer le backdrop résiduel s'il existe
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        // Restaurer le scroll du body
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    });
}

// Export Excel
function initializeExport() {
    const exportBtn = document.getElementById('export-insurance-btn');
    
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            const table = document.getElementById('tableInsurance');
            if (!table) return;
            
            // Créer les données pour l'export
            const data = [];
            const headers = ['Nom', 'Prénom', 'N° immatriculation', 'N° affiliation', 'Nom adhérent', 'Lien de parenté', 'Téléphone'];
            data.push(headers);
            
            // Récupérer toutes les lignes visibles
            const rows = table.querySelectorAll('tbody tr:not(.empty-row)');
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length > 1) { // Ignorer les lignes vides
                    const rowData = [
                        cells[1].textContent.trim(), // Nom
                        cells[2].textContent.trim(), // Prénom
                        cells[3] ? cells[3].textContent.trim() : '', // N° immatriculation
                        cells[4] ? cells[4].textContent.trim() : '', // N° affiliation
                        cells[5] ? cells[5].textContent.trim() : '', // Nom adhérent
                        cells[6] ? cells[6].textContent.trim() : '', // Lien de parenté
                        cells[7] ? cells[7].textContent.trim() : ''  // Téléphone
                    ];
                    data.push(rowData);
                }
            });
            
            // Créer et télécharger le fichier CSV
            const csvContent = data.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            
            if (link.download !== undefined) {
                const url = URL.createObjectURL(blob);
                link.setAttribute('href', url);
                link.setAttribute('download', 'dossiers_assurance.csv');
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                // Notification de succès
                Swal.fire({
                    icon: 'success',
                    title: 'Export réussi',
                    text: 'Le fichier a été téléchargé avec succès.',
                    timer: 2000,
                    showConfirmButton: false
                });
            }
        });
    }
}

// Gestion du changement automatique du bouton Exporter/Importer
function updateExportImportButton() {
    const exportImportIcon = document.getElementById('export-import-icon');
    const exportImportText = document.getElementById('export-import-text');
    const exportImportBtn = document.getElementById('export-import-btn');
    const checkedBoxes = document.querySelectorAll('#table-dossier-mutuelle .row-check:checked');
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
    if (e.target.id === 'select-all-insurance') {
        // Gestion de la case "Sélectionner tout"
        const isChecked = e.target.checked;
        const visibleCheckboxes = document.querySelectorAll('#table-dossier-mutuelle tbody tr:not([style*="display: none"]) .row-check');
        visibleCheckboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
        });
        updateExportImportButton();
    } else if (e.target.classList.contains('row-check')) {
        // Gestion des cases individuelles
        updateInsuranceCheckboxState();
        updateExportImportButton();
    }
});

// Mettre à jour l'état des checkboxes
function updateInsuranceCheckboxState() {
    const selectAllCheckbox = document.getElementById('select-all-insurance');
    if (!selectAllCheckbox) return;
    
    const visibleCheckboxes = Array.from(document.querySelectorAll('#table-dossier-mutuelle tbody tr:not([style*="display: none"]) .row-check'));
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
