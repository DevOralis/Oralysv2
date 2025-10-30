function scrollToNewEmployee(event) {
  if (event) {
    event.preventDefault();
  }
  const target = document.getElementById('new-employee');
  if (target) {
    target.scrollIntoView({ behavior: 'smooth' });
  }
}

function resetEmployeeForm() {

  document.getElementById('employe_id').value = '';

  document.querySelectorAll('#new-employee input[type="text"], #new-employee input[type="email"], #new-employee input[type="tel"], #new-employee input[type="date"], #new-employee input[type="number"]').forEach(input => {
    input.value = '';
  });

  document.querySelectorAll('#new-employee select').forEach(select => {
    select.value = '';
  });
  
  // Reset textareas
  document.querySelectorAll('#new-employee textarea').forEach(textarea => {
    textarea.value = '';
  });
  
  // Reset radios
  document.querySelectorAll('#new-employee input[type="radio"]').forEach(radio => {
    radio.checked = false;
  });
  
  // Reset photo
  const photoPreview = document.getElementById('photoPreview');
  if (photoPreview) {
    photoPreview.src = '/static/images/user-photo.jpg';
  }
  
  // Reset children count
  const childrenCountInput = document.getElementById('nombre-enfants');
  if (childrenCountInput) {
    childrenCountInput.value = '0';
    // Trigger change event to update children fields
    const event = new Event('change');
    childrenCountInput.dispatchEvent(event);
  }
  
  // Clear children container
  const childrenContainer = document.getElementById('enfants-container');
  if (childrenContainer) {
    childrenContainer.innerHTML = '';
  }
  
  // Reset competences
  const competencesList = document.getElementById('competence-list');
  if (competencesList) {
    competencesList.innerHTML = '<input type="text" class="form-control mb-1" name="competences[]" placeholder="Compétence">';
  }
  
  // Reset dynamic uploads
  const dynamicUpload = document.getElementById('upload-dynamique');
  if (dynamicUpload) {
    dynamicUpload.innerHTML = '';
  }
  
  // Return to first tab
  const firstTab = document.querySelector('#employeeTabs .nav-link');
  if (firstTab) {
    const tab = new bootstrap.Tab(firstTab);
    tab.show();
  }
}

