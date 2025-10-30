// Gestion des messages Django pour SweetAlert
function handleDjangoMessages() {
    const messagesContainer = document.getElementById('django-messages');
    if (!messagesContainer) return;

    const messages = messagesContainer.querySelectorAll('.message');
    messages.forEach(messageElement => {
        const level = messageElement.getAttribute('data-level');
        const text = messageElement.getAttribute('data-text');
        
        if (level === 'success') {
            Swal.fire({
                icon: 'success',
                title: 'Succès',
                text: text,
                confirmButtonText: 'OK',
                confirmButtonColor: '#28a745'
            });
        } else if (level === 'error') {
            Swal.fire({
                icon: 'error',
                title: 'Erreur',
                text: text,
                confirmButtonText: 'OK',
                confirmButtonColor: '#dc3545'
            });
        } else if (level === 'warning') {
            Swal.fire({
                icon: 'warning',
                title: 'Attention',
                text: text,
                confirmButtonText: 'OK',
                confirmButtonColor: '#ffc107'
            });
        }
    });

    // Nettoyer le conteneur après affichage
    messagesContainer.remove();
}

class PharmacyOrdersList {
    constructor() {
        this.allOrders = [];
        this.currentFilteredOrders = [];
        this.currentPage = 1;
        this.itemsPerPage = 5;
        this.currentOrderId = null;
        this.initialize();
    }

    initialize() {
        this.setupEventListeners();
        this.fetchFilteredOrders();
    }

    setupEventListeners() {
        // Scroll to form button
        const scrollToFormButton = document.getElementById("scrollToForm");
        if (scrollToFormButton) {
            scrollToFormButton.addEventListener("click", () => {
                const newOrderForm = document.getElementById("order-form") || document.getElementById("new-pharmacy-order-form");
                newOrderForm?.scrollIntoView({ behavior: "smooth", block: "start" });
            });
        }

        // Filter form
        const form = document.getElementById("filter-form");
        if (form) {
            form.addEventListener("submit", (e) => this.fetchFilteredOrders(e));
        }

        // Search input
        const searchInput = document.getElementById("search");
        if (searchInput) {
            searchInput.addEventListener("input", () => {
                clearTimeout(window.searchTimeout);
                window.searchTimeout = setTimeout(() => this.searchOrders(), 300);
            });
        }

        // Filter inputs
        ["start_date", "end_date", "supplier", "status"].forEach(id => {
            const input = document.getElementById(id);
            if (input) input.addEventListener("change", () => this.fetchFilteredOrders());
        });

        // Pagination buttons
        const prevButton = document.getElementById("prev-page");
        const nextButton = document.getElementById("next-page");
        if (prevButton) {
            prevButton.addEventListener("click", () => {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.displayOrders();
                }
            });
        }
        if (nextButton) {
            nextButton.addEventListener("click", () => {
                const totalPages = Math.ceil(this.currentFilteredOrders.length / this.itemsPerPage);
                if (this.currentPage < totalPages) {
                    this.currentPage++;
                    this.displayOrders();
                }
            });
        }

