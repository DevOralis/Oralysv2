document.addEventListener('DOMContentLoaded', function() {
    const productTableBody = document.getElementById('product-table-body');
    const pagination = document.getElementById('pagination');
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const generatePdfButton = document.getElementById('generate-pdf');
    
    // Variables pour le tri côté client
    let currentSortField = '';
    let currentSortOrder = 'asc';
    let allProducts = []; // Stockage de tous les produits pour le tri côté client

    // Function to fetch inventory data
    async function fetchInventoryData(page = 1, query = '', category = '', sortBy = '', sortOrder = 'asc') {
        try {
            const url = new URL('/inventory/products/list/json/', window.location.origin);
            url.searchParams.append('page', page);
            if (query) url.searchParams.append('q', query);
            if (category) url.searchParams.append('category', category);
            if (sortBy) {
                url.searchParams.append('sort_by', sortBy);
                url.searchParams.append('sort_order', sortOrder);
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            const data = await response.json();

            renderProducts(data.products, data.pagination);
        } catch (e) {
            console.error('Error fetching inventory data:', e);
            productTableBody.innerHTML = '<tr><td colspan="5" class="text-center">Erreur lors du chargement des produits</td></tr>';
        }
    }

    // Function to render products and pagination
    function renderProducts(products, paginationData) {
        productTableBody.innerHTML = '';
        if (products.length === 0) {
            productTableBody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Aucun produit trouvé</td></tr>';
            pagination.innerHTML = '';
            return;
        }

        products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td data-label="Réf.">${product.default_code}</td>
                <td data-label="Nom">${product.name}</td>
                <td data-label="Catégorie">${product.category ? product.category : '<span class="text-muted">Aucune catégorie</span>'}</td>
                <td data-label="Q.Totale" class="total-qty">${parseFloat(product.total_quantity).toFixed(2)}</td>
                <td data-label="Détails">
                    <i class="fas fa-chevron-down chevron-toggle" data-product-id="${product.id}"></i>
                </td>
            `;
            productTableBody.appendChild(row);

            // Add location table row
            const locationRow = document.createElement('tr');
            locationRow.className = 'location-row';
            locationRow.id = `location-row-${product.id}`;
            locationRow.style.display = 'none';
            locationRow.innerHTML = `
                <td colspan="6">
                    <table class="table table-responsive table-sm table-hover location-table" id="location-table-${product.id}">
                        <thead class="table-light">
                            <tr>
                                <th>Emplacement</th>
                                <th>Quantité</th>
                            </tr>
                        </thead>
                        <tbody id="location-table-body-${product.id}"></tbody>
                    </table>
                </td>
            `;
            productTableBody.appendChild(locationRow);

            // Populate location table
            populateLocationTable(product.id, product.locations);
        });

        // Render pagination
        pagination.innerHTML = '';
        if (paginationData.total_pages > 1) {
            if (paginationData.has_previous) {
                pagination.innerHTML += `
                    <li class="page-item">
                        <a class="page-link" href="#" data-page="${paginationData.previous_page_number}" aria-label="Précédent"><i class="fas fa-chevron-left d-block d-sm-none"></i><span class="d-none d-sm-block">&laquo; Préc</span></a>
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
                        <a class="page-link" href="#" data-page="${paginationData.next_page_number}" aria-label="Suivant"><i class="fas fa-chevron-right d-block d-sm-none"></i><span class="d-none d-sm-block">Suiv &raquo;</span></a>
                    </li>
                `;
            }
        }

        // Add pagination event listeners
        pagination.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', e => {
                e.preventDefault();
                const page = link.getAttribute('data-page');
                fetchInventoryData(page, searchInput.value);
            });
        });

        // Add chevron event listeners with mobile/desktop detection
        document.querySelectorAll('.chevron-toggle').forEach(button => {
            button.addEventListener('click', function() {
                const productId = this.getAttribute('data-product-id');
                
                // Détecter si on est sur mobile (écran < 992px = lg breakpoint)
                const isMobile = window.innerWidth < 992;
                
                if (isMobile) {
                    // Sur mobile : ouvrir le modal
                    showLocationModal(productId, this); // Pass the trigger element for accessibility
                } else {
                    // Sur desktop : affichage tableau actuel
                    const locationRow = document.getElementById(`location-row-${productId}`);
                    const locationTable = document.getElementById(`location-table-${productId}`);
                    const isVisible = locationRow.style.display === 'table-row';

                    if (!isVisible) {
                        locationRow.style.display = 'table-row';
                        locationTable.classList.add('show');
                        this.classList.remove('fa-chevron-down');
                        this.classList.add('fa-chevron-up');
                    } else {
                        locationRow.style.display = 'none';
                        locationTable.classList.remove('show');
                        this.classList.remove('fa-chevron-up');
                        this.classList.add('fa-chevron-down');
                    }
                }
            });
        });
    }

    // Function to populate location table
    function populateLocationTable(productId, locations) {
        const tableBody = document.getElementById(`location-table-body-${productId}`);
        if (!tableBody) {
            console.error(`Table body for product ${productId} not found`);
            return;
        }

        tableBody.innerHTML = '';
        if (Array.isArray(locations) && locations.length > 0) {
            locations.forEach(loc => {
                if (loc.location_id && loc.quantity_stored !== undefined && loc.location_name) {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td data-label="Emplacement">${loc.location_name}</td>
                        <td data-label="Quantité">${parseFloat(loc.quantity_stored).toFixed(2)}</td>
                    `;
                    tableBody.appendChild(row);
                } else {
                    console.warn(`Invalid location data for product ${productId}:`, loc);
                }
            });
        } else {
            console.log(`No locations for product ${productId}`);
            tableBody.innerHTML = '<tr><td colspan="2" class="text-muted">Aucun emplacement</td></tr>';
        }
        
        // Stocker les données de localisation pour le modal mobile
        if (!window.productLocations) {
            window.productLocations = {};
        }
        window.productLocations[productId] = locations || [];
    }

    // Handle PDF generation
    if (generatePdfButton) {
        generatePdfButton.addEventListener('click', async function() {
            try {
                const response = await fetch('/inventory/products/list/pdf/');
                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `inventory_${new Date().toISOString().split('T')[0].replace(/-/g, '')}.pdf`;
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

    // Handle search form submission
    if (searchForm) {
        searchForm.addEventListener('submit', e => {
            e.preventDefault();
            const categorySelect = document.querySelector('select[name="category"]');
            const category = categorySelect ? categorySelect.value : '';
            fetchInventoryData(1, searchInput.value, category);
        });
    }

    // Fonction de filtrage côté client
    function filterProducts(products, query, category) {
        return products.filter(product => {
            const matchesQuery = !query || 
                product.name.toLowerCase().includes(query.toLowerCase()) ||
                product.default_code.toLowerCase().includes(query.toLowerCase()) ||
                (product.category && product.category.toLowerCase().includes(query.toLowerCase()));
            
            const matchesCategory = !category || (product.category && product.category === category);
            
            return matchesQuery && matchesCategory;
        });
    }

    // Handle search input with auto-submit
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const categorySelect = document.querySelector('select[name="category"]');
                const category = categorySelect ? categorySelect.value : '';
                
                // Si on a des produits en cache et un tri actif, filtrer côté client
                if (allProducts.length > 0 && currentSortField) {
                    let filteredProducts = filterProducts(allProducts, this.value, category);
                    if (currentSortField) {
                        filteredProducts = sortProducts(filteredProducts, currentSortField, currentSortOrder);
                    }
                    renderProducts(filteredProducts, { total_pages: 1, current_page: 1, has_previous: false, has_next: false, page_range: [1] });
                } else {
                    // Sinon, faire un appel serveur
                    fetchInventoryData(1, this.value, category);
                }
            }, 500);
        });
    }

    // Fonction pour mettre à jour les icônes de tri
    function updateSortIcons(activeField, order) {
        document.querySelectorAll('.sortable i').forEach(icon => {
            icon.className = 'fas fa-sort text-muted';
        });
        
        const activeHeader = document.querySelector(`[data-sort-field="${activeField}"] i`);
        if (activeHeader) {
            activeHeader.className = order === 'asc' ? 'fas fa-sort-up text-primary' : 'fas fa-sort-down text-primary';
        }
    }
    
    // Gestionnaire d'événements pour le tri des colonnes
    function initializeSorting() {
        document.querySelectorAll('.sortable').forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                const field = this.getAttribute('data-sort-field');
                
                if (currentSortField === field) {
                    currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
                } else {
                    currentSortField = field;
                    currentSortOrder = 'asc';
                }
                
                // Fetch sorted data from server
                const query = searchInput.value;
                const categorySelect = document.querySelector('select[name="category"]');
                const category = categorySelect ? categorySelect.value : '';
                fetchInventoryData(1, query, category, currentSortField, currentSortOrder);
                
                updateSortIcons(currentSortField, currentSortOrder);
            });
        });
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
        
        // Mettre à jour le titre du modal
        modalTitle.textContent = `${productName} (${productRef})`;
        
        // Récupérer les données de localisation
        const locations = window.productLocations && window.productLocations[productId] ? window.productLocations[productId] : [];
        
        // Remplir le tableau du modal
        modalBody.innerHTML = '';
        if (locations.length > 0) {
            locations.forEach(loc => {
                if (loc.location_id && loc.quantity_stored !== undefined && loc.location_name) {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td data-label="Emplacement">
                            <i class="fas fa-map-marker-alt text-primary me-2"></i>
                            ${loc.location_name}
                        </td>
                        <td class="text-end" data-label="Quantité">
                            <span class="badge bg-primary">${parseFloat(loc.quantity_stored).toFixed(2)}</span>
                        </td>
                    `;
                    modalBody.appendChild(row);
                }
            });
            modalTotalLocations.textContent = locations.length;
        } else {
            modalBody.innerHTML = `
                <tr>
                    <td colspan="2" class="text-center text-muted p-4">
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
            if (window.innerWidth < 992) {
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

    // Initial data fetch
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page') || 1;
    const query = urlParams.get('q') || '';
    const category = urlParams.get('category') || '';
    fetchInventoryData(page, query, category).then(() => {
        // Initialiser le tri après le chargement des données
        initializeSorting();
    });
});