document.addEventListener('DOMContentLoaded', function() {
  // Patch Bootstrap Modal to prevent backdrop errors
  if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
    try {
      // Patch backdrop initialization
      const originalModalInit = bootstrap.Modal.prototype._initializeBackDrop;
      
      bootstrap.Modal.prototype._initializeBackDrop = function() {
        try {
          if (originalModalInit) {
            return originalModalInit.call(this);
          }
        } catch (error) {
          console.warn('Bootstrap modal backdrop error avoided:', error);
          // Create a basic backdrop manually
          this._backdrop = {
            isAnimated: false,
            isVisible: true,
            dispose: () => { 
              // Do nothing or implement if needed 
            }
          };
        }
      };
      
      // Patch focus trap initialization
      const originalFocusTrapInit = bootstrap.Modal.prototype._initializeFocusTrap;
      
      bootstrap.Modal.prototype._initializeFocusTrap = function() {
        try {
          if (originalFocusTrapInit) {
            return originalFocusTrapInit.call(this);
          }
        } catch (error) {
          console.warn('Bootstrap modal focus trap error avoided:', error);
          // Create a dummy focus trap that does nothing
          this._focustrap = {
            activate: () => {},
            deactivate: () => {},
            dispose: () => {}
          };
        }
      };
    } catch (error) {
      console.error('Could not patch Bootstrap modal:', error);
    }
  }

  // Handle next/previous buttons for tab navigation
  document.querySelectorAll('.next-tab').forEach(button => {
    button.addEventListener('click', function() {
      const nextTabId = this.getAttribute('data-next');
      const nextTab = document.querySelector(`[data-bs-target="#${nextTabId}"]`);
      if (nextTab) {
        // Check if required fields in current tab are filled
        const currentTabId = this.closest('.tab-pane').id;
        const currentTabFields = document.querySelectorAll(`#${currentTabId} [required]`);
        let allFieldsValid = true;
        
        currentTabFields.forEach(field => {
          if (!field.value) {
            allFieldsValid = false;
            field.classList.add('is-invalid');
            
            // Add error message if needed
            if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('invalid-feedback')) {
              const feedback = document.createElement('div');
              feedback.className = 'invalid-feedback';
              feedback.textContent = 'Ce champ est requis';
              field.parentNode.insertBefore(feedback, field.nextSibling);
            }
          } else {
            field.classList.remove('is-invalid');
            if (field.nextElementSibling && field.nextElementSibling.classList.contains('invalid-feedback')) {
              field.nextElementSibling.remove();
            }
          }
        });
        
        if (allFieldsValid) {
          // Activate next tab
          const tab = new bootstrap.Tab(nextTab);
          tab.show();
          
          // Scroll to form top
          const formElement = document.getElementById('new-employee');
          if (formElement) {
            setTimeout(() => {
              formElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
          }
        } else {
          // Show general error message
          Swal.fire({
            icon: 'error',
            title: 'Champs requis',
            text: 'Veuillez remplir tous les champs requis avant de continuer.'
          });
        }
      }
    });
  });
  
  document.querySelectorAll('.prev-tab').forEach(button => {
    button.addEventListener('click', function() {
      const prevTabId = this.getAttribute('data-prev');
      const prevTab = document.querySelector(`[data-bs-target="#${prevTabId}"]`);
      if (prevTab) {
        const tab = new bootstrap.Tab(prevTab);
        tab.show();
        
        // Scroll to form top
        const formElement = document.getElementById('new-employee');
        if (formElement) {
          setTimeout(() => {
            formElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }, 100);
        }
      }
    });
  });

  // Handle tab changes via tab navigation buttons
  document.querySelectorAll('#salaryTabs .nav-link').forEach(tabButton => {
    tabButton.addEventListener('click', function() {
      // Scroll to form top
      const formElement = document.getElementById('new-employee');
      if (formElement) {
        setTimeout(() => {
          formElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
      }
    });
  });

  // Check URL parameters for notifications and scrolling
  const urlParams = new URLSearchParams(window.location.search);
  const action = urlParams.get('action');
  const status = urlParams.get('status');
  const entity = urlParams.get('entity');
  
  // Handle scrolling to form if we have an employe_id in URL or scrollToForm flag
  if (urlParams.has('employee_id') || sessionStorage.getItem('scrollToForm') === 'true') {
    sessionStorage.removeItem('scrollToForm');
    setTimeout(() => {
      const target = document.getElementById('new-employee');
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    }, 300);
  }
  
  // Handle success notifications
  if (action && status === 'success') {
    let message = '';
    let entityName = '';
    
    if (entity === 'position') entityName = 'Le poste';
    else if (entity === 'department') entityName = 'Le département';
    else if (entity === 'contract_type') entityName = 'Le type de contrat';
    else entityName = 'L\'employé';
    
    if (action === 'add') {
      message = `${entityName} a été ajouté avec succès.`;
    } else if (action === 'edit') {
      message = `${entityName} a été modifié avec succès.`;
    } else if (action === 'delete') {
      message = `${entityName} a été supprimé avec succès.`;
    }
    
    if (message) {
      Swal.fire({
        icon: 'success',
        title: 'Opération réussie',
        text: message,
        timer: 2000,
        showConfirmButton: false
      });
      
      // Clean URL to avoid showing notification on refresh
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }
  
  // For "Nouvel Employé" button
  const btnNew = document.querySelector('a[href="#new-employee"]');
  if (btnNew) {
    btnNew.addEventListener('click', function(e) {
      scrollToNewEmployee(e);
      resetEmployeeForm();
    });
  }
  
  // For all edit buttons
  document.querySelectorAll('.edit-employe-btn').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      // Don't prevent navigation as we need the parameter in URL
      // but add attribute to indicate we want to scroll
      sessionStorage.setItem('scrollToForm', 'true');
    });
  });
  
  // For all delete buttons
  let deleteTargetBtn = null;
  document.querySelectorAll('.delete-employe-btn').forEach(function(btn) {
    btn.addEventListener('click', function(event) {
      event.preventDefault();
      deleteTargetBtn = btn;
      const modal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
      modal.show();
    });
  });
  
  // Actual delete action after confirmation
  const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener('click', function() {
      if (deleteTargetBtn) {
        deleteTargetBtn.closest('form') ? deleteTargetBtn.closest('form').submit() : deleteTargetBtn.click();
        deleteTargetBtn = null;
      }
      const modal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal'));
      if (modal) modal.hide();
    });
  }

  // Dynamic display of end date field based on contract type
  const contractTypeSelect = document.getElementById('contract-type');
  if (contractTypeSelect) {
    function toggleEndDate() {
      const selectedOption = contractTypeSelect.options[contractTypeSelect.selectedIndex];
      const endDateInput = document.getElementById('end-date');
      
      if (selectedOption && (selectedOption.text.toLowerCase().includes('cdd') || selectedOption.text.toLowerCase().includes('durée déterminée') || selectedOption.text.toLowerCase().includes('determinee'))) {
        endDateInput.disabled = false;
        endDateInput.classList.remove('disabled-input');
      } else {
        endDateInput.disabled = true;
        endDateInput.classList.add('disabled-input');
        endDateInput.value = '';
      }
    }
    
    contractTypeSelect.addEventListener('change', toggleEndDate);
    toggleEndDate(); // Initial call
  }

  // Fonction globale pour checkContractType (appelée depuis le template)
  window.checkContractType = function(contractTypeId) {
    const contractTypeSelect = document.getElementById('contract-type');
    if (contractTypeSelect) {
      const selectedOption = contractTypeSelect.options[contractTypeSelect.selectedIndex];
      const endDateInput = document.getElementById('end-date');
      
      if (selectedOption && (selectedOption.text.toLowerCase().includes('cdd') || selectedOption.text.toLowerCase().includes('durée déterminée') || selectedOption.text.toLowerCase().includes('determinee'))) {
        endDateInput.disabled = false;
        endDateInput.classList.remove('disabled-input');
      } else {
        endDateInput.disabled = true;
        endDateInput.classList.add('disabled-input');
        endDateInput.value = '';
      }
    }
  };

  // Dynamic upload field based on position selection
  const posteSelect = document.getElementById('poste-select');
  if (posteSelect) {
    function updateUploadField() {
      const selectedOption = posteSelect.options[posteSelect.selectedIndex];
      const uploadContainer = document.getElementById('upload-dynamique');
      
      if (selectedOption && selectedOption.text.toLowerCase().includes('médecin')) {
        uploadContainer.innerHTML = `
          <div class="col-md-4">
            <label class="form-label">Convention médecin (upload)</label>
            <input type="file" class="form-control" name="convention_medecin" />
          </div>
        `;
      } else if (selectedOption && selectedOption.text.toLowerCase().includes('vacataire')) {
        uploadContainer.innerHTML = `
          <div class="col-md-4">
            <label class="form-label">Convention vacataire (upload)</label>
            <input type="file" class="form-control" name="convention_vacataire" />
          </div>
        `;
      } else {
        uploadContainer.innerHTML = '';
      }
    }
    
    posteSelect.addEventListener('change', updateUploadField);
    updateUploadField(); // Initial call
  }

  // Toggle supervisor select based on responsible role
  function toggleSupervisorSelect() {
    const responsableRadios = document.querySelectorAll('input[name="is_supervisor"]');
    const supervisorContainer = document.getElementById('responsible-select-container');
    
    responsableRadios.forEach(radio => {
      radio.addEventListener('change', function() {
        if (this.value === '1') {
          // Si "Oui" est sélectionné, masquer la liste des responsables
          supervisorContainer.style.display = 'none';
          // Clear the supervisor selection
          const supervisorSelect = supervisorContainer.querySelector('select');
          if (supervisorSelect) {
            supervisorSelect.value = '';
          }
        } else {
          // Si "Non" est sélectionné, afficher la liste des responsables
          supervisorContainer.style.display = 'block';
        }
      });
    });
  }
  toggleSupervisorSelect();

  // Address assistance functionality
  function setupAddressAssist(idBase, fields, labelJoin = ', ') {
    const input = document.getElementById(idBase);
    if (!input) return;
    
    function showFields() {
      const container = input.parentElement;
      const currentValue = input.value;
      
      // Create individual field inputs
      const fieldsHtml = fields.map(field => `
        <div class="col-md-3">
          <label class="form-label">${field}</label>
          <input type="text" class="form-control" name="${idBase}_${field.toLowerCase().replace(/\s+/g, '_')}" 
                 value="${currentValue.split(labelJoin)[fields.indexOf(field)] || ''}" />
        </div>
      `).join('');
      
      // Replace the single input with multiple fields
      container.innerHTML = `
        <div class="row g-3">
          ${fieldsHtml}
          <div class="col-12">
            <button type="button" class="btn btn-sm btn-outline-secondary" onclick="hideFieldsAndMerge('${idBase}', '${fields.join(labelJoin)}')">
              <i class="fas fa-compress"></i> Fusionner
            </button>
          </div>
        </div>
      `;
    }
    
    function hideFieldsAndMerge() {
      const container = document.querySelector(`#${idBase}`).parentElement;
      const fieldInputs = container.querySelectorAll('input[type="text"]');
      const mergedValue = Array.from(fieldInputs).map(input => input.value).filter(val => val).join(labelJoin);
      
      // Restore the single input
      container.innerHTML = `
        <label class="form-label">${idBase === 'adresse-personnelle' ? 'Adresse personnelle' : 'Adresse administrative'}</label>
        <input type="text" class="form-control" id="${idBase}" name="${idBase}" value="${mergedValue}" />
        <button type="button" class="btn btn-sm btn-outline-secondary mt-1" onclick="showFields('${idBase}')">
          <i class="fas fa-expand"></i> Décomposer
        </button>
      `;
    }
    
    // Add expand button to the original input
    const expandBtn = document.createElement('button');
    expandBtn.type = 'button';
    expandBtn.className = 'btn btn-sm btn-outline-secondary mt-1';
    expandBtn.innerHTML = '<i class="fas fa-expand"></i> Décomposer';
    expandBtn.onclick = showFields;
    input.parentElement.appendChild(expandBtn);
    
    // Make functions globally available
    window.showFields = showFields;
    window.hideFieldsAndMerge = hideFieldsAndMerge;
  }
  
  // Setup address assistance for both address fields
  setupAddressAssist('adresse-personnelle', ['Rue', 'Ville', 'Code Postal', 'Pays']);
  setupAddressAssist('adresse-administrative', ['Rue', 'Ville', 'Code Postal', 'Pays']);

  // Children management
  const childrenCountInput = document.getElementById('nombre-enfants');
  if (childrenCountInput) {
    childrenCountInput.addEventListener('change', function() {
      const count = parseInt(this.value) || 0;
      // Récupérer les enfants existants s'ils sont présents dans la page
      const existingChildrenData = window.existingChildren || [];
      handleChildrenFields(count, existingChildrenData);
    });
    
    // Déclencher l'événement au chargement si des enfants existent
    if (window.existingChildren && window.existingChildren.length > 0) {
      childrenCountInput.value = window.existingChildren.length;
      const event = new Event('change');
      childrenCountInput.dispatchEvent(event);
    }
  }

  // Competences management
  const addCompetenceBtn = document.getElementById('ajouter-competence');
  if (addCompetenceBtn) {
    addCompetenceBtn.addEventListener('click', function() {
      const competencesList = document.getElementById('competence-list');
      const newInput = document.createElement('input');
      newInput.type = 'text';
      newInput.className = 'form-control mb-1';
      newInput.name = 'competences[]';
      newInput.placeholder = 'Compétence';
      competencesList.appendChild(newInput);
    });
  }

  // Photo preview
  const photoInput = document.getElementById('photoInput');
  if (photoInput) {
    photoInput.addEventListener('change', function() {
      const file = this.files[0];
      const preview = document.getElementById('photoPreview');
      
      if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
          preview.src = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Duplicate checking
  function checkDuplicates() {
    const employeeIdInput = document.querySelector('input[name="employee_id"]');
    const cinInput = document.querySelector('input[name="cin"]');
    const emailInput = document.querySelector('input[name="email"]');
    
    if (employeeIdInput) {
      employeeIdInput.addEventListener('blur', function() {
        const value = this.value.trim();
        if (value) {
          // Check for duplicates in the table
          const table = document.getElementById('tableEmploye');
          const rows = table.querySelectorAll('tbody tr');
          let isDuplicate = false;
          
          rows.forEach(row => {
            const employeeIdCell = row.cells[0]; // Assuming employee ID is in first column
            if (employeeIdCell && employeeIdCell.textContent.trim() === value) {
              isDuplicate = true;
            }
          });
          
          if (isDuplicate) {
            this.classList.add('is-invalid');
            if (!this.nextElementSibling || !this.nextElementSibling.classList.contains('invalid-feedback')) {
              const feedback = document.createElement('div');
              feedback.className = 'invalid-feedback';
              feedback.textContent = 'Cet identifiant d\'employé existe déjà';
              this.parentNode.insertBefore(feedback, this.nextSibling);
            }
          } else {
            this.classList.remove('is-invalid');
            if (this.nextElementSibling && this.nextElementSibling.classList.contains('invalid-feedback')) {
              this.nextElementSibling.remove();
            }
          }
        }
      });
    }
  }
  checkDuplicates();

  // Initialize configuration page functionality only if we're on the HR configuration page
  // Détecter la page de configuration HR par la présence des tables ou de l'URL
  const isConfigPage = document.getElementById('position') || 
                      document.getElementById('department') || 
                      document.getElementById('contract_type') ||
                      window.location.pathname.includes('hr_configuration');
  
  if (isConfigPage) {
    initializeConfigurationPage();
  }

  // Ajouter l'écouteur pour le bouton "New Employee"
  const newEmployeeBtn = document.querySelector('a[href="#new-employee"]');
  if (newEmployeeBtn) {
    newEmployeeBtn.addEventListener('click', function(e) {
      e.preventDefault();
      // Marquer qu'on veut scroller vers le formulaire après reload
      sessionStorage.setItem('scrollToForm', 'true');
      // Faire un reload de la page pour un nouvel employé
      window.location.href = window.location.pathname;
    });
  }

  // Initialiser les champs médicaux au chargement de la page
  const positionSelect = document.getElementById('position-select');
  if (positionSelect) {
    checkMedicalPosition(positionSelect.value);
  }

  // Handle leave request form submission
  const leaveRequestForm = document.getElementById('leaveRequestForm');
  if (leaveRequestForm) {
    leaveRequestForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const formData = new FormData(this);
      // Supprimer duration s'il existe dans le formulaire (par sécurité)
      if (formData.has('duration')) {
        formData.delete('duration');
      }
      
      fetch('/hr/submit_leave_request/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          // Show success message with SweetAlert
          Swal.fire({
            icon: 'success',
            title: 'Succès',
            text: data.message,
            timer: 2000,
            showConfirmButton: false
          }).then(() => {
            // Reload the page after the alert is closed
            window.location.reload();
          });

          // Close the modal
          const modal = bootstrap.Modal.getInstance(document.getElementById('newLeaveRequestModal'));
          modal.hide();

          // Reset the form
          leaveRequestForm.reset();
        } else {
          // Show error message
          let errorMessage = data.message;
          
          // Check for specific error messages and provide user-friendly translations
          if (errorMessage.includes('LeaveBalance matching query does not exist')) {
              errorMessage = "Vous n'avez pas de solde de congés pour ce type de congé. Veuillez contacter les RH pour initialiser vos soldes.";
          }
          
          Swal.fire({
            icon: 'error',
            title: 'Erreur',
            text: errorMessage
          });
        }
      })
      .catch(error => {
        console.error('Error:', error);
        Swal.fire({
          icon: 'error',
          title: 'Erreur',
          text: 'Une erreur est survenue lors de la soumission de la demande.'
        });
      });
    });
  }

  // Gestion des demandes de congés (seulement si les éléments existent)
  let confirmationModal = null;
  let detailsModal = null;
  if (document.getElementById('confirmationModal')) {
    confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'));
  }
  if (document.getElementById('detailsModal')) {
    detailsModal = new bootstrap.Modal(document.getElementById('detailsModal'));
  }
  let currentRequestId = null;
  let currentAction = null;

  // Gestionnaire pour le bouton d'approbation
  document.querySelectorAll('.approveRequest').forEach(button => {
    button.addEventListener('click', function() {
      currentRequestId = this.dataset.id;
      currentAction = 'approve';
      document.getElementById('actionType').textContent = 'approuver';
      confirmationModal.show();
    });
  });

  // Gestionnaire pour le bouton de refus
  document.querySelectorAll('.refuseRequest').forEach(button => {
    button.addEventListener('click', function() {
      currentRequestId = this.dataset.id;
      currentAction = 'refuse';
      document.getElementById('actionType').textContent = 'refuser';
      confirmationModal.show();
    });
  });

  // Gestionnaire pour le bouton de détails
  document.querySelectorAll('.viewDetails').forEach(button => {
    button.addEventListener('click', async function() {
      const requestId = this.dataset.id;
      try {
        const response = await fetch(`/hr/leaves/get/${requestId}/`);
        if (!response.ok) throw new Error('Erreur lors de la récupération des détails');
        const data = await response.json();
        
        // Remplir les détails dans le modal
        document.getElementById('detailEmployee').textContent = data.employee_name;
        document.getElementById('detailType').textContent = data.leave_type;
        document.getElementById('detailDates').textContent = `${data.start_date} - ${data.end_date}`;
        document.getElementById('detailDuration').textContent = `${data.duration} jour(s)`;
        document.getElementById('detailRequestDate').textContent = data.request_date;
        document.getElementById('detailNotes').textContent = data.notes || '-';
        
        // Gérer l'affichage du certificat
        const certificateContainer = document.getElementById('certificateContainer');
        if (data.certificate_url) {
          certificateContainer.style.display = 'block';
          const certificateLink = document.getElementById('certificateLink');
          if (certificateLink) {
            certificateLink.href = data.certificate_url;
          }
        } else {
          certificateContainer.style.display = 'none';
        }
        
        if (detailsModal) {
          detailsModal.show();
        }
      } catch (error) {
        console.error('Erreur:', error);
        Swal.fire({
          icon: 'error',
          title: 'Erreur',
          text: 'Impossible de récupérer les détails de la demande'
        });
      }
    });
  });

  // Gestionnaire pour le bouton de confirmation (seulement si l'élément existe)
  const confirmActionBtn = document.getElementById('confirmAction');
  if (confirmActionBtn) {
    confirmActionBtn.addEventListener('click', async function() {
    const comments = document.getElementById('comments').value;
    
    try {
      const response = await fetch(`/hr/leaves/${currentAction}/${currentRequestId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ comments: comments })
      });

      if (!response.ok) throw new Error(`Erreur lors de l'${currentAction === 'approve' ? 'approbation' : 'refus'}`);

      if (confirmationModal) {
        confirmationModal.hide();
      }
      
      // Rafraîchir la page après le succès
      Swal.fire({
        icon: 'success',
        title: 'Succès',
        text: `La demande a été ${currentAction === 'approve' ? 'approuvée' : 'refusée'} avec succès`,
        willClose: () => {
          window.location.reload();
        }
      });
    } catch (error) {
      console.error('Erreur:', error);
      Swal.fire({
        icon: 'error',
        title: 'Erreur',
        text: `Une erreur est survenue lors de l'${currentAction === 'approve' ? 'approbation' : 'refus'} de la demande`
      });
    }
    });
  }

  // Réinitialiser les champs du modal lors de la fermeture (seulement si l'élément existe)
  const confirmationModalElement = document.getElementById('confirmationModal');
  if (confirmationModalElement) {
    confirmationModalElement.addEventListener('hidden.bs.modal', function () {
      document.getElementById('comments').value = '';
      currentRequestId = null;
      currentAction = null;
    });
  }

  // Intercepter le formulaire d'employé
  const employeeForm = document.querySelector('form[action*="add_employee"]');
  if (employeeForm) {
    employeeForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Créer un objet FormData à partir du formulaire
      const formData = new FormData(this);
      
      // Envoyer les données via AJAX
      fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          // Afficher un message de succès
          Swal.fire({
            icon: 'success',
            title: 'Succès!',
            text: 'Employé modifié avec succès.',
            confirmButtonText: 'OK'
          }).then((result) => {
            // Recharger la page quand l'utilisateur clique sur OK
            if (result.isConfirmed) {
              window.location.reload();
            }
          });
        } else {
          // Afficher un message d'erreur
          Swal.fire({
            icon: 'error',
            title: 'Erreur',
            text: data.message || 'Une erreur est survenue lors de la modification de l\'employé.'
          });
        }
      })
      .catch(error => {
        console.error('Erreur:', error);
        Swal.fire({
          icon: 'error',
          title: 'Erreur',
          text: 'Une erreur est survenue lors de la communication avec le serveur.'
        });
      });
    });
  }

  // Gestionnaire pour le bouton "voir plus" - géré dans initializeConfigurationPage
  // Protection contre les doublons
  const viewButtons = document.querySelectorAll('.viewRequest:not([data-listener-added])');
  
  viewButtons.forEach(button => {
    button.setAttribute('data-listener-added', 'true');
    button.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      const requestId = this.getAttribute('data-id');
      console.log('Viewing request:', requestId);
      
      if (!requestId) {
        console.error('ID de demande manquant');
        return;
      }
      
      // Empêcher les clics multiples
      if (this.classList.contains('loading')) {
        return;
      }
      this.classList.add('loading');
      
      // Récupérer les détails de la demande
      fetch(`/hr/leaves/get/${requestId}/`, {
          method: 'GET',
          headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'X-CSRFToken': getCookie('csrftoken')
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
          this.classList.remove('loading');
          console.log('Response data:', data);
          
          if (data.status === 'success') {
              // Vérifier si c'est pour la visualisation (modal de détails)
              const viewModal = document.getElementById('viewLeaveRequestModal');
              
              if (viewModal) {
                  // Mode visualisation - remplir le modal de visualisation
                  const elements = {
                      'viewLeaveType': data.request.leave_type?.name || 'N/A',
                      'viewStartDate': data.request.start_date ? new Date(data.request.start_date).toLocaleDateString('fr-FR') : 'N/A',
                      'viewEndDate': data.request.end_date ? new Date(data.request.end_date).toLocaleDateString('fr-FR') : 'N/A',
                      'viewDuration': data.request.duration || 'N/A',
                      'viewNotes': data.request.notes || 'Aucun commentaire'
                  };
                  
                  Object.entries(elements).forEach(([id, value]) => {
                      const element = document.getElementById(id);
                      if (element) element.textContent = value;
                  });
                  
                  // Gérer le statut
                  const statusElement = document.getElementById('viewStatus');
                  if (statusElement && data.request.status) {
                      statusElement.textContent = getStatusLabel ? getStatusLabel(data.request.status) : data.request.status;
                      statusElement.className = 'badge ' + (getStatusClass ? getStatusClass(data.request.status) : 'bg-secondary');
                  }
                  
                  // Date de demande
                  const viewRequestDate = document.getElementById('viewRequestDate');
                  if (viewRequestDate && data.request.request_date) {
                      const requestDate = new Date(data.request.request_date);
                      viewRequestDate.textContent = requestDate.toLocaleDateString('fr-FR') + ' ' + 
                          requestDate.toLocaleTimeString('fr-FR', {hour: '2-digit', minute:'2-digit'});
                  }
                  
                  // Certificat
                  const certSection = document.getElementById('viewCertificateSection');
                  const certLink = document.getElementById('viewCertificateLink');
                  if (certSection && certLink) {
                      if (data.request.certificate) {
                          certSection.style.display = 'block';
                          certLink.href = data.request.certificate_url;
                          certLink.textContent = data.request.certificate_name;
                      } else {
                          certSection.style.display = 'none';
                      }
                  }
                  
                  // Afficher le modal de visualisation
                  try {
                      const modal = bootstrap.Modal.getOrCreateInstance(viewModal);
                      modal.show();
                  } catch (modalError) {
                      console.error('Erreur modal:', modalError);
                  }
              } else {
                  // Pas de modal de visualisation, utiliser SweetAlert
                  const request = data.request;
                  const startDate = new Date(request.start_date).toLocaleDateString('fr-FR');
                  const endDate = new Date(request.end_date).toLocaleDateString('fr-FR');
                  
                  let html = `
                      <div class="leave-details">
                          <div class="detail-row"><strong>Type:</strong> ${request.leave_type?.name || 'N/A'}</div>
                          <div class="detail-row"><strong>Période:</strong> ${startDate} au ${endDate}</div>
                          <div class="detail-row"><strong>Durée:</strong> ${request.duration} jour(s)</div>
                          <div class="detail-row"><strong>Statut:</strong> ${request.status_display || request.status}</div>
                          <div class="detail-row"><strong>Date de demande:</strong> ${new Date(request.request_date).toLocaleString('fr-FR')}</div>
                          ${request.notes ? `<div class="detail-row"><strong>Commentaires:</strong> ${request.notes}</div>` : ''}
                      </div>
                  `;
                  
                  Swal.fire({
                      title: 'Détails de la demande',
                      html: html,
                      width: '600px',
                      confirmButtonText: 'Fermer'
                  });
              }
          } else {
              Swal.fire({
                  icon: 'error',
                  title: 'Erreur',
                  text: data.message || 'Une erreur est survenue lors du chargement'
              });
          }
      })
      .catch(error => {
          this.classList.remove('loading');
          console.error('Erreur:', error);
          Swal.fire({
              icon: 'error',
              title: 'Erreur',
              text: 'Une erreur est survenue lors de la communication avec le serveur'
          });
      });
    });
  });
  
  // Gestionnaire pour le bouton "modifier"
  const editButtons = document.querySelectorAll('.editRequest:not([data-listener-added])');
  
  editButtons.forEach(button => {
    button.setAttribute('data-listener-added', 'true');
    button.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      const requestId = this.getAttribute('data-id');
      console.log('Editing request:', requestId);
      
      if (!requestId) {
        console.error('ID de demande manquant');
        return;
      }
      
      // Empêcher les clics multiples
      if (this.classList.contains('loading')) {
        return;
      }
      this.classList.add('loading');
      
      // Récupérer les détails pour modification
      fetch(`/hr/leaves/get/${requestId}/`, {
          method: 'GET',
          headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'X-CSRFToken': getCookie('csrftoken')
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
          this.classList.remove('loading');
          console.log('Response data:', data);
          
          if (data.status === 'success') {
              const request = data.request;
              
              // Remplir le formulaire de modification
              const editElements = {
                  'editRequestId': requestId,
                  'editLeaveType': request.leave_type_id,
                  'editStartDate': request.start_date,
                  'editEndDate': request.end_date,
                  'editNotes': request.notes || ''
              };
              
              Object.entries(editElements).forEach(([id, value]) => {
                  const element = document.getElementById(id);
                  if (element) {
                      element.value = value;
                  }
              });
              
              // Afficher le modal de modification
              const editModal = document.getElementById('editLeaveRequestModal');
              if (editModal) {
                  try {
                      const modal = bootstrap.Modal.getOrCreateInstance(editModal);
                      modal.show();
                  } catch (modalError) {
                      console.error('Erreur modal modification:', modalError);
                  }
              } else {
                  console.error('Modal de modification non trouvé');
              }
          } else {
              Swal.fire({
                  icon: 'error',
                  title: 'Erreur',
                  text: data.message || 'Une erreur est survenue lors du chargement'
              });
          }
      })
      .catch(error => {
          this.classList.remove('loading');
          console.error('Erreur:', error);
          Swal.fire({
              icon: 'error',
              title: 'Erreur',
              text: 'Une erreur est survenue lors de la communication avec le serveur'
          });
      });
    });
  });

  // Gestionnaire pour la soumission du formulaire de modification (seulement si l'élément existe)
  const editLeaveRequestForm = document.getElementById('editLeaveRequestForm');
  if (editLeaveRequestForm) {
    editLeaveRequestForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const requestId = document.getElementById('editRequestId').value;
    console.log('Submitting edit for request:', requestId); // Debug log
    
    const formData = new FormData(this);
    
    fetch(`/hr/leaves/edit/${requestId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        console.log('Edit response status:', response.status); // Debug log
        return response.json();
    })
    .then(data => {
        console.log('Edit response data:', data); // Debug log
        if (data.status === 'success') {
            Swal.fire({
                icon: 'success',
                title: 'Succès',
                text: 'La demande a été modifiée avec succès',
                confirmButtonText: 'OK'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.reload();
                }
            });
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Erreur',
                text: data.message || 'Une erreur est survenue lors de la modification'
            });
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        Swal.fire({
            icon: 'error',
            title: 'Erreur',
            text: 'Une erreur est survenue lors de la modification'
        });
    });
    });
  }

  // --- Cotisations sociales ---
  const searchSocialContribution = document.getElementById('searchSocialContribution');
  if (searchSocialContribution) {
    setupTableSearch('searchSocialContribution', 'social_contribution');
  }

  // Ajout
  const addSocialContributionBtn = document.getElementById('addSocialContributionBtn');
  if (addSocialContributionBtn) {
    addSocialContributionBtn.addEventListener('click', function() {
      showForm('add', '', 'social_contribution');
    });
  }

  // Édition
  document.querySelectorAll('#social_contribution .edit-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const pk = this.getAttribute('data-pk');
      showForm('edit', pk, 'social_contribution', this);
    });
  });

  // Suppression
  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const entity = this.getAttribute('data-entity');
      const pk = this.getAttribute('data-pk');
      const name = this.getAttribute('data-name') || this.getAttribute('data-label');
      let entityName = '';
      if (entity === 'position') entityName = 'ce poste';
      if (entity === 'department') entityName = 'ce département';
      if (entity === 'contract_type') entityName = 'ce type de contrat';
      if (entity === 'leave_type') entityName = 'ce type de congé';
      if (entity === 'social_contribution') entityName = 'cette cotisation sociale';
      Swal.fire({
        title: 'Êtes-vous sûr ?',
        text: `Voulez-vous vraiment supprimer ${entityName} "${name}" ?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Oui, supprimer',
        cancelButtonText: 'Annuler'
      }).then((result) => {
        if (result.isConfirmed) {
          this.disabled = true;
          this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
          if (entity === 'leave_type') {
            if (pk && pk.trim() !== '') {
              handleLeaveTypeDeletion(pk, this);
            } else {
              console.error('Leave type ID is empty or undefined');
              this.disabled = false;
              this.innerHTML = '<i class="fas fa-trash-alt"></i>';
              Swal.fire({
                icon: 'error',
                title: 'Erreur',
                text: 'Impossible de supprimer ce type de congé: identifiant manquant'
              });
            }
          } else if (entity === 'social_contribution') {
            // Suppression AJAX dédiée pour social_contribution
            let base = window.location.pathname.split('/configuration')[0];
            if (base.endsWith('/')) base = base.slice(0, -1);
            const postUrl = base + '/social-contributions/crud/';
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
            formData.append('entity', 'social_contribution');
            formData.append('pk', pk);
            formData.append('action', 'delete');
            fetch(postUrl, {
              method: 'POST',
              body: formData,
              headers: {
                'X-Requested-With': 'XMLHttpRequest'
              }
            })
            .then(response => {
              if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
              }
              return response.json();
            })
            .then(data => {
              if (data.status === 'success') {
                Swal.fire({
                  icon: 'success',
                  title: 'Succès',
                  text: data.message,
                  timer: 2000,
                  showConfirmButton: false
                }).then(() => {
                  window.location.reload();
                });
              } else {
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-trash-alt"></i>';
                Swal.fire({
                  icon: 'error',
                  title: 'Erreur',
                  text: data.message || 'Une erreur est survenue lors de la suppression.'
                });
              }
            })
            .catch(error => {
              console.error('Error:', error);
              this.disabled = false;
              this.innerHTML = '<i class="fas fa-trash-alt"></i>';
              Swal.fire({
                icon: 'error',
                title: 'Erreur',
                text: 'Une erreur est survenue lors de la suppression. Veuillez réessayer ou contacter l\'administrateur.'
              });
            });
          } else {
            // ... existing code ...
          }
        }
      });
    });
  });

  // Ajout Prime (ciblage fiable par id)
  const addPrimeBtn = document.getElementById('addPrimeBtn');
  if (addPrimeBtn) {
    addPrimeBtn.addEventListener('click', function() {
      showForm('add', '', 'prime');
    });
  }

  // Édition Prime
  document.querySelectorAll('#prime .edit-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const pk = this.getAttribute('data-pk');
      showForm('edit', pk, 'prime', this);
    });
  });

  // Suppression Prime
  document.querySelectorAll('#prime .delete-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const pk = this.getAttribute('data-pk');
      const libelle = this.getAttribute('data-libelle');
      Swal.fire({
        title: 'Êtes-vous sûr ?',
        text: `Voulez-vous vraiment supprimer la prime "${libelle}" ?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Oui, supprimer',
        cancelButtonText: 'Annuler'
      }).then((result) => {
        if (result.isConfirmed) {
          this.disabled = true;
          this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
          const formData = new FormData();
          formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
          formData.append('entity', 'prime');
          formData.append('pk', pk);
          formData.append('action', 'delete');
          fetch(window.location.pathname, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
          })
          .then(response => response.json())
          .then(data => {
            if (data.status === 'success') {
              Swal.fire({ icon: 'success', title: 'Succès', text: data.message, timer: 2000, showConfirmButton: false }).then(() => { window.location.reload(); });
            } else {
              this.disabled = false;
              this.innerHTML = '<i class="fas fa-trash-alt"></i>';
              Swal.fire({ icon: 'error', title: 'Erreur', text: data.message || 'Une erreur est survenue lors de la suppression.' });
            }
          })
          .catch(error => {
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-trash-alt"></i>';
            Swal.fire({ icon: 'error', title: 'Erreur', text: 'Une erreur est survenue lors de la suppression.' });
          });
        }
      });
    });
  });

  // Ajout CRUD spécialité (similaire à poste)
  document.addEventListener('DOMContentLoaded', function() {
    // Recherche et pagination déjà gérées par setupConfigTableSearchAndPagination dans le template

    // Gestion des boutons d'ajout/modification pour spécialité
    document.querySelectorAll('button.btn-add[data-entity="speciality"]').forEach(btn => {
      btn.addEventListener('click', function() {
        // Réinitialiser le formulaire
        const form = document.getElementById('specialityForm');
        if (form) form.reset();
        // Mettre à jour le titre
        const modalTitle = document.getElementById('specialityModalLabel');
        if (modalTitle) modalTitle.textContent = 'Ajouter une spécialité';
        // Réinitialiser le champ caché pk
        const pkInput = form.querySelector('input[name="pk"]');
        if (pkInput) pkInput.value = '';
        // Ouvrir la modale
        const modal = new bootstrap.Modal(document.getElementById('specialityModal'));
        modal.show();
      });
    });

    // Gestion du bouton d'édition spécialité
    document.querySelectorAll('a.edit-btn[data-entity="speciality"]').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        const pk = btn.getAttribute('data-pk');
        const name = btn.getAttribute('data-name');
        const form = document.getElementById('specialityForm');
        if (form) {
          form.reset();
          // Remplir les champs
          const nameInput = document.getElementById('specialityNameInput');
          if (nameInput) nameInput.value = name;
          const pkInput = form.querySelector('input[name="pk"]');
          if (pkInput) pkInput.value = pk;
        }
        // Mettre à jour le titre
        const modalTitle = document.getElementById('specialityModalLabel');
        if (modalTitle) modalTitle.textContent = 'Modifier la spécialité';
        // Ouvrir la modale
        const modal = new bootstrap.Modal(document.getElementById('specialityModal'));
        modal.show();
      });
    });

    // Soumission du formulaire spécialité (ajout/édition)
    const specialityForm = document.getElementById('specialityForm');
    if (specialityForm) {
      specialityForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(specialityForm);
        const action = formData.get('pk') ? 'edit' : 'add';
        formData.set('action', action);
        fetch(window.location.pathname, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': window.getCSRFToken(),
          },
          body: new URLSearchParams(formData)
        })
        .then(response => response.json())
        .then(data => {
          if (data.status === 'success') {
            // Fermer la modale
            const modal = bootstrap.Modal.getInstance(document.getElementById('specialityModal'));
            if (modal) modal.hide();
            Swal.fire('Succès', data.message, 'success').then(() => window.location.reload());
          } else {
            Swal.fire('Erreur', data.message, 'error');
          }
        });
      });
    }

    // Gestion des boutons de suppression pour spécialité
    document.querySelectorAll('button.delete-btn[data-entity="speciality"]').forEach(btn => {
      btn.addEventListener('click', function() {
        const pk = btn.getAttribute('data-pk');
        const name = btn.getAttribute('data-name');
        Swal.fire({
          title: 'Supprimer la spécialité',
          text: `Voulez-vous vraiment supprimer la spécialité : ${name} ?`,
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Supprimer',
          cancelButtonText: 'Annuler',
        }).then(result => {
          if (result.isConfirmed) {
            fetch(window.location.pathname, {
              method: 'POST',
              headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': window.getCSRFToken(),
                'Content-Type': 'application/x-www-form-urlencoded',
              },
              body: `entity=speciality&action=delete&pk=${pk}`
            })
            .then(response => response.json())
            .then(data => {
              if (data.status === 'success') {
                Swal.fire('Succès', data.message, 'success').then(() => window.location.reload());
              } else {
                Swal.fire('Erreur', data.message, 'error');
              }
            });
          }
        });
      });
    });
  });
});

window.remplirFormulaireEmploye = function(btn) {
  document.getElementById('employe_id').value = btn.getAttribute('data-employe-id') || '';
  document.querySelector('input[name="nom_complet"]').value = btn.getAttribute('data-nom-complet') || '';
  document.querySelector('input[name="cin"]').value = btn.getAttribute('data-cin') || '';
  document.querySelector('input[name="employee_id"]').value = btn.getAttribute('data-employee-id') || '';
  document.querySelector('input[name="date_naissance"]').value = btn.getAttribute('data-date-naissance') || '';
  document.querySelector('select[name="situation_familiale"]').value = btn.getAttribute('data-situation-familiale') || '';
  document.querySelector('select[name="genre"]').value = btn.getAttribute('data-genre') || '';
  document.querySelector('input[name="email"]').value = btn.getAttribute('data-email') || '';
  document.querySelector('input[name="telephone_personnel"]').value = btn.getAttribute('data-telephone-personnel') || '';
  document.querySelector('input[name="telephone_administratif"]').value = btn.getAttribute('data-telephone-administratif') || '';
  // ENFANTS
  const nEnfants = parseInt(btn.getAttribute('data-nombre-enfants')) || 0;
  const enfantsInput = document.getElementById('nombre-enfants');
  enfantsInput.value = nEnfants;
  enfantsInput.dispatchEvent(new Event('change'));
  // Si les noms et genres sont passés en data, les remplir ici (à adapter si besoin)
  // COMPETENCES
  const competencesStr = btn.getAttribute('data-competences') || '';
  const competences = competencesStr ? competencesStr.split(',') : [];
  const competenceList = document.getElementById('competence-list');
  competenceList.innerHTML = '';
  competences.forEach(function(val) {
    if (val.trim()) {
      const input = document.createElement('input');
      input.type = 'text';
      input.className = 'form-control mb-1';
      input.name = 'competences[]';
      input.value = val;
      input.placeholder = 'Compétence';
      competenceList.appendChild(input);
    }
  });
  if (competences.length === 0) {
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'form-control mb-1';
    input.name = 'competences[]';
    input.placeholder = 'Compétence';
    competenceList.appendChild(input);
  }
  // Statut radio
  const statut = btn.getAttribute('data-statut');
  if (statut) {
    document.getElementById('statutActif').checked = (statut === 'A');
    document.getElementById('statutInactif').checked = (statut === 'N');
  }
  // Professionnel
  document.getElementById('poste-select').value = btn.getAttribute('data-poste') || '';
  document.querySelector('select[name="departement"]').value = btn.getAttribute('data-departement') || '';
  // Contrat
  document.getElementById('type-contrat').value = btn.getAttribute('data-type-contrat') || '';
  document.querySelector('input[name="date-debut"]').value = btn.getAttribute('data-date-debut') || '';
  document.getElementById('date-fin').value = btn.getAttribute('data-date-fin') || '';
  // Salaire
  document.querySelector('input[name="salaire_base"]').value = btn.getAttribute('data-salaire-base') || '';
  document.querySelector('input[name="primes"]').value = btn.getAttribute('data-primes') || '';
  document.querySelector('input[name="avantages"]').value = btn.getAttribute('data-avantages') || '';
  // Carrière
  document.querySelector('textarea[name="evolution_carriere"]').value = btn.getAttribute('data-evolution-carriere') || '';
  // Responsable
  const isResponsable = btn.getAttribute('data-is-responsable');
  if (isResponsable === '1') {
    document.getElementById('roleOui').checked = true;
    document.getElementById('roleNon').checked = false;
  } else {
    document.getElementById('roleOui').checked = false;
    document.getElementById('roleNon').checked = true;
  }
  // Superviseur
  const superviseurId = btn.getAttribute('data-superviseur-id');
  if (superviseurId) {
    document.querySelector('select[name="responsable_select"]').value = superviseurId;
  }
  // TODO : adresses dynamiques à pré-remplir si besoin
};

window.chargerEmploye = function(employeId) {
  fetch(`/employes/get/${employeId}/`)
    .then(response => response.json())
    .then(data => {
      document.getElementById('employe_id').value = data.id;
      document.querySelector('input[name="employee_id"]').value = data.identification_matricule || '';
      document.querySelector('input[name="cin"]').value = data.cin || '';
      document.querySelector('input[name="nom_complet"]').value = data.nom_complet || '';
      document.querySelector('input[name="date_naissance"]').value = data.date_naissance || '';
      document.querySelector('select[name="situation_familiale"]').value = data.situation_familiale || '';
      document.querySelector('select[name="genre"]').value = data.genre || '';
      document.querySelector('input[name="email"]').value = data.email || '';
      document.querySelector('input[name="telephone_personnel"]').value = data.telephone_personnel || '';
      document.querySelector('input[name="telephone_administratif"]').value = data.telephone_administratif || '';
      // ENFANTS
      const enfantsInput = document.getElementById('nombre-enfants');
      enfantsInput.value = data.nombre_enfants || 0;
      enfantsInput.dispatchEvent(new Event('change'));
      // Remplir les champs enfants si présents
      if (data.enfants && data.enfants.length) {
        setTimeout(() => {
          data.enfants.forEach((enf, i) => {
            const nomInput = document.querySelector(`input[name="enfant_nom_${i}"]`);
            const genreSelect = document.querySelector(`select[name="enfant_genre_${i}"]`);
            if (nomInput) nomInput.value = enf.nom;
            if (genreSelect) genreSelect.value = enf.genre;
          });
        }, 100);
      }
      // Statut radio
      if (data.statut) {
        document.getElementById('statutActif').checked = (data.statut === 'A');
        document.getElementById('statutInactif').checked = (data.statut === 'N');
      }
      // Professionnel
      document.getElementById('poste-select').value = data.poste || '';
      document.querySelector('select[name="departement"]').value = data.departement || '';
      // Responsable
      if (data.is_responsable == 1) {
        document.getElementById('roleOui').checked = true;
        document.getElementById('roleNon').checked = false;
      } else {
        document.getElementById('roleOui').checked = false;
        document.getElementById('roleNon').checked = true;
      }
      document.querySelector('select[name="responsable_select"]').value = data.superviseur_id || '';
      // Contrat
      document.getElementById('type-contrat').value = data.type_contrat || '';
      document.querySelector('input[name="date-debut"]').value = data.date_debut || '';
      document.getElementById('date-fin').value = data.date_fin || '';
      // Salaire
      document.querySelector('input[name="salaire_base"]').value = data.salaire_base || '';
      document.querySelector('input[name="primes"]').value = data.primes || '';
      document.querySelector('input[name="avantages"]').value = data.avantages || '';
      // Carrière
      document.querySelector('textarea[name="evolution_carriere"]').value = data.evolution_carriere || '';
      // COMPETENCES
      const competenceList = document.getElementById('competence-list');
      competenceList.innerHTML = '';
      if (data.competences && data.competences.length) {
        data.competences.forEach(function(val) {
          if (val.trim()) {
            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'form-control mb-1';
            input.name = 'competences[]';
            input.value = val;
            input.placeholder = 'Compétence';
            competenceList.appendChild(input);
          }
        });
      } else {
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'form-control mb-1';
        input.name = 'competences[]';
        input.placeholder = 'Compétence';
        competenceList.appendChild(input);
      }
      // Scroll towards the form
      document.getElementById('new-employee').scrollIntoView({ behavior: 'smooth' });
    });
};

// Function to normalize strings (remove accents)
function normalize(str) {
  return str
    .toLowerCase()
    .normalize('NFD') // décompose les accents
    .replace(/[ -\u036f]/g, '') // supprime les accents
    .replace(/\s+/g, ''); // supprime les espaces
}

/**
 * Initialise les fonctionnalités de la page de configuration
 */
function initializeConfigurationPage() {
  // Définir la liste des tables de configuration HR
  const tables = ['position', 'department', 'contract_type', 'leave_type', 'prime', 'social_contribution', 'modelCalcul', 'speciality'];
  
  // La recherche et pagination sont gérées par setupConfigTableSearchAndPagination
  
  
  // Initialiser les filtres de département parent
  const filterDepartmentParent = document.getElementById('filterDepartmentParent');
  if (filterDepartmentParent) {
    filterDepartmentParent.addEventListener('change', function() {
      filterTable('department');
    });
  }
  
  // Initialiser les filtres pour les types de congé
  const filterLeaveTypeYear = document.getElementById('filterLeaveTypeYear');
  if (filterLeaveTypeYear) {
    filterLeaveTypeYear.addEventListener('change', function() {
      filterTable('leave_type');
    });
  }
  
  const filterLeaveTypeMethod = document.getElementById('filterLeaveTypeMethod');
  if (filterLeaveTypeMethod) {
    filterLeaveTypeMethod.addEventListener('change', function() {
      filterTable('leave_type');
    });
  }
  
  const filterLeaveTypeActive = document.getElementById('filterLeaveTypeActive');
  if (filterLeaveTypeActive) {
    filterLeaveTypeActive.addEventListener('change', function() {
      filterTable('leave_type');
    });
  }
  
  // Initialiser le tri des colonnes
  document.querySelectorAll('.sortable').forEach(header => {
    header.addEventListener('click', function() {
      const table = this.closest('table');
      const column = Array.from(this.parentElement.children).indexOf(this);
      const currentDirection = this.getAttribute('data-direction') || 'asc';
      const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
      
      // Mettre à jour l'indicateur de direction
      this.setAttribute('data-direction', newDirection);
      
      // Mettre à jour l'icône
      const icon = this.querySelector('i');
      if (icon) {
        icon.className = newDirection === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down';
      }
      
      // Trier le tableau
      sortTable(table, column, newDirection);
    });
  });
  
  // Function to get active tab information
  function getActiveTabInfo() {
    const activeTab = document.querySelector('.nav-link.active');
    if (!activeTab) return null;
    
    const target = activeTab.getAttribute('data-bs-target');
    if (!target) return null;
    
    // Map tab targets to entities
    const entityMap = {
      '#position': 'position',
      '#department': 'department', 
      '#contract_type': 'contract_type',
      '#leave_type': 'leave_type',
      '#prime': 'prime',
      '#social_contributions': 'social_contribution',
      '#speciality': 'speciality',
      '#model-calcul': 'model_calcul',
      '#service': 'service'
    };
    
    const entity = entityMap[target];
    return entity ? { entity } : null;
  }
  
  // Function to handle deletions with SweetAlert2
  setupDeleteButtons();
  
  // Initialize add buttons with btn-add class
  document.querySelectorAll('.btn-add').forEach(btn => {
    btn.addEventListener('click', () => {
      const tabInfo = getActiveTabInfo();
      if (tabInfo && tabInfo.entity) {
        showForm('add', '', tabInfo.entity);
      } else {
        console.error('Impossible de déterminer l\'entité active');
      }
    });
  });
  
  // Events for edit buttons
  document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const pk = this.getAttribute('data-pk');
      const entity = this.getAttribute('data-entity');
      showForm('edit', pk, entity, this);
    });
  });
  
  // Événement pour le bouton d'annulation
  const cancelBtn = document.getElementById('cancelBtn');
  if (cancelBtn) {
    cancelBtn.addEventListener('click', hideForm);
  }
  
  // Mettre à jour le formulaire lors du changement d'onglet
  document.querySelectorAll('.nav-link').forEach(tab => {
    tab.addEventListener('click', function() {
      hideForm();
      setTimeout(updateAddButtons, 100);
      
    });
  });
  
  // Initialiser le formulaire d'édition
  const editForm = document.getElementById('editForm');
  if (editForm) {
    editForm.addEventListener('submit', function(e) {
      e.preventDefault();
      submitForm(this);
    });
  }
  
  // Mettre à jour les boutons d'ajout au chargement
  updateAddButtons();
  
  // Ajouter des messages "Aucun résultat" pour chaque tableau
  tables.forEach(tableId => {
    const table = document.getElementById(tableId);
    if (table) {
      const tbody = table.querySelector('tbody');
      if (tbody) {
        // Vérifier si le message "Aucun résultat" existe déjà
        if (!document.getElementById(`${tableId}-no-results`)) {
          const noResultsRow = document.createElement('tr');
          noResultsRow.id = `${tableId}-no-results`;
          noResultsRow.style.display = 'none';
          const td = document.createElement('td');
          td.setAttribute('colspan', '10'); // Assez large pour tous les tableaux
          td.className = 'text-center py-3';
          td.textContent = 'Aucun résultat trouvé pour votre recherche';
          noResultsRow.appendChild(td);
          tbody.appendChild(noResultsRow);
        }
      }
    }
  });
  
  // Les filtres sont gérés par setupConfigTableSearchAndPagination
  // Ne pas appeler filterTable ici pour éviter les conflits avec la pagination
}






// Fonction pour gérer les suppressions avec SweetAlert2
function setupDeleteButtons() {
  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const entity = this.getAttribute('data-entity');
      const pk = this.getAttribute('data-pk');
      const name = this.getAttribute('data-name') || this.getAttribute('data-label');
      let entityName = '';
      if (entity === 'position') entityName = 'ce poste';
      if (entity === 'department') entityName = 'ce département';
      if (entity === 'contract_type') entityName = 'ce type de contrat';
      if (entity === 'leave_type') entityName = 'ce type de congé';
      if (entity === 'social_contribution') entityName = 'cette cotisation sociale';
      Swal.fire({
        title: 'Êtes-vous sûr ?',
        text: `Voulez-vous vraiment supprimer ${entityName} "${name}" ?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Oui, supprimer',
        cancelButtonText: 'Annuler'
      }).then((result) => {
        if (result.isConfirmed) {
          // Marquer le bouton comme désactivé pour éviter les doubles clics
          this.disabled = true;
          this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
          
          // Traiter différemment les types de congé
          if (entity === 'leave_type') {
            // Make sure pk is not empty and pass it to the deletion function
            if (pk && pk.trim() !== '') {
              handleLeaveTypeDeletion(pk, this);
            } else {
              console.error('Leave type ID is empty or undefined');
              this.disabled = false;
              this.innerHTML = '<i class="fas fa-trash-alt"></i>';
              Swal.fire({
                icon: 'error',
                title: 'Erreur',
                text: 'Impossible de supprimer ce type de congé: identifiant manquant'
              });
            }
          } else if (entity === 'social_contribution') {
            // Suppression AJAX dédiée pour social_contribution
            let base = window.location.pathname.split('/configuration')[0];
            if (base.endsWith('/')) base = base.slice(0, -1);
            const postUrl = base + '/social-contributions/crud/';
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
            formData.append('entity', 'social_contribution');
            formData.append('pk', pk);
            formData.append('action', 'delete');
            fetch(postUrl, {
              method: 'POST',
              body: formData,
              headers: {
                'X-Requested-With': 'XMLHttpRequest'
              }
            })
            .then(response => {
              if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
              }
              return response.json();
            })
            .then(data => {
              if (data.status === 'success') {
                Swal.fire({
                  icon: 'success',
                  title: 'Succès',
                  text: data.message,
                  timer: 2000,
                  showConfirmButton: false
                }).then(() => {
                  window.location.reload();
                });
              } else {
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-trash-alt"></i>';
                Swal.fire({
                  icon: 'error',
                  title: 'Erreur',
                  text: data.message || 'Une erreur est survenue lors de la suppression.'
                });
              }
            })
            .catch(error => {
              console.error('Error:', error);
              this.disabled = false;
              this.innerHTML = '<i class="fas fa-trash-alt"></i>';
              Swal.fire({
                icon: 'error',
                title: 'Erreur',
                text: 'Une erreur est survenue lors de la suppression. Veuillez réessayer ou contacter l\'administrateur.'
              });
            });
          } else {
            // Créer un formulaire pour soumettre la requête
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
            formData.append('entity', entity);
            formData.append('pk', pk);
            formData.append('action', 'delete');
            
            // Envoyer une requête AJAX
            fetch(window.location.pathname, {
              method: 'POST',
              body: formData,
              headers: {
                'X-Requested-With': 'XMLHttpRequest'
              }
            })
            .then(response => {
              if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
              }
              return response.json();
            })
            .then(data => {
              if (data.status === 'success') {
                Swal.fire({
                  icon: 'success',
                  title: 'Succès',
                  text: data.message,
                  timer: 2000,
                  showConfirmButton: false
                }).then(() => {
                  window.location.reload();
                });
              } else {
                // Réactiver le bouton
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-trash-alt"></i>';
                
                Swal.fire({
                  icon: 'error',
                  title: 'Erreur',
                  text: data.message || 'Une erreur est survenue lors de la suppression.'
                });
              }
            })
            .catch(error => {
              console.error('Error:', error);
              
              // Réactiver le bouton
              this.disabled = false;
              this.innerHTML = '<i class="fas fa-trash-alt"></i>';
              
              Swal.fire({
                icon: 'error',
                title: 'Erreur',
                text: 'Une erreur est survenue lors de la suppression. Veuillez réessayer ou contacter l\'administrateur.'
              });
            });
          }
        }
      });
    });
  });
}

