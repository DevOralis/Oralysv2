/**
 * Pharmacy Configuration JavaScript
 * Handles all configuration functionality for pharmacy module
 */

class PharmacyConfiguration {
    constructor() {
        this.initializeEventListeners();
        this.restoreActiveTab();
        this.checkUrlParams();
    }

    /**
     * Get CSRF token from cookies
     */
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (const element of cookies) {
                const cookie = element.trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Initialize all event listeners
     */
    initializeEventListeners() {
        // Tab change listeners
        this.initializeTabListeners();
        
        // Form handlers
        this.initializeHandlers();
    }

    /**
     * Initialize unified form submission handler
     */
    initializeUnifiedFormHandler() {
        const form = document.getElementById('editForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                
                const entity = document.getElementById('entityInput').value;
                const action = document.getElementById('actionInput').value;
                
                // Submit the form
                this.submitUnifiedForm(form, entity, action);
            });
        }
    }

    /**
     * Submit unified form
     */
    submitUnifiedForm(form, entity, action) {
        // Stop if the browser detects invalid fields
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        const formData = new FormData(form);
        
        fetch('/pharmacy/configuration/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    title: 'Succès !',
                    text: data.message || `${entity} ${action === 'add' ? 'ajouté' : 'modifié'} avec succès.`,
                    icon: 'success',
                    timer: 2000,
                    showConfirmButton: false
                }).then(() => {
                    this.hideFormCard();
                    window.location.reload();
                });
            } else {
                const errorMsg = typeof data.error === 'object'
                    ? Object.values(data.error).flat().join('\n')
                    : (data.error || 'Erreur lors de la soumission');
                throw new Error(errorMsg);
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            Swal.fire({
                title: 'Erreur !',
                text: error.message || 'Erreur lors de la soumission',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        });
    }

    /**
     * Initialize all handlers
     */
    initializeHandlers() {
        this.initializeUnifiedFormHandler();
        this.initializeFormButtonHandlers();
        this.initializePharmaformHandlers();
        this.initializeDciHandlers();
        this.initializePharmacyHandlers();
        this.initializeLocationTypeHandlers();
        this.initializeStoragePostHandlers();
        this.initializeCategoryHandlers();
        this.initializeUnitHandlers();
        this.initializeOperationTypeHandlers();
    }

    /**
     * Initialize form button handlers (cancel, save)
     */
    initializeFormButtonHandlers() {
        // Cancel button handler
        const cancelBtn = document.querySelector('.btn-cancel');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.hideFormCard();
            });
        }

        // Save button handler
        const saveBtn = document.querySelector('.btn-save');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                const form = document.getElementById('editForm');
                if (form) {
                    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                }
            });
        }
    }

    /**
     * Initialize tab functionality
     */
    initializeTabListeners() {
        // Save active tab to localStorage
        document.querySelectorAll('.nav-link[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', () => {
                const target = tab.getAttribute('data-bs-target').substring(1);
                localStorage.setItem('activeTab', target);
            });
        });
    }

    /**
     * Restore active tab from localStorage
     */
    restoreActiveTab() {
        const activeTab = localStorage.getItem('activeTab');
        if (activeTab) {
            const tabButton = document.querySelector(`[data-bs-target="#${activeTab}"]`);
            if (tabButton) {
                const tab = new bootstrap.Tab(tabButton);
                tab.show();
            }
        }
    }

    /**
     * Check URL parameters for success messages
     */
    checkUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const successMessages = {
            'success': 'La forme galénique a été enregistrée avec succès.',
            'dci_success': 'La DCI a été enregistrée avec succès.',
            'pharmacy_success': 'La pharmacie a été enregistrée avec succès.',
            'location_type_success': 'Le type du poste a été enregistré avec succès.',
            'location_success': "L'emplacement a été enregistré avec succès.",
            'operation_type_success': "Le type d'opération a été enregistré avec succès.",
            'category_success': "La catégorie a été enregistrée avec succès.",
            'unit_success': "L'unité de mesure a été enregistrée avec succès."
        };

        // Vérifier si on a déjà affiché un message pour cette session
        const sessionKey = 'pharmacy_config_success_shown';
        const currentUrl = window.location.href;
        const lastShownUrl = sessionStorage.getItem(sessionKey);

        for (const [param, message] of Object.entries(successMessages)) {
            if (urlParams.has(param)) {
                // Ne montrer le message que si on n'a pas déjà montré pour cette URL
                if (lastShownUrl !== currentUrl) {
                    this.showSuccessMessage(message);
                    sessionStorage.setItem(sessionKey, currentUrl);
                }
                // Toujours nettoyer l'URL
                window.history.replaceState({}, document.title, window.location.pathname);
                break;
            }
        }
    }

    /**
     * Show success message using SweetAlert
     */
    showSuccessMessage(message) {
        Swal.fire({
            icon: 'success',
            title: 'Succès',
            text: message,
            timer: 3000,
            showConfirmButton: false
        });
    }

    /**
     * Show form card with dynamic title and icon
     */
    showFormCard(entity, action, title) {
        console.log('showFormCard called with:', { entity, action, title });
        
        const formContainer = document.getElementById('editFormContainer');
        const formTitle = document.getElementById('formTitle');
        const formIcon = document.getElementById('formIcon');
        const entityInput = document.getElementById('entityInput');
        const actionInput = document.getElementById('actionInput');

        console.log('Form elements found:', {
            formContainer: !!formContainer,
            formTitle: !!formTitle,
            formIcon: !!formIcon,
            entityInput: !!entityInput,
            actionInput: !!actionInput
        });

        if (formContainer && formTitle && formIcon) {
            formTitle.textContent = title;
            formIcon.className = action === 'add' ? 'fas fa-plus me-2' : 'fas fa-edit me-2';

            if (entityInput) entityInput.value = entity;
            if (actionInput) actionInput.value = action;

            console.log('Hiding all field groups...');
            this.hideAllFieldGroups();
            console.log('Showing fields for entity:', entity);
            this.showFieldsForEntity(entity);

            formContainer.classList.remove('d-none');
            formContainer.scrollIntoView({ behavior: 'smooth' });
            console.log('Form card displayed successfully');
        } else {
            console.error('Missing form elements!');
        }
    }

    /**
     * Hide all field groups
     */
    hideAllFieldGroups() {
        const fieldGroups = [
            '.pharmaform-field',
            '.dci-field', 
            '.pharmacy-field',
            '.locationtype-field',
            '.storagepost-field',
            '.location-field',
            '.operationtype-field',
            '.category-field',
            '.unit-field'
        ];
        
        fieldGroups.forEach(selector => {
            document.querySelectorAll(selector).forEach(field => {
                field.style.display = 'none';
            });
        });
    }

    /**
     * Show fields for specific entity
     */
    showFieldsForEntity(entity) {
        const selector = `.${entity}-field`;
        console.log('Looking for fields with selector:', selector);
        
        const fields = document.querySelectorAll(selector);
        console.log('Fields found:', fields.length);
        
        fields.forEach((field, index) => {
            console.log(`Field ${index}:`, field);
            field.style.display = 'block';
        });
    }

    /**
     * Hide form card
     */
    hideFormCard() {
        const formContainer = document.getElementById('editFormContainer');
        if (formContainer) {
            formContainer.classList.add('d-none');
            this.clearAllFields();
        }
    }

    /**
     * Clear all form fields
     */
    clearAllFields() {
        const form = document.getElementById('editForm');
        if (form) {
            form.reset();
            document.getElementById('pkInput').value = '';
        }
    }

    /**
     * Populate pharmaform fields
     */
    populatePharmaformFields(id, name, description) {
        document.getElementById('pkInput').value = id;
        document.getElementById('pharmaformNameInput').value = name || '';
        document.getElementById('pharmaformDescriptionInput').value = description || '';
    }

    /**
     * Populate DCI fields
     */
    populateDciFields(id, name, description) {
        document.getElementById('pkInput').value = id;
        document.getElementById('dciNameInput').value = name || '';
        document.getElementById('dciDescriptionInput').value = description || '';
    }

    /**
     * Populate pharmacy fields
     */
    populatePharmacyFields(id, name, address) {
        document.getElementById('pkInput').value = id;
        document.getElementById('pharmacyNameInput').value = name || '';
        document.getElementById('pharmacyAddressInput').value = address || '';
    }

    /**
     * Populate location type fields
     */
    populateLocationTypeFields(id, name, description) {
        document.getElementById('pkInput').value = id;
        document.getElementById('locationTypeNameInput').value = name || '';
        document.getElementById('locationTypeDescriptionInput').value = description || '';
    }

    /**
     * Populate category fields
     */
    populateCategoryFields(id, name, description) {
        document.getElementById('pkInput').value = id;
        document.getElementById('categoryNameInput').value = name || '';
        document.getElementById('categoryDescriptionInput').value = description || '';
    }

    /**
     * Populate unit fields
     */
    populateUnitFields(id, name, symbol) {
        document.getElementById('pkInput').value = id;
        document.getElementById('unitNameInput').value = name || '';
        document.getElementById('unitSymbolInput').value = symbol || '';
    }

    /**
     * Populate location fields
     */
    populateStoragePostFields(id, name, locationType, parentLocation, pharmacy) {
        document.getElementById('pkInput').value = id;
        document.getElementById('locationNameInput').value = name || '';
        document.getElementById('locationTypeInput').value = locationType || '';
        document.getElementById('parentLocationInput').value = parentLocation || '';
        document.getElementById('locationPharmacyInput').value = pharmacy || '';
    }

    /**
     * Populate category fields
     */
    populateCategoryFields(id, name, description) {
        document.getElementById('pkInput').value = id;
        document.getElementById('categoryNameInput').value = name || '';
        document.getElementById('categoryDescriptionInput').value = description || '';
    }

    /**
     * Populate operation type fields
     */
    populateOperationTypeFields(id, name, description) {
        document.getElementById('pkInput').value = id;
        document.getElementById('operationTypeNameInput').value = name || '';
        document.getElementById('operationTypeDescriptionInput').value = description || '';
    }

    /**
     * Show confirmation dialog
     */
    showConfirmationDialog(title, text, onConfirm) {
        Swal.fire({
            title: title,
            text: text,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Oui, supprimer',
            cancelButtonText: 'Annuler'
        }).then(result => {
            if (result.isConfirmed) {
                onConfirm();
            }
        });
    }

    /**
     * Show loading state
     */
    showLoading(message = 'Chargement...') {
        Swal.fire({
            title: message,
            allowOutsideClick: false,
            didOpen: () => { Swal.showLoading(); }
        });
    }

    /**
     * Generic delete function
     */
    async deleteItem(url, successMessage) {
        try {
            this.showLoading('Suppression en cours...');
            
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'X-CSRFToken': this.getCookie('csrftoken'), 'X-Requested-With': 'XMLHttpRequest' }
            });
            
            const data = await response.json();
            
            if (data.success) {
                Swal.fire({
                    title: 'Supprimé !',
                    text: successMessage,
                    icon: 'success',
                    timer: 3000,
                    showConfirmButton: false
                });
                return true;
            } else {
                Swal.fire('Erreur', data.error || 'Impossible de supprimer cet élément.', 'error');
                return false;
            }
        } catch (error) {
            Swal.fire('Erreur', 'Une erreur est survenue lors de la suppression.', 'error');
            return false;
        }
    }

    /**
     * Generic form submission
     */
    async submitForm(form, successParam) {
        try {
            const formData = new FormData(form);
            const isEditing = formData.get('form_id') || formData.get('dci_id') || 
                             formData.get('pharmacy_id') || formData.get('location_type_id') ||
                             formData.get('location_id') || formData.get('operation_type_id') ||
                             formData.get('category_id') || formData.get('unit_id');

            this.showLoading(isEditing ? 'Modification en cours...' : 'Enregistrement en cours...');

            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-CSRFToken': this.getCookie('csrftoken'), 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (response.ok) {
                window.location.href = window.location.pathname + `?${successParam}=1`;
            } else {
                throw new Error('Erreur lors de l\'enregistrement');
            }
        } catch (error) {
            Swal.fire('Erreur', 'Une erreur est survenue lors de l\'enregistrement.', 'error');
        }
    }

    /**
     * Initialize pharmaceutical form handlers
     */
    initializePharmaformHandlers() {
        // New structure with unified form card
        const addBtns = document.querySelectorAll('.add-btn[data-entity="pharmaform"]');
        const editBtns = document.querySelectorAll('.edit-btn[data-entity="pharmaform"]');
        const formContainer = document.getElementById('editFormContainer');
        const formTitle = document.getElementById('formTitle');
        const formIcon = document.getElementById('formIcon');
        const cancelBtn = document.querySelector('.btn-cancel');
        const searchInput = document.getElementById('searchPharmaform');

        // Add button handlers
        addBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.showFormCard('pharmaform', 'add', 'Ajouter Forme Galénique');
            });
        });

        // Edit button handlers
        editBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const name = btn.dataset.name;
                const description = btn.dataset.description;
                
                this.showFormCard('pharmaform', 'edit', 'Modifier Forme Galénique');
                this.populatePharmaformFields(id, name, description);
            });
        });

        // Cancel button handler
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.hideFormCard();
            });
        }

        // Edit buttons
        document.querySelectorAll('.btn-edit-pharmaform').forEach(btn => {
            btn.addEventListener('click', () => {
                form.classList.remove('d-none');
                addBtn.classList.add('d-none');
                idInput.value = btn.dataset.id;
                nameInput.value = btn.dataset.name;
                descInput.value = btn.dataset.description;
            });
        });

        // Delete buttons
        document.querySelectorAll('.btn-delete-pharmaform').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const row = btn.closest('tr');
                const formName = row.querySelector('.pharmaform-name').textContent.trim();

                this.showConfirmationDialog(
                    'Confirmer la suppression',
                    `Voulez-vous vraiment supprimer la forme galénique "${formName}" ?`,
                    async () => {
                        const success = await this.deleteItem(
                            `/pharmacy/pharmaform/delete/${id}/`,
                            'La forme galénique a été supprimée avec succès.'
                        );
                        if (success) {
                            row.remove();
                        }
                    }
                );
            });
        });

        // Search functionality
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                const filter = searchInput.value.toLowerCase();
                const tableBody = document.querySelector('#pharmaform-table tbody');
                if (tableBody) {
                    tableBody.querySelectorAll('tr').forEach(row => {
                        const name = row.querySelector('.pharmaform-name')?.textContent.toLowerCase() || '';
                        const desc = row.querySelector('.pharmaform-desc')?.textContent.toLowerCase() || '';
                        row.style.display = (name.includes(filter) || desc.includes(filter)) ? '' : 'none';
                    });
                }
            });
        }


    }

    /**
     * Initialize DCI handlers
     */
    initializeDciHandlers() {
        console.log('Initializing DCI handlers...');
        
        // New structure with unified form card
        const addBtns = document.querySelectorAll('.add-btn[data-entity="dci"]');
        const editBtns = document.querySelectorAll('.edit-btn[data-entity="dci"]');
        const searchInput = document.getElementById('searchDci');

        console.log('DCI Add buttons found:', addBtns.length);
        console.log('DCI Edit buttons found:', editBtns.length);

        // Add button handlers
        addBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                console.log('DCI Add button clicked');
                this.showFormCard('dci', 'add', 'Ajouter DCI');
            });
        });

        // Edit button handlers
        editBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                console.log('DCI Edit button clicked');
                const id = btn.dataset.id;
                const name = btn.dataset.name;
                const description = btn.dataset.description;
                
                console.log('DCI data:', { id, name, description });
                this.showFormCard('dci', 'edit', 'Modifier DCI');
                this.populateDciFields(id, name, description);
            });
        });

        // Delete buttons
        document.querySelectorAll('.btn-delete-dci').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const row = btn.closest('tr');
                const dciName = row.querySelector('.dci-label').textContent.trim();

                this.showConfirmationDialog(
                    'Confirmer la suppression',
                    `Voulez-vous vraiment supprimer la DCI "${dciName}" ?`,
                    async () => {
                        const success = await this.deleteItem(
                            `/pharmacy/dci/delete/${id}/`,
                            'La DCI a été supprimée avec succès.'
                        );
                        if (success) {
                            row.remove();
                        }
                    }
                );
            });
        });

        // Search functionality
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                const filter = searchInput.value.toLowerCase();
                const tableBody = document.querySelector('#dci-table tbody');
                if (tableBody) {
                    tableBody.querySelectorAll('tr').forEach(row => {
                        const label = row.querySelector('.dci-label')?.textContent.toLowerCase() || '';
                        const desc = row.querySelector('.dci-desc')?.textContent.toLowerCase() || '';
                        row.style.display = (label.includes(filter) || desc.includes(filter)) ? '' : 'none';
                    });
                }
            });
        }

    }

    /**
     * Initialize pharmacy handlers
     */
    initializePharmacyHandlers() {
        // New structure with unified form card
        const addBtns = document.querySelectorAll('.add-btn[data-entity="pharmacy"]');
        const editBtns = document.querySelectorAll('.edit-btn[data-entity="pharmacy"]');
        const searchInput = document.getElementById('searchPharmacy');

        // Add button handlers
        addBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.showFormCard('pharmacy', 'add', 'Ajouter Pharmacie');
            });
        });

        // Edit button handlers
        editBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const name = btn.dataset.name;
                const address = btn.dataset.address;
                
                this.showFormCard('pharmacy', 'edit', 'Modifier Pharmacie');
                this.populatePharmacyFields(id, name, address);
            });
        });

        // Delete buttons
        document.querySelectorAll('.btn-delete-pharmacy').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const row = btn.closest('tr');
                const pharmacyName = row.querySelector('.pharmacy-label').textContent.trim();

                this.showConfirmationDialog(
                    'Confirmer la suppression',
                    `Voulez-vous vraiment supprimer la pharmacie "${pharmacyName}" ?`,
                    async () => {
                        const success = await this.deleteItem(
                            `/pharmacy/pharmacy/delete/${id}/`,
                            'La pharmacie a été supprimée avec succès.'
                        );
                        if (success) {
                            row.remove();
                        }
                    }
                );
            });
        });

        // Search functionality
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                const filter = searchInput.value.toLowerCase();
                const tableBody = document.querySelector('#pharmacy-table tbody');
                if (tableBody) {
                    tableBody.querySelectorAll('tr').forEach(row => {
                        const label = row.querySelector('.pharmacy-label')?.textContent.toLowerCase() || '';
                        const adress = row.querySelector('.pharmacy-adress')?.textContent.toLowerCase() || '';
                        row.style.display = (label.includes(filter) || adress.includes(filter)) ? '' : 'none';
                    });
                }
            });
        }


    }

    /**
     * Initialize location type handlers
     */
    initializeLocationTypeHandlers() {
        // New structure with unified form card
        const addBtns = document.querySelectorAll('.add-btn[data-entity="locationtype"]');
        const editBtns = document.querySelectorAll('.edit-btn[data-entity="locationtype"]');
        const searchInput = document.getElementById('searchLocationType');

        // Add button handlers
        addBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.showFormCard('locationtype', 'add', 'Ajouter Type de Stockage');
            });
        });

        // Edit button handlers
        editBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const name = btn.dataset.name;
                const description = btn.dataset.description;
                
                this.showFormCard('locationtype', 'edit', 'Modifier Type de Stockage');
                this.populateLocationTypeFields(id, name, description);
            });
        });

        // Delete buttons
        document.querySelectorAll('.btn-delete-location-type').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const row = btn.closest('tr');
                const typeName = row.querySelector('.location-type-name').textContent.trim();

                this.showConfirmationDialog(
                    'Confirmer la suppression',
                    `Voulez-vous vraiment supprimer le type du poste "${typeName}" ?`,
                    async () => {
                        const success = await this.deleteItem(
                            `/pharmacy/location-type/delete/${id}/`,
                            'Le type du poste a été supprimé avec succès.'
                        );
                        if (success) {
                            row.remove();
                        }
                    }
                );
            });
        });

        // Search functionality
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                const filter = searchInput.value.toLowerCase();
                const tableBody = document.querySelector('#location-type-table tbody');
                if (tableBody) {
                    tableBody.querySelectorAll('tr').forEach(row => {
                        const name = row.querySelector('.location-type-name')?.textContent.toLowerCase() || '';
                        const desc = row.querySelector('.location-type-desc')?.textContent.toLowerCase() || '';
                        row.style.display = (name.includes(filter) || desc.includes(filter)) ? '' : 'none';
                    });
                }
            });
        }


    }

    /**
     * Initialize location handlers
     */
    initializeLocationHandlers() {
        const addBtn = document.getElementById('add-location-btn');
        const form = document.getElementById('location-form');
        const formCard = document.getElementById('location-form-card');
        const cancelBtn = document.getElementById('cancel-location');
        const idInput = document.getElementById('location_id');
        const nameInput = document.getElementById('location_name');
        const typeSelect = document.getElementById('location_type_select');
        const parentSelect = document.getElementById('parent-location-select');
        const pharmacySelect = document.getElementById('pharmacy-select');
        const isParentToggle = document.getElementById('is-parent-toggle');
        const parentGroup = document.getElementById('parent-location-group');
        const searchInput = document.getElementById('search-location');
        const tableBody = document.querySelector('#location-table tbody');

        if (addBtn) {
            addBtn.addEventListener('click', () => {
                formCard.classList.remove('d-none');
                addBtn.classList.add('d-none');
                idInput.value = '';
                nameInput.value = '';
                typeSelect.value = '';
                parentSelect.value = '';
                pharmacySelect.value = '';
                isParentToggle.checked = false;
                parentGroup.style.display = '';
            });
        }

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                formCard.classList.add('d-none');
                addBtn.classList.remove('d-none');
                idInput.value = '';
                nameInput.value = '';
                typeSelect.value = '';
                parentSelect.value = '';
                pharmacySelect.value = '';
                isParentToggle.checked = false;
                parentGroup.style.display = '';
            });
        }

        // Parent toggle functionality
        if (isParentToggle && parentGroup) {
            const updateParentField = () => {
                parentGroup.style.display = isParentToggle.checked ? 'none' : '';
                if (isParentToggle.checked) {
                    parentSelect.value = '';
                }
            };
            isParentToggle.addEventListener('change', updateParentField);
            updateParentField();
        }

        // Edit buttons
        document.querySelectorAll('.btn-edit-location').forEach(btn => {
            btn.addEventListener('click', () => {
                formCard.classList.remove('d-none');
                addBtn.classList.add('d-none');
                idInput.value = btn.dataset.id;
                nameInput.value = btn.dataset.name;
                typeSelect.value = btn.dataset.locationType;
                parentSelect.value = btn.dataset.parentLocation;
                pharmacySelect.value = btn.dataset.pharmacy;
                isParentToggle.checked = btn.dataset.isParent === 'true';
                parentGroup.style.display = isParentToggle.checked ? 'none' : '';
            });
        });

        // Delete buttons
        document.querySelectorAll('.btn-delete-location').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const row = btn.closest('tr');
                const locationName = row.querySelector('.location-name').textContent.trim();

                this.showConfirmationDialog(
                    'Confirmer la suppression',
                    `Voulez-vous vraiment supprimer l'emplacement "${locationName}" ?`,
                    async () => {
                        const success = await this.deleteItem(
                            `/pharmacy/location/delete/${id}/`,
                            "L'emplacement a été supprimé avec succès."
                        );
                        if (success) {
                            row.remove();
                        }
                    }
                );
            });
        });

        // Search functionality
        if (searchInput && tableBody) {
            searchInput.addEventListener('input', () => {
                const filter = searchInput.value.toLowerCase();
                tableBody.querySelectorAll('tr').forEach(row => {
                    const name = row.querySelector('.location-name').textContent.toLowerCase();
                    const type = row.querySelector('.location-type').textContent.toLowerCase();
                    const parent = row.querySelector('.location-parent').textContent.toLowerCase();
                    const pharmacy = row.querySelector('.location-pharmacy').textContent.toLowerCase();
                    row.style.display = (name.includes(filter) || type.includes(filter) || parent.includes(filter) || pharmacy.includes(filter)) ? '' : 'none';
                });
            });
        }

        // Form submission
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitForm(form, 'location_success');
            });
        }
    }

    /**
     * Initialize operation type handlers
     */
    initializeOperationTypeHandlers() {
        // New structure with unified form card
        const addBtns = document.querySelectorAll('.add-btn[data-entity="operationtype"]');
        const editBtns = document.querySelectorAll('.edit-btn[data-entity="operationtype"]');
        const searchInput = document.getElementById('searchOperationType');

        // Add button handlers
        addBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.showFormCard('operationtype', 'add', 'Ajouter Type d\'Opération');
            });
        });

        // Edit button handlers
        editBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const name = btn.dataset.name;
                
                this.showFormCard('operationtype', 'edit', 'Modifier Type d\'Opération');
                this.populateOperationTypeFields(id, name);
            });
        });

        // Search functionality
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                const filter = searchInput.value.toLowerCase();
                const tableBody = document.querySelector('#operation-type-table tbody');
                if (tableBody) {
                    tableBody.querySelectorAll('tr').forEach(row => {
                        const label = row.querySelector('.operation-type-label')?.textContent.toLowerCase() || '';
                        row.style.display = (label.includes(filter)) ? '' : 'none';
                    });
                }
            });
        }
    }

    /**
     * Initialize storage post handlers
     */
    initializeStoragePostHandlers() {
        // New structure with unified form card
        const addBtns = document.querySelectorAll('.add-btn[data-entity="storagepost"]');
        const editBtns = document.querySelectorAll('.edit-btn[data-entity="storagepost"]');
        const searchInput = document.getElementById('searchStoragePost');

        // Add button handlers
        addBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.showFormCard('storagepost', 'add', 'Ajouter Poste de Stockage');
            });
        });

        // Edit button handlers
        editBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const name = btn.dataset.name;
                const description = btn.dataset.description;
                
                this.showFormCard('storagepost', 'edit', 'Modifier Poste de Stockage');
                this.populateStoragePostFields(id, name, description);
            });
        });

        // Search functionality
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                const filter = searchInput.value.toLowerCase();
                const tableBody = document.querySelector('#storage-post-table tbody');
                if (tableBody) {
                    tableBody.querySelectorAll('tr').forEach(row => {
                        const name = row.querySelector('.storage-post-name')?.textContent.toLowerCase() || '';
                        const description = row.querySelector('.storage-post-description')?.textContent.toLowerCase() || '';
                        row.style.display = (name.includes(filter) || description.includes(filter)) ? '' : 'none';
                    });
                }
            });
        }
    }

    /**
     * Initialize unit handlers
     */
    initializeUnitHandlers() {
        // New structure with unified form card
        const addBtns = document.querySelectorAll('.add-btn[data-entity="unit"]');
        const editBtns = document.querySelectorAll('.edit-btn[data-entity="unit"]');
        const searchInput = document.getElementById('searchUnit');

        // Add button handlers
        addBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.showFormCard('unit', 'add', 'Ajouter Unité de Mesure');
            });
        });

        // Edit button handlers
        editBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const name = btn.dataset.name;
                const symbol = btn.dataset.symbol;
                
                this.showFormCard('unit', 'edit', 'Modifier Unité de Mesure');
                this.populateUnitFields(id, name, symbol);
            });
        });

        // Search functionality
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                const filter = searchInput.value.toLowerCase();
                const tableBody = document.querySelector('#unit-table tbody');
                if (tableBody) {
                    tableBody.querySelectorAll('tr').forEach(row => {
                        const label = row.querySelector('.unit-label')?.textContent.toLowerCase() || '';
                        const symbol = row.querySelector('.unit-symbole')?.textContent.toLowerCase() || '';
                        row.style.display = (label.includes(filter) || symbol.includes(filter)) ? '' : 'none';
                    });
                }
            });
        }
    }

    /**
     * Initialize category handlers
     */
    initializeCategoryHandlers() {
        console.log('Initializing Category handlers...');
        
        const addBtns = document.querySelectorAll('.add-btn[data-entity="category"]');
        const editBtns = document.querySelectorAll('.edit-btn[data-entity="category"]');
        const searchInput = document.getElementById('searchCategory');

        console.log('Category Add buttons found:', addBtns.length);
        console.log('Category Edit buttons found:', editBtns.length);

        // Add button handlers
        addBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                console.log('Category Add button clicked');
                this.showFormCard('category', 'add', 'Ajouter Catégorie');
            });
        });

        // Edit button handlers
        editBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                console.log('Category Edit button clicked');
                const id = btn.dataset.id;
                const name = btn.dataset.name;
                const description = btn.dataset.description;
                
                console.log('Category data:', { id, name, description });
                this.showFormCard('category', 'edit', 'Modifier Catégorie');
                this.populateCategoryFields(id, name, description);
            });
        });

        // Search functionality
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                const filter = searchInput.value.toLowerCase();
                const tableBody = document.querySelector('#category-table tbody');
                if (tableBody) {
                    tableBody.querySelectorAll('tr').forEach(row => {
                        const name = row.querySelector('.category-label')?.textContent.toLowerCase() || '';
                        const desc = row.querySelector('.category-desc')?.textContent.toLowerCase() || '';
                        row.style.display = (name.includes(filter) || desc.includes(filter)) ? '' : 'none';
                    });
                }
            });
        }
    }

    /**
     * Initialize storage post handlers
     */
    initializeStoragePostHandlers() {
        console.log('Initializing Storage Post handlers...');
        
        const addBtns = document.querySelectorAll('.add-btn[data-entity="location"]');
        const editBtns = document.querySelectorAll('.edit-btn[data-entity="location"]');
        const searchInput = document.getElementById('searchLocation');

        console.log('Storage Post Add buttons found:', addBtns.length);
        console.log('Storage Post Edit buttons found:', editBtns.length);

        // Add button handlers
        addBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                console.log('Storage Post Add button clicked');
                this.showFormCard('location', 'add', 'Ajouter Poste de Stockage');
            });
        });

        // Edit button handlers
        editBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                console.log('Storage Post Edit button clicked');
                const id = btn.dataset.id;
                const name = btn.dataset.name;
                const locationType = btn.dataset.locationType;
                const parentLocation = btn.dataset.parentLocation;
                const pharmacy = btn.dataset.pharmacy;
                
                console.log('Storage Post data:', { id, name, locationType, parentLocation, pharmacy });
                this.showFormCard('location', 'edit', 'Modifier Poste de Stockage');
                this.populateStoragePostFields(id, name, locationType, parentLocation, pharmacy);
            });
        });

        // Search functionality
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                const filter = searchInput.value.toLowerCase();
                const tableBody = document.querySelector('#location tbody');
                if (tableBody) {
                    tableBody.querySelectorAll('tr').forEach(row => {
                        const name = row.querySelector('td[data-label="Nom"]')?.textContent.toLowerCase() || '';
                        const type = row.querySelector('td[data-label="Type"]')?.textContent.toLowerCase() || '';
                        const parent = row.querySelector('td[data-label="Parent"]')?.textContent.toLowerCase() || '';
                        const pharmacy = row.querySelector('td[data-label="Pharmacie"]')?.textContent.toLowerCase() || '';
                        row.style.display = (name.includes(filter) || type.includes(filter) || parent.includes(filter) || pharmacy.includes(filter)) ? '' : 'none';
                    });
                }
            });
        }
    }

    /**
     * Initialize operation type handlers
     */
    initializeOperationTypeHandlers() {
        console.log('Initializing Operation Type handlers...');
        
        const addBtns = document.querySelectorAll('.add-btn[data-entity="operationtype"]');
        const editBtns = document.querySelectorAll('.edit-btn[data-entity="operationtype"]');
        const searchInput = document.getElementById('searchOperationType');

        console.log('Operation Type Add buttons found:', addBtns.length);
        console.log('Operation Type Edit buttons found:', editBtns.length);

        // Add button handlers
        addBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                console.log('Operation Type Add button clicked');
                this.showFormCard('operationtype', 'add', 'Ajouter Type d\'Opération');
            });
        });

        // Edit button handlers
        editBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                console.log('Operation Type Edit button clicked');
                const id = btn.dataset.id;
                const name = btn.dataset.name;
                const description = btn.dataset.description;
                
                console.log('Operation Type data:', { id, name, description });
                this.showFormCard('operationtype', 'edit', 'Modifier Type d\'Opération');
                this.populateOperationTypeFields(id, name, description);
            });
        });

        // Search functionality
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                const filter = searchInput.value.toLowerCase();
                const tableBody = document.querySelector('#operation-table tbody');
                if (tableBody) {
                    tableBody.querySelectorAll('tr').forEach(row => {
                        const name = row.querySelector('.operation-label')?.textContent.toLowerCase() || '';
                        const desc = row.querySelector('.operation-desc')?.textContent.toLowerCase() || '';
                        row.style.display = (name.includes(filter) || desc.includes(filter)) ? '' : 'none';
                    });
                }
            });
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PharmacyConfiguration();
}); 