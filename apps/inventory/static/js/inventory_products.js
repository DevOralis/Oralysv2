document.addEventListener('DOMContentLoaded', function() {
    let locationsData;
    try {
        locationsData = JSON.parse(document.getElementById('locations-data').textContent || '[]');
    } catch (e) {
        console.warn('Erreur lors du parsing des données locations:', e);
        locationsData = [];
    }

    const plTableBody = document.getElementById('pl-table-body');
    const locationsJsonInput = document.getElementById('locations-json');
    const totalQtySpan = document.getElementById('total-qty');
    const addPlLineBtn = document.getElementById('add-pl-line');
    const productForm = document.getElementById('product-form');

    // Initialize productLocations
    let productLocations = [];
    const urlParams = new URLSearchParams(window.location.search);
    const locationsParam = urlParams.get('locations');
    if (locationsParam) {
        try {
            productLocations = JSON.parse(decodeURIComponent(locationsParam));
        } catch (e) {
            console.error('Erreur lors du parsing des paramètres URL:', e);
        }
    } else {
        // Utiliser les données initialisées par inventory_products_data.js
        productLocations = window.productLocations || [];
        console.log('Product locations loaded:', productLocations);
    }

    // Fonction pour calculer et mettre à jour la quantité totale
    function updateTotalQuantity() {
        let total = 0;
        plTableBody.querySelectorAll('.pl-row').forEach(row => {
            if (row.style.display !== 'none') {
                const locationId = row.querySelector('.location-select').value;
                const quantity = parseFloat(row.querySelector('.quantity-input').value) || 0;
                // Ne compter que les lignes avec emplacement sélectionné et quantité > 0
                if (locationId && quantity > 0 && !isNaN(quantity)) {
                    total += quantity;
                }
            }
        });
        if (totalQtySpan) totalQtySpan.textContent = total.toFixed(2);
        // Mettre à jour le champ total_quantity du formulaire
        const totalQuantityInput = document.getElementById('id_total_quantity');
        if (totalQuantityInput) {
            totalQuantityInput.value = total.toFixed(2);
        }
    }

    // Fonction pour mettre à jour le champ locations_json
    function updateLocationsJson() {
        const rows = plTableBody.querySelectorAll('.pl-row');
        const locations = Array.from(rows)
            .filter(row => {
                const locationId = row.querySelector('.location-select').value;
                const quantity = parseFloat(row.querySelector('.quantity-input').value) || 0;
                return locationId && quantity > 0; 
            })
            .map(row => {
                return {
                    location_id: row.querySelector('.location-select').value,
                    quantity_stored: parseFloat(row.querySelector('.quantity-input').value) || 0
                };
            });
        productLocations = locations;
        locationsJsonInput.value = JSON.stringify(locations);
    }

    // Function to check for duplicate locations
    function hasDuplicateLocations() {
        const rows = plTableBody.querySelectorAll('.pl-row');
        const seenLocations = new Set();
        let hasError = false;

        rows.forEach(row => {
            const locationId = row.querySelector('.location-select').value;
            if (locationId) {
                if (seenLocations.has(locationId)) {
                    hasError = true;
                    row.querySelector('.location-select').classList.add('is-invalid');
                } else {
                    row.querySelector('.location-select').classList.remove('is-invalid');
                    seenLocations.add(locationId);
                }
            }
        });

        return hasError;
    }
    // Fonction pour ajouter une ligne au tableau
    function addLocationRow(locationId = '', quantity = '') {
        if (!plTableBody) {
            return;
        }
        const row = document.createElement('tr');
        row.className = 'pl-row';
        row.innerHTML = `
            <td data-label="Emplacement">
                <select class="form-select form-select-sm location-select" name="location_id">
                    <option value="">Choisir un emplacement</option>
                    ${locationsData.map(loc => `
                        <option value="${loc.id}" ${loc.id == locationId ? 'selected' : ''}>
                            ${loc.name}
                        </option>
                    `).join('')}
                </select>
                <div class="invalid-feedback">Cet emplacement est déjà sélectionné.</div>
            </td>
            <td data-label="Quantité">
                <input type="number" step="0.01" min="0" class="form-control form-control-sm quantity-input" 
                       name="quantity_stored" value="${quantity}" placeholder="0.00">
            </td>
            <td data-label="Actions" class="text-center">
                <button type="button" class="btn btn-sm btn-light border text-danger remove-pl-line">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>
        `;

        plTableBody.appendChild(row);
        // Attacher les événements à la nouvelle ligne
        const locationSelect = row.querySelector('.location-select');
        const quantityInput = row.querySelector('.quantity-input');
        const removeBtn = row.querySelector('.remove-pl-line');

        locationSelect.addEventListener('change', function() {
            if (hasDuplicateLocations()) {
                Swal.fire({
                    icon: 'error',
                    title: 'Emplacement en double',
                    text: 'Cet emplacement est déjà sélectionné dans une autre ligne.',
                    confirmButtonColor: '#dc3545',
                    confirmButtonText: 'OK'
                });
                this.value = '';
            }
            updateLocationsJson();
            updateTotalQuantity();
        });

        quantityInput.addEventListener('input', function() {
            updateLocationsJson();
            updateTotalQuantity();
        });

        removeBtn.addEventListener('click', function() {
            row.remove();
            updateLocationsJson();
            updateTotalQuantity();
        });
    }

    // Fonction pour vider le tableau
    function clearTable() {
        if (plTableBody) {
            plTableBody.innerHTML = '';
        }
        updateLocationsJson();
        updateTotalQuantity();
    }

    // Initialiser le tableau avec les données existantes
    if (productLocations && productLocations.length > 0) {
        productLocations.forEach(loc => {
            addLocationRow(loc.location_id, loc.quantity_stored);
        });
    } else {
        // Ajouter une ligne vide par défaut pour permettre l'ajout d'emplacements
        addLocationRow();
    }
    // Attacher l'événement au bouton d'ajout
    if (addPlLineBtn) {
        addPlLineBtn.addEventListener('click', function(e) {
            e.preventDefault();
            addLocationRow();
        });
    }
    // Validation du formulaire
    if (productForm) {
        productForm.addEventListener('submit', function(e) {
            if (hasDuplicateLocations()) {
                e.preventDefault();
                Swal.fire({
                    icon: 'error',
                    title: 'Emplacements en double',
                    text: 'Vous avez sélectionné le même emplacement plusieurs fois. Veuillez corriger cela.',
                    confirmButtonColor: '#dc3545',
                    confirmButtonText: 'OK'
                });
                return false;
            }

            // Vérifier qu'il y a au moins une ligne avec un emplacement sélectionné
            const rows = plTableBody.querySelectorAll('.pl-row');
            let hasValidLocation = false;
            rows.forEach(row => {
                const locationId = row.querySelector('.location-select').value;
                const quantity = parseFloat(row.querySelector('.quantity-input').value) || 0;
                if (locationId && quantity > 0) {
                    hasValidLocation = true;
                }
            });

            // Mettre à jour les données avant soumission
            updateLocationsJson();
            updateTotalQuantity();
        });
    }

    // Initialiser les quantités totales
    updateTotalQuantity();
    updateLocationsJson();

    // ========================================
    // GESTION DU TRI DES COLONNES
    // ========================================
    // Initialize table sorting for product table (SERVER-SIDE SORTING)
    const productTable = document.getElementById('searchableTable');
    if (productTable) {
        const headers = productTable.querySelectorAll('th[data-sort-field]');
        
        // Set initial sort state from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const currentSortBy = urlParams.get('sort_by');
        const currentSortOrder = urlParams.get('sort_order');
        
        // Update header icons based on current sort
        if (currentSortBy && currentSortOrder) {
            headers.forEach(header => {
                const sortField = header.getAttribute('data-sort-field');
                const sortIcon = header.querySelector('.fas');
                if (sortIcon) {
                    if (sortField === currentSortBy) {
                        header.setAttribute('data-sort-direction', currentSortOrder);
                        if (currentSortOrder === 'asc') {
                            sortIcon.className = 'fas fa-sort-up ms-1 text-primary';
                        } else {
                            sortIcon.className = 'fas fa-sort-down ms-1 text-primary';
                        }
                    } else {
                        header.setAttribute('data-sort-direction', 'none');
                        sortIcon.className = 'fas fa-sort ms-1 text-muted';
                    }
                }
            });
        }
        
        headers.forEach(header => {
            const sortIcon = header.querySelector('.fas.fa-sort, .fas.fa-sort-up, .fas.fa-sort-down');
            if (sortIcon) {
                header.style.cursor = 'pointer';
                if (!header.getAttribute('data-sort-direction')) {
                    header.setAttribute('data-sort-direction', 'none');
                }
                
                header.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const sortField = header.getAttribute('data-sort-field');
                    if (!sortField) return;
                    
                    // Get current sort from URL parameters (more reliable than data attributes)
                    const urlParams = new URLSearchParams(window.location.search);
                    const currentSortBy = urlParams.get('sort_by');
                    const currentSortOrder = urlParams.get('sort_order');
                    
                    let newDirection = 'asc'; // Default direction
                    
                    // If we're clicking on the currently sorted column, toggle direction
                    if (currentSortBy === sortField) {
                        if (currentSortOrder === 'asc') {
                            newDirection = 'desc';
                        } else {
                            newDirection = 'asc';
                        }
                    } else {
                        // If we're clicking on a different column, start with ascending
                        newDirection = 'asc';
                    }
                    
                    // Build new URL with sort parameters
                    const currentUrl = new URL(window.location);
                    currentUrl.searchParams.set('sort_by', sortField);
                    currentUrl.searchParams.set('sort_order', newDirection);
                    
                    // Preserve current page as 1 when sorting
                    currentUrl.searchParams.set('page', '1');
                    
                    // Remove any hash to prevent scrolling to form
                    currentUrl.hash = '';
                    
                    // Navigate to new URL (this will trigger server-side sorting)
                    window.location.href = currentUrl.toString();
                });
            }
        });
    }
    
    // ========================================
    // TRI CÔTÉ SERVEUR - Fonction de tri côté client supprimée
    // Le tri est maintenant géré côté serveur pour tous les éléments
    // ========================================

    // ========================================
    // GESTION DU BOUTON DYNAMIQUE IMPORTER/EXPORTER
    // ========================================
    // Initialize dynamic export/import button
    function initializeDynamicExportButton() {
    const importBtn = document.getElementById('importBtn');
    const exportLink = document.getElementById('exportLink');
    const selectAllCheckbox = document.getElementById('selectAll');
    const rowCheckboxes = document.querySelectorAll('.row-check');
    
    if (!importBtn || !exportLink) return;
    
    // Function to update button visibility
    function updateButtonState() {
        const checkedBoxes = document.querySelectorAll('.row-check:checked');
        const hasSelection = checkedBoxes.length > 0;
        
        if (hasSelection) {
            // Mode Export - montrer le lien d'export, cacher le bouton import
            importBtn.style.display = 'none';
            exportLink.style.display = 'inline-block';
            
            // Update export button text to show selection count
            const exportText = exportLink.querySelector('span');
            if (exportText) {
                exportText.textContent = `Exporter (${checkedBoxes.length})`;
            }
            
            // Optionnel: mettre à jour l'URL d'export pour inclure seulement les éléments sélectionnés
            updateExportUrl(checkedBoxes);
        } else {
            // Mode Import - montrer le bouton import, cacher le lien d'export
            importBtn.style.display = 'inline-block';
            exportLink.style.display = 'none';
            
            // Reset export button text
            const exportText = exportLink.querySelector('span');
            if (exportText) {
                exportText.textContent = 'Exporter';
            }
        }
    }
    
    // Function to update export URL with selected items (optionnel)
    function updateExportUrl(checkedBoxes) {
        if (checkedBoxes.length > 0) {
            // Get selected product IDs
            const selectedIds = Array.from(checkedBoxes).map(checkbox => {
                return checkbox.closest('tr').getAttribute('data-product-id');
            }).filter(id => id);
            
            console.log('Selected IDs:', selectedIds);
            console.log('Number of selected items:', selectedIds.length);
            
            // Validate that we have valid IDs
            if (selectedIds.length === 0) {
                console.warn('No valid product IDs found in selection');
                return;
            }
            
            // Create export URL with selected IDs
            const baseUrl = exportLink.href.split('?')[0]; // Get base URL without parameters
            const exportUrl = new URL(baseUrl, window.location.origin);
            exportUrl.searchParams.set('ids', selectedIds.join(','));
            
            // Preserve existing search and category filters
            const searchInput = document.getElementById('product-search');
            const categorySelect = document.querySelector('select[name="category"]');
            
            if (searchInput && searchInput.value) {
                exportUrl.searchParams.set('q', searchInput.value);
            }
            if (categorySelect && categorySelect.value) {
                exportUrl.searchParams.set('category', categorySelect.value);
            }
            
            // Preserve current sort parameters
            const currentUrlParams = new URLSearchParams(window.location.search);
            const sortBy = currentUrlParams.get('sort_by');
            const sortOrder = currentUrlParams.get('sort_order');
            
            if (sortBy) {
                exportUrl.searchParams.set('sort_by', sortBy);
            }
            if (sortOrder) {
                exportUrl.searchParams.set('sort_order', sortOrder);
            }
            
            exportLink.href = exportUrl.toString();
        }
    }
    
    // Import button click handler
    if (importBtn) {
        importBtn.addEventListener('click', function() {
            // TODO: Implement import functionality
            alert('Fonctionnalité d\'importation à implémenter');
        });
    }
        
        // Listen to checkbox changes
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', updateButtonState);
        }
        
        // Use event delegation for row checkboxes to handle dynamically added rows
        document.addEventListener('change', function(e) {
            if (e.target && e.target.classList.contains('row-check')) {
                updateButtonState();
            }
        });
        
        // Also add direct listeners to existing checkboxes
        rowCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateButtonState);
        });
        
        // Initial state
        updateButtonState();
    }

    // Function to update the selected items counter
    function updateSelectedCount() {
        try {
            const selectedCount = document.querySelectorAll('.row-check:checked').length;
            const counterElement = document.getElementById('selectedCount');
            
            if (counterElement) {
                counterElement.textContent = selectedCount;
                counterElement.style.display = selectedCount > 0 ? 'inline' : 'none';
            }
            
            return selectedCount;
        } catch (error) {
            console.error('Erreur lors de la mise à jour du compteur:', error);
            return 0;
        }
    }
    
    // Initialize the dynamic button
    initializeDynamicExportButton();
    
    // Add event listeners for checkboxes to update the counter
    document.addEventListener('change', function(e) {
        if (e.target && e.target.classList.contains('row-check')) {
            updateSelectedCount();
        }
    });

    // ========================================
    // GESTION DU SELECT ALL POUR LES CHECKBOXES
    // ========================================
    
    // Select All functionality for checkboxes
    const selectAllCheckbox = document.getElementById('selectAll');
    
    // Function to reset all checkboxes and return to import mode
    function resetToImportMode() {
        try {
            // Uncheck all row checkboxes
            document.querySelectorAll('.row-check').forEach(checkbox => {
                checkbox.checked = false;
                // Déclencher manuellement l'événement change pour mettre à jour l'état
                const event = new Event('change', { bubbles: true });
                checkbox.dispatchEvent(event);
            });
            
            // Uncheck the select all checkbox
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = false;
                // Déclencher manuellement l'événement change
                const event = new Event('change', { bubbles: true });
                selectAllCheckbox.dispatchEvent(event);
            }
            
            // Clear any select all state from sessionStorage
            sessionStorage.removeItem('selectAllMode');
            sessionStorage.removeItem('selectAllFilterParams');
            
            // Update button state to show import button and hide export button
            const importBtn = document.getElementById('importBtn');
            const exportLink = document.getElementById('exportLink');
            
            if (importBtn && exportLink) {
                importBtn.style.display = 'inline-block';
                exportLink.style.display = 'none';
                
                // Reset export button text and URL
                const exportText = exportLink.querySelector('span');
                if (exportText) {
                    exportText.textContent = 'Exporter';
                }
                exportLink.href = '#'; // Reset export URL
            }
            
            // Mettre à jour le compteur d'éléments sélectionnés
            updateSelectedCount();
            
            // Forcer la mise à jour de l'interface utilisateur
            if (typeof updateButtonStateForSelectAll === 'function') {
                updateButtonStateForSelectAll();
            }
        } catch (error) {
            console.error('Erreur lors de la réinitialisation du mode import:', error);
        }
    }
    
    // Add cancel button event listener if it exists
    document.addEventListener('click', function(e) {
        if (e.target && e.target.id === 'cancelExport') {
            e.preventDefault();
            resetToImportMode();
        }
    });
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            if (this.checked) {
                // Show confirmation dialog for selecting all items across all pages
                Swal.fire({
                    title: 'Sélectionner tous les éléments ?',
                    text: 'Voulez-vous sélectionner tous les éléments filtrés (sur toutes les pages) ou seulement ceux de cette page ?',
                    icon: 'question',
                    showCancelButton: true,
                    showDenyButton: true,
                    confirmButtonText: 'Tous les éléments',
                    denyButtonText: 'Cette page seulement',
                    cancelButtonText: 'Annuler',
                    confirmButtonColor: '#3085d6',
                    denyButtonColor: '#1e90ff',
                    cancelButtonColor: '#6c757d'
                }).then((result) => {
                    if (result.isConfirmed) {
                        // Select all filtered items across all pages
                        selectAllFilteredItems();
                    } else if (result.isDenied) {
                        // Select only visible items on current page
                        const checkboxes = document.querySelectorAll('.row-check');
                        checkboxes.forEach(checkbox => {
                            checkbox.checked = true;
                        });
                        updateButtonState();
                    } else {
                        // User cancelled, uncheck the select all checkbox
                        this.checked = false;
                    }
                });
            } else {
                // Uncheck all visible checkboxes and clear any "select all" state
                const checkboxes = document.querySelectorAll('.row-check');
                checkboxes.forEach(checkbox => {
                    checkbox.checked = false;
                });
                clearSelectAllState();
                updateButtonState();
            }
        });
    }
    
    // Also handle individual checkbox changes to update select all state
    const rowCheckboxes = document.querySelectorAll('.row-check');
    rowCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (selectAllCheckbox) {
                const allChecked = Array.from(rowCheckboxes).every(cb => cb.checked);
                const noneChecked = Array.from(rowCheckboxes).every(cb => !cb.checked);
                
                if (allChecked) {
                    selectAllCheckbox.checked = true;
                    selectAllCheckbox.indeterminate = false;
                } else if (noneChecked) {
                    selectAllCheckbox.checked = false;
                    selectAllCheckbox.indeterminate = false;
                } else {
                    selectAllCheckbox.checked = false;
                    selectAllCheckbox.indeterminate = true;
                }
            }
        });
    });

    // ========================================
    // GESTION DE LA SUPPRESSION DES PRODUITS
    // ========================================
    
    // Add delete button event listeners
    document.querySelectorAll('.btn-delete-product').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-id');
            const productName = this.getAttribute('data-name');
            
            Swal.fire({
                title: 'Confirmer la suppression',
                text: `Êtes-vous sûr de vouloir supprimer le produit "${productName}" ?`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Oui, supprimer',
                cancelButtonText: 'Annuler',
                confirmButtonColor: '#dc3545',
                cancelButtonColor: '#6c757d'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Créer un formulaire temporaire pour la suppression
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = `/inventory/products/delete/${productId}/`;
                    
                    // Ajouter le token CSRF
                    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                    const csrfInput = document.createElement('input');
                    csrfInput.type = 'hidden';
                    csrfInput.name = 'csrfmiddlewaretoken';
                    csrfInput.value = csrfToken;
                    form.appendChild(csrfInput);
                    
                    document.body.appendChild(form);
                    form.submit();
                }
            });
        });
    });

    // ========================================
    // HELPER FUNCTIONS FOR SELECT ALL
    // ========================================
    
    // Function to select all filtered items across all pages
    function selectAllFilteredItems() {
        // Get current search and filter parameters
        const searchInput = document.getElementById('product-search');
        const categorySelect = document.querySelector('select[name="category"]');
        
        const searchQuery = searchInput ? searchInput.value : '';
        const categoryFilter = categorySelect ? categorySelect.value : '';
        
        // Store the "select all" state
        sessionStorage.setItem('selectAllFiltered', 'true');
        sessionStorage.setItem('selectAllQuery', searchQuery);
        sessionStorage.setItem('selectAllCategory', categoryFilter);
        
        // Check all visible checkboxes on current page
        const checkboxes = document.querySelectorAll('.row-check');
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
        });
        
        // Update button state to show export for all filtered items
        updateButtonStateForSelectAll();
        
        // Show success message
        Swal.fire({
            icon: 'success',
            title: 'Tous les éléments sélectionnés',
            text: 'Tous les éléments filtrés seront exportés (toutes pages confondues)',
            timer: 2000,
            showConfirmButton: false
        });
    }
    
    // Function to clear select all state
    function clearSelectAllState() {
        sessionStorage.removeItem('selectAllFiltered');
        sessionStorage.removeItem('selectAllQuery');
        sessionStorage.removeItem('selectAllCategory');
    }
    
    // Function to check if we're in "select all" mode
    function isSelectAllMode() {
        return sessionStorage.getItem('selectAllFiltered') === 'true';
    }
    
    // Function to update button state for select all mode
    function updateButtonStateForSelectAll() {
        const importBtn = document.getElementById('importBtn');
        const exportLink = document.getElementById('exportLink');
        
        if (importBtn && exportLink) {
            importBtn.style.display = 'none';
            exportLink.style.display = 'inline-block';
            
            // Update export button text to show "all items"
            const exportText = exportLink.querySelector('span');
            if (exportText) {
                exportText.textContent = 'Exporter (Tous)';
            }
            
            // Update export URL for all filtered items
            updateExportUrlForSelectAll();
        }
    }
    
    // Function to update export URL for select all mode
    function updateExportUrlForSelectAll() {
        const exportLink = document.getElementById('exportLink');
        if (!exportLink) return;
        
        // Get base URL without parameters
        const baseUrl = exportLink.href.split('?')[0];
        const exportUrl = new URL(baseUrl, window.location.origin);
        
        // Set select_all parameter to true
        exportUrl.searchParams.set('select_all', 'true');
        
        // Add current search and category filters
        const searchInput = document.getElementById('product-search');
        const categorySelect = document.querySelector('select[name="category"]');
        
        if (searchInput && searchInput.value) {
            exportUrl.searchParams.set('q', searchInput.value);
        }
        if (categorySelect && categorySelect.value) {
            exportUrl.searchParams.set('category', categorySelect.value);
        }
        
        // Preserve current sort parameters
        const currentUrlParams = new URLSearchParams(window.location.search);
        const sortBy = currentUrlParams.get('sort_by');
        const sortOrder = currentUrlParams.get('sort_order');
        
        if (sortBy) {
            exportUrl.searchParams.set('sort_by', sortBy);
        }
        if (sortOrder) {
            exportUrl.searchParams.set('sort_order', sortOrder);
        }
        
        // Update the export link
        exportLink.href = exportUrl.toString();
    }
    
    // Vérifier si nous sommes en mode sélection globale
    if (isSelectAllMode()) {
        // Vérifier que les filtres actuels correspondent à ceux stockés
        const searchInput = document.getElementById('product-search');
        const categorySelect = document.querySelector('select[name="category"]');
        
        const storedQuery = sessionStorage.getItem('selectAllQuery') || '';
        const storedCategory = sessionStorage.getItem('selectAllCategory') || '';
        
        const currentQuery = searchInput ? searchInput.value : '';
        const currentCategory = categorySelect ? categorySelect.value : '';
        
        if (storedQuery !== currentQuery || storedCategory !== currentCategory) {
            // Les filtres ont changé, on sort du mode sélection globale
            clearSelectAllState();
        } else {
            // Mettre à jour l'interface pour le mode sélection globale
            updateButtonStateForSelectAll();
        }
    }
    // ========================================
    // RECHERCHE ET TRI AJAX POUR PRODUCTS.HTML
    // ========================================
    
    // Variables pour la recherche et le tri AJAX
    let currentSortField = '';
    let currentSortOrder = 'asc';
    let allProducts = [];
    
    const productTableBody = document.querySelector('#product-table tbody');
    const productSearch = document.getElementById('product-search');
    const categorySelect = document.querySelector('select[name="category"]');
    const pagination = document.querySelector('.pagination');
    
    // Fonction pour récupérer les données produits via AJAX
    async function fetchProductsData(page = 1, query = '', category = '', sortBy = '', sortOrder = '') {
        try {
            const url = new URL('/inventory/products/list/json/', window.location.origin);
            url.searchParams.append('page', page);
            if (query) url.searchParams.append('q', query);
            if (category) url.searchParams.append('category', category);
            if (sortBy) url.searchParams.append('sort_by', sortBy);
            if (sortOrder) url.searchParams.append('sort_order', sortOrder);

            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            const data = await response.json();

            // Stocker tous les produits pour le tri côté client
            allProducts = data.products;
            renderProductsTable(data.products, data.pagination);
        } catch (e) {
            console.error('Error fetching products data:', e);
            if (productTableBody) {
                productTableBody.innerHTML = '<tr><td colspan="9" class="text-center">Erreur lors du chargement des produits</td></tr>';
            }
        }
    }
    
    // Fonction pour rendre le tableau des produits
    function renderProductsTable(products, paginationData) {
        if (!productTableBody) return;
        
        productTableBody.innerHTML = '';
        if (products.length === 0) {
            productTableBody.innerHTML = '<td colspan="9" class="text-center text-muted"><i class="fas fa-search me-2"></i>Aucun produit trouvé</td></tr>';
            if (pagination) pagination.innerHTML = '';
            return;
        }z

        products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="text-center">
                    <input type="checkbox" class="row-check" value="${product.id}">
                </td>
                <td>${product.default_code || ''}</td>
                <td>${product.name || ''}</td>
                <td class="d-none d-lg-table-cell">${product.category || '<span class="text-muted">Aucune catégorie</span>'}</td>
                <td class="d-none d-lg-table-cell">${product.standard_price ? parseFloat(product.standard_price).toFixed(2) + ' €' : '0.00 €'}</td>
                <td class="d-none d-lg-table-cell">${product.stock_minimal || '0'}</td>
                <td class="d-none d-lg-table-cell">${product.uom || ''}</td>
                <td class="d-none d-lg-table-cell">${product.total_quantity ? parseFloat(product.total_quantity).toFixed(2) : '0.00'}</td>
                <td class="text-center actions-column">
                    <a href="/inventory/products/${product.id}/update/" class="btn btn-sm btn-outline-primary" title="Modifier">
                        <i class="fas fa-edit"></i>
                    </a>
                    <button class="btn btn-sm btn-outline-danger" title="Supprimer" onclick="deleteProduct(${product.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            productTableBody.appendChild(row);
        });

        // Rendre la pagination
        if (pagination && paginationData.total_pages > 1) {
            pagination.innerHTML = '';
            if (paginationData.has_previous) {
                pagination.innerHTML += `
                    <li class="page-item">
                        <a class="page-link" href="#" data-page="${paginationData.previous_page_number}">Préc</a>
                    </li>
                `;
            }
            paginationData.page_range.forEach(page => {
                pagination.innerHTML += `
                    <li class="page-item ${page === paginationData.current_page ? 'active' : ''}">
                        <a class="page-link" href="#" data-page="${page}">${page}</a>
                    </li>
                `;
            });
            if (paginationData.has_next) {
                pagination.innerHTML += `
                    <li class="page-item">
                        <a class="page-link" href="#" data-page="${paginationData.next_page_number}">Suiv</a>
                    </li>
                `;
            }
            
            // Ajouter les gestionnaires d'événements pour la pagination
            pagination.querySelectorAll('.page-link').forEach(link => {
                link.addEventListener('click', e => {
                    e.preventDefault();
                    const page = link.getAttribute('data-page');
                    const query = productSearch ? productSearch.value : '';
                    const category = categorySelect ? categorySelect.value : '';
                    fetchProductsData(page, query, category, currentSortField, currentSortOrder);
                });
            });
        } else if (pagination) {
            pagination.innerHTML = '';
        }
        
        // Réinitialiser les gestionnaires pour les cases à cocher
        initializeDynamicExportButton();
    }
    
    // Fonction de tri côté client
    function sortProducts(products, field, order) {
        return [...products].sort((a, b) => {
            let aVal = a[field] || '';
            let bVal = b[field] || '';
            
            // Gestion spéciale pour les valeurs numériques
            if (['standard_price', 'stock_minimal', 'total_quantity'].includes(field)) {
                aVal = parseFloat(aVal) || 0;
                bVal = parseFloat(bVal) || 0;
            } else {
                // Conversion en string pour comparaison textuelle
                aVal = String(aVal).toLowerCase();
                bVal = String(bVal).toLowerCase();
            }
            
            if (order === 'asc') {
                return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
            } else {
                return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
            }
        });
    }
    
    // Fonction de filtrage côté client
    function filterProducts(products, query, category) {
        return products.filter(product => {
            const matchesQuery = !query || 
                (product.name && product.name.toLowerCase().includes(query.toLowerCase())) ||
                (product.default_code && product.default_code.toLowerCase().includes(query.toLowerCase())) ||
                (product.category && product.category.toLowerCase().includes(query.toLowerCase()));
            
            const matchesCategory = !category || (product.category && product.category === category);
            
            return matchesQuery && matchesCategory;
        });
    }
    
    // Fonction pour mettre à jour les icônes de tri
    function updateSortIcons(activeField, order) {
        document.querySelectorAll('.sortable i').forEach(icon => {
            icon.className = 'fas fa-sort ms-1 text-muted';
        });
        
        const activeHeader = document.querySelector(`[data-sort-field="${activeField}"] i`);
        if (activeHeader) {
            activeHeader.className = order === 'asc' ? 'fas fa-sort-up ms-1 text-primary' : 'fas fa-sort-down ms-1 text-primary';
        }
    }
    
    // Gestionnaire d'événements pour le tri des colonnes
    function initializeSorting() {
        document.querySelectorAll('.sortable').forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                const field = this.getAttribute('data-sort-field');
                
                // Basculer l'ordre si on clique sur la même colonne
                if (currentSortField === field) {
                    currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
                } else {
                    currentSortField = field;
                    currentSortOrder = 'asc';
                }
                
                // Si on a des produits en cache, trier côté client
                if (allProducts.length > 0) {
                    const query = productSearch ? productSearch.value : '';
                    const category = categorySelect ? categorySelect.value : '';
                    let filteredProducts = filterProducts(allProducts, query, category);
                    const sortedProducts = sortProducts(filteredProducts, currentSortField, currentSortOrder);
                    renderProductsTable(sortedProducts, { total_pages: 1, current_page: 1, has_previous: false, has_next: false, page_range: [1] });
                } else {
                    // Sinon, faire un appel serveur
                    const query = productSearch ? productSearch.value : '';
                    const category = categorySelect ? categorySelect.value : '';
                    fetchProductsData(1, query, category, currentSortField, currentSortOrder);
                }
                
                // Mettre à jour les icônes
                updateSortIcons(currentSortField, currentSortOrder);
            });
        });
    }

    // Gestionnaire pour la recherche en temps réel
    if (productSearch) {
        let searchTimeout;
        productSearch.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const category = categorySelect ? categorySelect.value : '';
                
                // Si on a des produits en cache et un tri actif, filtrer côté client
                if (allProducts.length > 0 && currentSortField) {
                    let filteredProducts = filterProducts(allProducts, this.value, category);
                    if (currentSortField) {
                        filteredProducts = sortProducts(filteredProducts, currentSortField, currentSortOrder);
                    }
                    renderProductsTable(filteredProducts, { total_pages: 1, current_page: 1, has_previous: false, has_next: false, page_range: [1] });
                } else {
                    // Sinon, faire un appel serveur
                    fetchProductsData(1, this.value, category, currentSortField, currentSortOrder);
                }
            }, 500);
        });
    }

    // Gestionnaire pour le filtre de catégorie
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            const query = productSearch ? productSearch.value : '';
            
            // Si on a des produits en cache et un tri actif, filtrer côté client
            if (allProducts.length > 0 && currentSortField) {
                let filteredProducts = filterProducts(allProducts, query, this.value);
                if (currentSortField) {
                    filteredProducts = sortProducts(filteredProducts, currentSortField, currentSortOrder);
                }
                renderProductsTable(filteredProducts, { total_pages: 1, current_page: 1, has_previous: false, has_next: false, page_range: [1] });
            } else {
                // Sinon, faire un appel serveur
                fetchProductsData(1, query, this.value, currentSortField, currentSortOrder);
            }
        });
    }
    
    // Chargement initial des données si on est sur la page products
    if (productTableBody && window.location.pathname.includes('/products/')) {
        fetchProductsData().then(() => {
            // Initialiser le tri après le chargement des données
            initializeSorting();
        });
    } else {
        // Initialiser le tri pour les données déjà présentes
        setTimeout(initializeSorting, 100);
    }

}); // Fin de l'écouteur d'événement DOMContentLoaded