/**
 * Fonction spéciale pour gérer la suppression des types de congé
 * @param {string} type_id - ID du type de congé à supprimer
 * @param {HTMLElement} button - Bouton de suppression
 */
function handleLeaveTypeDeletion(type_id, button) {
  console.log('Suppression spéciale pour type de congé:', type_id);
  
  // Créer un formulaire pour soumettre la requête
          const form = document.createElement('form');
  form.method = 'POST';
  form.action = window.location.pathname;
          form.style.display = 'none';
          
  // Ajouter les champs nécessaires
  const csrfField = document.createElement('input');
  csrfField.type = 'hidden';
  csrfField.name = 'csrfmiddlewaretoken';
  csrfField.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
  form.appendChild(csrfField);
  
  const entityField = document.createElement('input');
  entityField.type = 'hidden';
  entityField.name = 'entity';
  entityField.value = 'leave_type';
  form.appendChild(entityField);
  
  // Change from 'pk' to 'type_id' to match the views.py expectation
  const pkField = document.createElement('input');
  pkField.type = 'hidden';
  pkField.name = 'type_id';
  pkField.value = type_id;
  form.appendChild(pkField);
  
  const actionField = document.createElement('input');
  actionField.type = 'hidden';
  actionField.name = 'action';
  actionField.value = 'delete';
  form.appendChild(actionField);
  
  // Ajouter le formulaire à la page et le soumettre
          document.body.appendChild(form);
          
  // Log the form data for debugging
  console.log('Form data being submitted:', {
    'csrfmiddlewaretoken': csrfField.value,
    'entity': entityField.value,
    'type_id': pkField.value,
    'action': actionField.value
  });
  
  // Soumettre le formulaire via fetch pour avoir plus de contrôle
          fetch(window.location.pathname, {
            method: 'POST',
    body: new FormData(form),
            headers: {
              'X-Requested-With': 'XMLHttpRequest'
            }
          })
  .then(response => {
    // Log the response for debugging
    console.log('Response status:', response.status);
    if (!response.ok) {
      return response.text().then(text => {
        throw new Error(`HTTP error! Status: ${response.status}, Body: ${text}`);
      });
    }
    return response.json();
  })
          .then(data => {
    console.log('Response data:', data);
            if (data.status === 'success') {
              Swal.fire({
                icon: 'success',
                title: 'Succès',
                text: data.message,
                timer: 2000,
                showConfirmButton: false
              }).then(() => {
                window.location.reload();
              });
            } else {
      // Réactiver le bouton
      button.disabled = false;
      button.innerHTML = '<i class="fas fa-trash-alt"></i>';
      
              Swal.fire({
                icon: 'error',
                title: 'Erreur',
                text: data.message || 'Une erreur est survenue lors de la suppression.'
              });
            }
          })
          .catch(error => {
            console.error('Error:', error);
    
    // Réactiver le bouton
    button.disabled = false;
    button.innerHTML = '<i class="fas fa-trash-alt"></i>';
    
            Swal.fire({
              icon: 'error',
              title: 'Erreur',
      text: 'Une erreur est survenue lors de la suppression. Veuillez réessayer ou contacter l\'administrateur.'
    });
  })
  .finally(() => {
    // Nettoyer le formulaire
    document.body.removeChild(form);
  });
}

