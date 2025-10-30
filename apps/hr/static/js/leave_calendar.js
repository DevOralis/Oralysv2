document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    if (!calendarEl) {
        console.error('Calendar element not found');
        return;
    }
    
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: window.innerWidth < 768 ? 'dayGridWeek' : 'dayGridMonth',
        locale: 'fr',
        firstDay: 1,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,dayGridWeek'
        },
        buttonText: {
            today: "Aujourd'hui",
            month: 'Mois',
            week: 'Semaine'
        },
        dayHeaderFormat: { weekday: 'short' },
        events: function(info, successCallback, failureCallback) {
            fetch('/hr/leaves/get_calendar_events/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                const events = [];
                const leavesByDate = {};
                
                // Ajouter les jours fériés
                if (data.holidays) {
                    data.holidays.forEach(holiday => {
                        events.push({
                            title: holiday.name,
                            start: holiday.date,
                            allDay: true,
                            className: 'holiday-event',
                            display: 'background'
                        });
                    });
                }
                
                // Regrouper les employés par date
                if (data.leaves) {
                    data.leaves.forEach(leave => {
                        let start = new Date(leave.start_date);
                        let end = new Date(leave.end_date);
                        end.setDate(end.getDate() + 1);
                        
                        let currentDate = new Date(start);
                        while (currentDate < end) {
                            const weekday = currentDate.getDay();
                            const isWorkingDay = leave.working_days[weekday];
                            
                            if (isWorkingDay) {
                                const dateStr = currentDate.toISOString().split('T')[0];
                                
                                if (!leavesByDate[dateStr]) {
                                    leavesByDate[dateStr] = new Set();
                                }
                                
                                leavesByDate[dateStr].add(leave.employee_name);
                            }
                            
                            currentDate.setDate(currentDate.getDate() + 1);
                        }
                    });
                }
                
                // Créer un événement par date
                for (const [dateStr, employees] of Object.entries(leavesByDate)) {
                    events.push({
                        title: '•',
                        start: dateStr,
                        allDay: true,
                        className: 'leave-dot',
                        extendedProps: {
                            employees: Array.from(employees)
                        }
                    });
                }
                
                successCallback(events);
            })
            .catch(error => {
                console.error('Erreur lors de la récupération des événements:', error);
                failureCallback(error);
            });
        },
        eventContent: function(arg) {
            if (arg.event.classNames.includes('holiday-event')) {
                return;
            }
            
            const dot = document.createElement('div');
            dot.className = 'leave-dot';
            
            const employees = arg.event.extendedProps.employees;
            dot.title = `${employees.length} employé(s) en congé`;
            
            return { domNodes: [dot] };
        },
        eventClick: function(info) {
            if (info.event.classNames.includes('leave-dot')) {
                const employees = info.event.extendedProps.employees;
                let html = '<div style="max-height: 300px; overflow-y: auto;">';
                
                employees.forEach(employeeName => {
                    html += `<div class="employee-name">${employeeName}</div>`;
                });
                
                html += '</div>';
                
                Swal.fire({
                    title: 'Employés en congé',
                    html: html,
                    icon: 'info',
                    confirmButtonColor: '#1976d2',
                    confirmButtonText: 'Fermer',
                    width: '300px'
                });
            }
        },
        dayCellDidMount: function(arg) {
            if (arg.date.getDay() === 0 || arg.date.getDay() === 6) {
                arg.el.classList.add('fc-day-weekend');
            }
        },
        windowResize: function(view) {
            if (window.innerWidth < 768) {
                calendar.changeView('dayGridWeek');
            } else {
                calendar.changeView('dayGridMonth');
            }
        }
    });
    
    calendar.render();
    
    // Gestionnaire pour les boutons de détails
    const leaveDetailsModal = document.getElementById('leaveDetailsModal') ? 
        new bootstrap.Modal(document.getElementById('leaveDetailsModal')) : null;
        
    // Ajouter un gestionnaire d'événements pour l'événement de fermeture du modal
    if (leaveDetailsModal && document.getElementById('leaveDetailsModal')) {
        document.getElementById('leaveDetailsModal').addEventListener('hidden.bs.modal', function () {
            // Réinitialiser le contenu du modal pour éviter les problèmes d'affichage
            const modalBody = this.querySelector('.modal-body');
            if (modalBody) {
                modalBody.scrollTop = 0;
            }
            
            // S'assurer que le body retrouve son style normal
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            
            // Supprimer toutes les classes modal de Bootstrap du body
            document.body.classList.remove('modal-open');
            
            // Supprimer tous les backdrops qui pourraient rester
            const backdrops = document.querySelectorAll('.modal-backdrop');
            backdrops.forEach(backdrop => backdrop.remove());
            
            // Forcer la suppression de tout style inline sur le body
            document.body.removeAttribute('style');
        });
    }
        
    if (document.querySelectorAll('.viewLeaveDetails').length > 0) {
        document.querySelectorAll('.viewLeaveDetails').forEach(button => {
            button.addEventListener('click', function() {
                const requestId = this.getAttribute('data-id');
                
                // Nettoyer les éléments précédents
                if (document.getElementById('certificateLink')) {
                    const certificateParent = document.getElementById('certificateLink').parentNode;
                    const fileNameSpans = certificateParent.querySelectorAll('span.text-muted');
                    fileNameSpans.forEach(span => span.remove());
                }
                
                // Afficher un indicateur de chargement
                Swal.fire({
                    title: 'Chargement...',
                    text: 'Récupération des détails du congé',
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    didOpen: () => {
                        Swal.showLoading();
                    }
                });
                
                // Récupérer les détails du congé
                fetch(`/hr/leave-request-details/${requestId}/`)
                    .then(response => {
                        // Vérifier si la réponse est OK avant de parser en JSON
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        // Fermer l'indicateur de chargement
                        Swal.close();
                        
                        // Remplir les informations de l'employé
                        if (document.getElementById('employeeName')) {
                            document.getElementById('employeeName').textContent = data.request.employee_name || '-';
                        }
                        if (document.getElementById('employeeDepartment')) {
                            document.getElementById('employeeDepartment').textContent = data.request.employee_department || '-';
                        }
                        if (document.getElementById('employeePosition')) {
                            document.getElementById('employeePosition').textContent = data.request.employee_position || '-';
                        }
                        
                        // Remplir les informations du congé
                        if (document.getElementById('leaveType')) {
                            document.getElementById('leaveType').textContent = data.request.leave_type || '-';
                        }
                        if (document.getElementById('leavePeriod')) {
                            document.getElementById('leavePeriod').textContent = `${data.request.start_date} au ${data.request.end_date}`;
                        }
                        if (document.getElementById('leaveDuration')) {
                            document.getElementById('leaveDuration').textContent = data.request.duration || '-';
                        }
                        
                        // Définir le statut avec la bonne classe
                        if (document.getElementById('leaveStatus')) {
                            const statusElement = document.getElementById('leaveStatus');
                            statusElement.textContent = getStatusLabel(data.request.status);
                            statusElement.className = 'badge ' + getStatusClass(data.request.status);
                        }
                        
                        // Remplir les informations d'approbation
                        if (data.request.approval) {
                            if (document.getElementById('approvedBy')) {
                                document.getElementById('approvedBy').textContent = data.request.approval.employee_name || '-';
                            }
                            if (document.getElementById('approvalDate')) {
                                document.getElementById('approvalDate').textContent = data.request.approval.decision_date || '-';
                            }
                            if (document.getElementById('approvalComments')) {
                                document.getElementById('approvalComments').textContent = data.request.approval.comments || 'Aucun commentaire';
                            }
                        } else {
                            if (document.getElementById('approvedBy')) {
                                document.getElementById('approvedBy').textContent = '-';
                            }
                            if (document.getElementById('approvalDate')) {
                                document.getElementById('approvalDate').textContent = '-';
                            }
                            if (document.getElementById('approvalComments')) {
                                document.getElementById('approvalComments').textContent = 'Aucun commentaire';
                            }
                        }
                        
                        // Afficher la décision avec la bonne classe
                        if (document.getElementById('approvalDecision')) {
                            const decisionElement = document.getElementById('approvalDecision');
                            if (data.request.status === 'approved') {
                                decisionElement.textContent = 'Approuvé';
                                decisionElement.className = 'badge bg-success';
                            } else if (data.request.status === 'refused') {
                                decisionElement.textContent = 'Refusé';
                                decisionElement.className = 'badge bg-danger';
                            } else if (data.request.status === 'canceled') {
                                decisionElement.textContent = 'Annulé';
                                decisionElement.className = 'badge bg-warning';
                            } else {
                                decisionElement.textContent = 'Non traité';
                                decisionElement.className = 'badge bg-warning';
                            }
                        }
                        
                        // Remplir les notes de l'employé
                        if (document.getElementById('employeeNotes')) {
                            document.getElementById('employeeNotes').textContent = data.request.notes || 'Aucune note';
                        }
                        
                        // Gérer l'affichage du certificat médical
                        const certificateLink = document.getElementById('certificateLink');
                        const noCertificate = document.getElementById('noCertificate');
                        
                        const certificatePreview = document.getElementById('certificatePreview');
                        const certificateImage = document.getElementById('certificateImage');
                        
                        if (data.request.certificate_url && certificateLink && noCertificate) {
                            certificateLink.href = data.request.certificate_url;
                            certificateLink.classList.remove('d-none');
                            noCertificate.classList.add('d-none');
                            
                            // Ajouter le nom du fichier si disponible
                            if (data.request.certificate_name) {
                                const fileNameSpan = document.createElement('span');
                                fileNameSpan.className = 'd-block mt-2 text-muted';
                                fileNameSpan.textContent = data.request.certificate_name;
                                certificateLink.parentNode.appendChild(fileNameSpan);
                                
                                // Vérifier si c'est une image pour afficher un aperçu
                                const fileExtension = data.request.certificate_name.split('.').pop().toLowerCase();
                                if (['jpg', 'jpeg', 'png', 'gif'].includes(fileExtension) && certificateImage && certificatePreview) {
                                    certificateImage.src = data.request.certificate_url;
                                    certificatePreview.classList.remove('d-none');
                                    
                                    // Ajouter un événement pour agrandir l'image au clic
                                    certificateImage.onclick = function() {
                                        Swal.fire({
                                            imageUrl: data.request.certificate_url,
                                            imageAlt: 'Certificat médical',
                                            width: '80%',
                                            confirmButtonText: 'Fermer'
                                        });
                                    };
                                } else if (certificatePreview) {
                                    certificatePreview.classList.add('d-none');
                                }
                            }
                        } else if (certificateLink && noCertificate) {
                            certificateLink.classList.add('d-none');
                            noCertificate.classList.remove('d-none');
                            if (certificatePreview) {
                                certificatePreview.classList.add('d-none');
                            }
                        }
                        
                        // Afficher le modal
                        if (leaveDetailsModal) {
                            leaveDetailsModal.show();
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        Swal.fire({
                            icon: 'error',
                            title: 'Erreur',
                            text: 'Impossible de charger les détails de la demande. Veuillez réessayer.'
                        });
                    });
            });
        });
    }
    
    // Fonction pour obtenir le libellé du statut
    function getStatusLabel(status) {
        const statusLabels = {
            'draft': 'Brouillon',
            'submitted': 'Soumis',
            'approved': 'Approuvé',
            'refused': 'Refusé',
            'canceled': 'Annulé'
        };
        return statusLabels[status] || status;
    }
    
    // Fonction pour obtenir la classe CSS du statut
    function getStatusClass(status) {
        const statusClasses = {
            'draft': 'bg-secondary',
            'submitted': 'bg-info',
            'approved': 'bg-success',
            'refused': 'bg-danger',
            'canceled': 'bg-warning'
        };
        return statusClasses[status] || 'bg-secondary';
    }

    // Fonction utilitaire pour normaliser les chaînes (sans accents, minuscules)
    function normalize(str) {
        return str.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim();
    }

    // Variables globales pour le tri et la pagination de l'historique
    let historyCurrentSortColumn = -1;
    let historyCurrentSortDirection = 'asc';
    let historyAllRows = [];
    let historyFilteredRows = [];
    let historyCurrentPage = 1;
    const historyRowsPerPage = 5;

    // Pagination + recherche + tri pour la table d'historique du calendrier
    function setupCalendarHistoryTableSearchAndPagination() {
        const table = document.getElementById('calendarHistoryTable');
        if (!table) return;
        
        const tbody = table.querySelector('tbody');
        if (!tbody) return;
        
        const searchInput = document.getElementById('searchCalendarHistory');
        const pagination = document.getElementById('calendarHistoryPagination');
        if (!pagination) return;

        function getAllHistoryRows() {
            return Array.from(tbody.querySelectorAll('tr:not(.empty-row)'));
        }

        function filterHistoryRows() {
            const searchTerm = searchInput ? normalize(searchInput.value) : '';
            const statusFilter = document.getElementById('historyStatusFilter')?.value || '';
            
            let rows = historyAllRows;
            
            // Filtrer par recherche
            if (searchTerm) {
                rows = rows.filter(row => {
                    let concat = '';
                    for (let i = 0; i < row.cells.length; i++) {
                        concat += ' ' + normalize(row.cells[i].textContent);
                    }
                    return concat.includes(searchTerm);
                });
            }
            
            // Filtrer par statut
            if (statusFilter) {
                rows = rows.filter(row => {
                    const statusCell = row.cells[8]; // Colonne statut
                    if (!statusCell) return false;
                    const statusText = normalize(statusCell.textContent);
                    return statusText.includes(normalize(statusFilter));
                });
            }
            
            historyFilteredRows = rows;
            historyCurrentPage = 1;
            displayHistoryRows();
            updateHistoryPagination();
        }

        function displayHistoryRows() {
            // Cacher toutes les lignes
            historyAllRows.forEach(row => row.style.display = 'none');
            
            const start = (historyCurrentPage - 1) * historyRowsPerPage;
            const end = start + historyRowsPerPage;
            const pageRows = historyFilteredRows.slice(start, end);
            
            // Afficher les lignes de la page courante
            pageRows.forEach(row => row.style.display = '');
            
            // Gérer le message "aucun résultat"
            let noResultsRow = tbody.querySelector('.empty-row');
            if (historyFilteredRows.length === 0) {
                if (!noResultsRow) {
                    noResultsRow = document.createElement('tr');
                    noResultsRow.className = 'empty-row';
                    noResultsRow.innerHTML = `<td colspan="10" class="text-center py-3">Aucun résultat trouvé pour votre recherche</td>`;
                    tbody.appendChild(noResultsRow);
                }
                noResultsRow.style.display = '';
            } else if (noResultsRow) {
                noResultsRow.style.display = 'none';
            }
            
        }

        function updateHistoryPagination() {
            const totalPages = Math.max(1, Math.ceil(historyFilteredRows.length / historyRowsPerPage));
            pagination.innerHTML = '';
            if (totalPages <= 1) return;
            
            // Bouton Précédent avec format responsive
            const prev = document.createElement('li');
            prev.className = `page-item ${historyCurrentPage === 1 ? 'disabled' : ''}`;
            prev.innerHTML = `<a class="page-link" href="#" aria-label="Précédent">
              <i class="fas fa-chevron-left d-block d-sm-none"></i>
              <span class="d-none d-sm-block">&laquo; Préc</span>
            </a>`;
            prev.onclick = e => { e.preventDefault(); if (historyCurrentPage > 1) { historyCurrentPage--; displayHistoryRows(); updateHistoryPagination(); } };
            pagination.appendChild(prev);
            
            // Numéros de page
            for (let i = 1; i <= totalPages; i++) {
              const li = document.createElement('li');
              li.className = `page-item ${i === historyCurrentPage ? 'active' : ''}`;
              li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
              li.onclick = e => { e.preventDefault(); historyCurrentPage = i; displayHistoryRows(); updateHistoryPagination(); };
              pagination.appendChild(li);
            }
            
            // Bouton Suivant avec format responsive
            const next = document.createElement('li');
            next.className = `page-item ${historyCurrentPage === totalPages ? 'disabled' : ''}`;
            next.innerHTML = `<a class="page-link" href="#" aria-label="Suivant">
              <i class="fas fa-chevron-right d-block d-sm-none"></i>
              <span class="d-none d-sm-block">Suiv &raquo;</span>
            </a>`;
            next.onclick = e => { e.preventDefault(); if (historyCurrentPage < totalPages) { historyCurrentPage++; displayHistoryRows(); updateHistoryPagination(); } };
            pagination.appendChild(next);
        }

        // Fonction de tri
        function sortHistoryTable(columnIndex) {
            if (historyCurrentSortColumn === columnIndex) {
                historyCurrentSortDirection = historyCurrentSortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                historyCurrentSortColumn = columnIndex;
                historyCurrentSortDirection = 'asc';
            }
            
            // Mettre à jour les icônes de tri
            updateHistorySortIcons();
            
            // Trier les lignes filtrées
            historyFilteredRows.sort((a, b) => {
                let aVal = a.cells[columnIndex]?.textContent?.trim() || '';
                let bVal = b.cells[columnIndex]?.textContent?.trim() || '';
                
                // Tri spécial pour les dates (colonnes 3 et 4)
                if (columnIndex === 3 || columnIndex === 4) {
                    const aDate = parseDate(aVal);
                    const bDate = parseDate(bVal);
                    return historyCurrentSortDirection === 'asc' ? aDate - bDate : bDate - aDate;
                }
                
                // Tri spécial pour la durée (colonne 5)
                if (columnIndex === 5) {
                    const aDuration = parseInt(aVal.match(/\d+/)?.[0] || '0');
                    const bDuration = parseInt(bVal.match(/\d+/)?.[0] || '0');
                    return historyCurrentSortDirection === 'asc' ? aDuration - bDuration : bDuration - aDuration;
                }
                
                // Tri spécial pour le nombre d'enfants (colonne 6)
                if (columnIndex === 6) {
                    const aChildren = parseInt(aVal) || 0;
                    const bChildren = parseInt(bVal) || 0;
                    return historyCurrentSortDirection === 'asc' ? aChildren - bChildren : bChildren - aChildren;
                }
                
                // Tri alphabétique pour les autres colonnes
                aVal = aVal.toLowerCase();
                bVal = bVal.toLowerCase();
                
                if (historyCurrentSortDirection === 'asc') {
                    return aVal.localeCompare(bVal);
                } else {
                    return bVal.localeCompare(aVal);
                }
            });
            
            historyCurrentPage = 1;
            displayHistoryRows();
            updateHistoryPagination();
        }
        
        function updateHistorySortIcons() {
            const headers = table.querySelectorAll('th[data-sortable]');
            headers.forEach((header, index) => {
                const icon = header.querySelector('.sort-icon');
                const columnIndex = parseInt(header.getAttribute('data-sortable'));
                
                if (columnIndex === historyCurrentSortColumn) {
                    icon.className = historyCurrentSortDirection === 'asc' ? 'fas fa-sort-up sort-icon text-primary' : 'fas fa-sort-down sort-icon text-primary';
                } else {
                    icon.className = 'fas fa-sort sort-icon text-muted';
                }
            });
        }
        
        function parseDate(dateStr) {
            // Format attendu: dd/mm/yyyy
            const parts = dateStr.match(/\d{2}\/\d{2}\/\d{4}/);
            if (parts) {
                const [day, month, year] = parts[0].split('/');
                return new Date(year, month - 1, day);
            }
            return new Date(0);
        }
        
        // Ajouter les gestionnaires d'événements pour le tri
        const sortableHeaders = table.querySelectorAll('th[data-sortable]');
        sortableHeaders.forEach(header => {
            header.addEventListener('click', () => {
                const columnIndex = parseInt(header.getAttribute('data-sortable'));
                sortHistoryTable(columnIndex);
            });
        });
        
        // Gestionnaires d'événements pour la recherche et les filtres
        if (searchInput) {
            searchInput.addEventListener('input', filterHistoryRows);
        }
        
        const statusFilter = document.getElementById('historyStatusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', filterHistoryRows);
        }
        
        // Initialisation
        historyAllRows = getAllHistoryRows();
        historyFilteredRows = [...historyAllRows];
        displayHistoryRows();
        updateHistoryPagination();
    }

    // Initialiser la pagination avec un léger délai pour s'assurer que le DOM est prêt
    setTimeout(function() {
        if (document.getElementById('calendarHistoryTable') && document.getElementById('searchCalendarHistory')) {
            setupCalendarHistoryTableSearchAndPagination();
        }
    }, 100);

    // AJAX filtrage pour l'historique - pas de rechargement de page
    const searchInput = document.getElementById('searchCalendarHistory');
    const statusFilter = document.getElementById('historyStatusFilter');
    const tableBlock = document.getElementById('calendarHistoryTableBlock');
    
    function fetchHistoryAJAX() {
        const searchValue = searchInput ? searchInput.value : '';
        const statusValue = statusFilter ? statusFilter.value : '';
        const params = new URLSearchParams();
        
        if (searchValue) params.append('search', searchValue);
        if (statusValue) params.append('status', statusValue);
        
        const queryString = params.toString();
        const url = queryString ? `?${queryString}` : window.location.pathname;
        
        fetch(url, { 
            headers: { 'X-Requested-With': 'XMLHttpRequest' } 
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            // Le template partiel retourne directement le contenu sans wrapper
            // On remplace directement le contenu du tableBlock
            if (tableBlock) {
                tableBlock.innerHTML = html;
                
                // Re-initialiser la pagination et la recherche après AJAX
                setTimeout(function() {
                    if (typeof setupCalendarHistoryTableSearchAndPagination === 'function') {
                        setupCalendarHistoryTableSearchAndPagination();
                    }
                    
                    // Re-binder les filtres
                    bindHistoryFilters();
                }, 50);
            }
        })
        .catch(error => {
            // Afficher un message d'erreur à l'utilisateur si nécessaire
            console.error('Error fetching history:', error);
        });
    }
    
    function bindHistoryFilters() {
        const searchInput = document.getElementById('searchCalendarHistory');
        const statusFilter = document.getElementById('historyStatusFilter');
        
        // Supprimer les anciens event listeners pour éviter les doublons
        if (searchInput) {
            searchInput.removeEventListener('input', fetchHistoryAJAX);
            searchInput.addEventListener('input', fetchHistoryAJAX);
        }
        
        if (statusFilter) {
            statusFilter.removeEventListener('change', fetchHistoryAJAX);
            statusFilter.addEventListener('change', fetchHistoryAJAX);
        }
    }
    
    // Initialiser les filtres au chargement de la page
    bindHistoryFilters();

    // Gestion du changement automatique du bouton Exporter/Importer
    const exportImportBtn = document.getElementById('export-import-btn');
    const exportImportIcon = document.getElementById('export-import-icon');
    const exportImportText = document.getElementById('export-import-text');
    const selectAllCheckbox = document.getElementById('selectAllHistory');
    
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
