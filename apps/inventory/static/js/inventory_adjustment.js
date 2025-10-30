document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('adjustment-form');
  const inputs = document.querySelectorAll('.counted-input');
  const searchInput = document.getElementById('search-input');
  
  // Désactiver la recherche côté client car nous utilisons maintenant la recherche côté serveur
  // La recherche se fait maintenant via submitSearch() dans le template

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

  // Fonction pour mettre à jour l'indicateur d'ajustements stockés
  function updateAdjustmentIndicator() {
    const indicator = document.getElementById('adjustment-indicator');
    const countSpan = document.getElementById('adjustment-count');
    
    if (!indicator || !countSpan) return;
    
    let adjustmentCount = 0;
    
    // Compter tous les ajustements saisis
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('counted_')) {
        const value = localStorage.getItem(key);
        if (value && value.trim() !== '') {
          adjustmentCount++;
        }
      }
    }
    
    countSpan.textContent = adjustmentCount;
    indicator.style.display = adjustmentCount > 0 ? 'block' : 'none';
  }
  
  // Fonction pour ajouter tous les ajustements stockés au formulaire
  function addAllStoredAdjustments() {
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('counted_')) {
        const value = localStorage.getItem(key);
        if (value && value.trim() !== '') {
          // Vérifier si l'input existe déjà sur cette page
          const existingInput = document.querySelector(`input[name="${key}"]`);
          if (!existingInput) {
            // Créer un input caché pour cet ajustement
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = key;
            hiddenInput.value = value;
            form.appendChild(hiddenInput);
          }
        }
      }
    }
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
  
  // Initialiser l'indicateur au chargement
  updateAdjustmentIndicator();

  // Bouton "Effacer"
  const clearButton = document.getElementById('clear-inputs');
  if (clearButton) {
    clearButton.addEventListener('click', () => {
      // Effacer tous les ajustements stockés
      for (let i = localStorage.length - 1; i >= 0; i--) {
        const key = localStorage.key(i);
        if (key && key.startsWith('counted_')) {
          localStorage.removeItem(key);
        }
      }
      
      // Effacer les inputs visibles
      inputs.forEach(input => {
        input.value = '';
        updateDifference(input);
      });
      
      // Mettre à jour l'indicateur
      updateAdjustmentIndicator();
    });
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