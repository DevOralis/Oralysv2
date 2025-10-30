document.addEventListener('DOMContentLoaded', function() {
    let locationsData = window.locationsData || [];
    let productLocations = window.productLocations || [];

    const plTableBody = document.getElementById('pl-table-body');
    const locationsJsonInput = document.getElementById('locations-json');
    const totalQtySpan = document.getElementById('total-qty');
    const addPlLineBtn = document.getElementById('add-pl-line');
    const productForm = document.getElementById('product-form');

    // Fonction pour calculer et mettre à jour la quantité totale
    function updateTotalQuantity() {
        let total = 0;
        if (plTableBody) {
            plTableBody.querySelectorAll('.quantity-input').forEach(input => {
                const row = input.closest('.pl-row');
                if (row && row.style.display !== 'none') {
                    const value = parseFloat(input.value) || 0;
                    if (!isNaN(value)) total += value;
                }
            });
        }
        if (totalQtySpan) totalQtySpan.textContent = total.toFixed(2);
    }

    // Fonction pour mettre à jour le champ locations_json
    function updateLocationsJson() {
        if (!plTableBody) return;
        
        const rows = plTableBody.querySelectorAll('.pl-row');
        const locations = Array.from(rows).map(row => {
            const locationSelect = row.querySelector('.location-select');
            const quantityInput = row.querySelector('.quantity-input');
            if (locationSelect && quantityInput && locationSelect.value) {
                return {
                    location_id: parseInt(locationSelect.value),
                    quantity_stored: parseFloat(quantityInput.value) || 0
                };
            }
            return null;
        }).filter(loc => loc !== null);
        
        productLocations = locations;
        if (locationsJsonInput) {
            locationsJsonInput.value = JSON.stringify(locations);
        }
    }

    // Function to check for duplicate locations
    function hasDuplicateLocations() {
        if (!plTableBody) return false;
        
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
            <td data-label="Poste.stockage">
                <select class="form-select form-select-sm location-select" name="location_id">
                    <option value="">Choisir un poste de stockage</option>
                    ${locationsData.map(loc => {
                        const isSelected = String(loc.id) === String(locationId);
                        return `
                            <option value="${loc.id}" ${isSelected ? 'selected' : ''}>
                                ${loc.name}
                            </option>
                        `;
                    }).join('')}
                </select>
                <div class="invalid-feedback">Ce poste de stockage est déjà sélectionné.</div>
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
                    title: 'Erreur',
                    text: 'Ce poste de stockage est déjà sélectionné dans une autre ligne.',
                    icon: 'error',
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

    // ========================================
    // GESTION DES ÉVÉNEMENTS
    // ========================================

    function attachEventListeners() {
        // Add location row button
        if (addPlLineBtn) {
            addPlLineBtn.addEventListener('click', function(e) {
                e.preventDefault();
                addLocationRow();
            });
        }

        // Form submission with SweetAlert2
        if (productForm) {
            productForm.addEventListener('submit', function(e) {
                e.preventDefault();
                if (hasDuplicateLocations()) {
                    Swal.fire({
                        title: 'Erreur',
                        text: 'Vous avez sélectionné le même poste de stockage plusieurs fois. Veuillez corriger cela.',
                        icon: 'error',
                        confirmButtonText: 'OK'
                    });
                    return false;
                }

                const isEditMode = window.isEditMode;
                const actionText = isEditMode ? 'modifier' : 'créer';
                const productName = document.querySelector('#id_short_label')?.value || 'ce produit';

                Swal.fire({
                    title: `Confirmer ${actionText} le produit`,
                    text: `Voulez-vous vraiment ${actionText} ${productName} ?`,
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonText: `Oui, ${actionText}`,
                    cancelButtonText: 'Annuler',
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#d33'
                }).then((result) => {
                    if (result.isConfirmed) {
                        // Update locations before submission
                        updateLocationsJson();
                        updateTotalQuantity();

                        // Submit form via AJAX
                        fetch(productForm.action, {
                            method: 'POST',
                            body: new FormData(productForm),
                            headers: {
                                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                            }
                        })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! status: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then(data => {
                            if (data.status === 'success') {
                                Swal.fire({
                                    title: `Produit ${isEditMode ? 'modifié' : 'créé'} avec succès`,
                                    text: data.message,
                                    icon: 'success',
                                    confirmButtonText: 'OK'
                                }).then(() => {
                                    window.location.href = '/pharmacy/products/';
                                });
                            } else {
                                let errorMessage = data.message;
                                if (data.errors) {
                                    const errors = JSON.parse(data.errors);
                                    errorMessage += '\n' + Object.values(errors).map(err => err[0].message).join('\n');
                                }
                                Swal.fire({
                                    title: 'Erreur',
                                    text: errorMessage,
                                    icon: 'error',
                                    confirmButtonText: 'OK'
                                });
                            }
                        })
                        .catch(error => {
                            Swal.fire({
                                title: 'Erreur',
                                text: 'Une erreur s\'est produite lors de la communication avec le serveur.',
                                icon: 'error',
                                confirmButtonText: 'OK'
                            });
                            console.error('Error:', error);
                        });
                    }
                });
            });
        }

        // Delete product buttons - using event delegation for dynamic content
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('btn-delete-product') || 
                e.target.closest('.btn-delete-product')) {
                e.preventDefault();
                const button = e.target.classList.contains('btn-delete-product') ? 
                    e.target : e.target.closest('.btn-delete-product');
                handleDeleteProduct(button);
            }
        });
    }

    // ========================================
    // GESTION DE LA SUPPRESSION DES PRODUITS
    // ========================================

    function handleDeleteProduct(button) {
        const productId = button.getAttribute('data-id');
        const productName = button.getAttribute('data-name');
        
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
                // Utiliser AJAX pour la suppression
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                fetch(`/pharmacy/products/delete/${productId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken
                    },
                    body: `csrfmiddlewaretoken=${encodeURIComponent(csrfToken)}`
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    // Fonction pour décoder les caractères Unicode si nécessaire
                    function decodeUnicode(str) {
                        if (typeof str === 'string' && str.includes('\\u')) {
                            return str.replace(/\\u[\dA-F]{4}/gi, function(match) {
                                return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
                            });
                        }
                        return str;
                    }
                    
                    const title = decodeUnicode(data.title || 'Succès');
                    const message = decodeUnicode(data.message || 'Le produit a été supprimé avec succès.');
                    
                    if (data.status === 'success') {
                        Swal.fire({
                            title: title,
                            text: message,
                            icon: 'success',
                            confirmButtonText: 'OK'
                        }).then(() => {
                            // Recharger la page ou mettre à jour la liste
                            window.location.reload();
                        });
                    } else {
                        Swal.fire({
                            title: title,
                            text: message,
                            icon: 'error',
                            confirmButtonText: 'OK'
                        });
                    }
                })
                .catch(error => {
                    console.error('Erreur lors de la suppression:', error);
                    Swal.fire({
                        title: 'Erreur',
                        text: `Une erreur est survenue lors de la suppression: ${error.message}`,
                        icon: 'error',
                        confirmButtonText: 'OK'
                    });
                });
            }
        });
    }

    // ========================================
    // INITIALISATION PRINCIPALE
    // ========================================

    try {
        // Initialiser le tableau avec les données existantes
        if (productLocations && productLocations.length > 0) {
            productLocations.forEach((loc, index) => {
                addLocationRow(loc.location_id, loc.quantity_stored);
            });
        } else {
            // Ajouter une ligne vide par défaut
            addLocationRow();
        }

        // Attacher les événements
        attachEventListeners();
        
        // Initialiser les quantités totales
        updateTotalQuantity();
        updateLocationsJson();
        
    } catch (error) {
        console.error('Erreur lors de l\'initialisation:', error);
    }
});