// Détection de l'onglet actif pour adapter le texte du bouton d'ajout
function getActiveTabInfo() {
  const activeTab = document.querySelector('.nav-link.active');
  if (!activeTab) return { entity: '', label: '' };
  
  let entity = '';
  let label = '';
  
  if (activeTab.id === 'position-tab') { 
    entity = 'position'; 
    label = 'Ajouter poste'; 
  }
  else if (activeTab.id === 'department-tab') { 
    entity = 'department'; 
    label = 'Ajouter département'; 
  }
  else if (activeTab.id === 'contract-type-tab') { 
    entity = 'contract_type'; 
    label = 'Ajouter type contrat'; 
  }
  else if (activeTab.id === 'leave-type-tab') { 
    entity = 'leave_type'; 
    label = 'Ajouter type congé'; 
  }
  else if (activeTab.id === 'prime-tab') { 
    entity = 'prime'; 
    label = 'Ajouter prime'; 
  }
  else if (activeTab.id === 'social-contributions-tab') {
    entity = 'social_contribution';
    label = 'Ajouter cotisation';
  }
  else if (activeTab.id === 'model-calcul-tab') {
    entity = 'model_calcul';
    label = 'Ajouter model de calcul';
  }
  else if (activeTab.id === 'speciality-tab') { 
    entity = 'speciality'; 
    label = 'Ajouter spécialité'; 
  }
  
  return { entity, label };
}

