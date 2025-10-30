document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const cityFilter = document.getElementById('cityFilter');
    const supplierTable = document.getElementById('supplierTable');

    function fetchSuppliers() {
        const query = searchInput.value;
        const city = cityFilter.value;
        
        // Construct URL with query parameters
        const url = `?q=${encodeURIComponent(query)}&city=${encodeURIComponent(city)}`;

        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(response => response.json())
        .then(data => {
            supplierTable.innerHTML = data.html;
        })
        .catch(error => console.error('Error fetching suppliers:', error));
    }

    let debounceTimer;
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(fetchSuppliers, 300);
    });

    cityFilter.addEventListener('change', fetchSuppliers);

    // Prevent form submission from reloading the page
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        fetchSuppliers();
    });
});
