/*
 * Manager Approval Page JS
 * Handles:
 * 1. Table search / filter / sort / pagination
 * 2. Manager decision (approve / refuse) with SweetAlert
 * 3. View details popup via SweetAlert
 */

// Flag to use new Bootstrap modal implementation (disables legacy SweetAlert handlers)
window.USE_BOOTSTRAP_MANAGER = true;


// ---- UTILITIES ----
function normalize(str) {
  return str.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim();
}

// ---- TABLE HELPERS ----
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

  function filterRows() {
    const searchTerm = searchInput ? normalize(searchInput.value) : '';
    const selectedStatus = statusFilter ? statusFilter.value : '';
    const selectedType = typeFilter ? typeFilter.value : '';

    filteredRows = getAllRows().filter(row => {
      let match = true;
      if (searchTerm) {
        let concat = '';
        row.cells.forEach ? row.cells.forEach(c => concat += ' ' + normalize(c.textContent)) : '';
        match = match && concat.includes(searchTerm);
      }
      if (selectedStatus) {
        match = match && row.dataset.status === selectedStatus;
      }
      if (selectedType) {
        match = match && row.cells[2].textContent === selectedType;
      }
      return match;
    });

    if (currentSortColumn !== -1) {
      sortRows(currentSortColumn);
      return;
    }
    currentPage = 1;
    displayRows();
    updatePagination();
  }

  function displayRows() {
    getAllRows().forEach(r => r.style.display = 'none');
    const start = (currentPage - 1) * rowsPerPage;
    filteredRows.slice(start, start + rowsPerPage).forEach(r => r.style.display = '');

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

  function updateSortIcons() {
    table.querySelectorAll('th.sortable').forEach((h, idx) => {
      const icon = h.querySelector('.fas');
      if (!icon) return;
      if (idx === currentSortColumn) {
        icon.className = currentSortDirection === 'asc' ? 'fas fa-sort-up ms-1' : 'fas fa-sort-down ms-1';
      } else {
        icon.className = 'fas fa-sort ms-1 text-muted';
      }
    });
  }

  function parseDate(str) {
    const [d, m, y] = str.split('/');
    return new Date(`${y}-${m}-${d}`);
  }

  function sortRows(columnIndex) {
    if (currentSortColumn === columnIndex) {
      currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      currentSortColumn = columnIndex;
      currentSortDirection = 'asc';
    }

    filteredRows.sort((a, b) => {
      let aVal = a.cells[columnIndex].textContent.trim();
      let bVal = b.cells[columnIndex].textContent.trim();

      if (columnIndex === 3 || columnIndex === 4) {
        aVal = parseDate(aVal);
        bVal = parseDate(bVal);
      } else if (columnIndex === 5 || columnIndex === 6) {
        aVal = parseInt(aVal.match(/\d+/)?.[0] || '0', 10);
        bVal = parseInt(bVal.match(/\d+/)?.[0] || '0', 10);
      }

      if (currentSortDirection === 'asc') return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
      return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
    });

    updateSortIcons();
    currentPage = 1;
    displayRows();
    updatePagination();
  }

  function updatePagination() {
    const totalPages = Math.max(1, Math.ceil(filteredRows.length / rowsPerPage));
    pagination.innerHTML = '';
    if (totalPages <= 1) return;

    const prev = document.createElement('li');
    prev.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
    prev.innerHTML = `<a class="page-link" href="#" aria-label="Précédent"><i class="fas fa-chevron-left d-block d-sm-none"></i><span class="d-none d-sm-block">&laquo; Préc</span></a>`;
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
    next.innerHTML = `<a class="page-link" href="#" aria-label="Suivant"><i class="fas fa-chevron-right d-block d-sm-none"></i><span class="d-none d-sm-block">Suiv &raquo;</span></a>`;
    next.onclick = e => { e.preventDefault(); if (currentPage < totalPages) { currentPage++; displayRows(); updatePagination(); } };
    pagination.appendChild(next);
  }

  // Bind events
  if (searchInput) searchInput.addEventListener('input', filterRows);
  if (statusFilter) statusFilter.addEventListener('change', filterRows);
  if (typeFilter) typeFilter.addEventListener('change', filterRows);

  table.querySelectorAll('th.sortable').forEach((h, idx) => {
    h.addEventListener('click', () => sortRows(idx));
  });

  // Init
  filterRows();
}

// ---- MAIN LOGIC ----

