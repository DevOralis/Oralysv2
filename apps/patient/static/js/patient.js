// patient.js : gestion dynamique de la liste des patients (recherche, tri, suppression, pagination)

function bindPatientPagination() {
    // Utiliser la délégation d'événements sur le document pour les liens de pagination
    document.addEventListener('click', function(e) {
        const link = e.target.closest('.page-ajax');
        if (link && link.closest('#patient-table-block')) {
            e.preventDefault();
            
            fetch(link.getAttribute('href'), { 
                headers: { 'X-Requested-With': 'XMLHttpRequest' } 
            })
                .then(response => response.json())
                .then(data => {
                const tableBlock = document.getElementById('patient-table-block');
                if (tableBlock) {
                    tableBlock.innerHTML = data.html;
                    // Réattacher les événements après le chargement AJAX
    setupPatientTableFeatures();
                    attachPatientActionEvents();
                }
            })
            .catch(error => {
                console.error('Erreur pagination:', error);
            });
        }
    });
}

function attachPatientActionEvents() {
    // Les liens d'édition sont maintenant des liens normaux, pas besoin d'événement

    // Suppression avec confirmation
    document.querySelectorAll('.delete-patient-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const patientId = this.dataset.patientId;
            const patientName = this.dataset.patientName;
            
            Swal.fire({
                title: 'Confirmer la suppression',
                text: `Voulez-vous vraiment supprimer le patient "${patientName}" ?`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Oui, supprimer',
                cancelButtonText: 'Annuler'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = `/patient/delete/${patientId}/`;
                }
            });
        });
    });

    // Gestion du modal des détails patient
    document.querySelectorAll('.view-patient-details-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const patientId = this.dataset.patientId;
            const patientName = this.dataset.patientName;
            const patientPhone = this.dataset.patientPhone;
            const patientBirth = this.dataset.patientBirth;
            const patientGender = this.dataset.patientGender;
            const patientMedecin = this.dataset.patientMedecin;

            document.getElementById('modal-patient-name').textContent = patientName || '-';
            document.getElementById('modal-patient-phone').textContent = patientPhone || '-';
            document.getElementById('modal-patient-birth').textContent = patientBirth || '-';
            document.getElementById('modal-patient-gender').textContent = patientGender || '-';
            document.getElementById('modal-patient-medecin').textContent = patientMedecin || '-';

            const modal = new bootstrap.Modal(document.getElementById('patientDetailsModal'));
            modal.show();
        });
    });
}

function showEditPatientForm(patientId) {
    // Rediriger vers le formulaire d'édition
    window.location.href = `?patient_id=${patientId}#new-patient`;
}

