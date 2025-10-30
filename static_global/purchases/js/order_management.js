// Variables globales
        let allOrders = []; // Stockage de toutes les commandes
        let currentFilteredOrders = []; // Commandes filtrées par les autres filtres

        // Fonction globale pour la suppression
        function confirmDelete(orderId) {
            Swal.fire({
                title: 'Supprimer la commande ?',
                text: "Cette action est irréversible.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Oui, supprimer',
                cancelButtonText: 'Annuler'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = `/orders/delete/${orderId}/`;
                }
            });
        }

        // Fonction pour recherche alphabétique côté client
        function searchOrders() {
            const searchTerm = document.getElementById("search").value.toLowerCase().trim();

            if (!searchTerm) {
                // Si pas de recherche, afficher toutes les commandes filtrées
                displayOrders(currentFilteredOrders);
                return;
            }

            // Filtrer les commandes par recherche alphabétique
            const searchResults = currentFilteredOrders.filter(order => {
                return order.name.toLowerCase().includes(searchTerm) ||
                    order.partner_name.toLowerCase().includes(searchTerm);
            });

            displayOrders(searchResults);
        }

        // Fonction pour afficher les commandes dans le tableau
        function displayOrders(orders) {
            const tableBody = document.getElementById("order-table-body");
            tableBody.innerHTML = "";

            if (!orders || orders.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="6" class="text-center">Aucune commande trouvée.</td></tr>`;
                return;
            }

            orders.forEach(order => {
                const row = document.createElement("tr");
                row.innerHTML = `
            <td>${order.name}</td>
            <td>${order.partner_name || 'N/A'}</td> <!-- Ensure this matches the backend data -->
            <td>${order.date_order}</td>
            <td>${order.amount_total}</td>
            <td>${order.state_display}</td>
            <td>
                <button class="btn btn-sm btn-light border me-1 view-order-btn" data-order-id="${order.id}" data-bs-toggle="modal" data-bs-target="#order-detail-modal">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-light border me-1 edit-order-btn" data-order-id="${order.id}">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-light border text-danger me-1 delete-order-btn" data-order-id="${order.id}">
                    <i class="fas fa-trash-alt"></i>
                </button>
                <button class="btn btn-sm btn-success confirm-order-btn me-1" data-order-id="${order.id}" ${order.state !== 'draft' ? 'disabled' : ''}>
                    <i class="fas fa-check"></i> Confirmer
                </button>
            </td>
        `;
                tableBody.appendChild(row);
            });
        }

        document.addEventListener("DOMContentLoaded", () => {
            const form = document.getElementById("filter-form");
            const tableBody = document.getElementById("order-table-body");

            function fetchFilteredOrders(e) {
                if (e) e.preventDefault();

                const data = {
                    search: '', // Ne pas envoyer la recherche au serveur
                    start_date: document.getElementById("start_date").value,
                    end_date: document.getElementById("end_date").value,
                    supplier: document.getElementById("supplier").value,
                    status: document.getElementById("status").value,
                };

                fetch("{% url 'order_list_filtered' %}", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: new URLSearchParams(data)
                })
                    .then(response => response.json())
                    .then(data => {
                        allOrders = data.orders || [];
                        currentFilteredOrders = [...allOrders]; // Copie des commandes filtrées

                        // Appliquer la recherche après avoir reçu les données
                        searchOrders();
                    })
                    .catch(error => {
                        console.error("Erreur lors du chargement :", error);
                        tableBody.innerHTML = `<tr><td colspan="6" class="text-danger">Erreur lors du chargement des données.</td></tr>`;
                    });
            }

            // Event listeners
            form.addEventListener("submit", fetchFilteredOrders);

            // Recherche en temps réel côté client
            document.getElementById("search").addEventListener("input", () => {
                clearTimeout(window.searchTimeout);
                window.searchTimeout = setTimeout(searchOrders, 300);
            });

            // Filtres qui déclenchent un appel serveur
            document.getElementById("start_date").addEventListener("change", fetchFilteredOrders);
            document.getElementById("end_date").addEventListener("change", fetchFilteredOrders);
            document.getElementById("supplier").addEventListener("change", fetchFilteredOrders);
            document.getElementById("status").addEventListener("change", fetchFilteredOrders);

            fetchFilteredOrders(); // Initial load
        });

        document.addEventListener('DOMContentLoaded', function () {
            const scrollBtn = document.getElementById('scrollToForm');
            if (scrollBtn) {
                scrollBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    const target = document.getElementById('new-order-form');
                    if (target) {
                        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                });
            }

            // Handle edit button click
            document.addEventListener('click', function (e) {
                if (e.target.classList.contains('edit-order-btn')) {
                    const orderId = e.target.getAttribute('data-order-id');
                    window.location.href = `/orders/edit/${orderId}/`;
                }

                // Handle delete button click
                if (e.target.closest('.delete-order-btn')) {
                    const button = e.target.closest('.delete-order-btn');
                    const orderId = button.getAttribute('data-order-id');
                    confirmDelete(orderId);
                }
            });
        });

        // Gestion du clic sur le bouton "Voir les détails"
     document.addEventListener('click', function (e) {
    if (e.target.closest('.view-order-btn')) {
        const button = e.target.closest('.view-order-btn');
        const orderId = button.getAttribute('data-order-id');
        const modalContent = document.getElementById('order-detail-content');
        modalContent.innerHTML = '<p>Chargement des détails...</p>';

        fetch(`/purchases/orders/detail-json/${orderId}/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                const order = data.order;
                const lines = data.order_lines || [];
                let html = `
                    <h6>Commande: ${order.name}</h6>
                    <p><strong>Fournisseur:</strong> ${data.supplier.name || 'N/A'}</p> <!-- Updated to use data.supplier.name -->
                    <p><strong>Date:</strong> ${order.date_order}</p>
                    <p><strong>Statut:</strong> ${order.state_display || order.state}</p>
                    <p><strong>Devise:</strong> ${order.currency || 'MAD'}</p>
                    <p><strong>Notes:</strong> ${order.notes || 'Aucune'}</p>
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
                                    <th>Taxe (€)</th>
                                    <th>Total TTC</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                if (lines.length === 0) {
                    html += `
                        <tr>
                            <td colspan="7" class="text-center">Aucune ligne de commande.</td>
                        </tr>
                    `;
                } else {
                    lines.forEach(line => {
                        html += `
                            <tr>
                                <td>${line.name || 'N/A'}</td>
                                <td>${line.product_qty || 0}</td>
                                <td>${line.price_unit || 0}</td>
                                <td>${line.taxes ? line.taxes.join(', ') : 'Aucune'}</td>
                                <td>${line.price_subtotal || 0}</td>
                                <td>${line.tax_amount || 0}</td>
                                <td>${line.total_ttc || 0}</td>
                            </tr>
                        `;
                    });
                }
                html += `
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td colspan="4" class="text-end"><strong>Total HT:</strong></td>
                                    <td>${order.amount_untaxed || 0}</td>
                                    <td>${order.amount_tax || 0}</td>
                                    <td>${order.amount_total || 0}</td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                `;
                modalContent.innerHTML = html;
            })
            .catch(error => {
                modalContent.innerHTML = '<p class="text-danger">Erreur lors du chargement des détails.</p>';
                console.error('Erreur:', error);
            });
    }
});

// Gestion du clic sur le bouton "Confirmer"
document.addEventListener('click', function (e) {
    if (e.target.closest('.confirm-order-btn')) {
        const button = e.target.closest('.confirm-order-btn');
        const orderId = button.getAttribute('data-order-id');

        Swal.fire({
            title: 'Confirmer la commande ?',
            text: "Vous êtes sur le point de confirmer cette commande.",
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Oui, confirmer',
            cancelButtonText: 'Annuler',
            confirmButtonColor: '#28a745',
            cancelButtonColor: '#d33'
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/purchases/orders/confirm/${orderId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire('Confirmée !', 'La commande a été confirmée.', 'success');
                        // Recharge la liste après confirmation
                        // Soit reload, soit relancer fetchFilteredOrders()
                        setTimeout(() => location.reload(), 1000); // recharge la page après 1s
                    } else {
                        Swal.fire('Erreur', data.error || 'Impossible de confirmer.', 'error');
                    }
                })
                .catch(error => {
                    Swal.fire('Erreur', 'Une erreur est survenue.', 'error');
                    console.error('Erreur:', error);
                });
            }
        });
    }
});