// OLD SYSTEM COMPLETELY DISABLED
/*
document.addEventListener('DOMContentLoaded', () => {
  // Manager decision buttons
  const approvalTable = document.getElementById('approvalTable');
  if (approvalTable && !window.USE_BOOTSTRAP_MANAGER) {
    approvalTable.addEventListener('click', async (e) => {
      const btn = e.target.closest('.managerDecision');
      if (!btn) return;

      const requestId = btn.dataset.id;
      const decision = btn.dataset.decision;

      const { value: comments } = await Swal.fire({
        title: decision === 'approved' ? 'Approuver ?' : 'Refuser ?',
        input: 'textarea',
        inputLabel: 'Commentaire (optionnel)',
        inputPlaceholder: 'Ajoutez un commentaire...',
        showCancelButton: true,
        confirmButtonText: 'Confirmer',
        cancelButtonText: 'Annuler'
      });

      if (comments === undefined) return;

      try {
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        const res = await fetch(`/hr/leave-request-manager-decision/${requestId}/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
          },
          body: new URLSearchParams({ decision, comments: comments || '' })
        });
        if (!res.ok) {
          throw new Error(`Erreur HTTP ${res.status}`);
        }
        const data = await res.json();
        if (data.status === 'success') {
          Swal.fire({ icon: 'success', title: 'Succès', text: data.message, timer: 1500, showConfirmButton: false })
              .then(() => window.location.reload());
        } else {
          Swal.fire('Erreur', data.message, 'error');
        }
      } catch (err) {
        console.error(err);
        Swal.fire('Erreur', 'Une erreur est survenue', 'error');
      }
    });

    // View details buttons (legacy SweetAlert disabled via flag)
    if (!window.USE_BOOTSTRAP_MANAGER) {
      approvalTable.addEventListener('click', async (e) => {
        const btn = e.target.closest('.viewDetails');
        if (!btn) return;
        const reqId = btn.dataset.id;
        try {
          const resp = await fetch(`/hr/leaves/get/${reqId}/`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
          if (!resp.ok) {
            throw new Error(`Erreur HTTP ${resp.status}`);
          }
          const data = await resp.json();
          if (data.status === 'success') {
            const r = data.request;
            Swal.fire({
              title: 'Détails demande',
              html: `<strong>Employé:</strong> ${r.employee_name}<br>`+
                    `<strong>Type:</strong> ${r.leave_type}<br>`+
                    `<strong>Dates:</strong> Du ${r.start_date} au ${r.end_date}<br>`+
                    `<strong>Durée:</strong> ${r.duration} jour(s)<br>`+
                    `<strong>Commentaires:</strong> ${r.notes || 'N/A'}`,
              confirmButtonText: 'Fermer'
            });
          } else {
            Swal.fire('Erreur', data.message, 'error');
          }
        } catch (err) {
          console.error(err);
          Swal.fire('Erreur', 'Impossible de récupérer les détails', 'error');
        }
      });
    }
  }

  // Initialize table utilities
  setupApprovalTableSearchAndPagination();
});
*/

