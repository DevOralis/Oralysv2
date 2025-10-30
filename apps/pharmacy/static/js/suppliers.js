document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const supplierTableBody = document.getElementById('supplierTable');
    const searchInput = document.getElementById('searchInput');
    const cityFilter = document.getElementById('cityFilter');
    const paginationContainer = document.getElementById('supplierPagination');

    // State
    let currentPage = 1;
    let paginationData = null;

    // --- FUNCTIONS ---

    // 1. Fetch suppliers from server with pagination
    async function fetchSuppliers(page = 1, query = '', city = '') {
        try {
            const url = new URL(window.location.href);
            url.searchParams.set('page', page);
            if (query) url.searchParams.set('q', query);
            if (city) url.searchParams.set('city', city);

            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            const data = await response.json();

            // Update table content
            supplierTableBody.innerHTML = data.html;
            
            // Update pagination data
            paginationData = data.pagination;
            currentPage = paginationData.current_page;
            
            // Update pagination controls
            updatePagination();
            
        } catch (error) {
            console.error('Error fetching suppliers:', error);
            supplierTableBody.innerHTML = '<tr><td colspan="8" class="text-center text-danger">Erreur lors du chargement des fournisseurs</td></tr>';
        }
    }

    // 2. Filter suppliers (now server-side)
    function filterSuppliers() {
        const query = searchInput.value.trim();
        const city = cityFilter.value;
        fetchSuppliers(1, query, city); // Reset to page 1 when filtering
    }

    // 3. Generate and update pagination controls
    function updatePagination() {
        paginationContainer.innerHTML = '';
        
        if (!paginationData || paginationData.total_pages <= 1) return;

        // Previous Button
        if (paginationData.has_previous) {
            const prevLi = document.createElement('li');
            prevLi.className = 'page-item';
            prevLi.innerHTML = `<a class="page-link" href="#" data-page="${paginationData.previous_page_number}">&laquo; Préc</a>`;
            paginationContainer.appendChild(prevLi);
        }

        // Page Number Buttons
        paginationData.page_range.forEach(page => {
            const pageLi = document.createElement('li');
            pageLi.className = `page-item ${page === paginationData.current_page ? 'active' : ''}`;
            pageLi.innerHTML = `<a class="page-link" href="#" data-page="${page}">${page}</a>`;
            paginationContainer.appendChild(pageLi);
        });

        // Next Button
        if (paginationData.has_next) {
            const nextLi = document.createElement('li');
            nextLi.className = 'page-item';
            nextLi.innerHTML = `<a class="page-link" href="#" data-page="${paginationData.next_page_number}">Suiv &raquo;</a>`;
            paginationContainer.appendChild(nextLi);
        }
    }

    // --- INITIALIZATION & EVENT LISTENERS ---

    // Initial pagination setup (use server-side data if available)
    if (typeof window.paginationData !== 'undefined') {
        paginationData = window.paginationData;
        updatePagination();
    }

    // Event listeners for live search and filtering
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(filterSuppliers, 300); // Debounce search
        });
    }

    if (cityFilter) {
        cityFilter.addEventListener('change', filterSuppliers);
    }

    // Event listener for pagination clicks
    paginationContainer.addEventListener('click', function(e) {
        e.preventDefault();
        const target = e.target.closest('a');
        if (!target) return;

        const page = parseInt(target.dataset.page, 10);
        if (page && page !== currentPage) {
            const query = searchInput.value.trim();
            const city = cityFilter.value;
            fetchSuppliers(page, query, city);
        }
    });

    // --- DYNAMIC IMPORT/EXPORT BUTTON LOGIC ---
    const importExportBtn = document.getElementById('import-export-btn');
    const selectAllCheckbox = document.getElementById('select-all-checkbox');
    const rowCheckboxes = supplierTableBody.getElementsByClassName('row-check');

    function updateButtonState() {
        const anyChecked = Array.from(rowCheckboxes).some(cb => cb.checked);
        if (anyChecked) {
            importExportBtn.innerHTML = `<i class="fas fa-file-export"></i><span class="d-none d-lg-inline ms-1">Exporter</span>`;
        } else {
            importExportBtn.innerHTML = `<i class="fas fa-file-import"></i><span class="d-none d-lg-inline ms-1">Importer</span>`;
        }
    }

    supplierTableBody.addEventListener('change', function(e) {
        if (e.target.classList.contains('row-check')) {
            updateButtonState();
            // Uncheck 'select all' if any individual box is unchecked
            if (!e.target.checked) {
                selectAllCheckbox.checked = false;
            }
        }
    });

    selectAllCheckbox.addEventListener('change', function() {
        Array.from(rowCheckboxes).forEach(cb => cb.checked = selectAllCheckbox.checked);
        updateButtonState();
    });

    // Initial state check
    updateButtonState();

    // Force scroll to top on load to prevent jumping to the form
    window.addEventListener('load', () => {
        setTimeout(() => {
            window.scrollTo(0, 0);
        }, 0);
    });
});
