// Fonction utilitaire pour CSRF, accessible globalement
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

document.addEventListener('DOMContentLoaded', function() {
    // Vérifier si nous sommes sur la page des employés
    const tableBody = document.querySelector('#tableEmploye tbody');
    if (!tableBody) {
        return;
    }
    
    // Configuration
    const itemsPerPage = 5;
    let currentPage = 1;
    let filteredEmployees = [];
    
    // Éléments DOM
    const searchInput = document.getElementById('searchEmploye');
    const filterPoste = document.getElementById('filterPoste');
    const pagination = document.getElementById('employePagination');
    
    // Récupérer tous les employés du tableau
    function getAllEmployees() {
        const rows = Array.from(tableBody.querySelectorAll('tr:not(.no-results)'));
        return rows.map(row => ({
            element: row,
            name: (row.cells[1] && row.cells[1].textContent) ? row.cells[1].textContent.toLowerCase() : '',
            position: (row.cells[2] && row.cells[2].textContent) ? row.cells[2].textContent.toLowerCase() : '',
            department: (row.cells[3] && row.cells[3].textContent) ? row.cells[3].textContent.toLowerCase() : '',
            contract: (row.cells[4] && row.cells[4].textContent) ? row.cells[4].textContent.toLowerCase() : ''
        }));
    }
    
    // Filtrer les employés
    function filterEmployees() {
        const searchTerm = searchInput ? (searchInput.value.toLowerCase() || '') : '';
        const poste = filterPoste ? (filterPoste.value.toLowerCase() || '') : '';
        
        let filtered = getAllEmployees();
        
        // Appliquer les filtres
        if (searchTerm) {
            filtered = filtered.filter(emp => 
                emp.name.includes(searchTerm) ||
                emp.position.includes(searchTerm) ||
                emp.department.includes(searchTerm)
            );
        }
        
        if (poste) filtered = filtered.filter(emp => emp.position === poste);
        
        filteredEmployees = filtered;
        currentPage = 1;
        displayEmployees();
        updatePagination();
    }
    
    // Afficher les employés de la page courante
    function displayEmployees() {
        // Toujours utiliser la pagination - afficher seulement les employés de la page courante
        const start = (currentPage - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const pageEmployees = filteredEmployees.slice(start, end);
        
        // Cacher toutes les lignes
        const allRows = tableBody.querySelectorAll('tr');
        allRows.forEach(row => {
            row.style.display = 'none';
        });
        
        // Afficher les lignes de la page courante
        pageEmployees.forEach(emp => {
            emp.element.style.display = '';
            // Afficher aussi la ligne de détails si elle existe
            const employeeId = emp.element.querySelector('.delete-employee-btn')?.getAttribute('data-id');
            if (employeeId) {
                const detailRow = document.getElementById('details-' + employeeId);
                if (detailRow) {
                    detailRow.style.display = '';
                }
            }
        });
        
        // Afficher message si aucun résultat
        const noResultsRow = tableBody.querySelector('.no-results');
        if (pageEmployees.length === 0) {
            if (!noResultsRow) {
                const tr = document.createElement('tr');
                tr.className = 'no-results';
                tr.innerHTML = '<td colspan="6" class="text-center">Aucun résultat trouvé</td>';
                tableBody.appendChild(tr);
            } else {
                noResultsRow.style.display = '';
            }
        } else if (noResultsRow) {
            noResultsRow.style.display = 'none';
        }
    }
    
    // Mettre à jour la pagination
    function updatePagination() {
        const totalPages = Math.ceil(filteredEmployees.length / itemsPerPage);
        
        // Effacer la pagination existante (sauf les boutons précédent et suivant)
        const pageItems = pagination.querySelectorAll('.page-item:not(:first-child):not(:last-child)');
        pageItems.forEach(item => item.remove());
        
        // Générer dynamiquement les numéros de page
        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement('li');
            li.className = `page-item ${i === currentPage ? 'active' : ''}`;
            li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
            li.onclick = (e) => {
                e.preventDefault();
                currentPage = i;
                displayEmployees();
                updatePagination();
            };
            
            // Insérer avant le bouton suivant
            const nextButton = pagination.querySelector('.page-item:last-child');
            if (nextButton) {
                pagination.insertBefore(li, nextButton);
            } else {
                pagination.appendChild(li);
            }
        }
        
        // Mettre à jour les boutons précédent et suivant
        const firstPrevButton = pagination.querySelector('.page-item:first-child');
        if (firstPrevButton) {
            firstPrevButton.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
            if (currentPage > 1 && firstPrevButton.querySelector('a')) {
                firstPrevButton.querySelector('a').onclick = (e) => {
                    e.preventDefault();
                    currentPage--;
                    displayEmployees();
                    updatePagination();
                };
            }
        }
        
        const lastNextButton = pagination.querySelector('.page-item:last-child');
        if (lastNextButton) {
            lastNextButton.className = `page-item ${currentPage === totalPages || totalPages === 0 ? 'disabled' : ''}`;
            if (currentPage < totalPages && lastNextButton.querySelector('a')) {
                lastNextButton.querySelector('a').onclick = (e) => {
                    e.preventDefault();
                    currentPage++;
                    displayEmployees();
                    updatePagination();
                };
            }
        }
    }
    
    // Event listeners pour les filtres
    if (searchInput) {
        searchInput.addEventListener('input', filterEmployees);
    }
    if (filterPoste) {
        filterPoste.addEventListener('change', filterEmployees);
    }
    
    // Initialisation
    filteredEmployees = getAllEmployees();
    displayEmployees();
    updatePagination();

    // Gestion du formulaire d'employé avec SweetAlert
    const employeeForm = document.querySelector('form[action*="add_employee"]');
    if (employeeForm) {
        employeeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Créer un objet FormData à partir du formulaire
            const formData = new FormData(this);
            
            // Afficher un indicateur de chargement
            Swal.fire({
                title: 'Traitement en cours...',
                html: 'Veuillez patienter pendant que nous traitons votre demande.',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
            
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

    // Gestion du bouton "Voir détails"
    document.querySelectorAll('.view-details-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            const employeeId = btn.getAttribute('data-employee-id');
            const modalContent = document.getElementById('employeeDetailsContent');
            
            // Afficher le spinner de chargement
            modalContent.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Chargement...</span>
                    </div>
                    <p class="mt-2">Chargement des détails...</p>
                </div>
            `;
            
            // Charger les détails de l'employé
            fetch(`/hr/employee/${employeeId}/details/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const employee = data.employee;
                    console.log('Données employé reçues:', employee);
                    console.log('Nombre d\'enfants reçu:', employee.children_count);
                    modalContent.innerHTML = `
                        <div class="row">
                            ${employee.photo_url ? `
                            <div class="col-12 text-center mb-3">
                                <img src="${employee.photo_url}" alt="Photo de ${employee.full_name}" 
                                     class="rounded-circle" style="width: 120px; height: 120px; object-fit: cover; border: 3px solid #007bff;">
                            </div>
                            ` : ''}
                            
                            <div class="col-12">
                                <div class="row g-3">
                                    <!-- INFORMATIONS PERSONNELLES -->
                                    <div class="col-12"><h5 class="text-primary border-bottom pb-2"><i class="fas fa-user me-2"></i>Informations Personnelles</h5></div>
                                    
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Nom complet :</label>
                                        <p class="form-control-plaintext fs-6">${employee.full_name}</p>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">ID Employé :</label>
                                        <p class="form-control-plaintext fs-6"><span class="badge bg-info">${employee.employee_id}</span></p>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">CIN :</label>
                                        <p class="form-control-plaintext fs-6">${employee.national_id}</p>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Date de naissance :</label>
                                        <p class="form-control-plaintext fs-6">${employee.birth_date}</p>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Genre :</label>
                                        <p class="form-control-plaintext fs-6"><span class="badge ${employee.gender_raw === 'M' ? 'bg-primary' : 'bg-danger'}">${employee.gender}</span></p>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">État civil :</label>
                                        <p class="form-control-plaintext fs-6">${employee.marital_status}</p>
                                    </div>
                                    
                                    <!-- INFORMATIONS PROFESSIONNELLES -->
                                    <div class="col-12 mt-4"><h5 class="text-success border-bottom pb-2"><i class="fas fa-briefcase me-2"></i>Informations Professionnelles</h5></div>
                                    
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Poste :</label>
                                        <p class="form-control-plaintext fs-6"><span class="badge bg-primary">${employee.position}</span></p>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Département :</label>
                                        <p class="form-control-plaintext fs-6"><span class="badge bg-secondary">${employee.department}</span></p>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Spécialité :</label>
                                        <p class="form-control-plaintext fs-6">${employee.speciality}</p>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Type de contrat :</label>
                                        <p class="form-control-plaintext fs-6">
                                            <span class="badge bg-success">${employee.contract_type}</span>
                                        </p>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Salaire de base :</label>
                                        <p class="form-control-plaintext fs-6"><strong class="text-success">${employee.base_salary} DH</strong></p>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Modèle de calcul :</label>
                                        <p class="form-control-plaintext fs-6">${employee.model_calcul}</p>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Statut :</label>
                                        <p class="form-control-plaintext fs-6">
                                            <span class="badge ${employee.status === 'Active' ? 'bg-success' : 'bg-danger'}">${employee.status}</span>
                                        </p>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Rôle :</label>
                                        <p class="form-control-plaintext fs-6">
                                            ${employee.is_supervisor === 'Oui' ? '<span class="badge bg-warning text-dark"><i class="fas fa-crown me-1"></i>Superviseur</span>' : 'Employé'}
                                        </p>
                                    </div>
                                    ${employee.supervisor !== 'Non défini' ? `
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Superviseur :</label>
                                        <p class="form-control-plaintext fs-6">${employee.supervisor}</p>
                                    </div>
                                    ` : ''}
                                    
                                    <!-- INFORMATIONS DE CONTACT -->
                                    <div class="col-12 mt-4"><h5 class="text-info border-bottom pb-2"><i class="fas fa-address-book me-2"></i>Informations de Contact</h5></div>
                                    
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Email :</label>
                                        <p class="form-control-plaintext fs-6"><a href="mailto:${employee.email}" class="text-decoration-none">${employee.email}</a></p>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Téléphone personnel :</label>
                                        <p class="form-control-plaintext fs-6"><a href="tel:${employee.personal_phone}" class="text-decoration-none">${employee.personal_phone}</a></p>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Téléphone professionnel :</label>
                                        <p class="form-control-plaintext fs-6"><a href="tel:${employee.work_phone}" class="text-decoration-none">${employee.work_phone}</a></p>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Nombre d'enfants :</label>
                                        <p class="form-control-plaintext fs-6"><span class="badge bg-light text-dark">${employee.children_count}</span></p>
                                    </div>
                                    
                                    <!-- INFORMATIONS DES ENFANTS -->
                                    ${employee.children_details && employee.children_details.length > 0 ? `
                                    <div class="col-12 mt-4"><h5 class="text-success border-bottom pb-2"><i class="fas fa-child me-2"></i>Détails des Enfants</h5></div>
                                    <div class="col-12">
                                        <div class="row g-2">
                                            ${employee.children_details.map((child, index) => `
                                                <div class="col-md-6 mb-3">
                                                    <div class="card border-light shadow-sm">
                                                        <div class="card-body p-3">
                                                            <h6 class="card-title text-primary mb-2">
                                                                <i class="fas fa-user-circle me-2"></i>${child.name}
                                                            </h6>
                                                            <div class="row g-2">
                                                                <div class="col-6">
                                                                    <small class="text-muted">Genre :</small><br>
                                                                    <span class="badge ${child.gender === 'Male' ? 'bg-primary' : 'bg-danger'} fs-7">${child.gender}</span>
                                                                </div>
                                                                <div class="col-6">
                                                                    <small class="text-muted">Naissance :</small><br>
                                                                    <small class="fw-bold">${child.birth_date}</small>
                                                                </div>
                                                                <div class="col-12 mt-2">
                                                                    <small class="text-muted">Scolarisé :</small><br>
                                                                    <span class="badge ${child.is_scolarise === 'Oui' ? 'bg-success' : 'bg-secondary'} fs-7">
                                                                        <i class="fas ${child.is_scolarise === 'Oui' ? 'fa-graduation-cap' : 'fa-times'} me-1"></i>
                                                                        ${child.is_scolarise}
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            `).join('')}
                                        </div>
                                    </div>
                                    ` : ''}
                                    
                                    <!-- ADRESSES -->
                                    ${employee.personal_address !== 'Non défini' || employee.work_address !== 'Non défini' ? `
                                    <div class="col-12 mt-4"><h5 class="text-warning border-bottom pb-2"><i class="fas fa-map-marker-alt me-2"></i>Adresses</h5></div>
                                    ` : ''}
                                    
                                    ${employee.personal_address !== 'Non défini' ? `
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Adresse personnelle :</label>
                                        <p class="form-control-plaintext fs-6">${employee.personal_address}</p>
                                    </div>
                                    ` : ''}
                                    
                                    ${employee.work_address !== 'Non défini' ? `
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold text-secondary">Adresse professionnelle :</label>
                                        <p class="form-control-plaintext fs-6">${employee.work_address}</p>
                                    </div>
                                    ` : ''}
                                    
                                    <!-- COMPÉTENCES ET CARRIÈRE -->
                                    ${employee.skills !== 'Non défini' || employee.career_evolution !== 'Non défini' ? `
                                    <div class="col-12 mt-4"><h5 class="text-purple border-bottom pb-2"><i class="fas fa-graduation-cap me-2"></i>Compétences & Carrière</h5></div>
                                    ` : ''}
                                    
                                    ${employee.skills !== 'Non défini' ? `
                                    <div class="col-12">
                                        <label class="form-label fw-bold text-secondary">Compétences :</label>
                                        <div class="p-3 bg-light rounded">
                                            <p class="mb-0 fs-6">${employee.skills}</p>
                                        </div>
                                    </div>
                                    ` : ''}
                                    
                                    ${employee.career_evolution !== 'Non défini' ? `
                                    <div class="col-12 mt-3">
                                        <label class="form-label fw-bold text-secondary">Évolution de carrière :</label>
                                        <div class="p-3 bg-light rounded">
                                            <p class="mb-0 fs-6">${employee.career_evolution}</p>
                                        </div>
                                    </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                modalContent.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Erreur de communication avec le serveur.
                    </div>
                `;
            });
        });
    });

    // Gestion du bouton de suppression d'employé avec SweetAlert et AJAX
    document.querySelectorAll('.delete-employee-btn').forEach(function(btn) {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        const employeeId = btn.getAttribute('data-id');
        const employeeName = btn.getAttribute('data-name');
        Swal.fire({
          title: "Supprimer l'employé ?",
          text: `Voulez-vous vraiment supprimer ${employeeName} ?`,
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Oui, supprimer',
          cancelButtonText: 'Non'
        }).then((result) => {
          if (result.isConfirmed) {
            fetch('/hr/employees/delete/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
              },
              body: `employee_id=${employeeId}`
            })
            .then(response => response.json())
            .then(data => {
              if (data.status === 'success') {
                Swal.fire('Succès', 'Employé supprimé avec succès', 'success').then(() => {
                  window.location.reload();
                });
              } else {
                Swal.fire('Erreur', data.message || 'Erreur lors de la suppression', 'error');
              }
            })
            .catch(() => {
              Swal.fire('Erreur', 'Erreur de communication avec le serveur', 'error');
            });
          }
        });
      });
    });

    // Gestion dynamique des compétences avec protection contre les doublons
    let skillIndex = document.querySelectorAll('.skill-input').length;
    let isAddingSkill = false; // Flag pour éviter les ajouts multiples

    // Fonction pour ajouter une compétence
    function addNewSkill() {
        if (isAddingSkill) return; // Empêcher les ajouts multiples
        isAddingSkill = true;
        
        const skillsList = document.getElementById('skills-list');
        if (skillsList) {
            const newSkillDiv = document.createElement('div');
            newSkillDiv.className = 'input-group mb-2';
            newSkillDiv.innerHTML = `
                <span class="input-group-text"><i class="fas fa-star"></i></span>
                <input
                    type="text"
                    class="form-control skill-input"
                    name="skills_${skillIndex}"
                    placeholder="Compétence"
                    data-index="${skillIndex}"
                >
                <button type="button" class="btn btn-outline-danger remove-skill">
                    <i class="fas fa-times"></i>
                </button>
            `;
            skillsList.appendChild(newSkillDiv);
            skillIndex++;
        }
        
        // Réinitialiser le flag après un délai
        setTimeout(() => {
            isAddingSkill = false;
        }, 100);
    }

    // Utiliser la délégation d'événements
    document.addEventListener('click', function(e) {
        // Ajouter une nouvelle compétence
        if (e.target && e.target.id === 'add-skill') {
            e.preventDefault();
            e.stopImmediatePropagation();
            addNewSkill();
        }
        
        // Supprimer une compétence
        if (e.target && e.target.closest('.remove-skill')) {
            e.preventDefault();
            e.stopImmediatePropagation();
            e.target.closest('.input-group').remove();
        }
    }, true); // Utiliser la capture pour intercepter l'événement en premier
});