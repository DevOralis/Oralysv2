// Fonction utilitaire pour normaliser les chaînes (sans accents, minuscules)
function normalize(str) {
  return str.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim();
}

// Pagination + recherche + filtres + tri pour la table d'approbation
function setupApprovalTableSearchAndPagination() {
  const table = document.getElementById('approvalTable');
  if (!table) return;
  
  const tbody = table.querySelector('tbody');
  if (!tbody) return;
  
  const searchInput = document.getElementById('searchApproval');
  const statusFilter = document.getElementById('filterStatus');
  const typeFilter = document.getElementById('filterType');
  const pagination = document.getElementById('approvalPagination');
  const rowsPerPage = 5;
  let filteredRows = [];
  let currentPage = 1;
  let currentSortColumn = -1;
  let currentSortDirection = 'asc';

  function getAllRows() {
    return Array.from(tbody.querySelectorAll('tr:not(.empty-row)'));
  }

  // Fonction de tri sur toute la liste
  function sortRows(columnIndex) {
    if (currentSortColumn === columnIndex) {
      currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      currentSortColumn = columnIndex;
      currentSortDirection = 'asc';
    }
    
    // Trier toutes les lignes filtrées
    filteredRows.sort((a, b) => {
      let aValue = a.cells[columnIndex].textContent.trim();
      let bValue = b.cells[columnIndex].textContent.trim();
      
      // Traitement spécial pour les dates
      if (columnIndex === 3 || columnIndex === 4) { // Dates début/fin
        aValue = new Date(aValue.split('/').reverse().join('-'));
        bValue = new Date(bValue.split('/').reverse().join('-'));
      }
      // Traitement spécial pour la durée (extraire le nombre)
      else if (columnIndex === 5) {
        aValue = parseInt(aValue.match(/\d+/)?.[0] || '0');
        bValue = parseInt(bValue.match(/\d+/)?.[0] || '0');
      }
      // Traitement spécial pour le nombre d'enfants
      else if (columnIndex === 6) {
        aValue = parseInt(aValue) || 0;
        bValue = parseInt(bValue) || 0;
      }
      
      if (currentSortDirection === 'asc') {
        return aValue > bValue ? 1 : aValue < bValue ? -1 : 0;
      } else {
        return aValue < bValue ? 1 : aValue > bValue ? -1 : 0;
      }
    });
    
    // Mettre à jour les icônes de tri
    updateSortIcons();
    
    // Retourner à la première page et afficher
    currentPage = 1;
    displayRows();
    updatePagination();
  }
  
  // Mettre à jour les icônes de tri dans les en-têtes
  function updateSortIcons() {
    const headers = table.querySelectorAll('thead th');
    headers.forEach((header, index) => {
      const icon = header.querySelector('.sort-icon');
      if (icon) {
        if (index === currentSortColumn) {
          icon.className = `fas fa-sort-${currentSortDirection === 'asc' ? 'up' : 'down'} sort-icon ms-1`;
        } else {
          icon.className = 'fas fa-sort sort-icon ms-1';
        }
      }
    });
  }

  function filterRows() {
    const searchTerm = searchInput ? normalize(searchInput.value) : '';
    const selectedStatus = statusFilter ? statusFilter.value : '';
    const selectedType = typeFilter ? typeFilter.value : '';
    let rows = getAllRows();
    rows = rows.filter(row => {
      let match = true;
      if (searchTerm) {
        let concat = '';
        for (let i = 0; i < row.cells.length; i++) {
          concat += ' ' + normalize(row.cells[i].textContent);
        }
        match = match && concat.includes(searchTerm);
      }
      if (selectedStatus) {
        match = match && (!selectedStatus || row.dataset.status === selectedStatus);
      }
      if (selectedType) {
        match = match && row.cells[1].textContent === selectedType;
      }
      return match;
    });
    filteredRows = rows;
    
    // Réappliquer le tri si une colonne est sélectionnée
    if (currentSortColumn !== -1) {
      sortRows(currentSortColumn);
      return; // sortRows() appelle déjà displayRows() et updatePagination()
    }
    
    currentPage = 1;
    displayRows();
    updatePagination();
  }

  function displayRows() {
    getAllRows().forEach(row => row.style.display = 'none');
    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const pageRows = filteredRows.slice(start, end);
    pageRows.forEach(row => row.style.display = '');
    let noResultsRow = tbody.querySelector('.empty-row');
    if (filteredRows.length === 0) {
      if (!noResultsRow) {
        noResultsRow = document.createElement('tr');
        noResultsRow.className = 'empty-row';
        noResultsRow.innerHTML = `<td colspan="8" class="text-center py-3">Aucun résultat trouvé pour votre recherche</td>`;
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
    
    // Bouton Précédent avec format responsive
    const prev = document.createElement('li');
    prev.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
    prev.innerHTML = `<a class="page-link" href="#" aria-label="Précédent">
      <i class="fas fa-chevron-left d-block d-sm-none"></i>
      <span class="d-none d-sm-block">&laquo; Préc</span>
    </a>`;
    prev.onclick = e => { e.preventDefault(); if (currentPage > 1) { currentPage--; displayRows(); updatePagination(); } };
    pagination.appendChild(prev);
    
    // Numéros de page
    for (let i = 1; i <= totalPages; i++) {
      const li = document.createElement('li');
      li.className = `page-item ${i === currentPage ? 'active' : ''}`;
      li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
      li.onclick = e => { e.preventDefault(); currentPage = i; displayRows(); updatePagination(); };
      pagination.appendChild(li);
    }
    
    // Bouton Suivant avec format responsive
    const next = document.createElement('li');
    next.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
    next.innerHTML = `<a class="page-link" href="#" aria-label="Suivant">
      <i class="fas fa-chevron-right d-block d-sm-none"></i>
      <span class="d-none d-sm-block">Suiv &raquo;</span>
    </a>`;
    next.onclick = e => { e.preventDefault(); if (currentPage < totalPages) { currentPage++; displayRows(); updatePagination(); } };
    pagination.appendChild(next);
  }

  // Ajouter les gestionnaires de tri sur les en-têtes cliquables
  const sortableHeaders = table.querySelectorAll('thead th[data-sortable]');
  sortableHeaders.forEach((header, index) => {
    header.style.cursor = 'pointer';
    header.addEventListener('click', () => {
      const columnIndex = parseInt(header.dataset.sortable);
      sortRows(columnIndex);
    });
    
    // Les icônes de tri sont maintenant incluses dans le HTML
    // Aucune action nécessaire ici
  });

  if (searchInput) {
    searchInput.addEventListener('input', filterRows);
  }
  if (statusFilter) {
    statusFilter.addEventListener('change', filterRows);
  }
  if (typeFilter) {
    typeFilter.addEventListener('change', filterRows);
  }
  filteredRows = getAllRows();
  displayRows();
  updatePagination();
}

document.addEventListener('DOMContentLoaded', function() {
  // Variables globales
  let currentRequestId = null;
  let currentAction = null;
  const confirmationModalElem = document.getElementById('confirmationModal');
  const confirmationModal = confirmationModalElem ? new bootstrap.Modal(confirmationModalElem) : null;
  const detailsModalElem = document.getElementById('detailsModal');
  const detailsModal = detailsModalElem ? new bootstrap.Modal(detailsModalElem) : null;
  
  // Gestionnaire pour le formulaire de création de demande de congé
  const hrLeaveRequestForm = document.getElementById('hrLeaveRequestForm');
  const startDateInput = document.getElementById('startDate');
  const endDateInput = document.getElementById('endDate');
  const durationInput = document.getElementById('duration');

  // Gérer la soumission du formulaire
  if (hrLeaveRequestForm) {
    hrLeaveRequestForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const formData = new FormData(this);
      
      // Ajout du jeton CSRF si manquant
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
      if (csrfToken && !formData.has('csrfmiddlewaretoken')) {
        formData.append('csrfmiddlewaretoken', csrfToken.value);
      }
      
      fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrfToken.value
        }
      })
      .then(response => {
        // Vérifier si la réponse est OK avant de parser en JSON
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        if (data.status === 'success') {
          Swal.fire({
            icon: 'success',
            title: 'Succès',
            text: data.message,
            showConfirmButton: false,
            timer: 1500,
            willClose: () => {
              window.location.reload();
            }
          });
        } else {
          Swal.fire({
            icon: 'error',
            title: 'Erreur',
            text: data.message
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

  // Initialiser les dates avec la date du jour
  const today = new Date().toISOString().split('T')[0];
  if (startDateInput) startDateInput.value = today;
  if (endDateInput) endDateInput.value = today;

  // Mettre à jour la durée quand les dates changent
  function updateDuration() {
    if (startDateInput && endDateInput && durationInput &&
        startDateInput.value && endDateInput.value) {
      const start = new Date(startDateInput.value);
      const end = new Date(endDateInput.value);
      const diffTime = Math.abs(end - start);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
      durationInput.value = diffDays;
    }
  }

  if (startDateInput) startDateInput.addEventListener('change', updateDuration);
  if (endDateInput) endDateInput.addEventListener('change', updateDuration);

  // Gestionnaires pour les boutons d'action
  document.querySelectorAll('.approveRequest').forEach(button => {
    button.addEventListener('click', function() {
      currentRequestId = this.dataset.id;
      currentAction = 'approve';
      document.getElementById('actionType').textContent = 'approuver';
      confirmationModal.show();
    });
  });
  
  document.querySelectorAll('.refuseRequest').forEach(button => {
    button.addEventListener('click', function() {
      currentRequestId = this.dataset.id;
      currentAction = 'refuse';
      document.getElementById('actionType').textContent = 'refuser';
      confirmationModal.show();
    });
  });
  
  // Préparation du modal pour la décision du chef de service
  const managerDecisionModalElem = document.getElementById('managerDecisionModal');
  const managerDecisionModal = managerDecisionModalElem ? new bootstrap.Modal(managerDecisionModalElem) : null;
  let managerCurrentRequestId = null;
  let managerCurrentDecision = null;

  // Gestionnaires pour la décision du chef de service
  document.querySelectorAll('.managerDecision').forEach(button => {
    button.addEventListener('click', function() {
      managerCurrentRequestId = this.dataset.id;
      managerCurrentDecision = this.dataset.decision; // 'approved' or 'refused'
      if (managerDecisionModalElem) {
        const actionText = managerCurrentDecision === 'approved' ? 'approuver' : 'refuser';
        managerDecisionModalElem.querySelector('#managerActionType').textContent = actionText;
        managerDecisionModalElem.querySelector('#managerComments').value = '';
        managerDecisionModal.show();
      }
    });
  });

  // Confirmation bouton du modal décision chef
  const confirmManagerBtn = document.getElementById('confirmManagerAction');
  if (confirmManagerBtn) {
    confirmManagerBtn.addEventListener('click', async function () {
      const comments = document.getElementById('managerComments').value;
      const csrfTokenElem = document.querySelector('input[name="csrfmiddlewaretoken"]');
      if (!csrfTokenElem) {
        Swal.fire('Erreur', 'Jeton CSRF manquant', 'error');
        return;
      }
      try {
        const res = await fetch(`/hr/leave-request-manager-decision/${managerCurrentRequestId}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfTokenElem.value,
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: new URLSearchParams({
            decision: managerCurrentDecision,
            comments: comments || ''
          })
        });
        const data = await res.json();
        managerDecisionModal.hide();
        if (data.status === 'success') {
          Swal.fire({
            icon: 'success',
            title: 'Succès',
            text: data.message,
            timer: 1500,
            showConfirmButton: false
          }).then(() => window.location.reload());
        } else {
          Swal.fire('Erreur', data.message, 'error');
        }
      } catch (err) {
        console.error(err);
        Swal.fire('Erreur', 'Une erreur est survenue', 'error');
      }
    });
  }

  // FIN gestion décision chef (modal Bootstrap)
  /*


      const { value: text } = await Swal.fire({
        title: decision === 'approved' ? 'Approuver ?' : 'Refuser ?',
        input: 'textarea',
        inputLabel: 'Commentaire (optionnel)',
        inputPlaceholder: 'Ajoutez un commentaire...',
        inputAttributes: {
          'aria-label': 'Commentaire'
        },
        showCancelButton: true,
        confirmButtonText: 'Confirmer',
        cancelButtonText: 'Annuler',
        inputValidator: (value) => null
      });

      if (text === undefined) return; // Annulé

      try {
        const csrfTokenElem = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (!csrfTokenElem) {
          Swal.fire('Erreur', 'Jeton CSRF manquant', 'error');
          return;
        }
        const res = await fetch(`/hr/leave-request-manager-decision/${requestId}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfTokenElem.value,
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: new URLSearchParams({
            decision: decision,
            comments: text || ''
          })
        });
        const data = await res.json();
        if (data.status === 'success') {
          Swal.fire({
            icon: 'success',
            title: 'Succès',
            text: data.message,
            timer: 1500,
            showConfirmButton: false
          }).then(() => window.location.reload());
        } else {
          Swal.fire('Erreur', data.message, 'error');
        }
      } catch (err) {
        console.error(err);
        Swal.fire('Erreur', 'Une erreur est survenue', 'error');
      }
    });
  });

  */
  
  // Gestionnaire pour le bouton de confirmation
  const confirmActionBtn = document.getElementById('confirmAction');
  if (confirmActionBtn) {
    confirmActionBtn.addEventListener('click', function() {
      const comments = document.getElementById('comments').value;
      
      // Vérifier que currentRequestId et currentAction sont définis
      if (!currentRequestId || !currentAction) {
        Swal.fire({
          icon: 'error',
          title: 'Erreur',
          text: 'Impossible de traiter la demande. Veuillez réessayer.'
        });
        return;
      }
      
      const url = `/hr/leave-request-${currentAction}/${currentRequestId}/`;
      
      // Récupérer le jeton CSRF
      const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
      if (!csrfTokenElement) {
        Swal.fire({
          icon: 'error',
          title: 'Erreur',
          text: 'Jeton de sécurité manquant. Veuillez recharger la page.'
        });
        return;
      }
      
      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrfTokenElement.value
        },
        body: `comments=${encodeURIComponent(comments)}`
      })
      .then(response => {
        // Vérifier si la réponse est OK avant de parser en JSON
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        confirmationModal.hide();
        if (data.status === 'success') {
          Swal.fire({
            icon: 'success',
            title: 'Succès',
            text: data.message,
            showConfirmButton: false,
            timer: 1500,
            willClose: () => {
              window.location.reload();
            }
          });
        } else {
          Swal.fire({
            icon: 'error',
            title: 'Erreur',
            text: data.message
          });
        }
      })
      .catch(error => {
        console.error('Error:', error);
        Swal.fire({
          icon: 'error',
          title: 'Erreur',
          text: 'Une erreur est survenue lors du traitement de la demande.'
        });
      });
    });
  }

  // Gestionnaire pour les boutons de détails
  document.querySelectorAll('.viewDetails').forEach(button => {
    button.addEventListener('click', function() {
      const requestId = this.dataset.id;
      currentRequestId = requestId;
      fetch(`/hr/leave-request-details/${requestId}/`)
        .then(response => {
          // Vérifier si la réponse est OK avant de parser en JSON
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          document.getElementById('detailEmployee').textContent = data.request.employee_name;
          document.getElementById('detailType').textContent = data.request.leave_type;
          document.getElementById('detailDates').textContent = `${data.request.start_date} au ${data.request.end_date}`;
          document.getElementById('detailDuration').textContent = `${data.request.duration} jour(s)`;
          document.getElementById('detailRequestDate').textContent = data.request.request_date;
          document.getElementById('detailNotes').textContent = data.request.notes;
          
          const certificateContainer = document.getElementById('certificateContainer');
          if (data.request.certificate_url) {
            certificateContainer.style.display = 'block';
            document.getElementById('detailCertificate').href = data.request.certificate_url;
          } else {
            certificateContainer.style.display = 'none';
          }
          
          detailsModal.show();
        })
        .catch(error => {
          console.error('Error:', error);
          Swal.fire({
            icon: 'error',
            title: 'Erreur',
            text: 'Impossible de charger les détails de la demande. Veuillez vérifier l\'URL et réessayer.'
          });
        });
    });
  });

  // Gestionnaires pour les boutons d'action dans le modal de détails
  const detailApproveBtn = document.getElementById('detailApprove');
  if (detailApproveBtn) {
    detailApproveBtn.addEventListener('click', function() {
      detailsModal.hide();
      currentAction = 'approve';
      document.getElementById('actionType').textContent = 'approuver';
      confirmationModal.show();
    });
  }

  const detailRefuseBtn = document.getElementById('detailRefuse');
  if (detailRefuseBtn) {
    detailRefuseBtn.addEventListener('click', function() {
      detailsModal.hide();
      currentAction = 'refuse';
      document.getElementById('actionType').textContent = 'refuser';
      confirmationModal.show();
    });
  }

  // Gestionnaire pour les boutons "Voir détails"
  document.querySelectorAll('.viewDetails').forEach(button => {
    button.addEventListener('click', function() {
      const requestId = this.dataset.id;
      currentRequestId = requestId;
      
      // Récupérer les détails de la demande de congé (qui contient déjà toutes les infos nécessaires)
      fetch(`/hr/leave-request-details/${requestId}/`)
        .then(response => response.json())
        .then(data => {
          if (data.status === 'success') {
            const request = data.request;
            
            // Remplir les informations de l'employé (déjà dans la réponse)
            document.getElementById('detailEmployee').textContent = request.employee_name || 'Non défini';
            document.getElementById('detailDepartment').textContent = request.employee_department || 'Non défini';
            
            // Remplir les informations du congé
            document.getElementById('detailType').textContent = request.leave_type || 'Non défini';
            document.getElementById('detailDates').textContent = `Du ${request.start_date} au ${request.end_date}`;
            document.getElementById('detailDuration').textContent = request.duration + ' jour(s)' || 'Non défini';
            document.getElementById('detailRequestDate').textContent = request.request_date || 'Non défini';
            document.getElementById('detailNotes').textContent = request.notes || 'Aucune note';
            
            // Gérer le document joint
            const certificateContainer = document.getElementById('certificateContainer');
            const certificateLink = document.getElementById('detailCertificate');
            
            if (request.certificate_url) {
              certificateContainer.style.display = 'block';
              certificateLink.href = request.certificate_url;
              certificateLink.textContent = request.certificate_name || 'Voir le document';
            } else {
              certificateContainer.style.display = 'none';
            }
            
            // Pour les infos manquantes (enfants, situation familiale), récupérer du tableau
            const row = this.closest('tr');
            const cells = row.querySelectorAll('td');
            
            // Récupérer enfants et situation familiale depuis le tableau
            document.getElementById('detailChildrenCount').textContent = cells[6]?.textContent.trim() || '0';
            document.getElementById('detailMaritalStatus').textContent = cells[7]?.textContent.trim() || 'Non défini';
          } else {
            // En cas d'erreur, essayer de récupérer les données du tableau
            const row = this.closest('tr');
            const cells = row.querySelectorAll('td');
            
            // Extraire les informations visibles du tableau (ajuster les index selon la structure)
            document.getElementById('detailEmployee').textContent = cells[1]?.textContent.trim() || 'Non défini';
            document.getElementById('detailType').textContent = cells[2]?.textContent.trim() || 'Non défini';
            document.getElementById('detailDuration').textContent = cells[5]?.textContent.trim() || 'Non défini';
            document.getElementById('detailChildrenCount').textContent = cells[6]?.textContent.trim() || '0';
            document.getElementById('detailMaritalStatus').textContent = cells[7]?.textContent.trim() || 'Non défini';
            document.getElementById('detailDepartment').textContent = 'Non disponible';
            document.getElementById('detailRequestDate').textContent = 'Non disponible';
            document.getElementById('detailNotes').textContent = 'Non disponible';
            document.getElementById('certificateContainer').style.display = 'none';
          }
        })
        .catch(error => {
          console.error('Erreur lors de la récupération des détails:', error);
          // Fallback: récupérer les données visibles du tableau
          const row = this.closest('tr');
          const cells = row.querySelectorAll('td');
          
          document.getElementById('detailEmployee').textContent = cells[1]?.textContent.trim() || 'Non défini';
          document.getElementById('detailType').textContent = cells[2]?.textContent.trim() || 'Non défini';
          document.getElementById('detailDuration').textContent = cells[5]?.textContent.trim() || 'Non défini';
          document.getElementById('detailChildrenCount').textContent = cells[6]?.textContent.trim() || '0';
          document.getElementById('detailMaritalStatus').textContent = cells[7]?.textContent.trim() || 'Non défini';
          document.getElementById('detailDepartment').textContent = 'Non disponible';
          document.getElementById('detailRequestDate').textContent = 'Non disponible';
          document.getElementById('detailNotes').textContent = 'Non disponible';
          document.getElementById('certificateContainer').style.display = 'none';
        });
      
      // Afficher le modal
      detailsModal.show();
    });
  });
  
  // Initialisation de la pagination
  if (document.getElementById('approvalTable') && document.getElementById('searchApproval')) {
    setupApprovalTableSearchAndPagination();
  }

  const newLeaveRequestCollapse = document.getElementById('newLeaveRequest');
  if (newLeaveRequestCollapse) {
    newLeaveRequestCollapse.addEventListener('shown.bs.collapse', function () {
      this.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  // Gestion du changement automatique du bouton Exporter/Importer
  const exportImportBtn = document.getElementById('export-import-btn');
  const exportImportIcon = document.getElementById('export-import-icon');
  const exportImportText = document.getElementById('export-import-text');
  const selectAllCheckbox = document.getElementById('selectAll');
  
  function updateExportImportButton() {
      const checkedBoxes = document.querySelectorAll('.row-check:checked');
      const hasCheckedItems = checkedBoxes.length > 0;
      
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
  
  // Event listener pour la case "Sélectionner tout"
  if (selectAllCheckbox) {
      selectAllCheckbox.addEventListener('change', function() {
          const rowCheckboxes = document.querySelectorAll('.row-check');
          rowCheckboxes.forEach(checkbox => {
              checkbox.checked = this.checked;
          });
          updateExportImportButton();
      });
  }
  
  // Event listeners pour les cases individuelles
  document.addEventListener('change', function(e) {
      if (e.target.classList.contains('row-check')) {
          updateExportImportButton();
          
          // Mettre à jour la case "Sélectionner tout"
          const allCheckboxes = document.querySelectorAll('.row-check');
          const checkedCheckboxes = document.querySelectorAll('.row-check:checked');
          
          if (selectAllCheckbox) {
              selectAllCheckbox.checked = allCheckboxes.length === checkedCheckboxes.length;
              selectAllCheckbox.indeterminate = checkedCheckboxes.length > 0 && checkedCheckboxes.length < allCheckboxes.length;
          }
      }
  });
  
  // Initialiser l'état du bouton au chargement
  updateExportImportButton();
});
