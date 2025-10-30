// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeTableSearch();
    initializeColumnFilters();
    initializeSelectAll();
    initializeTableSorting();
    initializeCharts();
    initializeResponsiveTable();
    initializeResponsiveForms();
    
    // Add resize listener with debouncing
    window.addEventListener('resize', debounce(handleWindowResize, 250));
});

// Table search functionality
function initializeTableSearch() {
    const searchInputs = document.querySelectorAll('#product-search, #product-search2, #globalSearch2');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.card').querySelector('table tbody');
            const rows = table.querySelectorAll('tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    });
}

// Select All functionality for checkboxes
function initializeSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.row-check');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }
    
    // Also handle individual checkbox changes to update select all state
    const rowCheckboxes = document.querySelectorAll('.row-check');
    rowCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (selectAllCheckbox) {
                const allChecked = Array.from(rowCheckboxes).every(cb => cb.checked);
                const noneChecked = Array.from(rowCheckboxes).every(cb => !cb.checked);
                
                if (allChecked) {
                    selectAllCheckbox.checked = true;
                    selectAllCheckbox.indeterminate = false;
                } else if (noneChecked) {
                    selectAllCheckbox.checked = false;
                    selectAllCheckbox.indeterminate = false;
                } else {
                    selectAllCheckbox.checked = false;
                    selectAllCheckbox.indeterminate = true;
                }
            }
        });
    });
}

// Table sorting functionality
function initializeTableSorting() {
    const tables = document.querySelectorAll('.table');
    
    tables.forEach(table => {
        const headers = table.querySelectorAll('th');
        
        headers.forEach((header, columnIndex) => {
            const sortIcon = header.querySelector('.fas.fa-sort');
            if (sortIcon) {
                header.style.cursor = 'pointer';
                header.setAttribute('data-sort-direction', 'none');
                
                header.addEventListener('click', function() {
                    // Reset other headers
                    headers.forEach(h => {
                        if (h !== header) {
                            const otherIcon = h.querySelector('.fas');
                            if (otherIcon) {
                                otherIcon.className = 'fas fa-sort ms-1 text-muted';
                                h.setAttribute('data-sort-direction', 'none');
                            }
                        }
                    });
                    
                    // Toggle current header
                    const currentDirection = header.getAttribute('data-sort-direction');
                    let newDirection;
                    
                    if (currentDirection === 'none' || currentDirection === 'desc') {
                        newDirection = 'asc';
                        sortIcon.className = 'fas fa-sort-up ms-1 text-primary';
                    } else {
                        newDirection = 'desc';
                        sortIcon.className = 'fas fa-sort-down ms-1 text-primary';
                    }
                    
                    header.setAttribute('data-sort-direction', newDirection);
                    
                    // Sort the table
                    sortTable(table, columnIndex, newDirection);
                });
            }
        });
    });
}

// Sort table by column
function sortTable(table, columnIndex, direction) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Skip if no rows to sort
    if (rows.length === 0) return;
    
    // Determine if column contains numbers, dates, or text
    const firstCellText = rows[0].children[columnIndex]?.textContent.trim() || '';
    
    // Check if it's a date (formats: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY, etc.)
    const isDate = /^\d{4}-\d{2}-\d{2}$|^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}$|^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2}$/.test(firstCellText) ||
                   /^\d{1,2}\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}$/i.test(firstCellText);
    
    // Check if it's numeric
    const isNumeric = !isDate && !isNaN(parseFloat(firstCellText.replace(/[^\d.-]/g, ''))) && 
                     (firstCellText.match(/\d/) !== null);
    
    rows.sort((a, b) => {
        const aText = a.children[columnIndex]?.textContent.trim() || '';
        const bText = b.children[columnIndex]?.textContent.trim() || '';
        
        let aValue, bValue;
        
        if (isDate) {
            // For date sorting, convert to Date objects
            aValue = parseDate(aText);
            bValue = parseDate(bText);
            
            if (direction === 'asc') {
                return aValue - bValue; // Plus ancien en premier
            } else {
                return bValue - aValue; // Plus récent en premier
            }
        } else if (isNumeric) {
            // For numeric sorting, extract numbers
            aValue = parseFloat(aText.replace(/[^\d.-]/g, '')) || 0;
            bValue = parseFloat(bText.replace(/[^\d.-]/g, '')) || 0;
            
            if (direction === 'asc') {
                return aValue - bValue;
            } else {
                return bValue - aValue;
            }
        } else {
            // For text sorting, use locale compare
            aValue = aText.toLowerCase();
            bValue = bText.toLowerCase();
            
            if (direction === 'asc') {
                return aValue.localeCompare(bValue);
            } else {
                return bValue.localeCompare(aValue);
            }
        }
    });
    
    // Re-append sorted rows
    rows.forEach(row => tbody.appendChild(row));
}

