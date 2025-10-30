document.addEventListener('DOMContentLoaded', function () {
    const scrollToFormBtn = document.getElementById('scrollToForm');
    if (scrollToFormBtn) {
        scrollToFormBtn.addEventListener('click', function () {
            document.getElementById('formulaire-fournisseur').scrollIntoView({ behavior: 'smooth' });
        });
    }

    const searchInput = document.getElementById('searchInput');
    const countryFilter = document.getElementById('countryFilter');
    const cityFilter = document.getElementById('cityFilter');
    const supplierTable = document.getElementById('supplierTable');
    let rows = supplierTable.getElementsByTagName('tr');

    function filterTable() {
        const searchText = searchInput.value.toLowerCase();
        const selectedCountry = countryFilter.value.toLowerCase();
        const selectedCity = cityFilter.value.toLowerCase();

        for (let row of rows) {
            const name = row.cells[1].textContent.toLowerCase();
            const email = row.cells[2].textContent.toLowerCase();
            const phone = row.cells[3].textContent.toLowerCase();
            const address = row.cells[4].textContent.toLowerCase();
            const city = row.cells[5].textContent.toLowerCase();

            const matchesSearch = name.includes(searchText) || email.includes(searchText) || phone.includes(searchText);
            const matchesCountry = selectedCountry ? address.includes(selectedCountry) : true;
            const matchesCity = selectedCity ? city.includes(selectedCity) : true;

            row.style.display = matchesSearch && matchesCountry && matchesCity ? '' : 'none';
        }
    }

    if (searchInput) searchInput.addEventListener('input', filterTable);
    if (countryFilter) countryFilter.addEventListener('change', filterTable);
    if (cityFilter) cityFilter.addEventListener('change', filterTable);

    const pagination = document.getElementById('pagination');
    const rowsPerPage = 10;
    let currentPage = 1;

    function setupPagination() {
        const totalRows = rows.length;
        const totalPages = Math.ceil(totalRows / rowsPerPage);
        pagination.innerHTML = '';

        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = '<a class="page-link" href="#">Préc</a>';
        prevLi.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                showPage();
            }
        });
        pagination.appendChild(prevLi);

        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement('li');
            li.className = `page-item ${i === currentPage ? 'active' : ''}`;
            li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
            li.addEventListener('click', () => {
                currentPage = i;
                showPage();
            });
            pagination.appendChild(li);
        }

        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
        nextLi.innerHTML = '<a class="page-link" href="#">Suiv</a>';
        nextLi.addEventListener('click', () => {
            if (currentPage < totalPages) currentPage++;
            showPage();
        });
        pagination.appendChild(nextLi);

        showPage();
    }

    function showPage() {
        const start = (currentPage - 1) * rowsPerPage;
        const end = start + rowsPerPage;

        for (let i = 0; i < rows.length; i++) {
            rows[i].style.display = i >= start && i < end ? '' : 'none';
        }

        const pageItems = pagination.getElementsByClassName('page-item');
        for (let item of pageItems) item.classList.remove('active');
        if (pageItems[currentPage]) pageItems[currentPage].classList.add('active');
    }

    if (pagination) setupPagination();

    function attachDeleteListeners() {
        const deleteButtons = document.querySelectorAll('.btn-delete');
        deleteButtons.forEach(button => {
            button.removeEventListener('click', handleDelete);
            button.addEventListener('click', handleDelete);
        });
    }

    function handleDelete() {
        const supplierId = this.getAttribute('data-id');
        Swal.fire({
            title: 'Êtes-vous sûr ?',
            text: 'Cette action supprimera le fournisseur de manière permanente.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Oui, supprimer',
            cancelButtonText: 'Annuler'
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/pharmacy/suppliers/${supplierId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'success') {
                        Swal.fire('Supprimé !', data.message, 'success').then(() => {
                            const row = this.closest('tr');
                            row.remove();
                            rows = supplierTable.getElementsByTagName('tr');
                            setupPagination();
                        });
                    } else {
                        Swal.fire('Erreur !', data.message, 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    Swal.fire('Erreur !', 'Une erreur est survenue lors de la suppression.', 'error');
                });
            }
        });
    }

    attachDeleteListeners();

    // Handle edit button click
    document.querySelectorAll('.btn-edit').forEach(button => {
        button.addEventListener('click', function() {
            const supplierId = this.dataset.id;
            const url = `/pharmacy/suppliers/${supplierId}/update/`;
            
            // Show loading state
            const formContainer = document.getElementById('form-container');
            if (formContainer) {
                formContainer.innerHTML = '<div class="text-center p-4"><div class="spinner-border" role="status"><span class="visually-hidden">Chargement...</span></div></div>';
            }
            
            // Make AJAX GET request to load the form
            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'form') {
                    // Update the form container with the received HTML
                    if (formContainer) {
                        formContainer.innerHTML = data.html;
                        // Scroll to form
                        document.getElementById('formulaire-fournisseur').scrollIntoView({ behavior: 'smooth' });
                        // Re-initialize any necessary JS for the form
                        initializeFormHandlers();
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (formContainer) {
                    formContainer.innerHTML = `
                        <div class="alert alert-danger">
                            Erreur lors du chargement du formulaire. Veuillez réessayer.
                        </div>`;
                }
            });
        });
    });

    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const url = form.action;

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(async response => {
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    // Si ce n'est pas du JSON, on essaie de lire le texte de la réponse
                    const text = await response.text();
                    console.error('Réponse non-JSON reçue:', text);
                    // Si c'est une redirection HTML, on redirige
                    if (response.redirected) {
                        window.location.href = response.url;
                        return;
                    }
                    throw new Error('La réponse du serveur n\'est pas au format attendu');
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    Swal.fire({
                        title: 'Succès !',
                        text: data.message,
                        icon: 'success',
                        confirmButtonText: 'OK'
                    }).then(() => {
                        // ✅ Redirection après ajout ou modification :
                        window.location.href = "/pharmacy/suppliers";
                    });
                } else {
                    console.error('Form submission failed:', data);

                    let errorMessage = data.message || 'Une erreur est survenue lors de l\'enregistrement.';

                    if (data.errors) {
                        const errorList = [];
                        for (const [field, errors] of Object.entries(data.errors)) {
                            errorList.push(`${field}: ${errors.join(', ')}`);
                        }
                        errorMessage = errorList.join('<br>');
                    }

                    Swal.fire({
                        title: 'Erreur !',
                        html: errorMessage,
                        icon: 'error',
                        confirmButtonText: 'OK'
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire({
                    title: 'Erreur !',
                    text: 'Une erreur réseau est survenue. Veuillez réessayer.',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            });
        });
    }

    function initializeFormHandlers() {
        // Re-initialize any necessary JS for the form
    }
});