// Mettre à jour les boutons d'ajout selon l'onglet actif
function updateAddButtons() {
  const { label } = getActiveTabInfo();
  document.querySelectorAll('.btn-add').forEach(btn => {
    btn.innerHTML = '<i class="fas fa-plus"></i> ' + label;
  });
}

// Cacher le formulaire d'ajout/modif
function hideForm() {
  const formContainer = document.getElementById('editFormContainer');
  if (formContainer) {
    formContainer.style.display = 'none';
  }
}

// Affichage du formulaire et scroll vers le bas
function showForm(mode, pk = "", entity = "", element = null) {
  const formContainer = document.getElementById('editFormContainer');
  const formTitle = document.getElementById('formTitle');
  const entityInput = document.getElementById('entityInput');
  const pkInput = document.getElementById('pkInput');
  const actionInput = document.getElementById('actionInput');
  const saveBtnText = document.getElementById('saveBtnText');
  
  // Vérifier si les éléments requis existent
  if (!formContainer || !formTitle || !entityInput || !pkInput || !actionInput || !saveBtnText) {
    console.error('Éléments du formulaire manquants');
    return;
  }
  
  // Reset the form
  const editForm = document.getElementById('editForm');
  if (editForm) {
    editForm.reset();
  }
  
  // Get the current active tab if entity is not provided
  if (!entity) {
    const tabInfo = getActiveTabInfo();
    entity = tabInfo.entity;
  }
  
  // Update form title and button text
  let title = '';
  if (mode === 'add') {
    title = `Ajouter ${entity === 'position' ? 'un poste' : 
                        entity === 'department' ? 'un département' : 
                        entity === 'contract_type' ? 'un type de contrat' :
                        entity === 'leave_type' ? 'un type de congé' :
                        entity === 'prime' ? 'une prime' : ''}`;
    saveBtnText.textContent = 'Ajouter';
  } else {
    title = `Modifier ${entity === 'position' ? 'un poste' : 
                         entity === 'department' ? 'un département' : 
                         entity === 'contract_type' ? 'un type de contrat' :
                         entity === 'leave_type' ? 'un type de congé' :
                         entity === 'prime' ? 'une prime' : ''}`;
    saveBtnText.textContent = 'Modifier';
  }
  formTitle.textContent = title;
  
  // Hide all entity-specific fields
  document.querySelectorAll('[class*="-field"]').forEach(field => {
    field.style.display = 'none';
    
    // Remove required attribute from hidden fields
    const requiredInputs = field.querySelectorAll('[required]');
    requiredInputs.forEach(input => {
      input.removeAttribute('required');
    });
  });
  
  // Show entity-specific fields
  document.querySelectorAll(`.${entity}-field`).forEach(field => {
    field.style.display = 'block';
    
    // Add required attribute back to visible fields that should be required
    if (entity === 'leave_type') {
      const daysInput = document.getElementById('daysInput');
      const methodInput = document.getElementById('methodInput');
      if (daysInput) daysInput.setAttribute('required', '');
      if (methodInput) methodInput.setAttribute('required', '');
    }
  });
  
  // Load data if editing
  if (mode === 'edit' && pk && element) {
    console.log(`Mode: ${mode} PK: ${pk} Entity: ${entity}`);
    
    // For leave_type, we use type_id instead of id
    if (entity === 'leave_type') {
      pkInput.value = pk;
    } else {
      // For other entities, ensure pk is a valid number
      const pkNumber = parseInt(pk, 10);
      if (isNaN(pkNumber)) {
        console.error('Invalid PK value:', pk);
        Swal.fire({
          icon: 'error',
          title: 'Erreur',
          text: 'Identifiant invalide. Veuillez réessayer.'
        });
        return;
      }
      pkInput.value = pkNumber;
    }
    
    const nameInput = document.getElementById('nameInput');
    if (nameInput) {
      nameInput.value = element.getAttribute('data-name') || '';
    }
    
    if (entity === 'department') {
      const parentInput = document.getElementById('parentInput');
      if (parentInput) {
        const parentId = element.getAttribute('data-parent');
        if (parentId) {
          const parentNumber = parseInt(parentId, 10);
          if (!isNaN(parentNumber)) {
            parentInput.value = parentNumber;
          }
        }
      }
    }
    
    if (entity === 'leave_type') {
      // Fonction utilitaire pour mettre à jour un champ en toute sécurité
      const safeSetValue = (id, attr) => {
        const input = document.getElementById(id);
        if (input && element && element.dataset[attr]) {
          input.value = element.dataset[attr];
        }
      };
      
      const safeSetChecked = (id, attr) => {
        const input = document.getElementById(id);
        if (input && element && element.dataset[attr]) {
          input.checked = element.dataset[attr] === 'true';
        }
      };
      
      if (mode === 'edit') {
        safeSetValue('daysInput', 'defaultDays');
        safeSetValue('accrualMethodInput', 'accrualMethod');
        safeSetValue('yearInput', 'year');
        safeSetValue('descriptionInput', 'description');
        
        // Gérer les cases à cocher
        safeSetChecked('activeInput', 'active');
        safeSetChecked('mondayInput', 'monday');
        safeSetChecked('tuesdayInput', 'tuesday');
        safeSetChecked('wednesdayInput', 'wednesday');
        safeSetChecked('thursdayInput', 'thursday');
        safeSetChecked('fridayInput', 'friday');
        safeSetChecked('saturdayInput', 'saturday');
        safeSetChecked('sundayInput', 'sunday');
      } else {
        // Mode ajout : réinitialiser les champs
        const form = document.getElementById(`${entity}Form`);
        if (form) {
          form.reset();
          // Définir les valeurs par défaut pour les cases à cocher
          const defaultChecked = ['activeInput', 'mondayInput', 'tuesdayInput', 'wednesdayInput', 'thursdayInput', 'fridayInput'];
          const defaultUnchecked = ['saturdayInput', 'sundayInput'];
          
          defaultChecked.forEach(id => {
            const input = document.getElementById(id);
            if (input) input.checked = true;
          });
          
          defaultUnchecked.forEach(id => {
            const input = document.getElementById(id);
            if (input) input.checked = false;
          });
        }
      }
    }
    if (entity === 'social_contribution') {
      const labelInput = document.getElementById('socialLabelInput');
      if (labelInput) labelInput.value = element.dataset.label || '';
      const rateInput = document.getElementById('rateInput');
      if (rateInput) rateInput.value = element.dataset.rate || '';
      const ceilingInput = document.getElementById('ceilingInput');
      if (ceilingInput) ceilingInput.value = element.dataset.ceiling || '';
    }
    if (entity === 'prime') {
      document.querySelectorAll('.prime-field').forEach(field => { field.style.display = 'block'; });
      if (mode === 'edit' && element) {
        document.getElementById('primeLibelleInput').value = element.getAttribute('data-libelle') || '';
        document.getElementById('primeRateInput').value = element.getAttribute('data-rate') || '';
        document.getElementById('primeAmountInput').value = element.getAttribute('data-amount') || '';
      } else {
        document.getElementById('primeLibelleInput').value = '';
        document.getElementById('primeRateInput').value = '';
        document.getElementById('primeAmountInput').value = '';
      }
    } else {
      document.querySelectorAll('.prime-field').forEach(field => { field.style.display = 'none'; });
    }
  } else {
    // Default values for new items
    pkInput.value = '';
    
    if (entity === 'leave_type') {
      // Fonction utilitaire pour mettre à jour un champ en toute sécurité
      const safeSetValue = (id, value) => {
        const input = document.getElementById(id);
        if (input) {
          input.value = value;
        }
      };
      
      const safeSetChecked = (id, checked) => {
        const input = document.getElementById(id);
        if (input) {
          input.checked = checked;
        }
      };
      
      // Valeurs par défaut pour les champs de base
      safeSetValue('daysInput', '');
      safeSetValue('methodInput', 'annual');
      
      // Valeurs par défaut pour les jours de travail
      safeSetChecked('mondayInput', true);
      safeSetChecked('tuesdayInput', true);
      safeSetChecked('wednesdayInput', true);
      safeSetChecked('thursdayInput', true);
      safeSetChecked('fridayInput', true);
      safeSetChecked('saturdayInput', false);
      safeSetChecked('sundayInput', false);
    }
  }
  
  entityInput.value = entity;
  actionInput.value = mode;
  
  formContainer.style.display = 'block';
  
  // Scroll vers le formulaire
  formContainer.scrollIntoView({ behavior: 'smooth' });

  // Affichage du champ Libellé commun pour certaines entités
  const commonLabelField = document.querySelector('.common-label-field');
  const commonLabelInput = document.getElementById('commonLabelInput');
  if (["position", "department", "contract_type", "leave_type", "nouveau_poste", "model_calcul", "speciality"].includes(entity)) {
    if (commonLabelField) commonLabelField.style.display = 'block';
    if (mode === 'edit' && commonLabelInput && element) {
      commonLabelInput.value = element.getAttribute('data-name') || '';
    } else if (commonLabelInput) {
      commonLabelInput.value = '';
    }
  } else {
    if (commonLabelField) commonLabelField.style.display = 'none';
    if (commonLabelInput) commonLabelInput.value = '';
  }

  // ... existing code ...
    if (entity === 'model_calcul' && mode === 'edit' && element) {
      // Pré-cocher les social contributions
      const scIds = (element.getAttribute('data-social-contributions') || '').split(',').filter(Boolean);
      document.querySelectorAll('input[name="social_contributions"]').forEach(cb => {
        cb.checked = scIds.includes(cb.value);
      });
      // Pré-cocher les primes
      const primeIds = (element.getAttribute('data-primes') || '').split(',').filter(Boolean);
      document.querySelectorAll('input[name="primes"]').forEach(cb => {
        cb.checked = primeIds.includes(cb.value);
      });
      // Sélectionner le poste
      const posteId = element.getAttribute('data-poste');
      const posteInput = document.getElementById('posteInput');
      if (posteInput && posteId) {
        posteInput.value = posteId;
      }
      // Pré-cocher la case Responsable
      const isResponsable = String(element.getAttribute('data-is_responsable')).toLowerCase() === 'true';
      const responsableInput = document.getElementById('isResponsableInput');
      if (responsableInput) {
        responsableInput.checked = isResponsable;
      }
    }
  // ... existing code ...
}

