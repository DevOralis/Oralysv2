// Script pour la page de configuration HR

document.addEventListener('DOMContentLoaded', function() {
    // Masquer le formulaire d'édition au chargement de la page
    document.getElementById('editFormContainer').style.display = 'none';
    
    // Gestion des onglets
    const tabButtons = document.querySelectorAll('.nav-link');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    // Restaurer l'onglet actif depuis localStorage
    const activeTab = localStorage.getItem('hrConfigActiveTab') || 'position';
    
    // Activer l'onglet sauvegardé
    const activeTabButton = document.querySelector(`[data-bs-target="#${activeTab}"]`);
    const activeTabPane = document.getElementById(activeTab);
    
    if (activeTabButton && activeTabPane) {
        // Supprimer la classe 'active' de tous les onglets
        tabButtons.forEach(button => button.classList.remove('active'));
        tabPanes.forEach(pane => pane.classList.remove('active', 'show'));
        
        // Ajouter la classe 'active' aux bons onglets
        activeTabButton.classList.add('active');
        activeTabPane.classList.add('active', 'show');
        
        // Gérer l'affichage des champs de formulaire
        hideAllFormFields();
        showRelevantFormFields(activeTab);
    }
    
    // Sauvegarder l'onglet actif lors du clic
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-bs-target').substring(1);
            localStorage.setItem('hrConfigActiveTab', tabId);
            
            // Gérer l'affichage des champs de formulaire
            hideAllFormFields();
            showRelevantFormFields(tabId);
        });
    });
    
    // Fonction pour masquer tous les champs de formulaire
    function hideAllFormFields() {
        const formFields = document.querySelectorAll('.common-label-field, .department-field, .leave_type-field, .social_contribution-field, .prime-field, .model_calcul-field, .acte-field, .holiday-field');
        formFields.forEach(field => {
            field.style.display = 'none';
            // Supprimer l'attribut required des champs cachés
            const inputs = field.querySelectorAll('input[required], select[required]');
            inputs.forEach(input => {
                input.removeAttribute('required');
                input.setAttribute('data-was-required', 'true');
            });
        });
    }
    
    // Fonction pour afficher les champs pertinents
    function showRelevantFormFields(tabId) {
        // Ne pas masquer les contenus d'onglets lors de l'ouverture du formulaire
        // Le contenu de l'onglet doit rester visible avec le tableau
        
        // S'assurer que l'onglet correct est actif seulement si ce n'est pas déjà le cas
        const activeContent = document.getElementById(tabId);
        if (activeContent && !activeContent.classList.contains('active')) {
            // Masquer tous les contenus d'onglets
            const tabContents = document.querySelectorAll('.tab-pane');
            tabContents.forEach(content => {
                content.classList.remove('active', 'show');
            });
            // Afficher le contenu de l'onglet sélectionné
            activeContent.classList.add('active', 'show');
        }
        
        // Mettre à jour le texte du bouton d'ajout en fonction de l'onglet actif
        updateAddButtonText(tabId);
        
        // Afficher les champs de formulaire pertinents
        switch(tabId) {
            case 'position':
            case 'contract_type':
            case 'speciality':
                document.querySelectorAll('.common-label-field').forEach(field => {
                    field.style.display = 'block';
                    // Restaurer l'attribut required pour les champs visibles
                    const inputs = field.querySelectorAll('input[data-was-required], select[data-was-required]');
                    inputs.forEach(input => {
                        input.setAttribute('required', 'required');
                        input.removeAttribute('data-was-required');
                    });
                });
                break;
            case 'department':
                document.querySelectorAll('.common-label-field, .department-field').forEach(field => {
                    field.style.display = 'block';
                    // Restaurer l'attribut required pour les champs visibles
                    const inputs = field.querySelectorAll('input[data-was-required], select[data-was-required]');
                    inputs.forEach(input => {
                        input.setAttribute('required', 'required');
                        input.removeAttribute('data-was-required');
                    });
                });
                break;
            case 'leave_type':
                document.querySelectorAll('.common-label-field, .leave_type-field').forEach(field => {
                    field.style.display = 'block';
                    // Restaurer l'attribut required pour les champs visibles
                    const inputs = field.querySelectorAll('input[data-was-required], select[data-was-required]');
                    inputs.forEach(input => {
                        input.setAttribute('required', 'required');
                        input.removeAttribute('data-was-required');
                    });
                });
                break;
            case 'social_contributions':  // Mettre à jour pour utiliser le bon ID
                document.querySelectorAll('.social_contribution-field').forEach(field => {
                    field.style.display = 'block';
                    // Restaurer l'attribut required pour les champs visibles
                    const inputs = field.querySelectorAll('input[data-was-required], select[data-was-required]');
                    inputs.forEach(input => {
                        input.setAttribute('required', 'required');
                        input.removeAttribute('data-was-required');
                    });
                });
                break;
            case 'prime':
                document.querySelectorAll('.prime-field').forEach(field => {
                    field.style.display = 'block';
                    // Restaurer l'attribut required pour les champs visibles
                    const inputs = field.querySelectorAll('input[data-was-required], select[data-was-required]');
                    inputs.forEach(input => {
                        input.setAttribute('required', 'required');
                        input.removeAttribute('data-was-required');
                    });
                });
                break;
            case 'model-calcul':  // Mettre à jour pour utiliser le bon ID
                document.querySelectorAll('.model_calcul-field').forEach(field => {
                    field.style.display = 'block';
                    // Restaurer l'attribut required pour les champs visibles
                    const inputs = field.querySelectorAll('input[data-was-required], select[data-was-required]');
                    inputs.forEach(input => {
                        input.setAttribute('required', 'required');
                        input.removeAttribute('data-was-required');
                    });
                });
                break;
            case 'service':
            case 'acte':
                document.querySelectorAll('.acte-field').forEach(field => {
                    field.style.display = 'block';
                    // Restaurer l'attribut required pour les champs visibles
                    const inputs = field.querySelectorAll('input[data-was-required], select[data-was-required]');
                    inputs.forEach(input => {
                        input.setAttribute('required', 'required');
                        input.removeAttribute('data-was-required');
                    });
                });
                break;
            case 'holiday':
                document.querySelectorAll('.holiday-field').forEach(field => {
                    field.style.display = 'block';
                    const inputs = field.querySelectorAll('input[data-was-required], select[data-was-required]');
                    inputs.forEach(input => {
                        input.setAttribute('required', 'required');
                        input.removeAttribute('data-was-required');
                    });
                });
                break;
        }
    }
    
    // Fonction pour mettre à jour le texte du bouton d'ajout
    function updateAddButtonText(tabId) {
        // Trouver le bouton d'ajout dans l'onglet actif
        const activeTabPane = document.getElementById(tabId);
        if (!activeTabPane) return;
        
        const addButton = activeTabPane.querySelector('.add-btn');
        if (!addButton) return;
        
        const buttonTexts = {
            'position': 'Ajouter poste',
            'department': 'Ajouter département',
            'contract_type': 'Ajouter type de contrat',
            'leave_type': 'Ajouter type de congé',
            'prime': 'Ajouter prime',
            'social_contributions': 'Ajouter cotisation sociale',
            'model-calcul': 'Ajouter model de calcul',
            'speciality': 'Ajouter spécialité',
            'service': 'Ajouter Acte',
            'acte': 'Ajouter Acte',
            'holiday': 'Ajouter jour férié'
        };
        
        const buttonText = buttonTexts[tabId] || 'Ajouter';
        const icon = '<i class="fas fa-plus"></i> ';
        
        // Mettre à jour le contenu du span au lieu de tout le bouton
        const buttonSpan = addButton.querySelector('span');
        if (buttonSpan) {
            buttonSpan.textContent = buttonText;
        } else {
            addButton.innerHTML = icon + buttonText;
        }
    }
    
    // Gestion des événements pour les boutons d'ajout, d'édition et de suppression
    document.addEventListener('click', function(e) {
        // Bouton d'ajout
        if (e.target.closest('.add-btn')) {
            const button = e.target.closest('.add-btn');
            const entity = button.getAttribute('data-entity');
            
            // Appeler la fonction d'ajout avec l'entité appropriée
            if (typeof openAddModal === 'function') {
                openAddModal(entity);
            }
        }
        
        // Bouton d'édition
        if (e.target.closest('.edit-btn')) {
            const button = e.target.closest('.edit-btn');
            const entity = button.getAttribute('data-entity');
            const id = button.getAttribute('data-id');
            const name = button.getAttribute('data-name');
            
            // Récupérer les attributs supplémentaires si présents
            const rate = button.getAttribute('data-rate');
            const amount = button.getAttribute('data-amount');
            const ceiling = button.getAttribute('data-ceiling');
            const socialContributions = button.getAttribute('data-social-contributions');
            const primes = button.getAttribute('data-primes');
            const prix = button.getAttribute('data-prix');
            const price = button.getAttribute('data-price');
            
            // Appeler la fonction d'édition avec les paramètres appropriés
            if (typeof openEditModal === 'function') {
                openEditModal(entity, id, name, rate, amount, ceiling, socialContributions, primes, prix, price);
            }
        }
        
        // Bouton d'annulation
        if (e.target.closest('.cancel-btn')) {
            // Appeler la fonction pour masquer le formulaire
            if (typeof hideEditForm === 'function') {
                hideEditForm();
            }
        }
        
        // Bouton de suppression
        if (e.target.closest('.delete-btn')) {
            const button = e.target.closest('.delete-btn');
            const entity = button.getAttribute('data-entity');
            const id = button.getAttribute('data-id');
            const name = button.getAttribute('data-name');
            
            // Appeler la fonction de suppression avec les paramètres appropriés
            if (typeof deleteItem === 'function') {
                deleteItem(entity, id, name);
            }
        }
    });
    
    // Gestion du formulaire d'ajout/modification
    const editForm = document.getElementById('editForm');
    if (editForm) {
        // Récupérer l'URL d'action AVANT le clonage pour éviter les conflits DOM
        // Utiliser getAttributeNode pour éviter les conflits avec les champs nommés 'action'
        const actionAttr = editForm.getAttributeNode('action');
        const originalFormActionUrl = actionAttr ? actionAttr.value : window.location.pathname;
        
        // Supprimer tous les anciens event listeners pour éviter les doublons
        const newEditForm = editForm.cloneNode(true);
        editForm.parentNode.replaceChild(newEditForm, editForm);
        
        newEditForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Form submission started');
            
            // Désactiver le bouton de soumission pour éviter les soumissions multiples
            const submitBtn = newEditForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enregistrement...';
            }
            
            // Récupérer les données du formulaire
            const formData = new FormData(newEditForm);
            
            // Utiliser l'URL d'action récupérée avant le clonage
            console.log('Form action URL:', originalFormActionUrl);
            
            fetch(originalFormActionUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                
                // Réactiver le bouton
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fas fa-save"></i> Enregistrer';
                }
                
                if (data.status === 'success') {
                    console.log('Success response received');
                    // Afficher un message de succès
                    Swal.fire({
                        icon: 'success',
                        title: 'Succès',
                        text: data.message,
                        timer: 2000,
                        showConfirmButton: false
                    }).then(() => {
                        // Recharger la page pour afficher les changements
                        location.reload();
                    });
                } else {
                    console.log('Error response received:', data.message);
                    // Afficher un message d'erreur
                    Swal.fire({
                        icon: 'error',
                        title: 'Erreur',
                        text: data.message || 'Une erreur est survenue.',
                        confirmButtonText: 'OK'
                    });
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                
                // Réactiver le bouton
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fas fa-save"></i> Enregistrer';
                }
                
                // Afficher un message d'erreur
                Swal.fire({
                    icon: 'error',
                    title: 'Erreur de connexion',
                    text: 'Une erreur est survenue lors de l\'enregistrement des données. Veuillez réessayer.',
                    confirmButtonText: 'OK'
                });
            });
        });
    }
    
    // Gestionnaire pour le bouton Annuler
    document.addEventListener('click', function(e) {
        // Vérifier si le clic est sur un bouton Annuler ou à l'extérieur du formulaire
        if (e.target.classList.contains('cancel-btn') || 
            e.target.closest && e.target.closest('.cancel-btn')) {
            e.preventDefault();
            // Masquer le formulaire avec une animation
            const formContainer = document.getElementById('editFormContainer');
            if (formContainer) {
                formContainer.style.display = 'none';
                // Réinitialiser le formulaire
                const editForm = document.getElementById('editForm');
                if (editForm) {
                    editForm.reset();
                    // Réactiver le bouton de soumission s'il était désactivé
                    const submitBtn = editForm.querySelector('button[type="submit"]');
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = '<i class="fas fa-save"></i> Enregistrer';
                    }
                }
            }
        }
    });
    
    // CSRF token helper
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };
    
    // Fonction pour ouvrir le modal d'ajout
    window.openAddModal = function(entity) {
        // Mettre à jour le titre du formulaire
        const entityNames = {
            'position': 'poste',
            'department': 'département',
            'contract_type': 'type de contrat',
            'leave_type': 'type de congé',
            'prime': 'prime',
            'social_contribution': 'cotisation sociale',
            'model_calcul': 'modèle de calcul',
            'speciality': 'spécialité',
            'acte': 'acte',
            'holiday': 'jour férié'
        };
        
        const entityName = entityNames[entity] || entity;
        document.getElementById('formTitle').textContent = 'Ajouter ' + entityName;
        
        // Mettre à jour l'icône du formulaire
        const formIcon = document.getElementById('formIcon');
        if (formIcon) {
            formIcon.className = 'fas fa-plus me-2';
        }
        
        // Mettre à jour le texte et l'icône du bouton de sauvegarde
        const saveBtnText = document.getElementById('saveBtnText');
        const saveBtnIcon = document.getElementById('saveBtnIcon');
        if (saveBtnText) {
            saveBtnText.textContent = 'Ajouter';
        }
        if (saveBtnIcon) {
            saveBtnIcon.className = 'fas fa-plus';
        }
        
        // Définir les valeurs des champs cachés
        document.getElementById('entityInput').value = entity;
        document.getElementById('pkInput').value = '';
        document.getElementById('actionInput').value = 'add';
        
        // Réinitialiser tous les champs du formulaire
        const form = document.getElementById('editForm');
        if (form) {
            form.reset();
            
            // Décocher toutes les cases à cocher
            const checkboxes = form.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
        }
        
        // Afficher les champs pertinents
        hideAllFormFields();
        
        // Utiliser le bon identifiant pour l'onglet "Cotisations Sociales" et "Model de Calcul"
        const tabId = entity === 'social_contribution' ? 'social_contributions' : 
                     (entity === 'model_calcul' ? 'model-calcul' : entity);
        showRelevantFormFields(tabId);
        
        // Mettre à jour le texte du bouton après avoir affiché les champs
        updateAddButtonText(tabId);
        
        // Afficher le formulaire sous la liste
        document.getElementById('editFormContainer').style.display = 'block';
        
        // Faire défiler jusqu'au formulaire
        document.getElementById('editFormContainer').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    };
    
    // Fonction pour ouvrir le modal d'édition
    window.openEditModal = function(entity, id, name, rate, amount, ceiling, socialContributions, primes, prix, price) {
        // Mettre à jour le titre du formulaire
        const entityNames = {
            'position': 'poste',
            'department': 'département',
            'contract_type': 'type de contrat',
            'leave_type': 'type de congé',
            'prime': 'prime',
            'social_contribution': 'cotisation sociale',
            'model_calcul': 'modèle de calcul',
            'speciality': 'spécialité',
            'acte': 'acte',
            'holiday': 'jour férié'
        };
        
        const entityName = entityNames[entity] || entity;
        document.getElementById('formTitle').textContent = 'Modifier ' + entityName;
        
        // Mettre à jour l'icône du formulaire
        const formIcon = document.getElementById('formIcon');
        if (formIcon) {
            formIcon.className = 'fas fa-edit me-2';
        }
        
        // Mettre à jour le texte et l'icône du bouton de sauvegarde
        const saveBtnText = document.getElementById('saveBtnText');
        const saveBtnIcon = document.getElementById('saveBtnIcon');
        if (saveBtnText) {
            saveBtnText.textContent = 'Modifier';
        }
        if (saveBtnIcon) {
            saveBtnIcon.className = 'fas fa-edit';
        }
        
        // Remplir les champs du formulaire avec les données existantes
        document.getElementById('entityInput').value = entity;
        document.getElementById('pkInput').value = id;
        document.getElementById('actionInput').value = 'edit';
        
        // Remplir les champs en fonction de l'entité
        switch(entity) {
            case 'position':
            case 'department':
            case 'contract_type':
            case 'leave_type':
            case 'speciality':
                document.getElementById('commonLabelInput').value = name;
                break;
            case 'prime':
                document.getElementById('primeLibelleInput').value = name;
                document.getElementById('primeRateInput').value = rate;
                document.getElementById('primeAmountInput').value = amount;
                break;
            case 'social_contribution':
                document.getElementById('socialLabelInput').value = name;
                document.getElementById('rateInput').value = rate;
                document.getElementById('ceilingInput').value = ceiling;
                break;
            case 'model_calcul':
                document.getElementById('modelCalculLibelleInput').value = name;
                // Pour les sélections multiples, nous devons les gérer séparément
                if (socialContributions) {
                    const scIds = socialContributions.split(',');
                    scIds.forEach(id => {
                        const checkbox = document.getElementById('scCheckbox' + id);
                        if (checkbox) {
                            checkbox.checked = true;
                        }
                    });
                }
                if (primes) {
                    const primesIds = primes.split(',');
                    primesIds.forEach(id => {
                        const checkbox = document.getElementById('primeCheckbox' + id);
                        if (checkbox) {
                            checkbox.checked = true;
                        }
                    });
                }
                break;
            case 'acte':
                document.getElementById('acteLibelleInput').value = name;
                document.getElementById('actePriceInput').value = price || prix;
                break;
            case 'holiday':
                document.getElementById('holidayNameInput').value = name;
                const btn = document.querySelector(`.edit-btn[data-entity="holiday"][data-id="${id}"]`);
                const d = btn ? btn.getAttribute('data-day') : '';
                const m = btn ? btn.getAttribute('data-month') : '';
                const daySel = document.getElementById('holidayDayInput');
                const monthSel = document.getElementById('holidayMonthInput');
                if (daySel) daySel.value = d || '';
                if (monthSel) monthSel.value = m || '';
                break;
        }
        
        // Afficher les champs pertinents
        hideAllFormFields();
        
        // Utiliser le bon identifiant pour l'onglet "Cotisations Sociales" et "Model de Calcul"
        const tabId = entity === 'social_contribution' ? 'social_contributions' : 
                     (entity === 'model_calcul' ? 'model-calcul' : entity);
        showRelevantFormFields(tabId);
        
        // Afficher le formulaire sous la liste
        document.getElementById('editFormContainer').style.display = 'block';
        
        // Faire défiler jusqu'au formulaire
        document.getElementById('editFormContainer').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    };
    
    // Fonction pour supprimer un élément
    window.deleteItem = function(entity, id, name) {
        // Afficher une boîte de dialogue de confirmation
        Swal.fire({
            title: 'Confirmer la suppression',
            text: `Êtes-vous sûr de vouloir supprimer "${name}" ?`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Oui, supprimer',
            cancelButtonText: 'Annuler',
            confirmButtonColor: '#d33',
            cancelButtonColor: '#6c757d',
            allowOutsideClick: false
        }).then((result) => {
            if (result.isConfirmed) {
                // Afficher un indicateur de chargement
                Swal.showLoading();
                
                // Envoyer la requête de suppression via l'endpoint CRUD approprié
                const formData = new FormData();
                formData.append('action', 'delete');
                formData.append('entity', entity);
                formData.append('pk', id);
                formData.append('name', name);
                
                // Déterminer l'URL en fonction de l'entité
                let url;
                switch(entity) {
                    case 'position':
                        url = '/hr/position/crud/';
                        break;
                    case 'department':
                        url = '/hr/department/crud/';
                        break;
                    case 'contract_type':
                        url = '/hr/contract-type/crud/';
                        break;
                    case 'leave_type':
                        url = '/hr/leaves/type/crud/';
                        break;
                    case 'social_contribution':
                        url = '/hr/social-contributions/crud/';
                        break;
                    case 'prime':
                        url = '/hr/prime/crud/';
                        break;
                    case 'model_calcul':
                        url = '/hr/model-calcul/crud/';
                        break;
                    case 'acte':
                        url = '/hr/configuration/';
                        break;
                    case 'holiday':
                        url = '/hr/configuration/';
                        break;
                    case 'speciality':
                    default:
                        url = '/hr/configuration/crud/';
                }
                
                // Envoyer la requête
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData,
                    credentials: 'same-origin'
                })
                .then(response => {
                    console.log('Réponse HTTP reçue:', response.status);
                    if (!response.ok) {
                        return response.json().then(errData => {
                            console.error('Erreur du serveur:', errData);
                            throw new Error(errData.message || `Erreur HTTP: ${response.status}`);
                        }).catch(() => {
                            throw new Error(`Erreur HTTP: ${response.status}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Données reçues:', data);
                    if (data.status === 'success') {
                        // Afficher un message de succès
                        Swal.fire({
                            icon: 'success',
                            title: 'Succès',
                            text: data.message || 'Suppression effectuée avec succès',
                            confirmButtonText: 'OK'
                        }).then(() => {
                            // Recharger la page pour mettre à jour la liste
                            location.reload();
                        });
                    } else {
                        throw new Error(data.message || 'Erreur lors de la suppression');
                    }
                })
                .catch(error => {
                    console.error('Erreur lors de la suppression:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Erreur',
                        text: error.message || 'Une erreur est survenue lors de la suppression',
                        confirmButtonText: 'OK'
                    });
                });
            }
        });
    };
    
    // Fonction pour obtenir le cookie CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Fonction pour masquer le formulaire et réinitialiser les champs
    window.hideEditForm = function() {
        const formContainer = document.getElementById('editFormContainer');
        const editForm = document.getElementById('editForm');
        
        if (formContainer) {
            formContainer.style.display = 'none';
        }
        
        if (editForm) {
            editForm.reset();
            // Réactiver le bouton de soumission s'il était désactivé
            const submitBtn = editForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-save"></i> Enregistrer';
            }
        }
        
        hideAllFormFields();
    };
    
    // Gestion du changement automatique des boutons Exporter/Importer
    
    // Liste des sections avec leurs IDs correspondants
    const sections = [
        { name: 'position', selectAllId: 'selectAllPosition', tableId: 'position' },
        { name: 'department', selectAllId: 'selectAllDepartment', tableId: 'department' },
        { name: 'contract-type', selectAllId: 'selectAllContractType', tableId: 'contract_type' },
        { name: 'leave-type', selectAllId: 'selectAllLeaveType', tableId: 'leave_type' },
        { name: 'prime', selectAllId: 'selectAllPrime', tableId: 'prime' },
        { name: 'social-contributions', selectAllId: 'selectAllSocialContributions', tableId: 'social_contribution' },
        { name: 'model-calcul', selectAllId: 'selectAllModelCalcul', tableId: 'modelCalcul' },
        { name: 'speciality', selectAllId: 'selectAllSpeciality', tableId: 'speciality' },
        { name: 'service', selectAllId: 'selectAllService', tableId: 'service' },
        { name: 'holiday', selectAllId: 'selectAllHoliday', tableId: 'holiday' }
    ];
    
    // Fonction pour mettre à jour un bouton export/import spécifique
    function updateExportImportButton(sectionName, tableId = null) {
        const exportImportIcon = document.getElementById(`export-import-icon-${sectionName}`);
        const exportImportText = document.getElementById(`export-import-text-${sectionName}`);
        
        // Utiliser tableId si fourni, sinon utiliser sectionName
        const targetTableId = tableId || sectionName;
        const checkedBoxes = document.querySelectorAll(`#${targetTableId} .row-check:checked`);
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
        // Gestion des cases "Sélectionner tout"
        sections.forEach(section => {
            if (e.target.id === section.selectAllId) {
                const rowCheckboxes = document.querySelectorAll(`#${section.tableId} .row-check`);
                rowCheckboxes.forEach(checkbox => {
                    checkbox.checked = e.target.checked;
                });
                updateExportImportButton(section.name, section.tableId);
            }
        });
        
        // Gestion des cases individuelles
        if (e.target.classList.contains('row-check')) {
            // Déterminer dans quelle section se trouve la case cochée
            const table = e.target.closest('table');
            if (table) {
                const tableId = table.id;
                const section = sections.find(s => s.tableId === tableId);
                
                if (section) {
                    const selectAllCheckbox = document.getElementById(section.selectAllId);
                    const allCheckboxes = document.querySelectorAll(`#${tableId} .row-check`);
                    const checkedCheckboxes = document.querySelectorAll(`#${tableId} .row-check:checked`);
                    
                    if (selectAllCheckbox) {
                        selectAllCheckbox.checked = allCheckboxes.length === checkedCheckboxes.length;
                        selectAllCheckbox.indeterminate = checkedCheckboxes.length > 0 && checkedCheckboxes.length < allCheckboxes.length;
                    }
                    updateExportImportButton(section.name, section.tableId);
                }
            }
        }
    });
    
    // Initialiser l'état des boutons au chargement
    sections.forEach(section => {
        updateExportImportButton(section.name, section.tableId);
    });
    
    // Réinitialiser les boutons lors du changement d'onglet
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            setTimeout(() => {
                sections.forEach(section => {
                    updateExportImportButton(section.name, section.tableId);
                });
            }, 100);
        });
    });

    // Initialisation de la page
setTimeout(function() {
    console.log('Configuration page initialized');
}, 100);

    // (holiday seed/filter removed per request)
});