// Parse date from various formats
function parseDate(dateString) {
    if (!dateString) return new Date(0);
    
    const dateStr = dateString.trim();
    
    // Format: YYYY-MM-DD (ISO format)
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
        return new Date(dateStr);
    }
    
    // Format: DD/MM/YYYY or DD-MM-YYYY
    const ddmmyyyy = dateStr.match(/^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})$/);
    if (ddmmyyyy) {
        const [, day, month, year] = ddmmyyyy;
        return new Date(year, month - 1, day);
    }
    
    // Format: DD/MM/YY or DD-MM-YY
    const ddmmyy = dateStr.match(/^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2})$/);
    if (ddmmyy) {
        const [, day, month, year] = ddmmyy;
        const fullYear = parseInt(year) < 50 ? 2000 + parseInt(year) : 1900 + parseInt(year);
        return new Date(fullYear, month - 1, day);
    }
    
    // Format: DD mois YYYY (français)
    const frenchMonths = {
        'janvier': 0, 'février': 1, 'mars': 2, 'avril': 3, 'mai': 4, 'juin': 5,
        'juillet': 6, 'août': 7, 'septembre': 8, 'octobre': 9, 'novembre': 10, 'décembre': 11
    };
    
    const frenchDate = dateStr.match(/^(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})$/i);
    if (frenchDate) {
        const [, day, month, year] = frenchDate;
        const monthIndex = frenchMonths[month.toLowerCase()];
        return new Date(year, monthIndex, day);
    }
    
    // Fallback: try native Date parsing
    const fallbackDate = new Date(dateStr);
    return isNaN(fallbackDate.getTime()) ? new Date(0) : fallbackDate;
}

// Column filter functionality for CRUD table
function initializeColumnFilters() {
    const columnFilters = document.querySelectorAll('.column-filter');
    columnFilters.forEach(filter => {
        filter.addEventListener('input', function() {
            const colIndex = this.getAttribute('data-column');
            const filterValue = this.value.toLowerCase();
            const table = this.closest('table').querySelector('tbody');
            const rows = table.querySelectorAll('tr');
            
            rows.forEach(row => {
                const cellText = row.children[colIndex]?.innerText.toLowerCase() || '';
                const shouldShow = !filterValue || cellText.includes(filterValue);
                
                // Check if row should be hidden due to other filters
                let showRow = shouldShow;
                const otherFilters = table.closest('.card').querySelectorAll('.column-filter');
                otherFilters.forEach(otherFilter => {
                    if (otherFilter !== this && otherFilter.value) {
                        const otherColIndex = otherFilter.getAttribute('data-column');
                        const otherCellText = row.children[otherColIndex]?.innerText.toLowerCase() || '';
                        const otherFilterValue = otherFilter.value.toLowerCase();
                        if (!otherCellText.includes(otherFilterValue)) {
                            showRow = false;
                        }
                    }
                });
                
                row.style.display = showRow ? '' : 'none';
            });
        });
    });
}

// Responsive table enhancements
function initializeResponsiveTable() {
    const tables = document.querySelectorAll('.table-responsive .table');
    
    tables.forEach(table => {
        // Add touch scrolling for horizontal tables on mobile
        if (window.innerWidth <= 767) {
            table.style.touchAction = 'pan-x';
        }
        
        // Enhance mobile table experience
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            // Add click handler for better mobile interaction
            row.addEventListener('click', function(e) {
                if (window.innerWidth <= 767 && !e.target.closest('button, input, a')) {
                    // Add visual feedback for mobile taps
                    row.style.backgroundColor = 'var(--alice-blue)';
                    setTimeout(() => {
                        row.style.backgroundColor = '';
                    }, 200);
                }
            });
        });
    });
}

// Responsive form enhancements
function initializeResponsiveForms() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        // Auto-focus first input on desktop, avoid on mobile
        // Auto-focus only when it won't cause unwanted scroll.
        // ‑ HR pages and inventory products are already excluded.
        // ‑ On pharmacy products page, focus only when user explicitly navigated with #product-form-card
        const isPharmacyProductsPage = window.location.pathname.includes('/pharmacy/products/');
        const shouldSkipFocus = isPharmacyProductsPage && window.location.hash !== '#product-form-card';

        if (window.innerWidth > 767 &&
            !window.location.pathname.includes('/hr/') &&
            !window.location.pathname.includes('/inventory/products/') &&
            !shouldSkipFocus) {
            const firstInput = form.querySelector('input:not([type="hidden"]), select, textarea');
            if (firstInput && !firstInput.hasAttribute('autofocus')) {
                firstInput.focus();
            }
        }

        // Enhance mobile form experience
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            // Add better mobile keyboard types
            if (input.type === 'email' && !input.hasAttribute('inputmode')) {
                input.setAttribute('inputmode', 'email');
            }
            if (input.type === 'tel' && !input.hasAttribute('inputmode')) {
                input.setAttribute('inputmode', 'tel');
            }
            if (input.type === 'number' && !input.hasAttribute('inputmode')) {
                input.setAttribute('inputmode', 'numeric');
            }
        });
    });
}

// Initialize responsive features on window resize
function handleWindowResize() {
    // Reinitialize responsive features when window is resized
    initializeResponsiveTable();
    
    // Close mobile sidebar on resize to desktop
    if (window.innerWidth > 991) {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        if (sidebar) sidebar.classList.remove('show');
        if (overlay) overlay.classList.remove('show');
    }
}

// Debounce function for resize events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize all charts (placeholder)
function initializeCharts() {
    // Chart initialization code would go here
    console.log('Charts initialized');
}