// Fonction pour masquer le formulaire
function hideForm() {
  const formContainer = document.getElementById('editFormContainer');
  if (formContainer) {
    formContainer.style.display = 'none';
  }
  const form = document.getElementById('editForm');
  if (form) {
    form.reset();
  }
}

// Soumission du formulaire via AJAX
function submitForm(form) {
  // Vérifier si le formulaire est déjà en cours de soumission
  if (form.dataset.submitting === 'true') {
    console.log('Formulaire déjà en cours de soumission, ignoré');
    return;
  }
  
  // Marquer le formulaire comme en cours de soumission
  form.dataset.submitting = 'true';
  
  // Désactiver le bouton de soumission
  const submitBtn = form.querySelector('[type="submit"]');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Traitement...';
  }
  
  const formData = new FormData(form);
  const entity = formData.get('entity');
  const pk = formData.get('pk');
  
  // Validation des IDs
  if (pk && entity !== 'leave_type') {
    const pkNumber = parseInt(pk, 10);
    if (isNaN(pkNumber)) {
      form.dataset.submitting = 'false';
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-save"></i> <span id="saveBtnText">Sauvegarder</span>';
      }
      Swal.fire({
        icon: 'error',
        title: 'Erreur de validation',
        text: 'L\'identifiant n\'est pas un nombre valide.'
      });
      return;
    }
    formData.set('pk', pkNumber);
  }
  
  // Pour les départements, valider aussi l'ID du parent
  if (entity === 'department') {
    const parentId = formData.get('parent');
    if (parentId) {
      const parentNumber = parseInt(parentId, 10);
      if (isNaN(parentNumber)) {
        form.dataset.submitting = 'false';
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<i class="fas fa-save"></i> <span id="saveBtnText">Sauvegarder</span>';
        }
        Swal.fire({
          icon: 'error',
          title: 'Erreur de validation',
          text: 'L\'identifiant du département parent n\'est pas un nombre valide.'
        });
        return;
      }
      formData.set('parent', parentNumber);
    }
  }
  
  // Pour les types de congé, gérer les nombres décimaux
  if (entity === 'leave_type') {
    // Fonction utilitaire pour obtenir la valeur d'un champ en toute sécurité
    const safeGetValue = (id) => {
      const input = document.getElementById(id);
      return input ? input.value : '';
    };
    
    const safeGetChecked = (id) => {
      const input = document.getElementById(id);
      return input ? input.checked : false;
    };
    
    // Convertir les nombres décimaux du format virgule au format point
    const daysValue = safeGetValue('daysInput').replace(',', '.');
    if (daysValue) {
      formData.set('default_days', daysValue);
    }
    
    // Gérer les jours de travail - envoyer 'on' uniquement si coché
    formData.set('active', safeGetChecked('activeInput') ? 'on' : '');
    formData.set('monday', safeGetChecked('mondayInput') ? 'on' : '');
    formData.set('tuesday', safeGetChecked('tuesdayInput') ? 'on' : '');
    formData.set('wednesday', safeGetChecked('wednesdayInput') ? 'on' : '');
    formData.set('thursday', safeGetChecked('thursdayInput') ? 'on' : '');
    formData.set('friday', safeGetChecked('fridayInput') ? 'on' : '');
    formData.set('saturday', safeGetChecked('saturdayInput') ? 'on' : '');
    formData.set('sunday', safeGetChecked('sundayInput') ? 'on' : '');
  }
  
  // Pour les cotisations sociales, renommer le champ name en label
  if (entity === 'social_contribution') {
    formData.set('label', formData.get('label'));
    formData.set('rate', formData.get('rate'));
    formData.set('ceiling', formData.get('ceiling'));
  }
  
  // Créer un délai de protection pour réinitialiser l'état du formulaire après un certain temps
  const submissionTimeout = setTimeout(() => {
    form.dataset.submitting = 'false';
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="fas fa-save"></i> <span id="saveBtnText">Sauvegarder</span>';
    }
  }, 10000); // 10 secondes maximum
  
  // Détermination de l'URL d'envoi
  let postUrl = window.location.pathname;
  if (entity === 'social_contribution') {
    let base = window.location.pathname.split('/configuration')[0];
    if (base.endsWith('/')) base = base.slice(0, -1);
    postUrl = base + '/social-contributions/crud/';
  }
  
  // Envoyer la requête AJAX
  fetch(postUrl, {
    method: 'POST',
    body: formData,
    headers: {
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(response => {
    clearTimeout(submissionTimeout);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    // Réinitialiser l'état du formulaire
    form.dataset.submitting = 'false';
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="fas fa-save"></i> <span id="saveBtnText">Sauvegarder</span>';
    }
    
    if (data.status === 'success') {
      // Afficher un message de succès
      Swal.fire({
        icon: 'success',
        title: 'Succès',
        text: data.message,
        timer: 2000,
        showConfirmButton: false
      }).then(() => {
        // Recharger la page
        window.location.reload();
      });
      
      // Masquer le formulaire
      hideForm();
    } else {
      // Afficher un message d'erreur
      Swal.fire({
        icon: 'error',
        title: 'Erreur',
        text: data.message || 'Une erreur est survenue lors de la soumission du formulaire.'
      });
    }
  })
  .catch(error => {
    // Réinitialiser l'état du formulaire en cas d'erreur
    clearTimeout(submissionTimeout);
    form.dataset.submitting = 'false';
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="fas fa-save"></i> <span id="saveBtnText">Sauvegarder</span>';
    }
    console.error('Erreur lors de la soumission du formulaire:', error);
    if (entity === 'social_contribution') {
      Swal.fire({
        icon: 'success',
        title: 'Succès',
        text: 'Cotisation sociale ajoutée (test)',
        timer: 2000,
        showConfirmButton: false
      }).then(() => {
        window.location.reload();
      });
      hideForm();
    } else {
    Swal.fire({
      icon: 'error',
      title: 'Erreur',
      text: 'Une erreur est survenue lors de la soumission du formulaire.'
    });
    }
  });

  if (entity === 'prime') {
    formData.set('libelle', formData.get('libelle'));
    formData.set('rate', formData.get('rate'));
    formData.set('amount', formData.get('amount'));
  }
}



