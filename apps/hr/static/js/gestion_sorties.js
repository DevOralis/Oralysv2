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
    // Vérifier si nous sommes sur la page des sorties
    const tableBody = document.querySelector('#sorties-table-body');
    if (!tableBody) {
        return;
    }
    
    // Configuration
    const itemsPerPage = 5;
    let currentPage = 1;
    let filteredSorties = [];
    
    // Éléments DOM
    const searchInput = document.getElementById('search-input');
    const filterTypeSortie = document.getElementById('filter-type-sortie');
    const pagination = document.getElementById('sortiesPagination');
    
    // Récupérer toutes les sorties du tableau
    function getAllSorties() {
        const rows = Array.from(tableBody.querySelectorAll('tr:not(.no-results)'));
        return rows.map(row => ({
            element: row,
            name: (row.cells[1] && row.cells[1].textContent) ? row.cells[1].textContent.toLowerCase() : '',
            type: (row.cells[2] && row.cells[2].textContent) ? row.cells[2].textContent.toLowerCase() : '',
            motif: (row.cells[3] && row.cells[3].textContent) ? row.cells[3].textContent.toLowerCase() : '',
            date: (row.cells[4] && row.cells[4].textContent) ? row.cells[4].textContent.toLowerCase() : ''
        }));
    }
    
    // Filtrer les sorties
    function filterSorties() {
        const searchTerm = searchInput ? (searchInput.value.toLowerCase() || '') : '';
        const typeSortie = filterTypeSortie ? (filterTypeSortie.value.toLowerCase() || '') : '';
        
        let filtered = getAllSorties();
        
        // Appliquer les filtres
        if (searchTerm) {
            filtered = filtered.filter(sortie => 
                sortie.name.includes(searchTerm) ||
                sortie.type.includes(searchTerm) ||
                sortie.motif.includes(searchTerm) ||
                sortie.date.includes(searchTerm)
            );
        }
        
        if (typeSortie) filtered = filtered.filter(sortie => sortie.type.includes(typeSortie));
        
        filteredSorties = filtered;
        currentPage = 1;
        displaySorties();
        updatePagination();
    }
    
    // Afficher les sorties de la page courante
    function displaySorties() {
        // Toujours utiliser la pagination - afficher seulement les sorties de la page courante
        const start = (currentPage - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const pageSorties = filteredSorties.slice(start, end);
        
        // Cacher toutes les lignes
        const allRows = tableBody.querySelectorAll('tr');
        allRows.forEach(row => {
            row.style.display = 'none';
        });
        
        // Afficher les lignes de la page courante
        pageSorties.forEach(sortie => {
            sortie.element.style.display = '';
        });
        
        // Afficher message si aucun résultat
        const noResultsRow = tableBody.querySelector('.no-results');
        if (pageSorties.length === 0) {
            if (!noResultsRow) {
                const tr = document.createElement('tr');
                tr.className = 'no-results';
                tr.innerHTML = '<td colspan="8" class="text-center">Aucun résultat trouvé</td>';
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
        const totalPages = Math.ceil(filteredSorties.length / itemsPerPage);
        
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
                displaySorties();
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
        const prevButton = document.getElementById('prevPageSortie');
        const prevButtonLi = prevButton ? prevButton.closest('.page-item') : pagination.querySelector('.page-item:first-child');
        
        if (prevButtonLi) {
            prevButtonLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
            if (currentPage > 1 && prevButton) {
                prevButton.onclick = (e) => {
                    e.preventDefault();
                    currentPage--;
                    displaySorties();
                    updatePagination();
                };
            } else if (prevButton) {
                prevButton.onclick = (e) => {
                    e.preventDefault();
                };
            }
        }
        
        const nextButton = document.getElementById('nextPageSortie');
        const nextButtonLi = nextButton ? nextButton.closest('.page-item') : pagination.querySelector('.page-item:last-child');
        
        if (nextButtonLi) {
            nextButtonLi.className = `page-item ${currentPage === totalPages || totalPages === 0 ? 'disabled' : ''}`;
            if (currentPage < totalPages && nextButton) {
                nextButton.onclick = (e) => {
                    e.preventDefault();
                    currentPage++;
                    displaySorties();
                    updatePagination();
                };
            } else if (nextButton) {
                nextButton.onclick = (e) => {
                    e.preventDefault();
                };
            }
        }
    }
    
    // Event listeners pour les filtres
    if (searchInput) {
        searchInput.addEventListener('input', filterSorties);
    }
    if (filterTypeSortie) {
        filterTypeSortie.addEventListener('change', filterSorties);
    }
    
    // Initialisation
    filteredSorties = getAllSorties();
    displaySorties();
    updatePagination();
});