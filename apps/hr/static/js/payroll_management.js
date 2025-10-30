document.addEventListener('DOMContentLoaded', function() {
    const payrollForm = document.getElementById('payrollForm');
    if (payrollForm) {
        payrollForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Empêcher la soumission normale

            // Valider les champs manuellement
            const employeeId = document.getElementById('employeeSelect').value;
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;

            if (!employeeId || !startDate || !endDate) {
                Swal.fire({
                    icon: 'error',
                    title: 'Champs requis',
                    text: 'Veuillez sélectionner un employé et les dates de début et de fin.',
                });
                return;
            }

            // Construire l'URL et ouvrir dans un nouvel onglet
            const url = this.action + '?' + new URLSearchParams(new FormData(this)).toString();
            window.open(url, '_blank');

            // Recharger la page après un court délai pour afficher la nouvelle entrée
            setTimeout(function() {
                location.reload();
            }, 1500); // 1.5 secondes de délai
        });
    }

    const historyContainer = document.getElementById('payrollHistoryContainer');
    const filtersForm = document.getElementById('payrollHistoryFilters');
    
    if (!historyContainer || !filtersForm) {
        console.log('Éléments payroll history non trouvés');
        return;
    }

    function fetchHistoryAJAX() {
        const params = new URLSearchParams(new FormData(filtersForm)).toString();
        fetch(`?${params}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.text())
        .then(data => {
            historyContainer.innerHTML = data;
            // Réinitialiser les checkboxes après le chargement AJAX
            setTimeout(initializeAfterAJAX, 100);
        });
    }

    const searchInput = filtersForm.querySelector('input[name="search"]');
    const employeeSelect = filtersForm.querySelector('select[name="employee_id"]');
    
    if (searchInput) {
        searchInput.addEventListener('input', fetchHistoryAJAX);
    }
    if (employeeSelect) {
        employeeSelect.addEventListener('change', fetchHistoryAJAX);
    }

    historyContainer.addEventListener('click', function(e) {
        if (e.target.tagName === 'A' && e.target.closest('.pagination')) {
            e.preventDefault();
            const url = e.target.href;
            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(data => {
                historyContainer.innerHTML = data;
                // Réinitialiser les checkboxes après le changement de page
                setTimeout(initializeAfterAJAX, 100);
            })
            .catch(error => console.error('Error fetching payroll history:', error));
        }
    });

    // Gestion du bouton d'export de l'historique
    const exportHistoryBtn = document.getElementById('exportPayrollHistoryBtn');
    if (exportHistoryBtn) {
        exportHistoryBtn.addEventListener('click', function() {
            const params = new URLSearchParams(new FormData(filtersForm)).toString();
            const exportUrl = `/hr/payroll/export/?${params}`;
            
            // Créer un lien temporaire pour télécharger
            const link = document.createElement('a');
            link.href = exportUrl;
            link.download = `historique_bulletins_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // Feedback utilisateur
            Swal.fire({
                icon: 'success',
                title: 'Export en cours',
                text: 'Le téléchargement de l\'historique va commencer...',
                timer: 2000,
                showConfirmButton: false
            });
        });
    }

    // Gestion simple des checkboxes comme hr.html
    function setupPayrollCheckboxes() {
        const selectAllCheckbox = document.getElementById('selectAll');
        const rowCheckboxes = document.querySelectorAll('.row-check');
        
        // Supprimer les anciens event listeners pour éviter les doublons
        if (selectAllCheckbox) {
            // Cloner l'élément pour supprimer tous les event listeners
            const newSelectAll = selectAllCheckbox.cloneNode(true);
            selectAllCheckbox.parentNode.replaceChild(newSelectAll, selectAllCheckbox);
            
            // Ajouter le nouvel event listener
            newSelectAll.addEventListener('change', function() {
                const currentRowCheckboxes = document.querySelectorAll('.row-check');
                currentRowCheckboxes.forEach(checkbox => {
                    checkbox.checked = this.checked;
                });
                updateExportImportButton();
            });
        }
        
        // Supprimer et re-ajouter les event listeners pour les cases individuelles
        rowCheckboxes.forEach(checkbox => {
            const newCheckbox = checkbox.cloneNode(true);
            checkbox.parentNode.replaceChild(newCheckbox, checkbox);
            
            newCheckbox.addEventListener('change', function() {
                const currentSelectAll = document.getElementById('selectAll');
                const currentRowCheckboxes = document.querySelectorAll('.row-check');
                const allChecked = Array.from(currentRowCheckboxes).every(cb => cb.checked);
                const someChecked = Array.from(currentRowCheckboxes).some(cb => cb.checked);
                
                if (currentSelectAll) {
                    currentSelectAll.checked = allChecked;
                    currentSelectAll.indeterminate = someChecked && !allChecked;
                }
                updateExportImportButton();
            });
        });
    }

    // Initialiser les checkboxes après chargement AJAX
    function initializeAfterAJAX() {
        setupPayrollCheckboxes();
        updateExportImportButton();
        
        // Réinitialiser l'état de la case "Sélectionner tout"
        const selectAllCheckbox = document.getElementById('selectAll');
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        }
    }

    // Appeler après le chargement initial
    initializeAfterAJAX();

    // Gestion du modal des détails
    function setupPayrollDetailsModal() {
        const detailButtons = document.querySelectorAll('.view-payroll-details');
        
        detailButtons.forEach(button => {
            button.addEventListener('click', function() {
                const employee = this.getAttribute('data-employee');
                const generatedBy = this.getAttribute('data-generated-by');
                const generatedAt = this.getAttribute('data-generated-at');
                const period = this.getAttribute('data-period');
                const startDate = this.getAttribute('data-start-date');
                const endDate = this.getAttribute('data-end-date');
                
                // Remplir le modal avec les données
                document.getElementById('modalEmployee').textContent = employee;
                document.getElementById('modalGeneratedBy').textContent = generatedBy;
                document.getElementById('modalGeneratedAt').textContent = generatedAt;
                document.getElementById('modalPeriod').textContent = period;
                document.getElementById('modalStartDate').textContent = startDate;
                document.getElementById('modalEndDate').textContent = endDate;
                
                // Ouvrir le modal
                const modalElement = document.getElementById('payrollDetailsModal');
                const modal = new bootstrap.Modal(modalElement, {
                    backdrop: true,
                    keyboard: true,
                    focus: true
                });
                modal.show();
                
                // S'assurer que le modal se ferme correctement
                modalElement.addEventListener('hidden.bs.modal', function () {
                    document.body.classList.remove('modal-open');
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {
                        backdrop.remove();
                    }
                });
            });
        });
    }

    // Fonction de tri côté client pour le tableau payroll
    function setupPayrollSorting() {
        const sortableHeaders = document.querySelectorAll('#payrollHistoryTable .sortable');
        
        sortableHeaders.forEach(header => {
            header.addEventListener('click', function() {
                const sortField = this.dataset.sort;
                const currentDirection = this.dataset.direction || 'asc';
                const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
                
                // Mettre à jour l'icône de tri
                updateSortIcons(this, newDirection);
                
                // Trier le tableau côté client
                sortTableByColumn(sortField, newDirection);
                
                // Sauvegarder la direction pour ce header
                this.dataset.direction = newDirection;
            });
        });
    }

    function sortTableByColumn(sortField, direction) {
        const table = document.getElementById('payrollHistoryTable');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr:not(.empty-row)'));
        
        rows.sort((a, b) => {
            let aValue, bValue;
            
            switch(sortField) {
                case 'employee':
                    aValue = a.querySelector('[data-label="Employé"]')?.textContent.trim() || '';
                    bValue = b.querySelector('[data-label="Employé"]')?.textContent.trim() || '';
                    break;
                case 'generated_by':
                    aValue = a.querySelector('[data-label="Généré par"]')?.textContent.trim() || '';
                    bValue = b.querySelector('[data-label="Généré par"]')?.textContent.trim() || '';
                    break;
                case 'generated_at':
                    aValue = a.querySelector('[data-label="Date génération"]')?.textContent.trim() || '';
                    bValue = b.querySelector('[data-label="Date génération"]')?.textContent.trim() || '';
                    break;
                case 'period':
                    aValue = a.querySelector('[data-label="Période"] .badge')?.textContent.trim() || '';
                    bValue = b.querySelector('[data-label="Période"] .badge')?.textContent.trim() || '';
                    break;
                default:
                    return 0;
            }
            
            const comparison = aValue.localeCompare(bValue, 'fr', { numeric: true });
            return direction === 'asc' ? comparison : -comparison;
        });
        
        // Réorganiser les lignes
        rows.forEach(row => tbody.appendChild(row));
    }

    function updateSortIcons(activeHeader, direction) {
        // Réinitialiser toutes les icônes
        document.querySelectorAll('#payrollHistoryTable .sort-icon').forEach(icon => {
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

    // Initialiser les checkboxes, modal et tri après chargement AJAX
    function initializeAfterAJAX() {
        setupPayrollCheckboxes();
        setupPayrollDetailsModal();
        setupPayrollSorting();
    }

    // Appeler après le chargement initial
    initializeAfterAJAX();

    // Réinitialiser après chaque mise à jour AJAX
    const originalFetchHistoryAJAX = fetchHistoryAJAX;
    fetchHistoryAJAX = function() {
        const promise = originalFetchHistoryAJAX();
        if (promise && promise.then) {
            promise.then(() => {
                setTimeout(initializeAfterAJAX, 100);
            });
        } else {
            setTimeout(initializeAfterAJAX, 100);
        }
        return promise;
    };

    // Gestion du changement automatique du bouton Exporter/Importer
    function updateExportImportButton() {
        const exportImportIcon = document.getElementById('export-import-icon');
        const exportImportText = document.getElementById('export-import-text');
        const checkedBoxes = document.querySelectorAll('.row-check:checked');
        const hasCheckedItems = checkedBoxes.length > 0;
        
        if (exportImportIcon && exportImportText) {
            if (hasCheckedItems) {
                // Changer en mode "Exporter" quand des cases sont cochées
                exportImportIcon.className = 'fas fa-file-export';
                exportImportText.textContent = 'Exporter';
            } else {
                // Mode par défaut "Importer" quand aucune case n'est cochée
                exportImportIcon.className = 'fas fa-file-import';
                exportImportText.textContent = 'Importer';
            }
        }
    }
    
    // Utiliser la délégation d'événements pour gérer les checkboxes dynamiques
    document.addEventListener('change', function(e) {
        if (e.target.id === 'selectAll') {
            // Gestion de la case "Sélectionner tout"
            const rowCheckboxes = document.querySelectorAll('.row-check');
            rowCheckboxes.forEach(checkbox => {
                checkbox.checked = e.target.checked;
            });
            updateExportImportButton();
        } else if (e.target.classList.contains('row-check')) {
            // Gestion des cases individuelles
            const selectAllCheckbox = document.getElementById('selectAll');
            const allCheckboxes = document.querySelectorAll('.row-check');
            const checkedCheckboxes = document.querySelectorAll('.row-check:checked');
            
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = allCheckboxes.length === checkedCheckboxes.length;
                selectAllCheckbox.indeterminate = checkedCheckboxes.length > 0 && checkedCheckboxes.length < allCheckboxes.length;
            }
            updateExportImportButton();
        }
    });
    
    // Mettre à jour la fonction updateExportButton existante pour utiliser la nouvelle logique
    window.updateExportButton = updateExportImportButton;
    
    // Initialiser l'état du bouton au chargement
    updateExportImportButton();

});