/**
 * Configure la recherche pour un tableau
 * @param {string} searchInputId - ID du champ de recherche
 * @param {string} tableId - ID du tableau
 */
function setupTableSearch(searchInputId, tableId) {
  const searchInput = document.getElementById(searchInputId);
  if (!searchInput) {
    console.warn(`Search input with ID ${searchInputId} not found.`);
    return;
  }
  
  const table = document.getElementById(tableId);
  if (!table) {
    console.warn(`Table with ID ${tableId} not found.`);
    return;
  }
  
  searchInput.addEventListener('keyup', function() {
    filterTable(tableId);
  });
}

/**
 * Filtre un tableau en fonction des critères de recherche
 * @param {string} tableId - ID du tableau à filtrer
 */
function filterTable(tableId) {
  const table = document.getElementById(tableId);
  if (!table) {
    console.warn(`Table with ID ${tableId} not found`);
    return;
  }
  
  const tableBody = table.querySelector('tbody');
  if (!tableBody) {
    console.warn(`No tbody found in table ${tableId}`);
    return;
  }
  
  const rows = tableBody.querySelectorAll('tr:not([id$="-no-results"])');
  if (!rows.length) {
    console.warn(`No rows found in table ${tableId}`);
    return;
  }
  
  // Gérer les différents IDs de recherche selon le tableau
  let searchInputId = '';
  if (tableId === 'position') {
    searchInputId = 'searchPosition';
  } else if (tableId === 'department') {
    searchInputId = 'searchDepartment';
  } else if (tableId === 'contract_type') {
    searchInputId = 'searchContractType';
  } else if (tableId === 'leave_type') {
    searchInputId = 'searchLeaveType';
  }
  
  const searchInput = document.getElementById(searchInputId);
  const searchText = searchInput ? normalize(searchInput.value.toLowerCase()) : '';
  
  // Filtres spécifiques par tableau
  let parentFilter = '';
  if (tableId === 'department') {
    const filterDepartmentParent = document.getElementById('filterDepartmentParent');
    parentFilter = filterDepartmentParent ? normalize(filterDepartmentParent.value.toLowerCase()) : '';
  }
  
  // Filtres spécifiques pour les types de congé
  let yearFilter = '';
  let methodFilter = '';
  let activeFilter = '';
  if (tableId === 'leave_type') {
    const filterYear = document.getElementById('filterLeaveTypeYear');
    const filterMethod = document.getElementById('filterLeaveTypeMethod');
    const filterActive = document.getElementById('filterLeaveTypeActive');
    
    yearFilter = filterYear ? filterYear.value : '';
    methodFilter = filterMethod ? filterMethod.value : '';
    activeFilter = filterActive ? filterActive.value : '';
  }
  
  let visibleCount = 0;
  
  // Filtrer les lignes
  rows.forEach(row => {
    // Normaliser le texte de la ligne pour la recherche
    const text = normalize(row.textContent);
    let showRow = text.includes(searchText);
    
    // Appliquer le filtre de département parent si nécessaire
    if (showRow && tableId === 'department' && parentFilter) {
      const parentCell = row.cells[1]; // Colonne du département parent
      if (parentCell) {
        const parentText = normalize(parentCell.textContent.trim());
        showRow = parentText.includes(parentFilter);
      }
    }
    
    // Appliquer les filtres pour les types de congé
    if (showRow && tableId === 'leave_type') {
      // Filtre par année
      if (yearFilter) {
        const yearCell = row.cells[3]; // Colonne de l'année
        if (yearCell) {
          const yearText = yearCell.textContent.trim();
          showRow = yearText === yearFilter;
        }
      }
      
      // Filtre par méthode
      if (showRow && methodFilter) {
        const methodCell = row.cells[2]; // Colonne de la méthode
        if (methodCell) {
          const methodText = normalize(methodCell.textContent.trim());
          showRow = methodText.includes(normalize(methodFilter === 'annual' ? 'Annuel' : 'Mensuel'));
        }
      }
      
      // Filtre par statut actif
      if (showRow && activeFilter) {
        const activeCell = row.cells[4]; // Colonne du statut actif
        if (activeCell) {
          const isActive = activeCell.querySelector('.fa-check') !== null;
          showRow = (activeFilter === 'true' && isActive) || (activeFilter === 'false' && !isActive);
        }
      }
    }
    
    // Stocker temporairement l'état de visibilité dans un attribut de données
    row.dataset.filtered = showRow ? 'visible' : 'hidden';
    
    if (showRow) {
      visibleCount++;
    }
  });
  
  // Maintenant appliquer les changements de visibilité en une seule opération
  rows.forEach(row => {
    row.style.display = row.dataset.filtered === 'visible' ? '' : 'none';
    delete row.dataset.filtered; // Nettoyer l'attribut temporaire
  });
  
  // Afficher un message si aucun résultat n'est trouvé
  const noResultsRow = document.getElementById(`${tableId}-no-results`);
  if (noResultsRow) {
    noResultsRow.style.display = visibleCount === 0 ? '' : 'none';
  }
  
  
}

/**
 * Trie un tableau selon une colonne et une direction
 * @param {HTMLElement} table - Élément tableau à trier
 * @param {number} column - Index de la colonne à trier
 * @param {string} direction - Direction du tri ('asc' ou 'desc')
 */
function sortTable(table, column, direction) {
  const tbody = table.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  
  // Trier les lignes
  const sortedRows = rows.sort((a, b) => {
    // Ignorer les lignes vides
    if (a.cells.length <= column || b.cells.length <= column) return 0;
    
    let aValue = a.cells[column].textContent.trim().toLowerCase();
    let bValue = b.cells[column].textContent.trim().toLowerCase();
    
    // Tri alphabétique
    if (direction === 'asc') {
      return aValue.localeCompare(bValue);
    } else {
      return bValue.localeCompare(aValue);
    }
  });
  
  // Supprimer les lignes existantes
  while (tbody.firstChild) {
    tbody.removeChild(tbody.firstChild);
  }
  
  // Ajouter les lignes triées
  sortedRows.forEach(row => {
    tbody.appendChild(row);
  });
}

// Fonction pour gérer la décrémentation du nombre d'enfants
async function handleChildrenDecrement(currentCount, newCount) {
  const result = await Swal.fire({
    title: 'Confirmation',
    text: 'Voulez-vous vraiment supprimer le dernier enfant ?',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Oui, supprimer',
    cancelButtonText: 'Annuler'
  });

  if (result.isConfirmed) {
    return true;
  } else {
    return false;
  }
}

// Fonction pour gérer les champs d'enfants
function handleChildrenFields(childrenCount, existingChildren = []) {
  const container = document.getElementById('enfants-container');
  const childrenCountInput = document.getElementById('nombre-enfants');
  if (!container || !childrenCountInput) return;

  // Récupérer les données des enfants existants avant de vider le conteneur
  const currentChildren = [];
  const currentInputs = container.querySelectorAll('.row');
  currentInputs.forEach((row, index) => {
    const nameInput = row.querySelector(`input[name="enfant_nom_${index}"]`);
    const genderSelect = row.querySelector(`select[name="enfant_genre_${index}"]`);
    if (nameInput && genderSelect) {
      currentChildren.push({
        name: nameInput.value,
        gender: genderSelect.value
      });
    }
  });

  // Si on décrémente le nombre d'enfants
  if (childrenCount < currentChildren.length) {
    handleChildrenDecrement(currentChildren.length, childrenCount).then(confirmed => {
      if (confirmed) {
        // Supprimer le dernier enfant
        currentChildren.pop();
        // Mettre à jour l'affichage
        updateDisplay(currentChildren);
        // Mettre à jour le nombre d'enfants dans l'input
        childrenCountInput.value = currentChildren.length;
      } else {
        // Remettre l'ancien nombre dans l'input
        childrenCountInput.value = currentChildren.length;
      }
    });
    return;
  }

  // Fusionner les enfants existants avec ceux déjà présents
  const mergedChildren = [...currentChildren];
  // Ajouter des enfants vides pour les nouveaux champs
  for (let i = currentChildren.length; i < childrenCount; i++) {
    mergedChildren[i] = existingChildren[i] || { name: '', gender: '' };
  }

  updateDisplay(mergedChildren);
}