// ---------------- MANAGER APPROVAL MODAL IMPLEMENTATION ----------------
// Prevent conflicts and ensure only our modals work
if (!window.MANAGER_APPROVAL_INITIALIZED) {
  window.MANAGER_APPROVAL_INITIALIZED = true;
  
  document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    
    console.log('Initializing Manager Approval modals - SINGLE TIME');
    
    // Disable any existing modal event listeners that might conflict
    document.querySelectorAll('.managerDecision, .viewDetails').forEach(element => {
      element.style.pointerEvents = 'none';
      setTimeout(() => {
        element.style.pointerEvents = 'auto';
      }, 100);
    });
    
    // Initialize table utilities first
    setupApprovalTableSearchAndPagination();

    // Variables pour SweetAlert
    let currentRequestId = null;
    let currentDecision = null;



    // Gestionnaires pour la décision du chef de service avec SweetAlert
    document.querySelectorAll('.managerDecision').forEach(button => {
      button.addEventListener('click', async function(e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        
        currentRequestId = this.dataset.id;
        currentDecision = this.dataset.decision; // 'approved' or 'refused'
        
        const actionText = currentDecision === 'approved' ? 'approuver' : 'refuser';
        
        const { value: comments } = await Swal.fire({
          title: `${actionText.charAt(0).toUpperCase() + actionText.slice(1)} cette demande ?`,
          input: 'textarea',
          inputLabel: 'Commentaire (optionnel)',
          inputPlaceholder: 'Ajoutez un commentaire...',
          showCancelButton: true,
          confirmButtonText: 'Confirmer',
          cancelButtonText: 'Annuler',
          confirmButtonColor: currentDecision === 'approved' ? '#28a745' : '#dc3545'
        });

        if (comments !== undefined) {
          // Traiter la décision
          await submitDecision(comments);
        }
      });
    });

    // Gestionnaire pour les boutons de détails avec SweetAlert
    document.querySelectorAll('.viewDetails').forEach(button => {
      button.addEventListener('click', async function(e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        
        const requestId = this.dataset.id;
        currentRequestId = requestId;
        
        // Get data from the table row
        const row = this.closest('tr');
        const cells = row ? row.querySelectorAll('td') : [];
        
        const getCleanText = (cell) => {
          if (!cell) return '';
          const badge = cell.querySelector('.badge');
          return badge ? badge.textContent.trim() : cell.textContent.trim();
        };
        
        // Create details HTML
        const detailsHtml = `
          <div class="text-left">
            <p><strong>Employé:</strong> ${getCleanText(cells[1]) || 'Non défini'}</p>
            <p><strong>Type:</strong> ${getCleanText(cells[2]) || 'Non défini'}</p>
            <p><strong>Dates:</strong> Du ${getCleanText(cells[3])} au ${getCleanText(cells[4])}</p>
            <p><strong>Durée:</strong> ${getCleanText(cells[5]) || 'Non défini'}</p>
            <p><strong>Enfants:</strong> ${getCleanText(cells[6]) || '0'}</p>
            <p><strong>Situation:</strong> ${getCleanText(cells[7]) || 'Non défini'}</p>
          </div>
        `;
        
        const result = await Swal.fire({
          title: 'Détails de la demande',
          html: detailsHtml,
          showCancelButton: true,
          showDenyButton: true,
          confirmButtonText: '<i class="fas fa-check"></i> Approuver',
          denyButtonText: '<i class="fas fa-times"></i> Refuser',
          cancelButtonText: 'Fermer',
          confirmButtonColor: '#28a745',
          denyButtonColor: '#dc3545',
          width: '600px'
        });

        if (result.isConfirmed) {
          // Approuver
          currentDecision = 'approved';
          const { value: comments } = await Swal.fire({
            title: 'Approuver cette demande ?',
            input: 'textarea',
            inputLabel: 'Commentaire (optionnel)',
            inputPlaceholder: 'Ajoutez un commentaire...',
            showCancelButton: true,
            confirmButtonText: 'Confirmer',
            cancelButtonText: 'Annuler',
            confirmButtonColor: '#28a745'
          });
          
          if (comments !== undefined) {
            await submitDecision(comments);
          }
        } else if (result.isDenied) {
          // Refuser
          currentDecision = 'refused';
          const { value: comments } = await Swal.fire({
            title: 'Refuser cette demande ?',
            input: 'textarea',
            inputLabel: 'Commentaire (optionnel)',
            inputPlaceholder: 'Ajoutez un commentaire...',
            showCancelButton: true,
            confirmButtonText: 'Confirmer',
            cancelButtonText: 'Annuler',
            confirmButtonColor: '#dc3545'
          });
          
          if (comments !== undefined) {
            await submitDecision(comments);
          }
        }
      });
    });

    // Fonction pour soumettre la décision
    async function submitDecision(comments) {
      try {
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        const res = await fetch(`/hr/leave-request-manager-decision/${currentRequestId}/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: new URLSearchParams({ decision: currentDecision, comments: comments || '' })
        });
        
        // Vérifier si la réponse est OK
        if (!res.ok) {
          if (res.status === 403) {
            throw new Error('Accès non autorisé - vous n\'avez pas les permissions nécessaires');
          }
          throw new Error(`Erreur HTTP ${res.status}`);
        }
        
        // Vérifier le type de contenu avant de parser
        const contentType = res.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          throw new Error('Réponse non-JSON reçue du serveur');
        }
        
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
          Swal.fire('Erreur', data.message || 'Une erreur est survenue', 'error');
        }
      } catch (err) {
        console.error('Erreur lors de la soumission:', err);
        Swal.fire('Erreur', err.message || 'Une erreur est survenue lors du traitement de votre demande', 'error');
      }
    }
    
  });
}