        // Global click handler for buttons
        document.addEventListener("click", (e) => this.handleButtonClicks(e));
    }

    handleButtonClicks(e) {
        const target = e.target.closest(".view-order-btn, .delete-order-btn, .confirm-order-btn, .duplicate-order-btn");
        if (!target) return;

        const orderId = target.getAttribute("data-order-id");
        if (!orderId) return;

        if (target.matches(".view-order-btn")) {
            this.viewOrderDetails(orderId);
        } else if (target.matches(".delete-order-btn")) {
            this.confirmDelete(orderId);
        } else if (target.matches(".confirm-order-btn")) {
            this.confirmOrder(orderId);
        } else if (target.matches(".duplicate-order-btn")) {
            this.duplicateOrder(orderId);
        }
    }

    confirmDelete(orderId) {
        Swal.fire({
            title: "Supprimer la commande ?",
            text: "Cette action est irréversible.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            confirmButtonText: "Oui, supprimer",
            cancelButtonText: "Annuler"
        }).then((result) => {
            if (result.isConfirmed) {
                this.deleteOrder(orderId);
            }
        });
    }

    async deleteOrder(orderId) {
        try {
            const response = await fetch(`/pharmacy/orders/delete/${orderId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            });

            // Vérifier le statut HTTP avant de parser le JSON
            if (!response.ok) {
                console.error('Erreur HTTP:', response.status, response.statusText);
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                Swal.fire({
                    title: 'Supprimé!',
                    text: 'La commande a été supprimée avec succès.',
                    icon: 'success',
                    timer: 2000,
                    showConfirmButton: false
                });
                // Recharger la liste des commandes
                this.fetchFilteredOrders();
            } else {
                Swal.fire({
                    title: 'Erreur!',
                    text: data.error || 'Erreur lors de la suppression de la commande.',
                    icon: 'error'
                });
            }
        } catch (error) {
            console.error('Erreur lors de la suppression:', error);
            Swal.fire({
                title: 'Erreur!',
                text: 'Une erreur est survenue lors de la suppression.',
                icon: 'error'
            });
        }
    }

    getCookie(name) {
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

    searchOrders() {
        const searchInput = document.getElementById("search");
        if (!searchInput) return;

        const searchTerm = searchInput.value.toLowerCase().trim();

        this.currentFilteredOrders = searchTerm
            ? this.allOrders.filter(order => {
                return (
                    (order.name?.toLowerCase().includes(searchTerm)) ||
                    (order.supplier_name?.toLowerCase().includes(searchTerm)) ||
                    (order.date_order?.toLowerCase().includes(searchTerm)) ||
                    (String(order.amount_total)?.toLowerCase().includes(searchTerm)) ||
                    (order.state?.toLowerCase().includes(searchTerm)) ||
                    (order.state_display?.toLowerCase().includes(searchTerm))
                );
            })
            : [...this.allOrders];

        this.currentPage = 1;
        this.displayOrders();
    }

    displayOrders() {
        const tableBody = document.getElementById("order-table-body");
        if (!tableBody) return;

        tableBody.innerHTML = "";

        if (!this.currentFilteredOrders?.length) {
            tableBody.innerHTML = `<tr><td colspan="7" class="text-center">Aucune commande trouvée.</td></tr>`;
            this.updatePaginationInfo("1", true, true);
            return;
        }

        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const paginatedOrders = this.currentFilteredOrders.slice(startIndex, startIndex + this.itemsPerPage);

        paginatedOrders.forEach(order => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${this.escapeHtml(order.name || "N/A")}</td>
                <td>${this.escapeHtml(order.supplier_name || "N/A")}</td>
                <td>${this.escapeHtml(order.date_order || "N/A")}</td>
                <td>${this.escapeHtml(order.amount_total || "0")}</td>
                <td>${this.escapeHtml(order.state_display || order.state || "N/A")}</td>
                <td>
                        <button class="btn btn-sm btn-light border me-1 view-order-btn" data-order-id="${order.id}" data-bs-toggle="modal" data-bs-target="#order-detail-modal">
                            <i class="fas fa-eye"></i>
                        </button>
                        <a href="/pharmacy/orders/edit/${order.id}/" class="btn btn-sm btn-light border me-1">
                            <i class="fas fa-edit"></i>
                        </a>
                        <button class="btn btn-sm btn-light border text-danger me-1 delete-order-btn" data-order-id="${order.id}">
                        <i class="fas fa-trash-alt"></i>
                        </button>

                        <button class="btn btn-sm btn-primary confirm-order-btn me-1" data-order-id="${order.id}" ${order.state !== "draft" ? "disabled" : ""}>
                            <i class="fas fa-check"></i>
                        </button>
                        ${order.state !== "confirmed" ? `<a href="/pharmacy/orders/request-price/${order.id}/pdf/" class="btn btn-sm btn-success me-1"><i class="fas fa-file-invoice"></i></a>` : ""}
                        ${order.state !== "confirmed" ? `<button class="btn btn-sm btn-warning duplicate-order-btn" data-order-id="${order.id}"><i class="fas fa-copy"></i></button>` : ""}
                    </td>
            `;
            tableBody.appendChild(row);
        });

        this.updatePagination();
    }

    updatePagination() {
        const totalPages = Math.ceil(this.currentFilteredOrders.length / this.itemsPerPage);
        this.updatePaginationInfo(` ${this.currentPage}`, this.currentPage === 1, this.currentPage === totalPages || totalPages === 0);
    }

    updatePaginationInfo(pageText, prevDisabled, nextDisabled) {
        const pageInfo = document.getElementById("page-info");
        const prevButton = document.getElementById("prev-page");
        const nextButton = document.getElementById("next-page");

        if (pageInfo) pageInfo.textContent = pageText;
        if (prevButton) prevButton.disabled = prevDisabled;
        if (nextButton) nextButton.disabled = nextDisabled;
    }

    escapeHtml(text) {
        const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
        return text.toString().replace(/[&<>"']/g, m => map[m]);
    }

    async fetchFilteredOrders(e) {
        if (e) e.preventDefault();

        const inputs = {
            start_date: document.getElementById("start_date")?.value || "",
            end_date: document.getElementById("end_date")?.value || "",
            supplier: document.getElementById("supplier")?.value || "",
            status: document.getElementById("status")?.value || ""
        };
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value;

        if (!csrfToken) {
            console.error("Token CSRF non trouvé");
            return;
        }

        try {
            const response = await fetch(window.ORDER_LIST_FILTERED_URL, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({ ...inputs, search: "" })
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            this.allOrders = data.orders || [];
            this.currentFilteredOrders = [...this.allOrders];
            this.currentPage = 1;
            this.displayOrders();
        } catch (error) {
            console.error("Erreur lors du chargement :", error);
            const tableBody = document.getElementById("order-table-body");
            if (tableBody) {
                tableBody.innerHTML = `<tr><td colspan="7" class="text-danger">Erreur lors du chargement des données.</td></tr>`;
            }
        }
    }

    async viewOrderDetails(orderId) {
        this.currentOrderId = orderId;
        const modalContent = document.getElementById("order-detail-content");
        if (!modalContent) return;

        modalContent.innerHTML = "<p>Chargement des détails...</p>";

        try {
            const response = await fetch(`/pharmacy/orders/detail-json/${orderId}/`, {
                method: "GET",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")?.value || "",
                    "Content-Type": "application/json"
                }
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            const order = data.order || {};
            const supplier = data.supplier || {};
            const lines = data.order_lines || [];

            let html = `
                <h1>Commande Pharmacie: ${this.escapeHtml(order.name || "N/A")}</h1>
                <div class="order-info">
                    <p><strong>Fournisseur:</strong> ${this.escapeHtml(supplier.name || "N/A")}</p>
                    <p><strong>Adresse:</strong> ${this.escapeHtml(supplier.address || "N/A")}</p>
                    <p><strong>Date:</strong> ${this.escapeHtml(order.date_order || "N/A")}</p>
                    <p><strong>Statut:</strong> ${this.escapeHtml(order.state_display || order.state || "N/A")}</p>
                    <p><strong>Devise:</strong> ${this.escapeHtml(order.currency || "MAD")}</p>
                    <p><strong>Notes:</strong> ${this.escapeHtml(order.notes || "Aucune")}</p>
                `;

            if (order.state === "confirmed") {
                html += `
                    <div class="order-info">
                        <p><strong>Référence Fournisseur :</strong> ${this.escapeHtml(order.supplier_ref || "Non spécifiée")}</p>
                        <p><strong>Mode de Paiement :</strong> ${this.escapeHtml(order.payment_mode || "Non spécifié")}</p>
                    </div>
                `;
            }

            html += `
                </div>
                <h6>Lignes de commande</h6>
                <div class="table-responsive">
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Produit</th>
                                <th>Quantité</th>
                                <th>Prix unitaire</th>
                                <th>Taxe</th>
                                <th>Sous-total HT</th>
                                <th>Taxe (MAD)</th>
                                <th>Total TTC</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            html += lines.length === 0
                ? `<tr><td colspan="7" class="text-center">Aucune ligne de commande.</td></tr>`
                : lines.map(line => `
                    <tr>
                        <td>${this.escapeHtml(line.name || "N/A")}</td>
                        <td>${this.escapeHtml(line.product_qty || "0")}</td>
                        <td>${this.escapeHtml(line.price_unit || "0")}</td>
                        <td>${this.escapeHtml(line.tax?.valeur ? line.tax.valeur + "%" : "Aucune")}</td>
                        <td>${this.escapeHtml(line.price_subtotal || "0")}</td>
                        <td>${this.escapeHtml(line.tax_amount || "0")}</td>
                        <td>${this.escapeHtml(line.total_ttc || "0")}</td>
                    </tr>
                `).join("");

            html += `
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colspan="4" class="text-end"><strong>Total HT:</strong></td>
                                <td>${this.escapeHtml(order.amount_untaxed || "0")}</td>
                                <td>${this.escapeHtml(order.amount_tax || "0")}</td>
                                <td>${this.escapeHtml(order.amount_total || "0")}</td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            `;

            modalContent.innerHTML = html;

            const printButton = document.getElementById("print-order-btn");
            if (printButton) {
                printButton.setAttribute("data-order-id", orderId);
                printButton.onclick = () => {
                    window.location.href = `/pharmacy/order/${orderId}/pdf/`;
                };
            }
        } catch (error) {
            modalContent.innerHTML = `<p class="text-danger">Erreur lors du chargement des détails.</p>`;
            console.error("Erreur:", error);
        }
    }

    async confirmOrder(orderId) {
        const result = await Swal.fire({
            title: "Référence fournisseur",
            input: "text",
            inputLabel: "Entrez la référence du fournisseur",
            inputPlaceholder: "REF-FOURNISSEUR",
            inputValidator: value => !value?.trim() ? "La référence est requise !" : null,
            showCancelButton: true,
            confirmButtonText: "Suivant",
            cancelButtonText: "Annuler"
        });

        if (!result.isConfirmed || !result.value) return;

        const supplierRef = result.value.trim();
        const result2 = await Swal.fire({
            title: "Mode de paiement",
            input: "select",
            inputOptions: window.PAYMENT_MODES,
            inputPlaceholder: "Choisissez un mode",
            showCancelButton: true,
            confirmButtonText: "Confirmer",
            cancelButtonText: "Annuler"
        });

        if (!result2.isConfirmed || !result2.value) return;

        const paymentModeId = result2.value;
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value;

        if (!csrfToken) {
            Swal.fire("Erreur", "Token CSRF non trouvé.", "error");
            return;
        }

        try {
            const response = await fetch(`/pharmacy/orders/confirm/${orderId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ supplier_ref: supplierRef, payment_mode_id: paymentModeId })
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            if (data.success) {
                Swal.fire("Confirmée !", "La commande a été confirmée avec succès.", "success")
                    .then(() => location.reload());
            } else {
                Swal.fire("Erreur", data.error || "Impossible de confirmer.", "error");
            }
        } catch (error) {
            Swal.fire("Erreur", "Une erreur est survenue.", "error");
            console.error("Erreur:", error);
        }
    }

    async duplicateOrder(orderId) {
        const result = await Swal.fire({
            title: "Choisir le fournisseur",
            html: `
                <select id="new-supplier-id" class="swal2-select" style="width: 80%; padding: 8px; border-radius: 4px; border: 1px solid #ccc;">
                    ${window.SUPPLIERS_OPTIONS || ''}
                </select>
            `,
            showCancelButton: true,
            confirmButtonText: "Dupliquer",
            cancelButtonText: "Annuler",
            didOpen: () => {
                const select = document.getElementById("new-supplier-id");
                if (select) {
                    select.style.fontSize = "14px";
                    select.style.boxSizing = "border-box";
                }
            },
            preConfirm: () => {
                const supplierId = document.getElementById("new-supplier-id")?.value;
                if (!supplierId) {
                    Swal.showValidationMessage("Veuillez sélectionner un fournisseur.");
                    return false;
                }
                return supplierId;
            }
        });

        if (result.isConfirmed) {
            const supplierId = result.value;
            const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value;

            if (!csrfToken) {
                Swal.fire("Erreur", "Token CSRF non trouvé.", "error");
                return;
            }

            try {
                const response = await fetch(`/pharmacy/orders/duplicate/${orderId}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ supplier_id: supplierId })
                });

                // Vérifier le statut HTTP avant de parser le JSON
                if (!response.ok) {
                    console.error('Erreur HTTP:', response.status, response.statusText);
                    throw new Error(`Erreur HTTP: ${response.status}`);
                }

                const data = await response.json();
                if (data.success) {
                    Swal.fire("Succès", "Commande dupliquée avec succès.", "success")
                        .then(() => location.reload());
                } else {
                    Swal.fire("Erreur", data.error || "Erreur inconnue.", "error");
                }
            } catch (error) {
                Swal.fire("Erreur", "Une erreur est survenue.", "error");
                console.error("Erreur:", error);
            }
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    // Gérer les messages Django en premier
    handleDjangoMessages();
    
    // Initialiser la liste des commandes
    new PharmacyOrdersList();
}); 