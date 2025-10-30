document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('adjustment-form');
    const inputs = document.querySelectorAll('.counted-input');
    const searchInput = document.getElementById('search-input');
    const adjustmentIndicator = document.getElementById('adjustment-indicator');
    const adjustmentCount = document.getElementById('adjustment-count');
    
    // Fonction pour mettre à jour l'indicateur d'ajustements stockés
    function updateAdjustmentIndicator() {
        let count = 0;
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('counted_')) {
                const value = localStorage.getItem(key);
                if (value && value.trim() !== '') {
                    // Compter tous les ajustements saisis, même si égaux à la quantité stockée
                    count++;
                }
            }
        }
        
        if (adjustmentCount) {
            adjustmentCount.textContent = count;
        }
        
        if (adjustmentIndicator) {
            if (count > 0) {
                adjustmentIndicator.style.display = 'block';
            } else {
                adjustmentIndicator.style.display = 'none';
            }
        }
    }
    
    // Fonction de recherche dans le tableau
    function filterTable(query) {
        const lowerQuery = query.toLowerCase();
        let visibleCount = 0;
        
        // Récupérer les lignes à chaque recherche pour éviter les problèmes de cache
        const tableRows = document.querySelectorAll('tbody tr:not(.no-results-row)');
        
        // Supprimer l'ancien message "Aucun résultat" s'il existe
        const existingNoResultsRow = document.querySelector('.no-results-row');
        if (existingNoResultsRow) {
            existingNoResultsRow.remove();
        }
        
        tableRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            let found = false;
            
            // Chercher dans toutes les cellules sauf la dernière (Différence)
            for (let i = 0; i < cells.length - 1; i++) {
                if (cells[i].textContent.toLowerCase().includes(lowerQuery)) {
                    found = true;
                    break;
                }
            }
            
            const shouldShow = found || query === '';
            row.style.display = shouldShow ? '' : 'none';
            if (shouldShow) visibleCount++;
        });
        
        // Ajouter un message "Aucun résultat" si nécessaire
        if (visibleCount === 0 && query !== '') {
            const tbody = document.querySelector('tbody');
            const noResultsRow = document.createElement('tr');
            noResultsRow.className = 'no-results-row';
            
            noResultsRow.innerHTML = `
                <td colspan="7" class="text-center text-muted py-4">
                    <i class="fas fa-search me-2"></i>
                    Aucun produit trouvé pour "${query}"
                </td>
            `;
            
            tbody.appendChild(noResultsRow);
        }
    }
    
    // Gestionnaire du champ de recherche avec délai (debounce)
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                filterTable(this.value);
            }, 300); // Délai de 300ms pour éviter trop d'appels
        });
        
        // Empêcher la soumission sur Enter
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                clearTimeout(searchTimeout);
                filterTable(this.value);
            }
        });
    }
    

  
    // Fonction de calcul de différence
    function updateDifference(input) {
      const stored = parseFloat(input.dataset.stored);
      const counted = parseFloat(input.value);
      const diffCell = input.closest('tr').querySelector('.diff-cell');
  
      if (!isNaN(counted)) {
        const diff = counted - stored;
        diffCell.textContent = diff.toFixed(2);
        diffCell.classList.remove('diff-positive', 'diff-negative');
        if (diff > 0) diffCell.classList.add('diff-positive');
        else if (diff < 0) diffCell.classList.add('diff-negative');
      } else {
        diffCell.textContent = '—';
        diffCell.classList.remove('diff-positive', 'diff-negative');
      }
    }
  
    // Fonction pour nettoyer et valider une valeur numérique
    function cleanNumericValue(value) {
      if (!value || value.trim() === '') return '';
      let cleaned = value.toString().replace(',', '.');
      if (isNaN(parseFloat(cleaned))) return '';
      return cleaned;
    }
  
    // Initialiser et gérer les changements
    inputs.forEach(input => {
      const key = input.name;
      
      // Nettoyer la valeur initiale si nécessaire
      if (input.value) {
        input.value = cleanNumericValue(input.value);
      }
      
      // Toujours calculer la différence pour la valeur actuelle
      updateDifference(input);
      
      // Si l'input a une valeur (sauvegardée), l'afficher et calculer la différence
      if (input.value && input.value.trim() !== '') {
        updateDifference(input);
      } else {
        // Seulement charger depuis localStorage si l'input est vide
        const storedVal = localStorage.getItem(key);
        if (storedVal !== null && storedVal.trim() !== '') {
          input.value = cleanNumericValue(storedVal);
          updateDifference(input);
        }
      }
      
      // Écouter les changements et sauvegarder dans localStorage
      input.addEventListener('input', () => {
        // Nettoyer la valeur saisie
        input.value = cleanNumericValue(input.value);
        updateDifference(input);
        
        // Sauvegarder toute quantité comptée saisie
        if (input.value.trim() !== '') {
          localStorage.setItem(key, input.value);
        } else {
          localStorage.removeItem(key);
        }
        
        // Mettre à jour l'indicateur
        updateAdjustmentIndicator();
      });
    });
  
    // Bouton "Effacer"
    const clearButton = document.getElementById('clear-inputs');
    if (clearButton) {
      clearButton.addEventListener('click', () => {
        inputs.forEach(input => {
          input.value = '';
          localStorage.removeItem(input.name);
          updateDifference(input);
        });
        // Nettoyer tous les ajustements stockés
        for (let i = localStorage.length - 1; i >= 0; i--) {
          const key = localStorage.key(i);
          if (key && key.startsWith('counted_')) {
            localStorage.removeItem(key);
          }
        }
        // Mettre à jour l'indicateur
        updateAdjustmentIndicator();
      });
    }
    
    // Initialiser l'indicateur au chargement de la page
    updateAdjustmentIndicator();
  
    // Fonction pour ajouter tous les ajustements stockés au formulaire
    function addAllStoredAdjustments() {
        // Parcourir tout le localStorage pour trouver les ajustements
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('counted_')) {
                const value = localStorage.getItem(key);
                if (value && value.trim() !== '') {
                    // Vérifier si l'input existe déjà dans le formulaire
                    let existingInput = form.querySelector(`input[name="${key}"]`);
                    
                    if (!existingInput) {
                        // Créer un input hidden pour cette valeur
                        const hiddenInput = document.createElement('input');
                        hiddenInput.type = 'hidden';
                        hiddenInput.name = key;
                        hiddenInput.value = value;
                        form.appendChild(hiddenInput);
                    } else {
                        // Mettre à jour la valeur si l'input existe
                        existingInput.value = value;
                    }
                }
            }
        }
    }

    // Confirmation avec Swal et rechargement après sauvegarde
    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        
        // Compter tous les ajustements saisis
        let adjustmentCount = 0;
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('counted_')) {
                const value = localStorage.getItem(key);
                if (value && value.trim() !== '') {
                    adjustmentCount++;
                }
            }
        }
        
        if (adjustmentCount === 0) {
            Swal.fire({
                icon: 'warning',
                title: 'Aucun ajustement',
                text: 'Vous n\'avez saisi aucune quantité comptée à enregistrer.',
                confirmButtonText: 'OK'
            });
            return;
        }
        
        Swal.fire({
          title: 'Confirmer l\'ajustement ?',
          text: `Voulez-vous vraiment enregistrer les ${adjustmentCount} quantité(s) comptée(s) de toutes les pages ?`,
          icon: 'question',
          showCancelButton: true,
          confirmButtonText: 'Oui, enregistrer',
          cancelButtonText: 'Annuler',
          confirmButtonColor: '#198754'
        }).then((result) => {
          if (result.isConfirmed) {
            // Ajouter tous les ajustements stockés au formulaire
            addAllStoredAdjustments();
            
            // Afficher un indicateur de chargement
            Swal.fire({
              title: 'Enregistrement en cours...',
              text: 'Veuillez patienter...',
              allowOutsideClick: false,
              didOpen: () => {
                Swal.showLoading();
              }
            });
            
            // Soumettre le formulaire
            form.submit();
          }
        });
      });
    }
  
    // Détecter le type de navigation
    const navigationType = performance.getEntriesByType('navigation')[0]?.type;
    
    // Nettoyer localStorage uniquement lors d'un reload manuel (F5)
    // et non lors de la navigation entre les pages de pagination
    if (navigationType === 'reload') {
      // Nettoyer TOUS les ajustements stockés
      for (let i = localStorage.length - 1; i >= 0; i--) {
        const key = localStorage.key(i);
        if (key && key.startsWith('counted_')) {
          localStorage.removeItem(key);
        }
      }
      
      // Cacher l'indicateur
      const adjustmentIndicator = document.getElementById('adjustment-indicator');
      if (adjustmentIndicator) {
        adjustmentIndicator.style.display = 'none';
      }
    }
  }); 