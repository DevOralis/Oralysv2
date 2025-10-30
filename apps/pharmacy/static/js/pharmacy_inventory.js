document.addEventListener('DOMContentLoaded', function() {
    const productTableBody = document.getElementById('product-table-body');
    const pagination = document.getElementById('pagination');
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const generatePdfButton = document.getElementById('generate-pdf');
    
    let currentSortField = '';
    let currentSortOrder = 'asc';

    async function fetchInventoryData(page = 1, query = '', category = '', sortBy = '', sortOrder = 'asc') {
        try {
            const url = new URL('/pharmacy/products/list/json/', window.location.origin);
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
            console.error('Error fetching pharmacy inventory data:', e);
            productTableBody.innerHTML = '<tr><td colspan="5" class="text-center">Erreur lors du chargement des produits</td></tr>';
        }
    }

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
                <td data-label="Code">${product.default_code}</td>
                <td data-label="Libellé">${product.name}</td>
                <td data-label="Catégorie">${product.category ? product.category : '<span class="text-muted">Aucune catégorie</span>'}</td>
                <td data-label="Q.Totale" class="total-qty">${parseFloat(product.total_quantity).toFixed(2)}</td>
                <td data-label="Détails">
                    <i class="fas fa-chevron-down chevron-toggle" data-product-id="${product.id}"></i>
                </td>
            `;
            productTableBody.appendChild(row);

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

            populateLocationTable(product.id, product.locations);
        });

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

        pagination.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', e => {
                e.preventDefault();
                const page = link.getAttribute('data-page');
                fetchInventoryData(page, searchInput.value);
            });
        });

        document.querySelectorAll('.chevron-toggle').forEach(button => {
            button.addEventListener('click', function() {
                const productId = this.getAttribute('data-product-id');
                const isMobile = window.innerWidth < 992;
                
                if (isMobile) {
                    showLocationModal(productId, this);
                } else {
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

    function populateLocationTable(productId, locations) {
        const tableBody = document.getElementById(`location-table-body-${productId}`);
        if (!tableBody) return;

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
                }
            });
        } else {
            tableBody.innerHTML = '<tr><td colspan="2" class="text-muted">Aucun emplacement</td></tr>';
        }
        
        if (!window.productLocations) window.productLocations = {};
        window.productLocations[productId] = locations || [];
    }

    if (generatePdfButton) {
        generatePdfButton.addEventListener('click', async function() {
            try {
                const response = await fetch('/pharmacy/products/list/pdf/');
                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `pharmacy_inventory_${new Date().toISOString().split('T')[0].replace(/-/g, '')}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            } catch (e) {
                console.error('Error generating PDF:', e);
                Swal.fire({ icon: 'error', title: 'Erreur', text: 'Impossible de générer le PDF.' });
            }
        });
    }

    if (searchForm) {
        searchForm.addEventListener('submit', e => {
            e.preventDefault();
            const category = document.querySelector('select[name="category"]').value;
            fetchInventoryData(1, searchInput.value, category);
        });
    }

    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const category = document.querySelector('select[name="category"]').value;
                fetchInventoryData(1, this.value, category);
            }, 500);
        });
    }

    function updateSortIcons(activeField, order) {
        document.querySelectorAll('.sortable i').forEach(icon => {
            icon.className = 'fas fa-sort text-muted';
        });
        
        const activeHeader = document.querySelector(`[data-sort-field="${activeField}"] i`);
        if (activeHeader) {
            activeHeader.className = order === 'asc' ? 'fas fa-sort-up text-primary' : 'fas fa-sort-down text-primary';
        }
    }
    
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
                
                const query = searchInput.value;
                const category = document.querySelector('select[name="category"]').value;
                fetchInventoryData(1, query, category, currentSortField, currentSortOrder);
                
                updateSortIcons(currentSortField, currentSortOrder);
            });
        });
    }

    function showLocationModal(productId, triggerElement) {
        const locationModalElement = document.getElementById('locationModal');
        const modal = bootstrap.Modal.getOrCreateInstance(locationModalElement);
        const modalBody = document.getElementById('modalLocationTableBody');
        const modalTitle = document.getElementById('modalProductName');
        const modalTotalLocations = document.getElementById('modalTotalLocations');
        
        const productRow = document.querySelector(`[data-product-id="${productId}"]`).closest('tr');
        const productName = productRow.querySelector('[data-label="Libellé"]').textContent;
        const productRef = productRow.querySelector('[data-label="Code"]').textContent;
        
        modalTitle.textContent = `${productName} (${productRef})`;
        
        const locations = window.productLocations[productId] || [];
        
        modalBody.innerHTML = '';
        if (locations.length > 0) {
            locations.forEach(loc => {
                if (loc.location_id && loc.quantity_stored !== undefined && loc.location_name) {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td data-label="Emplacement"><i class="fas fa-map-marker-alt text-primary me-2"></i>${loc.location_name}</td>
                        <td class="text-end" data-label="Quantité"><span class="badge bg-primary">${parseFloat(loc.quantity_stored).toFixed(2)}</span></td>
                    `;
                    modalBody.appendChild(row);
                }
            });
            modalTotalLocations.textContent = locations.length;
        } else {
            modalBody.innerHTML = `<tr><td colspan="2" class="text-center text-muted p-4"><i class="fas fa-exclamation-triangle me-2"></i>Aucun emplacement trouvé</td></tr>`;
            modalTotalLocations.textContent = '0';
        }
        
        modal.show();

        locationModalElement.addEventListener('hidden.bs.modal', () => {
            if (triggerElement) triggerElement.focus();
        }, { once: true });
    }
    
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
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

    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page') || 1;
    const query = urlParams.get('q') || '';
    const category = urlParams.get('category') || '';
    fetchInventoryData(page, query, category).then(() => {
        initializeSorting();
    });
});
