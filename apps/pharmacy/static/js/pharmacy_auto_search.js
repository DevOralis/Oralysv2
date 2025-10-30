// ========================================
// RECHERCHE AUTOMATIQUE UNIVERSELLE PHARMACY
// ========================================

/**
 * Fonction universelle pour activer la recherche automatique
 * sur n'importe quel champ de recherche dans les templates pharmacy
 */
function initializeUniversalAutoSearch() {
    // Liste des sélecteurs possibles pour les champs de recherche
    const searchSelectors = [
        '#product-search',        // productsList.html
        '#search',               // pharmacy_orders_list.html
        '#search-input',         // autres templates
        '#searchInput',          // suppliers.html
        'input[name="q"]',       // formulaires de recherche génériques
        'input[name="search"]',  // formulaires de recherche génériques
        '.pharmacy-search-input' // classe générique
    ];

    // Parcourir tous les sélecteurs possibles
    searchSelectors.forEach(selector => {
        const searchInput = document.querySelector(selector);
        
        if (searchInput) {
            // Vérifier si l'élément n'a pas déjà un event listener
            if (!searchInput.hasAttribute('data-auto-search-enabled')) {
                
                console.log(`Initialisation de la recherche automatique pour: ${selector}`);
                
                // Marquer l'élément comme ayant la recherche automatique
                searchInput.setAttribute('data-auto-search-enabled', 'true');
                
                // Variable pour stocker le timeout
                let searchTimeout;
                
                // Event listener pour la recherche automatique
                searchInput.addEventListener('input', function() {
                    // Nettoyer le timeout précédent
                    clearTimeout(searchTimeout);
                    
                    // Créer un nouveau timeout
                    searchTimeout = setTimeout(() => {
                        console.log(`Recherche automatique déclenchée pour: ${this.value}`);
                        
                        // Vérifier si l'input fait partie d'un formulaire
                        const form = this.closest('form');
                        if (form) {
                            // Soumettre le formulaire
                            form.submit();
                        } else {
                            // Si pas de formulaire, déclencher un événement personnalisé
                            const searchEvent = new CustomEvent('autoSearch', {
                                detail: { 
                                    value: this.value,
                                    input: this
                                }
                            });
                            document.dispatchEvent(searchEvent);
                        }
                    }, 500); // Délai de 500ms comme dans productsList
                });
                
                // Event listener pour Entrée (pour compatibilité)
                searchInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        clearTimeout(searchTimeout);
                        
                        const form = this.closest('form');
                        if (form) {
                            form.submit();
                        }
                    }
                });
                
                console.log(`Recherche automatique activée pour: ${selector}`);
            }
        }
    });
}

/**
 * Fonction pour activer la recherche automatique sur un élément spécifique
 * @param {string} selector - Sélecteur CSS de l'élément
 * @param {number} delay - Délai en millisecondes (défaut: 500)
 */
function enableAutoSearchForElement(selector, delay = 500) {
    const element = document.querySelector(selector);
    
    if (element && !element.hasAttribute('data-auto-search-enabled')) {
        element.setAttribute('data-auto-search-enabled', 'true');
        
        let searchTimeout;
        
        element.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const form = this.closest('form');
                if (form) {
                    form.submit();
                } else {
                    const searchEvent = new CustomEvent('autoSearch', {
                        detail: { 
                            value: this.value,
                            input: this
                        }
                    });
                    document.dispatchEvent(searchEvent);
                }
            }, delay);
        });
        
        element.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                clearTimeout(searchTimeout);
                
                const form = this.closest('form');
                if (form) {
                    form.submit();
                }
            }
        });
        
        console.log(`Recherche automatique activée pour: ${selector} avec délai: ${delay}ms`);
    }
}

/**
 * Fonction pour désactiver la recherche automatique sur un élément
 * @param {string} selector - Sélecteur CSS de l'élément
 */
function disableAutoSearchForElement(selector) {
    const element = document.querySelector(selector);
    
    if (element && element.hasAttribute('data-auto-search-enabled')) {
        // Cloner l'élément pour supprimer tous les event listeners
        const newElement = element.cloneNode(true);
        element.parentNode.replaceChild(newElement, element);
        
        // Supprimer l'attribut
        newElement.removeAttribute('data-auto-search-enabled');
        
        console.log(`Recherche automatique désactivée pour: ${selector}`);
    }
}

// ========================================
// INITIALISATION AUTOMATIQUE
// ========================================

// Initialiser automatiquement quand le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
    // Attendre un peu pour s'assurer que tous les éléments sont chargés
    setTimeout(() => {
        initializeUniversalAutoSearch();
    }, 100);
});

// Réinitialiser si le contenu de la page change (AJAX, etc.)
if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver(function(mutations) {
        let shouldReinitialize = false;
        
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                // Vérifier si des nouveaux éléments de recherche ont été ajoutés
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const hasSearchInput = node.querySelector && (
                            node.querySelector('input[type="search"]') ||
                            node.querySelector('input[name="q"]') ||
                            node.querySelector('input[name="search"]') ||
                            node.querySelector('.pharmacy-search-input')
                        );
                        
                        if (hasSearchInput) {
                            shouldReinitialize = true;
                        }
                    }
                });
            }
        });
        
        if (shouldReinitialize) {
            setTimeout(() => {
                initializeUniversalAutoSearch();
            }, 100);
        }
    });
    
    // Observer les changements dans le body
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Exporter les fonctions pour utilisation externe
window.PharmacyAutoSearch = {
    init: initializeUniversalAutoSearch,
    enable: enableAutoSearchForElement,
    disable: disableAutoSearchForElement
};
