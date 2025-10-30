document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-input-primary');
    
    // Get CSRF token
    function getCsrfToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfInput ? csrfInput.value : '';
    }
    
    // Show toast messages
    function showToast(icon, message) {
        Swal.fire({
            icon: icon,
            title: icon === 'success' ? 'Succès!' : 'Erreur!',
            text: message,
            timer: 3000,
            timerProgressBar: true,
            showConfirmButton: false
        });
    }
    
    // Initialize sorting exactly like inventory
    function initializeSorting() {
        const activitiesTable = document.getElementById('activities-table');
        if (activitiesTable) {
            const headers = activitiesTable.querySelectorAll('th[data-sort-field]');
            
            // Set initial sort state from URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const currentSortBy = urlParams.get('sort_by');
            const currentSortOrder = urlParams.get('sort_order');
            
            // Update header icons based on current sort
            if (currentSortBy && currentSortOrder) {
                headers.forEach(header => {
                    const sortField = header.getAttribute('data-sort-field');
                    const sortIcon = header.querySelector('.fas');
                    if (sortIcon) {
                        if (sortField === currentSortBy) {
                            header.setAttribute('data-sort-direction', currentSortOrder);
                            if (currentSortOrder === 'asc') {
                                sortIcon.className = 'fas fa-sort-up ms-1 text-primary';
                            } else {
                                sortIcon.className = 'fas fa-sort-down ms-1 text-primary';
                            }
                        } else {
                            header.setAttribute('data-sort-direction', 'none');
                            sortIcon.className = 'fas fa-sort ms-1 text-muted';
                        }
                    }
                });
            }
            
            headers.forEach(header => {
                const sortIcon = header.querySelector('.fas.fa-sort, .fas.fa-sort-up, .fas.fa-sort-down');
                if (sortIcon) {
                    header.style.cursor = 'pointer';
                    if (!header.getAttribute('data-sort-direction')) {
                        header.setAttribute('data-sort-direction', 'none');
                    }
                    
                    header.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        const sortField = header.getAttribute('data-sort-field');
                        if (!sortField) return;
                        
                        // Get current sort from URL parameters (more reliable than data attributes)
                        const urlParams = new URLSearchParams(window.location.search);
                        const currentSortBy = urlParams.get('sort_by');
                        const currentSortOrder = urlParams.get('sort_order');
                        
                        let newDirection = 'asc'; // Default direction
                        
                        // If we're clicking on the currently sorted column, toggle direction
                        if (currentSortBy === sortField) {
                            if (currentSortOrder === 'asc') {
                                newDirection = 'desc';
                            } else {
                                newDirection = 'asc';
                            }
                        } else {
                            // If we're clicking on a different column, start with ascending
                            newDirection = 'asc';
                        }
                        
                        // Build new URL with sort parameters
                        const currentUrl = new URL(window.location);
                        currentUrl.searchParams.set('sort_by', sortField);
                        currentUrl.searchParams.set('sort_order', newDirection);
                        
                        // Preserve current page as 1 when sorting
                        currentUrl.searchParams.set('page', '1');
                        
                        // Remove any hash to prevent scrolling to form
                        currentUrl.hash = '';
                        
                        // Navigate to new URL (this will trigger server-side sorting)
                        window.location.href = currentUrl.toString();
                    });
                }
            });
        }
    }
    
    // Bind event listeners
    function bindEventListeners() {
        // Delete buttons
        document.querySelectorAll('.btn-delete-activity').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const activityId = this.getAttribute('data-id');
                const activityTitle = this.getAttribute('data-title');
                
                Swal.fire({
                    title: 'Êtes-vous sûr?',
                    text: `Voulez-vous vraiment supprimer l'activité "${activityTitle}"?`,
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#d33',
                    cancelButtonColor: '#3085d6',
                    confirmButtonText: 'Oui, supprimer!',
                    cancelButtonText: 'Annuler'
                }).then((result) => {
                    if (result.isConfirmed) {
                        deleteActivity(activityId);
                    }
                });
            });
        });
        
        // Preview buttons
        document.querySelectorAll('.btn-view-activity').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const activityId = this.getAttribute('data-id');
                previewActivity(activityId);
            });
        });
    }
    
    // Delete activity
    async function deleteActivity(activityId) {
        try {
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', getCsrfToken());
            
            const response = await fetch(`/therapeutic_activities/activities/${activityId}/delete/`, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                showToast('success', data.message);
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                showToast('error', data.message);
            }
        } catch (error) {
            console.error('Error deleting activity:', error);
            showToast('error', 'Erreur de connexion au serveur');
        }
    }
    
    // Preview activity
    async function previewActivity(activityId) {
        try {
            const response = await fetch(`/therapeutic_activities/activities/${activityId}/preview/`, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            
            const data = await response.json();
            
            Swal.fire({
                title: data.title,
                html: data.html,
                width: '60%',
                showCloseButton: true,
                showConfirmButton: false
            });
        } catch (error) {
            console.error('Error loading preview:', error);
            showToast('error', 'Erreur de chargement de l\'aperçu');
        }
    }
    
    // Search with debounce like inventory
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const form = document.getElementById('search-form');
                if (form) {
                    form.submit();
                }
            }, 500);
        });
    }
    
    // Auto scroll to form if present
    if (window.activityListConfig && window.activityListConfig.showForm) {
        const formEl = document.getElementById('activity-form-card');
        if (formEl) {
            formEl.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    // Handle URL messages
    function handleUrlMessages() {
        const urlParams = new URLSearchParams(window.location.search);
        const message = urlParams.get('message');
        const type = urlParams.get('type');
        
        if (message) {
            if (type === 'success') {
                showToast('success', decodeURIComponent(message));
            } else {
                showToast('error', decodeURIComponent(message));
            }
            
            // Clean URL
            const url = new URL(window.location);
            url.searchParams.delete('message');
            url.searchParams.delete('type');
            window.history.replaceState({}, document.title, url.toString());
        }
    }
    
    // Initialize everything
    initializeSorting();
    bindEventListeners();
    handleUrlMessages();
});