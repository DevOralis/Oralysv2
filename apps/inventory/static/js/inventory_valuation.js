document.addEventListener('DOMContentLoaded', function() {
    const tableBody = document.getElementById('product-table-body');
    const pagination = document.getElementById('pagination');
    const searchInput = document.getElementById('search-input');
    const categorySelect = document.querySelector('select[name="category"]');
    const totalStockValueEl = document.getElementById('totalStockValue');
    const generatePdfButton = document.getElementById('generate-val-pdf');

    let currentSortField = 'name';
    let currentSortOrder = 'asc';

    async function fetchProducts(page = 1, query = '', category = '', sortBy = 'name', sortOrder = 'asc') {
        try {
            const url = new URL('/inventory/valuation/json/', window.location.origin);
            url.searchParams.append('page', page);
            if (query) url.searchParams.append('q', query);
            if (category) url.searchParams.append('category', category);
            url.searchParams.append('sort_by', sortBy);
            url.searchParams.append('sort_order', sortOrder);

            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            const data = await response.json();

            renderProducts(data.products, data.pagination, data.total_stock_value);
        } catch (error) {
            console.error('Error fetching products:', error);
            tableBody.innerHTML = '<tr><td colspan="7" class="text-center">Erreur de chargement des données.</td></tr>';
        }
    }

    function renderProducts(products, paginationData, totalValue) {
        tableBody.innerHTML = '';
        if (products.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Aucun produit trouvé</td></tr>';
            totalStockValueEl.textContent = '0.00 DH';
            const totalStockValueMobileEl = document.getElementById('totalStockValueMobile');
            if (totalStockValueMobileEl) {
                totalStockValueMobileEl.textContent = '0.00 DH';
            }
            pagination.innerHTML = '';
            return;
        }

        products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td data-label="Réf.">${product.default_code || ''}</td>
                <td data-label="Nom">${product.name}</td>
                <td data-label="Catégorie">${product.category ? product.category : '<span class="text-muted">Aucune catégorie</span>'}</td>
                <td data-label="Q.Totale" class="total-qty">${product.total_quantity.toFixed(2)}</td>
                <td data-label="Prix Unitaire" class="unit-price">${product.standard_price.toFixed(2)} <span class="currency">DH</span></td>
                <td data-label="Prix Total" class="total-price">${product.total_price.toFixed(2)} <span class="currency">DH</span></td>
                <td data-label="Détails"><i class="fas fa-chevron-down chevron-toggle" data-product-id="${product.id}"></i></td>
            `;
            tableBody.appendChild(row);

            const locationRow = document.createElement('tr');
            locationRow.className = 'location-row';
            locationRow.id = `location-row-${product.id}`;
            locationRow.style.display = 'none';
            locationRow.innerHTML = `
                <td colspan="7">
                    <table class="table table-responsive table-sm table-hover location-table" id="location-table-${product.id}">
                        <thead class="table-light">
                            <tr><th>Emplacement</th><th>Quantité</th><th>Prix Unitaire</th><th>Prix Total</th></tr>
                        </thead>
                        <tbody id="location-table-body-${product.id}">
                            ${product.locations.length > 0 ? product.locations.map(loc => `
                                <tr>
                                    <td data-label="Emplacement">${loc.location_name}</td>
                                    <td data-label="Quantité">${loc.quantity_stored.toFixed(2)}</td>
                                    <td data-label="Prix Unitaire">${product.standard_price.toFixed(2)} <span class="currency">DH</span></td>
                                    <td data-label="Prix Total">${loc.location_price.toFixed(2)} <span class="currency">DH</span></td>
                                </tr>`).join('') : '<tr><td colspan="4" class="text-center">Aucun emplacement</td></tr>'}
                        </tbody>
                    </table>
                </td>
            `;
            tableBody.appendChild(locationRow);

            // Stocker les données de localisation pour le modal mobile
            if (!window.productLocations) {
                window.productLocations = {};
            }
            window.productLocations[product.id] = product.locations || [];
        });

        totalStockValueEl.textContent = `${totalValue.toFixed(2)} DH`;
        // Mettre à jour aussi la version mobile
        const totalStockValueMobileEl = document.getElementById('totalStockValueMobile');
        if (totalStockValueMobileEl) {
            totalStockValueMobileEl.textContent = `${totalValue.toFixed(2)} DH`;
        }
        renderPagination(paginationData);
        attachToggleEventListeners();
    }

    function renderPagination(pag) {
        pagination.innerHTML = '';
        if (pag.has_previous) {
            pagination.innerHTML += `<li class="page-item"><a class="page-link" href="#" data-page="${pag.previous_page_number}" aria-label="Précédent"><i class="fas fa-chevron-left d-block d-sm-none"></i><span class="d-none d-sm-block">&laquo; Préc</span></a></li>`;
        }
        pag.page_range.forEach(page => {
            pagination.innerHTML += `<li class="page-item ${page === pag.current_page ? 'active' : ''}"><a class="page-link" href="#" data-page="${page}">${page}</a></li>`;
        });
        if (pag.has_next) {
            pagination.innerHTML += `<li class="page-item"><a class="page-link" href="#" data-page="${pag.next_page_number}" aria-label="Suivant"><i class="fas fa-chevron-right d-block d-sm-none"></i><span class="d-none d-sm-block">Suiv &raquo;</span></a></li>`;
        }
        pagination.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', e => {
                e.preventDefault();
                fetchProducts(link.getAttribute('data-page'), searchInput.value, categorySelect.value, currentSortField, currentSortOrder);
            });
        });
    }

    function attachToggleEventListeners() {
        document.querySelectorAll('.chevron-toggle').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const productId = this.getAttribute('data-product-id');
                
                // Détecter si on est sur mobile (écran < 768px)
                const isMobile = window.innerWidth < 768;

                if (isMobile) {
                    // Sur mobile : ouvrir le modal
                    showLocationModal(productId, this);
                } else {
                    // Sur desktop : affichage tableau actuel
                    const locationRow = document.getElementById(`location-row-${productId}`);
                    const locationTable = document.getElementById(`location-table-${productId}`);
                    
                    if (!locationRow) {
                        return;
                    }
                    
                    const isVisible = locationRow.style.display === 'table-row';

                    if (!isVisible) {
                        locationRow.style.display = 'table-row';
                        if (locationTable) locationTable.classList.add('show');
                        this.classList.remove('fa-chevron-down');
                        this.classList.add('fa-chevron-up');
                    } else {
                        locationRow.style.display = 'none';
                        if (locationTable) locationTable.classList.remove('show');
                        this.classList.remove('fa-chevron-up');
                        this.classList.add('fa-chevron-down');
                    }
                }
            });
        });
    }

    function updateSortIcons() {
        document.querySelectorAll('.sortable i').forEach(icon => icon.className = 'fas fa-sort text-muted');
        const activeHeader = document.querySelector(`[data-sort-field="${currentSortField}"] i`);
        if (activeHeader) activeHeader.className = `fas fa-sort-${currentSortOrder === 'asc' ? 'up' : 'down'} text-primary`;
    }

    function initializeSorting() {
        document.querySelectorAll('.sortable').forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                const field = this.getAttribute('data-sort-field');
                currentSortOrder = (currentSortField === field && currentSortOrder === 'asc') ? 'desc' : 'asc';
                currentSortField = field;
                fetchProducts(1, searchInput.value, categorySelect.value, currentSortField, currentSortOrder);
                updateSortIcons();
            });
        });
    }

    let searchTimeout;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            fetchProducts(1, searchInput.value, categorySelect.value, currentSortField, currentSortOrder);
        }, 500);
    });

    categorySelect.addEventListener('change', () => {
        fetchProducts(1, searchInput.value, categorySelect.value, currentSortField, currentSortOrder);
    });

    const initialParams = new URLSearchParams(window.location.search);
    fetchProducts(
        initialParams.get('page') || 1,
        initialParams.get('q') || '',
        initialParams.get('category') || '',
        currentSortField,
        currentSortOrder
    ).then(() => {
        initializeSorting();
        updateSortIcons();
    });

    // Handle PDF generation
    if (generatePdfButton) {
        generatePdfButton.addEventListener('click', async function() {
            try {
                const response = await fetch('/inventory/valuation/pdf/');
                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `inventory_valuation_${new Date().toISOString().split('T')[0].replace(/-/g, '')}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            } catch (e) {
                console.error('Error generating PDF:', e);
                Swal.fire({
                    icon: 'error',
                    title: 'Erreur',
                    text: 'Impossible de générer le PDF. Veuillez réessayer.',
                });
            }
        });
    } else {
        console.error('Generate PDF button not found');
    }

    // Fonction pour afficher le modal des emplacements (mobile)
    function showLocationModal(productId, triggerElement) {
        const locationModalElement = document.getElementById('locationModal');
        const modal = bootstrap.Modal.getOrCreateInstance(locationModalElement);
        const modalBody = document.getElementById('modalLocationTableBody');
        const modalTitle = document.getElementById('modalProductName');
        const modalTotalLocations = document.getElementById('modalTotalLocations');

        // Récupérer les données du produit
        const productRow = document.querySelector(`[data-product-id="${productId}"]`).closest('tr');
        const productName = productRow ? productRow.querySelector('[data-label="Nom"]').textContent : 'Produit';
        const productRef = productRow ? productRow.querySelector('[data-label="Réf."]').textContent : '';
        const unitPriceText = productRow ? productRow.querySelector('[data-label="Prix Unitaire"]').textContent : '0.00 DH';
        const unitPrice = parseFloat(unitPriceText.replace(' DH', '')) || 0;
        
        // Mettre à jour le titre du modal
        modalTitle.textContent = `${productName} (${productRef})`;
        
        // Récupérer les données de localisation
        const locations = window.productLocations && window.productLocations[productId] ? window.productLocations[productId] : [];
        
        // Remplir le tableau du modal
        modalBody.innerHTML = '';
        if (locations.length > 0) {
            locations.forEach(loc => {
                if (loc.location_name && loc.quantity_stored !== undefined && loc.location_price !== undefined) {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td data-label="Emplacement">
                            <i class="fas fa-map-marker-alt text-primary me-2"></i>
                            ${loc.location_name}
                        </td>
                        <td class="text-end" data-label="Quantité">
                            <span class="badge bg-primary">${parseFloat(loc.quantity_stored).toFixed(2)}</span>
                        </td>
                        <td class="text-end" data-label="Prix Unitaire">
                            <span class="badge bg-info">${unitPrice.toFixed(2)} DH</span>
                        </td>
                        <td class="text-end" data-label="Prix Total">
                            <span class="badge bg-success">${parseFloat(loc.location_price).toFixed(2)} DH</span>
                        </td>
                    `;
                    modalBody.appendChild(row);
                }
            });
            modalTotalLocations.textContent = locations.length;
        } else {
            modalBody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-muted p-4">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Aucun emplacement trouvé
                    </td>
                </tr>
            `;
            modalTotalLocations.textContent = '0';
        }

        // Afficher le modal
        modal.show();

        // Gérer l'accessibilité du focus
        locationModalElement.addEventListener('shown.bs.modal', () => {
            const closeButton = locationModalElement.querySelector('.btn-close');
            if (closeButton) closeButton.focus();
        }, { once: true });

        locationModalElement.addEventListener('hidden.bs.modal', () => {
            if (triggerElement) {
                triggerElement.focus();
            }
        }, { once: true });
    }

    // Gérer le redimensionnement de la fenêtre pour basculer entre desktop/mobile
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            // Fermer les tableaux ouverts si on passe en mode mobile
            if (window.innerWidth < 768) {
                document.querySelectorAll('.location-row').forEach(row => {
                    if (row.style.display === 'table-row') {
                        row.style.display = 'none';
                        const productId = row.id.replace('location-row-', '');
                        const chevron = document.querySelector(`[data-product-id="${productId}"]`);
                        if (chevron) {
                            chevron.classList.remove('fa-chevron-up');
                            chevron.classList.add('fa-chevron-down');
                        }
                    }
                });
            }
        }, 100);
    });
});