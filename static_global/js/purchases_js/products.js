document.addEventListener('DOMContentLoaded', function() {
    // Load locations data
    let locationsData;
    try {
        locationsData = JSON.parse(document.getElementById('locations-data').textContent || '[]');
        console.log('locationsData:', locationsData);
    } catch (e) {
        console.error('Error parsing locations-data:', e);
        locationsData = [];
    }

    // Load product types data
    let productTypesData;
    try {
        productTypesData = JSON.parse(document.getElementById('product-types-data').textContent || '[]');
        console.log('productTypesData:', productTypesData);
    } catch (e) {
        console.error('Error parsing product-types-data:', e);
        productTypesData = [];
    }

    const plTableBody = document.getElementById('pl-table-body');
    const locationsJsonInput = document.getElementById('locations-json');
    const totalQtySpan = document.getElementById('total-qty');
    const addPlLineBtn = document.getElementById('add-pl-line');
    const productForm = document.getElementById('product-form');
    const productTypeSelect = document.getElementById('id_product_type');

    // Initialize productLocations
    let productLocations = [];
    try {
        productLocations = window.productLocations || [];
        console.log('productLocations from window:', productLocations);
    } catch (e) {
        console.error('Error initializing productLocations:', e);
        productLocations = [];
    }

    // Fonction pour calculer et mettre à jour la quantité totale
    function updateTotalQuantity() {
        let total = 0;
        plTableBody.querySelectorAll('.quantity-input').forEach(input => {
            const row = input.closest('.pl-row');
            if (row && row.style.display !== 'none') {
                const value = parseFloat(input.value) || 0;
                if (!isNaN(value)) total += value;
            }
        });
        if (totalQtySpan) totalQtySpan.textContent = total.toFixed(2);
        const totalQuantityInput = document.getElementById('id_total_quantity');
        if (totalQuantityInput) {
            totalQuantityInput.value = total.toFixed(2);
        }
    }

    // Fonction pour mettre à jour le champ locations_json
    function updateLocationsJson() {
        const rows = plTableBody.querySelectorAll('.pl-row');
        const locations = Array.from(rows)
            .filter(row => row.style.display !== 'none')
            .map(row => {
                return {
                    location_id: row.querySelector('.location-select').value,
                    quantity_stored: parseFloat(row.querySelector('.quantity-input').value) || 0
                };
            })
            .filter(loc => loc.location_id && loc.quantity_stored > 0); // Only include valid entries
        productLocations = locations;
        locationsJsonInput.value = JSON.stringify(locations);
        console.log('Updated locations_json:', locations);
    }

    // Function to check for duplicate locations
    function hasDuplicateLocations() {
        const rows = plTableBody.querySelectorAll('.pl-row');
        const seenLocations = new Set();
        let hasError = false;

        rows.forEach(row => {
            if (row.style.display !== 'none') {
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
            }
        });

        return hasError;
    }

    // Fonction pour vérifier si le type est "stockable"
    function isStockableType(typeId) {
        const type = productTypesData.find(pt => pt.id == typeId);
        return type && type.label.toLowerCase() === 'stockable';
    }

    // Fonction pour afficher/masquer la section des emplacements
    function toggleLocationsSection(show) {
        const plTable = document.getElementById('pl-table');
        const addPlLineBtn = document.getElementById('add-pl-line');
        const totalQtySection = document.querySelector('.d-flex.justify-content-between.mb-3');

        if (plTable && addPlLineBtn && totalQtySection) {
            plTable.style.display = show ? 'table' : 'none';
            addPlLineBtn.style.display = show ? 'inline-block' : 'none';
            totalQtySection.style.display = show ? 'flex' : 'none';

            if (!show) {
                clearTable();
                updateTotalQuantity();
                updateLocationsJson();
            }
        }
    }

    // Fonction pour ajouter une ligne au tableau
    function addLocationRow(locationId = '', quantity = '') {
        console.log('Adding row with locationId:', locationId, 'quantity:', quantity);
        if (!plTableBody) {
            console.error('plTableBody is null');
            return;
        }
        const row = document.createElement('tr');
        row.className = 'pl-row';
        row.innerHTML = `
            <td>
                <select class="form-select form-select-sm location-select" name="location_id">
                    <option value="">Sélectionner un emplacement</option>
                    ${locationsData.map(loc => `
                        <option value="${loc.id}" ${loc.id == locationId ? 'selected' : ''}>
                            ${loc.name}
                        </option>
                    `).join('')}
                </select>
                <div class="invalid-feedback">Cet emplacement est déjà sélectionné.</div>
            </td>
            <td>
                <input type="number" class="form-control form-control-sm quantity-input" name="quantity_stored" value="${quantity || ''}" step="0.01" min="0">
                <div class="invalid-feedback">La quantité doit être supérieure à 0.</div>
            </td>
            <td>
                <button type="button" class="btn btn-sm btn-danger btn-remove-line">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>
        `;
        plTableBody.appendChild(row);

        const locationSelect = row.querySelector('.location-select');
        const quantityInput = row.querySelector('.quantity-input');
        const removeButton = row.querySelector('.btn-remove-line');

        if (locationSelect && quantityInput && removeButton) {
            locationSelect.addEventListener('change', () => {
                updateLocationsJson();
                hasDuplicateLocations();
            });
            quantityInput.addEventListener('input', () => {
                updateTotalQuantity();
                updateLocationsJson();
            });
            removeButton.addEventListener('click', () => {
                console.log('Removing row');
                row.style.display = 'none'; // Soft delete to preserve data
                updateTotalQuantity();
                updateLocationsJson();
                hasDuplicateLocations();
            });
        } else {
            console.error('Failed to find elements in row:', { locationSelect, quantityInput, removeButton });
        }

        updateTotalQuantity();
        updateLocationsJson();
    }

    // Clear table before adding rows
    function clearTable() {
        while (plTableBody.firstChild) {
            plTableBody.removeChild(plTableBody.firstChild);
        }
        console.log('Table cleared');
    }

    // Initialize table with existing product locations
    console.log('Initial productLocations:', productLocations);
    if (Array.isArray(productLocations) && productLocations.length > 0) {
        clearTable();
        productLocations.forEach(loc => {
            if (loc.location_id && loc.quantity_stored !== undefined) {
                console.log('Adding location row:', loc);
                addLocationRow(loc.location_id, loc.quantity_stored.toString());
            } else {
                console.warn('Invalid location data:', loc);
            }
        });
    } else {
        console.log('No product locations to display');
        clearTable();
    }

    // Handle product type change
    if (productTypeSelect) {
        toggleLocationsSection(isStockableType(productTypeSelect.value));
        productTypeSelect.addEventListener('change', function() {
            const showLocations = isStockableType(this.value);
            toggleLocationsSection(showLocations);
            if (showLocations && productLocations.length > 0) {
                clearTable();
                productLocations.forEach(loc => {
                    if (loc.location_id && loc.quantity_stored !== undefined) {
                        addLocationRow(loc.location_id, loc.quantity_stored.toString());
                    }
                });
            }
        });
    } else {
        console.error('productTypeSelect is null');
    }

    // Add new location row
    if (addPlLineBtn) {
        addPlLineBtn.addEventListener('click', () => {
            if (isStockableType(productTypeSelect.value)) {
                addLocationRow();
            } else {
                Swal.fire({
                    icon: 'warning',
                    title: 'Action impossible',
                    text: 'Le type de produit doit être "stockable" pour ajouter un emplacement.',
                });
            }
        });
    } else {
        console.error('addPlLineBtn is null');
    }

    // Form submission validation
    if (productForm) {
        productForm.addEventListener('submit', function(e) {
            const rows = plTableBody.querySelectorAll('.pl-row');
            const data = [];
            let hasError = false;
            const seenLocations = new Set();

            if (isStockableType(productTypeSelect.value)) {
                rows.forEach(row => {
                    if (row.style.display !== 'none') {
                        const locationId = row.querySelector('.location-select').value;
                        const quantity = parseFloat(row.querySelector('.quantity-input').value) || 0;
                        row.querySelector('.location-select').classList.remove('is-invalid');
                        row.querySelector('.quantity-input').classList.remove('is-invalid');

                        if (locationId || quantity > 0) {
                            if (!locationId) {
                                hasError = true;
                                row.querySelector('.location-select').classList.add('is-invalid');
                            }
                            if (quantity <= 0) {
                                hasError = true;
                                row.querySelector('.quantity-input').classList.add('is-invalid');
                            }
                            if (locationId && seenLocations.has(locationId)) {
                                hasError = true;
                                row.querySelector('.location-select').classList.add('is-invalid');
                            }
                            if (locationId && quantity > 0) {
                                seenLocations.add(locationId);
                                data.push({ location_id: locationId, quantity_stored: quantity });
                            }
                        }
                    }
                });
            }

            if (hasError) {
                e.preventDefault();
                Swal.fire({
                    icon: 'error',
                    title: 'Erreur',
                    text: 'Veuillez corriger les erreurs : emplacements dupliqués ou quantités invalides.',
                });
                console.log('Form submission prevented due to errors');
                return false;
            }

            locationsJsonInput.value = JSON.stringify(data);
            console.log('Form submitted with locations_json:', data);
        });
    } else {
        console.error('productForm is null');
    }

    // Handle product deletion
document.querySelectorAll('.btn-delete-product').forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault(); // bloque la navigation / soumission

        const productId = this.getAttribute('data-id');
        const productName = this.getAttribute('data-name');
        Swal.fire({
            title: 'Supprimer ?',
            text: `Supprimer le produit "${productName}" ?`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Oui, supprimer',
            cancelButtonText: 'Annuler',
            confirmButtonColor: '#d33'
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/purchases/products/${productId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                }).then(response => {
                    if (response.ok) {
                        Swal.fire('Supprimé', '', 'success').then(() => location.reload());
                    } else {
                        Swal.fire('Erreur', 'Impossible de supprimer le produit.', 'error');
                    }
                }).catch(() => {
                    Swal.fire('Erreur', 'Impossible de supprimer le produit.', 'error');
                });
            }
        });
    });
});


    // Handle select all checkbox
    const selectAllCheckbox = document.getElementById('select-all-products');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            document.querySelectorAll('.select-product').forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    } else {
        console.error('select-all-products checkbox is null');
    }

    // Handle search input
    const searchInput = document.getElementById('product-search');
    const tableBody = document.querySelector('.table tbody');
    let timer = null;
    if (searchInput && tableBody) {
        searchInput.addEventListener('input', function() {
            clearTimeout(timer);
            timer = setTimeout(() => {
                const q = searchInput.value;
                fetch(`/inventory/products/ajax/?q=${encodeURIComponent(q)}`)
                    .then(response => response.json())
                    .then(data => {
                        tableBody.innerHTML = data.html;
                        document.querySelectorAll('.btn-delete-product').forEach(button => {
                            button.addEventListener('click', function() {
                                const productId = this.getAttribute('data-id');
                                const productName = this.getAttribute('data-name');
                                Swal.fire({
                                    title: 'Supprimer ?',
                                    text: `Supprimer le produit "${productName}" ?`,
                                    icon: 'warning',
                                    showCancelButton: true,
                                    confirmButtonText: 'Oui, supprimer',
                                    cancelButtonText: 'Annuler',
                                    confirmButtonColor: '#d33'
                                }).then((result) => {
                                    if (result.isConfirmed) {
                                        const form = document.createElement('form');
                                        form.method = 'POST';
                                        form.action = `/purchases/products/${productId}/delete/`;
                                        form.innerHTML = `<input type="hidden" name="csrfmiddlewaretoken" value="${document.querySelector('[name=csrfmiddlewaretoken]').value}">`;
                                        document.body.appendChild(form);
                                        form.submit();
                                    }
                                });
                            });
                        });
                    });
            }, 300);
        });
    } else {
        console.error('searchInput or tableBody is null');
    }

    // Initialize locations_json
    updateLocationsJson();
});