document.addEventListener('DOMContentLoaded', function() {
    const newPatientCard = document.getElementById('new-patient');
    const addNewPatientBtn = document.getElementById('add-new-patient-btn');
    const cancelButton = newPatientCard ? newPatientCard.querySelector('.btn-secondary') : null;

    // Cacher la carte par défaut
    if (newPatientCard) {
        newPatientCard.style.display = 'none';
    }

    // Afficher la carte au clic sur "Nouveau patient"
    if (addNewPatientBtn) {
        addNewPatientBtn.addEventListener('click', function(e) {
            e.preventDefault();
            newPatientCard.style.display = 'block';
            newPatientCard.scrollIntoView({ behavior: 'smooth' });
        });
    }

    // Cacher la carte au clic sur "Annuler"
    if (cancelButton) {
        cancelButton.addEventListener('click', function() {
            newPatientCard.style.display = 'none';
        });
    }

    // Initialiser la pagination AJAX (5 patients par page)
    bindPatientPagination();
    
    // Initialiser les fonctionnalités du tableau
    setupPatientTableFeatures();
    
    // Attacher les événements d'actions
    attachPatientActionEvents();

    // Gestion de l'affichage des champs d'assurance
    function toggleInsuranceFields() {
        const hasInsuranceYes = document.getElementById('hasInsuranceYes');
        const hasInsuranceNo = document.getElementById('hasInsuranceNo');
        const insuranceFields = document.getElementById('insuranceFields');
        
        if (hasInsuranceYes && hasInsuranceNo && insuranceFields) {
            if (hasInsuranceYes.checked) {
                insuranceFields.style.display = 'block';
            } else {
                insuranceFields.style.display = 'none';
            }
        }
    }

    // Événements pour les boutons radio d'assurance
    const hasInsuranceYes = document.getElementById('hasInsuranceYes');
    const hasInsuranceNo = document.getElementById('hasInsuranceNo');
    
    if (hasInsuranceYes) {
        hasInsuranceYes.addEventListener('change', toggleInsuranceFields);
    }
    if (hasInsuranceNo) {
        hasInsuranceNo.addEventListener('change', toggleInsuranceFields);
    }
    
    // Initialiser l'état des champs d'assurance au chargement
    toggleInsuranceFields();

    // Validation du champ CIN
    const cinInput = document.querySelector('input[name="cin"]');
    if (cinInput) {
        cinInput.addEventListener('blur', function() {
            validateCIN(this);
        });
        
        cinInput.addEventListener('input', function() {
            // Convertir automatiquement en majuscules
            this.value = this.value.toUpperCase();
            
            // Validation en temps réel pendant la saisie
            validateCINRealTime(this);
        });
        
        // Validation initiale si le champ a déjà une valeur
        if (cinInput.value) {
            validateCINRealTime(cinInput);
        }
    }
    
    // Validation du formulaire avant soumission
    const patientForm = document.querySelector('form[action*="patient_list_create"]');
    if (patientForm) {
        patientForm.addEventListener('submit', function(e) {
            const cinField = this.querySelector('input[name="cin"]');
            if (cinField && !validateCIN(cinField)) {
                e.preventDefault();
                cinField.focus();
                return false;
            }
        });
    }

    // La navigation des onglets est gérée par le script inline dans patient.html
    // pour utiliser l'API Bootstrap Tab correctement

    document.querySelectorAll('.edit-mutuelle-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const patientId = btn.getAttribute('data-id');
            fetch(`/patient/mutuelle-edit-form/${patientId}/`)
                .then(response => response.text())
                .then(html => {
                    const container = document.getElementById('mutuelle-edit-form-container');
                    container.innerHTML = html;
                    container.style.display = 'block';
                    container.scrollIntoView({ behavior: 'smooth' });
                });
        });
    });
});

// Fonction pour configurer toutes les fonctionnalités du tableau
function setupPatientTableFeatures() {
    const table = document.getElementById('tablePatient');
    if (!table) return;
    
    // Activer les checkboxes
    setupPatientCheckboxes();
}

// Fonction de tri pour le tableau des patients
function setupPatientSorting() {
    const sortableHeaders = document.querySelectorAll('#tablePatient .sortable');
    
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const sortField = this.dataset.sort;
            const currentDirection = this.dataset.direction || 'asc';
            const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
            
            // Mettre à jour l'icône de tri
            updatePatientSortIcons(this, newDirection);
            
            // Trier le tableau côté client
            sortPatientTable(sortField, newDirection);
            
            // Sauvegarder la direction pour ce header
            this.dataset.direction = newDirection;
        });
    });
}

