/**
 * Utilitaires SweetAlert pour le module Pharmacy
 * Évite les affichages répétés de messages de succès/erreur
 */

class PharmacySweetAlertUtils {
    constructor() {
        this.sessionKeys = {
            'config': 'pharmacy_config_success_shown',
            'products': 'pharmacy_products_success_shown',
            'orders': 'pharmacy_orders_success_shown',
            'stock_moves': 'pharmacy_stock_moves_success_shown',
            'suppliers': 'pharmacy_suppliers_success_shown'
        };
    }

    /**
     * Affiche un message de succès seulement si pas déjà affiché pour cette URL
     * @param {string} message - Le message à afficher
     * @param {string} module - Le module (config, products, orders, etc.)
     */
    showSuccessOnce(message, module = 'config') {
        const sessionKey = this.sessionKeys[module] || this.sessionKeys['config'];
        const currentUrl = window.location.href;
        const lastShownUrl = sessionStorage.getItem(sessionKey);

        if (lastShownUrl !== currentUrl) {
            this.showSuccess(message);
            sessionStorage.setItem(sessionKey, currentUrl);
        }
    }

    /**
     * Affiche un message d'erreur seulement si pas déjà affiché pour cette URL
     * @param {string} message - Le message à afficher
     * @param {string} module - Le module (config, products, orders, etc.)
     */
    showErrorOnce(message, module = 'config') {
        const sessionKey = this.sessionKeys[module] || this.sessionKeys['config'];
        const currentUrl = window.location.href;
        const lastShownUrl = sessionStorage.getItem(sessionKey);

        if (lastShownUrl !== currentUrl) {
            this.showError(message);
            sessionStorage.setItem(sessionKey, currentUrl);
        }
    }

    /**
     * Affiche un message de succès standard
     * @param {string} message - Le message à afficher
     */
    showSuccess(message) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: 'Succès !',
                text: message,
                icon: 'success',
                timer: 3000,
                showConfirmButton: false
            });
        } else {
            alert('Succès: ' + message);
        }
    }

    /**
     * Affiche un message d'erreur standard
     * @param {string} message - Le message à afficher
     */
    showError(message) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: 'Erreur !',
                text: message,
                icon: 'error',
                confirmButtonColor: '#dc3545',
                confirmButtonText: 'OK'
            });
        } else {
            alert('Erreur: ' + message);
        }
    }

    /**
     * Nettoie les paramètres URL de succès et affiche le message approprié
     * @param {Object} successMessages - Objet avec les paramètres et messages
     * @param {string} module - Le module concerné
     */
    handleUrlSuccessParams(successMessages, module = 'config') {
        const urlParams = new URLSearchParams(window.location.search);
        const sessionKey = this.sessionKeys[module] || this.sessionKeys['config'];
        const currentUrl = window.location.href;
        const lastShownUrl = sessionStorage.getItem(sessionKey);

        for (const [param, message] of Object.entries(successMessages)) {
            if (urlParams.has(param)) {
                // Ne montrer le message que si on n'a pas déjà montré pour cette URL
                if (lastShownUrl !== currentUrl) {
                    this.showSuccess(message);
                    sessionStorage.setItem(sessionKey, currentUrl);
                }
                // Toujours nettoyer l'URL
                window.history.replaceState({}, document.title, window.location.pathname);
                break;
            }
        }
    }

    /**
     * Nettoie tous les paramètres de succès de l'URL sans afficher de message
     */
    cleanUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const successParams = [
            'success', 'dci_success', 'pharmacy_success', 'location_type_success',
            'location_success', 'operation_type_success', 'category_success', 'unit_success',
            'product_success', 'order_success', 'stock_move_success', 'supplier_success'
        ];

        let hasSuccessParam = false;
        for (const param of successParams) {
            if (urlParams.has(param)) {
                hasSuccessParam = true;
                break;
            }
        }

        if (hasSuccessParam) {
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    }

    /**
     * Réinitialise le cache des messages affichés pour un module
     * @param {string} module - Le module à réinitialiser
     */
    resetCache(module = 'config') {
        const sessionKey = this.sessionKeys[module] || this.sessionKeys['config'];
        sessionStorage.removeItem(sessionKey);
    }

    /**
     * Réinitialise tout le cache des messages affichés
     */
    resetAllCache() {
        Object.values(this.sessionKeys).forEach(key => {
            sessionStorage.removeItem(key);
        });
    }
}

// Instance globale
window.PharmacySweetAlert = new PharmacySweetAlertUtils();

// Nettoyage automatique au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Nettoyer les paramètres URL orphelins après un délai
    setTimeout(() => {
        window.PharmacySweetAlert.cleanUrlParams();
    }, 5000);
});