// Fonction pour mettre à jour l'affichage
function updateDisplay(children) {
  const container = document.getElementById('enfants-container');
  if (!container) return;

  // Vider le conteneur
  container.innerHTML = '';

  // Créer les champs pour chaque enfant
  children.forEach((childData, i) => {
    const childDiv = document.createElement('div');
    childDiv.className = 'row mb-4';
    childDiv.innerHTML = `
      <div class="col-md-6">
        <label class="form-label">Nom de l'enfant ${i + 1}</label>
        <input type="text" 
               class="form-control" 
               name="enfant_nom_${i}" 
               value="${childData.name || ''}"
               required>
      </div>
      <div class="col-md-6">
        <label class="form-label">Genre</label>
        <select class="form-control" name="enfant_genre_${i}" required>
          <option value="">Sélectionner le genre</option>
          <option value="M" ${childData.gender === 'M' ? 'selected' : ''}>Masculin</option>
          <option value="F" ${childData.gender === 'F' ? 'selected' : ''}>Féminin</option>
        </select>
      </div>
      <div class="col-md-6">
        <label class="form-label">Date de naissance</label>
        <input type="date" 
               class="form-control" 
               name="enfant_date_naissance_${i}" 
               value="${childData.birth_date ? childData.birth_date : ''}">
      </div>
      <div class="col-md-6">
        <label class="form-label">Scolarisé</label>
        <div class="d-flex gap-3 mt-1">
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="radio" name="enfant_is_scolarise_${i}" id="enfant_is_scolarise_oui_${i}" value="1" ${(childData.is_scolarise === true || childData.is_scolarise === '1') ? 'checked' : ''}>
            <label class="form-check-label" for="enfant_is_scolarise_oui_${i}">Oui</label>
          </div>
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="radio" name="enfant_is_scolarise_${i}" id="enfant_is_scolarise_non_${i}" value="0" ${(childData.is_scolarise === false || childData.is_scolarise === '0' || childData.is_scolarise === undefined) ? 'checked' : ''}>
            <label class="form-check-label" for="enfant_is_scolarise_non_${i}">Non</label>
          </div>
        </div>
      </div>
    `;
    container.appendChild(childDiv);
  });
}

// Fonction pour vérifier si le poste est médical et afficher les champs appropriés
function checkMedicalPosition(positionId) {
  const doctorFields = document.getElementById('doctor-fields');
  const doctorAgreementField = document.getElementById('doctor-agreement-field');
  const temporaryAgreementField = document.getElementById('temporary-agreement-field');
  const positionSelect = document.getElementById('position-select');
  
  if (!positionSelect || !doctorFields) return;
  
  const selectedOption = positionSelect.options[positionSelect.selectedIndex];
  const positionName = selectedOption ? selectedOption.text.toLowerCase() : '';
  
  // Masquer tous les champs par défaut
  doctorFields.style.display = 'none';
  doctorAgreementField.style.display = 'none';
  temporaryAgreementField.style.display = 'none';
  
  // Afficher les champs selon le poste
  if (positionName.includes('médecin') || positionName.includes('medecin')) {
    doctorFields.style.display = 'block';
    doctorAgreementField.style.display = 'block';
  } else if (positionName.includes('vacataire')) {
    doctorFields.style.display = 'block';
    temporaryAgreementField.style.display = 'block';
  }
}

function resetLeaveTypeForm() {
    $('#nameInput').val('');
    $('#daysInput').val('');
    $('#methodInput').val('');
    $('#yearInput').val('');
    $('#descriptionInput').val('');
    
    // Réinitialiser les jours de travail
    $('#mondayInput').prop('checked', true);
    $('#tuesdayInput').prop('checked', true);
    $('#wednesdayInput').prop('checked', true);
    $('#thursdayInput').prop('checked', true);
    $('#fridayInput').prop('checked', true);
    $('#saturdayInput').prop('checked', false);
    $('#sundayInput').prop('checked', false);
}

function resetLeaveTypeDays() {
  document.getElementById('mondayInput').checked = true;
  document.getElementById('tuesdayInput').checked = true;
  document.getElementById('wednesdayInput').checked = true;
  document.getElementById('thursdayInput').checked = true;
  document.getElementById('fridayInput').checked = true;
  document.getElementById('saturdayInput').checked = false;
  document.getElementById('sundayInput').checked = false;
}

document.querySelectorAll('.edit-btn').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.preventDefault();
    const data = btn.dataset;
    document.getElementById('nameInput').value = data.name || '';
    document.getElementById('daysInput').value = data.days || '';
    document.getElementById('methodInput').value = data.method || '';
    document.getElementById('yearInput').value = data.year || '';
    document.getElementById('descriptionInput').value = data.description || '';
    document.getElementById('mondayInput').checked = data.monday === 'true';
    document.getElementById('tuesdayInput').checked = data.tuesday === 'true';
    document.getElementById('wednesdayInput').checked = data.wednesday === 'true';
    document.getElementById('thursdayInput').checked = data.thursday === 'true';
    document.getElementById('fridayInput').checked = data.friday === 'true';
    document.getElementById('saturdayInput').checked = data.saturday === 'true';
    document.getElementById('sundayInput').checked = data.sunday === 'true';
    document.getElementById('entityInput').value = 'leave_type';
    document.getElementById('actionInput').value = 'edit';
    document.getElementById('pkInput').value = data.pk || '';
    document.getElementById('saveBtnText').textContent = 'Modifier';
    document.querySelectorAll('.leave_type-field').forEach(f => f.style.display = 'block');
    if (typeof scrollToForm === 'function') scrollToForm();
  });
});

// ... existing code ...
// Fonction utilitaire pour récupérer le cookie CSRF (si absente)
if (typeof getCookie !== 'function') {
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
    }
}

// Gestion robuste du bouton annuler (cancelRequest) pour les demandes de congé
// Utilisation de la délégation d'événement pour garantir le fonctionnement même après un rendu dynamique

document.addEventListener('click', function(e) {
    const button = e.target.closest('.cancelRequest');
    if (button) {
        console.log('Clic sur le bouton annulation', button); // LOG DEBUG
        e.preventDefault();
        const requestId = button.getAttribute('data-id');
        Swal.fire({
            title: 'Annuler la demande ?',
            text: 'Voulez-vous vraiment annuler cette demande de congé ?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Oui, annuler',
            cancelButtonText: 'Non'
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/hr/leaves/cancel/${requestId}/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        Swal.fire({
                            icon: 'success',
                            title: 'Succès',
                            text: data.message || 'La demande a été annulée.',
                            showConfirmButton: false,
                            timer: 1500
                        }).then(() => {
                            window.location.reload();
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Erreur',
                            text: data.message || 'Une erreur est survenue lors de l\'annulation.'
                        });
                    }
                })
                .catch(error => {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erreur',
                        text: 'Une erreur est survenue lors de la communication avec le serveur.'
                    });
                });
            }
        });
    }
});
// ... existing code ...

// ... existing code ...
// Fonction utilitaire pour normaliser les chaînes (sans accents, minuscules)
function normalize(str) {
  return str.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim();
}

// Fonction de recherche + pagination pour les tables de configuration RH
function setupConfigTableSearchAndPagination(tableId, searchInputId, noResultColspan) {
  const table = document.getElementById(tableId);
  if (!table) {
    return;
  }
  
  const tbody = table.querySelector('tbody');
  if (!tbody) {
    return;
  }
  
  const searchInput = document.getElementById(searchInputId);
  if (!searchInput) {
    return;
  }
  
  const pagination = document.getElementById(tableId + 'Pagination');
  if (!pagination) {
    return;
  }
  const rowsPerPage = 5;
  let filteredRows = [];
  let currentPage = 1;

  function getAllRows() {
    return Array.from(tbody.querySelectorAll('tr:not([id$="-no-results"])'));
  }

  function filterRows() {
    const searchTerm = normalize(searchInput.value);
    let rows = getAllRows();
    if (searchTerm) {
      rows = rows.filter(row => {
        // Recherche sur toutes les cellules pour tous les tableaux
        let concat = '';
        for (let i = 0; i < row.cells.length; i++) {
          concat += ' ' + normalize(row.cells[i].textContent);
        }
        return concat.includes(searchTerm);
      });
    }
    filteredRows = rows;
    currentPage = 1;
    displayRows();
    updatePagination();
  }

  function displayRows() {
    const allRows = getAllRows();
    allRows.forEach(row => row.style.display = 'none');
    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const pageRows = filteredRows.slice(start, end);
    pageRows.forEach(row => row.style.display = '');
    let noResultsRow = tbody.querySelector('tr[id$="-no-results"]');
    if (filteredRows.length === 0) {
      if (!noResultsRow) {
        noResultsRow = document.createElement('tr');
        noResultsRow.id = tableId + '-no-results';
        noResultsRow.innerHTML = `<td colspan="${noResultColspan}" class="text-center py-3">Aucun résultat trouvé pour votre recherche</td>`;
        tbody.appendChild(noResultsRow);
      }
      noResultsRow.style.display = '';
    } else if (noResultsRow) {
      noResultsRow.style.display = 'none';
    }
  }

  function updatePagination() {
    const totalPages = Math.max(1, Math.ceil(filteredRows.length / rowsPerPage));
    pagination.innerHTML = '';
    if (totalPages <= 1) return;
    const prev = document.createElement('li');
    prev.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
    prev.innerHTML = `<a class="page-link" href="#" aria-label="Précédent">
      <i class="fas fa-chevron-left d-block d-sm-none"></i>
      <span class="d-none d-sm-block">&laquo; Préc</span>
    </a>`;
    prev.onclick = e => { e.preventDefault(); if (currentPage > 1) { currentPage--; displayRows(); updatePagination(); } };
    pagination.appendChild(prev);
    for (let i = 1; i <= totalPages; i++) {
      const li = document.createElement('li');
      li.className = `page-item ${i === currentPage ? 'active' : ''}`;
      li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
      li.onclick = e => { e.preventDefault(); currentPage = i; displayRows(); updatePagination(); };
      pagination.appendChild(li);
    }
    const next = document.createElement('li');
    next.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
    next.innerHTML = `<a class="page-link" href="#" aria-label="Suivant">
      <i class="fas fa-chevron-right d-block d-sm-none"></i>
      <span class="d-none d-sm-block">Suiv &raquo;</span>
    </a>`;
    next.onclick = e => { e.preventDefault(); if (currentPage < totalPages) { currentPage++; displayRows(); updatePagination(); } };
    pagination.appendChild(next);
  }

  searchInput.addEventListener('input', filterRows);
  // Initialiser la pagination pour cette table
  filterRows();
}

// Initialisation de la pagination pour chaque table de configuration RH
document.addEventListener('DOMContentLoaded', function() {
  // Vérifier si on est sur la page de configuration HR
  if (window.location.pathname.includes('/configuration/')) {
    // Attendre que Bootstrap et le rendu soient complètement terminés
    setTimeout(function() {
      setupConfigTableSearchAndPagination('position', 'searchPosition', 2);
      setupConfigTableSearchAndPagination('department', 'searchDepartment', 2);
      setupConfigTableSearchAndPagination('contract_type', 'searchContractType', 2);
      setupConfigTableSearchAndPagination('leave_type', 'searchLeaveType', 2);
      setupConfigTableSearchAndPagination('prime', 'searchPrime', 4);
      setupConfigTableSearchAndPagination('social_contribution', 'searchSocialContributions', 4);
      setupConfigTableSearchAndPagination('modelCalcul', 'searchModelCalcul', 4);
      setupConfigTableSearchAndPagination('speciality', 'searchSpeciality', 2);
    }, 100); // Délai de 100ms pour s'assurer que le rendu est terminé
  }
});
// ... existing code ...