function sortPatientTable(sortField, direction) {
    const table = document.getElementById('tablePatient');
    if (!table) {
        console.warn('Table tablePatient non trouvée pour le tri');
        return;
    }
    
    const tbody = table.querySelector('tbody');
    if (!tbody) {
        console.warn('tbody non trouvé pour le tri');
        return;
    }
    
    const rows = Array.from(tbody.querySelectorAll('tr:not(.empty-row)'));
    
    rows.sort((a, b) => {
        let aValue, bValue;
        
        switch(sortField) {
            case 'nom':
                // Chercher dans la colonne Nom (peut contenir strong ou juste du texte)
                const nomCellA = a.querySelector('[data-label="Nom"]');
                const nomCellB = b.querySelector('[data-label="Nom"]');
                aValue = nomCellA ? nomCellA.textContent.trim().split('\n')[0].trim() : '';
                bValue = nomCellB ? nomCellB.textContent.trim().split('\n')[0].trim() : '';
                break;
            case 'prenom':
                aValue = a.querySelector('[data-label="Prénom"]')?.textContent.trim() || '';
                bValue = b.querySelector('[data-label="Prénom"]')?.textContent.trim() || '';
                break;
            case 'medecin':
                aValue = a.querySelector('[data-label="Médecin traitant"]')?.textContent.trim() || '';
                bValue = b.querySelector('[data-label="Médecin traitant"]')?.textContent.trim() || '';
                break;
            case 'sexe':
                aValue = a.querySelector('[data-label="Sexe"]')?.textContent.trim() || '';
                bValue = b.querySelector('[data-label="Sexe"]')?.textContent.trim() || '';
                break;
            case 'naissance':
                aValue = a.querySelector('[data-label="Date de naissance"]')?.textContent.trim() || '';
                bValue = b.querySelector('[data-label="Date de naissance"]')?.textContent.trim() || '';
                break;
            case 'telephone':
                aValue = a.querySelector('[data-label="Téléphone"]')?.textContent.trim() || '';
                bValue = b.querySelector('[data-label="Téléphone"]')?.textContent.trim() || '';
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

function updatePatientSortIcons(activeHeader, direction) {
    // Réinitialiser toutes les icônes
    document.querySelectorAll('#tablePatient .sort-icon').forEach(icon => {
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

// Fonction pour gérer les checkboxes des patients
function setupPatientCheckboxes() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const rowCheckboxes = document.querySelectorAll('#tablePatient .row-check');
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            const visibleCheckboxes = document.querySelectorAll('#tablePatient tbody tr:not([style*="display: none"]) .row-check');
            visibleCheckboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
            });
        });
    }
    
    // Gérer les checkboxes individuelles
    rowCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateCheckboxState();
        });
    });
}

function updateCheckboxState() {
    const selectAllCheckbox = document.getElementById('selectAll');
    if (!selectAllCheckbox) return;
    
    const visibleCheckboxes = Array.from(document.querySelectorAll('#tablePatient tbody tr:not([style*="display: none"]) .row-check'));
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

// Gestion du changement automatique du bouton Exporter/Importer
function updateExportImportButton() {
    const exportImportIcon = document.getElementById('export-import-icon');
    const exportImportText = document.getElementById('export-import-text');
    const checkedBoxes = document.querySelectorAll('#tablePatient .row-check:checked');
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
        const isChecked = e.target.checked;
        const visibleCheckboxes = document.querySelectorAll('#tablePatient tbody tr:not([style*="display: none"]) .row-check');
        visibleCheckboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
        });
        updateExportImportButton();
    } else if (e.target.classList.contains('row-check')) {
        // Gestion des cases individuelles
        updateCheckboxState();
    }
});

// Fonction de validation du CIN (pour la soumission et blur)
function validateCIN(input) {
    const value = input.value.trim();
    
    // Si le champ est vide, c'est valide (optionnel)
    if (value === '') {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        return true;
    }
    
    // Vérifier le format : 8 à 20 caractères alphanumériques en majuscules
    const cinPattern = /^[A-Z0-9]{8,20}$/;
    
    if (cinPattern.test(value)) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        return true;
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
        
        // Afficher une alerte d'erreur
        Swal.fire({
            title: 'Format CIN invalide',
            text: 'Le N° CIN doit contenir entre 8 et 20 caractères alphanumériques en majuscules.\nExemple: A12345678',
            icon: 'error',
            confirmButtonText: 'OK',
            confirmButtonColor: '#d33'
        });
        
        return false;
    }
}

// Fonction de validation en temps réel du CIN (pendant la saisie)
function validateCINRealTime(input) {
    const value = input.value.trim();
    
    // Supprimer les classes précédentes
    input.classList.remove('is-valid', 'is-invalid');
    
    // Si le champ est vide, neutre (pas de couleur)
    if (value === '') {
        return true;
    }
    
    // Vérifier le format : 8 à 20 caractères alphanumériques en majuscules
    const cinPattern = /^[A-Z0-9]{8,20}$/;
    
    if (cinPattern.test(value)) {
        // Format correct : vert
        input.classList.add('is-valid');
        return true;
    } else {
        // Format incorrect : rouge
        input.classList.add('is-invalid');
        return false;
    }
} 