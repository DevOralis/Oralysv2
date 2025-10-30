/**
 * Met à jour la coloration des badges d'état.
 * @param {string} activeState - draft | confirmed | done | canceled
 */
function updateBadgeStates(activeState) {
  document.querySelectorAll('.badge-state').forEach(badge => {
    badge.classList.remove(
      'badge-draft-active',
      'badge-confirmed-active',
      'badge-done-active',
      'badge-canceled-active'
    );
    switch (badge.dataset.state) {
      case 'draft':
        if (activeState === 'draft') badge.classList.add('badge-draft-active');
        break;
      case 'confirmed':
        if (activeState === 'confirmed')
          badge.classList.add('badge-confirmed-active');
        break;
      case 'done':
        if (activeState === 'done') badge.classList.add('badge-done-active');
        break;
      case 'canceled':
        if (activeState === 'canceled')
          badge.classList.add('badge-canceled-active');
        break;
    }
  });
}

/**
 * Affiche/masque la colonne "quantité arrivée" et la date effective
 * en fonction de l'état du mouvement.
 * @param {string} state - draft | confirmed | done | canceled
 */
function updateFormFields(state) {
  const effectiveDateField = document.getElementById('effective-date-field');
  const arrivedColumn = document.getElementById('arrived-column');
  const arrivedCells = document.querySelectorAll('.arrived-cell');

  const showArrived = state === 'done';
  if (effectiveDateField) effectiveDateField.style.display = showArrived ? 'block' : 'none';
  if (arrivedColumn)     arrivedColumn.style.display   = showArrived ? 'table-cell' : 'none';
  arrivedCells.forEach(cell => (cell.style.display = showArrived ? 'table-cell' : 'none'));
}

/* ---------------------------- Code principal ------------------------------ */
document.addEventListener('DOMContentLoaded', () => {
  // Vérifier si les scripts JSON sont présents
  const stockScriptElement = document.getElementById('stock-by-product-location');
  const productsScriptElement = document.getElementById('products-data');
  console.log('Script stock-by-product-location présent:', !!stockScriptElement);
  console.log('Script products-data présent:', !!productsScriptElement);
  if (stockScriptElement) {
    console.log('Contenu du script stock:', stockScriptElement.textContent.substring(0, 100) + '...');
  }
  console.log('===============================');
  
  /* ----- Sélecteurs principaux ----- */
  const tbody            = document.getElementById('move-lines-tbody');
  const addRowBtn        = document.getElementById('add-row-btn');
  const productsScript   = document.getElementById('products-data');
  const orderSelect      = document.getElementById('order-select');
  const supplierSelect   = document.getElementById('supplier-select');
  const opTypeSelect     = document.getElementById('id_operation_type');
  const sourceLocationCol= document.getElementById('source-location-col');
  const destLocationCol  = document.getElementById('dest-location-col');
  const departmentField  = document.getElementById('department-field');
  const supplierField    = document.getElementById('supplier-field');
  const orderField       = document.getElementById('order-field');
  const linesInput       = document.getElementById('lines-json');
  const moveForm         = document.getElementById('move-form');

  const isEdit = !!moveForm && !!moveForm.getAttribute('data-state') && moveForm.getAttribute('data-state') !== 'draft';
  const isCanceled = !!moveForm && moveForm.getAttribute('data-state') === 'canceled';

  // Si le mouvement est annulé, désactiver toutes les interactions
  if (isCanceled) {
    // Désactiver tous les champs de formulaire
    const formInputs = moveForm.querySelectorAll('input, select, textarea, button[type="submit"]');
    formInputs.forEach(input => {
      if (input.type !== 'hidden') {
        input.disabled = true;
      }
    });
    
    // Désactiver le bouton d'ajout de ligne
    if (addRowBtn) {
      addRowBtn.style.display = 'none';
    }
    
    // Désactiver les boutons de suppression dans le tableau
    const deleteButtons = tbody.querySelectorAll('.btn-delete-line');
    deleteButtons.forEach(btn => {
      btn.style.display = 'none';
    });
    
    return; 
  }

  /* ----- Chargement des produits ----- */
  let productsData = [];
  try {
    productsData = JSON.parse(productsScript ? productsScript.textContent : '[]');
  } catch (e) {
    productsData = [];
  }

  // Charger les données de stock depuis le script JSON
  let stockByProductLocation = {};
  try {
    const stockScript = document.getElementById('stock-by-product-location');
    if (stockScript && stockScript.textContent) {
      stockByProductLocation = JSON.parse(stockScript.textContent);
    }
  } catch (e) {
    console.error('Erreur lors du chargement des données de stock:', e);
    stockByProductLocation = {};
  }

  // Exposer les données globalement pour la validation
  window.stockByProductLocation = stockByProductLocation;
  window.productsData = productsData;
  
  console.log('=== DONNÉES CHARGÉES ===');
  console.log('stockByProductLocation chargé:', Object.keys(stockByProductLocation).length, 'entrées');
  console.log('productsData chargé:', productsData.length, 'produits');
  console.log('========================');

  /* ----------------- Fonctions utilitaires internes ----------------- */

  /** Crée un <select> produit avec Select2 (si dispo). */
  function createProductSelect(selectedId = '') {
    const select = document.createElement('select');
    select.name = 'product';
    select.className = 'form-select';
    let options = '<option value="">Choisir un produit</option>';
    productsData.forEach(prod => {
      const displayName = prod.name || 'Produit sans nom';
      options += `<option value="${prod.id}" ${prod.id == selectedId ? 'selected' : ''}>
                    ${displayName}
                  </option>`;
    });
    select.innerHTML = options;

    // Appliquer les styles initiaux
    if (selectedId) {
      select.setAttribute('data-selected', 'true');
      select.style.color = '#212529';
    } else {
      select.setAttribute('data-selected', 'false');
      select.style.color = '#6c757d';
    }

    // Activation Select2 si présent
    if (typeof $ !== 'undefined' && $.fn.select2) {
      $(select).select2({
        placeholder: 'Choisir un produit',
        allowClear : true
      }).on('change', function() {
        // Appliquer les styles après changement avec Select2
        if (this.value === '') {
          this.setAttribute('data-selected', 'false');
          this.style.color = '#6c757d';
        } else {
          this.setAttribute('data-selected', 'true');
          this.style.color = '#212529';
        }
      });
    } else {
      // Pour les selects sans Select2, ajouter l'écouteur d'événement
      select.addEventListener('change', function() {
        if (this.value === '') {
          this.setAttribute('data-selected', 'false');
          this.style.color = '#6c757d';
        } else {
          this.setAttribute('data-selected', 'true');
          this.style.color = '#212529';
        }
      });
    }
    return select;
  }

  /** Renvoie l'objet produit à partir de son ID. */
  const getProductById = id => productsData.find(p => p.id == id);

  /**
   * Ajoute une ligne dans le tableau.
   * @param {string|number} productId
   * @param {string|number} quantity
   * @param {string|number} uomId
   * @param {string|number} quantityArrived
   */
  function addLine(productId = '', quantity = '', uomId = '', quantityArrived = '') {
    if (!tbody) return;

    const tr = document.createElement('tr');

    /* -- Colonne produit -- */
    const tdProduct = document.createElement('td');
    tdProduct.dataset.label = 'Produit ';
    const productSelect = createProductSelect(productId);
    tdProduct.appendChild(productSelect);
    tr.appendChild(tdProduct);

    /* -- Colonne quantité demandée -- */
    const tdQty = document.createElement('td');
    tdQty.dataset.label = 'Qté.D ';
    const inputQty = document.createElement('input');
    inputQty.type  = 'number';
    inputQty.name  = 'quantity_demanded';
    inputQty.className = 'form-control';
    inputQty.value = quantity;
    inputQty.min   = 0;
    inputQty.step  = '0.01';
    inputQty.readOnly = moveForm?.dataset.state === 'done';
    tdQty.appendChild(inputQty);
    tr.appendChild(tdQty);

    /* -- Colonne unité (lecture seule) -- */
    const tdUom = document.createElement('td');
    tdUom.dataset.label = 'Unité ';
    const uomInput  = document.createElement('input');
    const uomHidden = document.createElement('input');
    uomInput .type  = 'text';
    uomInput .className = 'form-control';
    uomInput .name  = 'uom_label';
    uomInput .readOnly = true;
    uomInput .tabIndex = -1;
    uomHidden.type  = 'hidden';
    uomHidden.name  = 'uom';

    const prod = getProductById(productId);
    if (prod) {
      uomInput.value  = prod.uom_label;
      uomHidden.value = prod.uom_id;
    }
    tdUom.appendChild(uomInput);
    tdUom.appendChild(uomHidden);
    tr.appendChild(tdUom);

    // Colonne quantité arrivée (visible uniquement en "done")
    const isDone = (moveForm?.dataset.state || 'draft') === 'done';
    let inputArrived = null;
    if (isDone) {
      const tdArrived = document.createElement('td');
      tdArrived.setAttribute('data-label', 'Qté.A ');
      tdArrived.className = 'arrived-cell';
      inputArrived = document.createElement('input');
      inputArrived.type  = 'number';
      inputArrived.name  = 'quantity_arrived';
      inputArrived.className = 'form-control';
      inputArrived.value = quantityArrived;
      inputArrived.min   = 0;
      inputArrived.step  = '0.01';
      inputArrived.readOnly = true;
      tdArrived.appendChild(inputArrived);
      tr.appendChild(tdArrived);
    }

    /* -- Colonne suppression -- */
    const tdDel = document.createElement('td');
    tdDel.dataset.label = 'Supp ';
    const btnDel = document.createElement('button');
    btnDel.type  = 'button';
    btnDel.className = 'btn btn-link text-danger btn-delete-row';
    btnDel.innerHTML = '<i class="fas fa-trash-alt"></i>';
    btnDel.onclick = () => {
      if (tbody.rows.length > 1) {
        tr.remove();
        updateLinesJson();
      } else {
        Swal.fire({
          icon: 'error',
          title: 'Erreur',
          text : 'Il doit rester au moins une ligne.',
          confirmButtonColor: '#dc3545',
          confirmButtonText: 'OK'
        });
      }
    };
    if (moveForm?.dataset.state !== 'done') {
      tdDel.appendChild(btnDel);
    }
    tr.appendChild(tdDel);

    /* -- Listeners de mise à jour -- */
    productSelect.addEventListener('change', () => {
      const p = getProductById(productSelect.value);
      uomInput.value  = p ? p.uom_label : '';
      uomHidden.value = p ? p.uom_id    : '';
      updateLinesJson();
    });
    inputQty    .addEventListener('input', updateLinesJson);
    if (inputArrived) inputArrived.addEventListener('input', updateLinesJson);

    tbody.appendChild(tr);
    updateLinesJson();
  }
  window.addLine = addLine; // utilisé par le pré‑remplissage serveur

  /** Vide toutes les lignes du tableau. */
  const clearLines = () => {
    if (tbody) {
      tbody.innerHTML = '';
      updateLinesJson();
    }
  };

  /** Sérialise les lignes dans le champ caché "lines-json". */
  function updateLinesJson() {
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const data = rows.map(r => ({
      product          : r.querySelector('select[name="product"]')?.value || '',
      quantity_demanded: r.querySelector('input[name="quantity_demanded"]')?.value || '',
      uom              : r.querySelector('input[name="uom"]')?.value || '',
      quantity_arrived : r.querySelector('input[name="quantity_arrived"]')?.value || ''
    }));
    if (linesInput) linesInput.value = JSON.stringify(data);
  }

  /* ------------------ Fetch commandes & lignes (livraison) ----------------- */

  function loadOrdersForSupplier(supplierId, cb) {
    if (!supplierId) {
      orderSelect.innerHTML = '<option value="">Choisir une commande</option>';
      clearLines();
      cb?.([]);
      return;
    }

    fetch(`/inventory/api/purchase_orders?supplier_id=${supplierId}`)
      .then(r => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(json => {
        const orders = Array.isArray(json) ? json : json.orders || [];
        orderSelect.innerHTML = '<option value="">Choisir une commande</option>';

        orders.forEach(o => {
          const opt = document.createElement('option');
          opt.value = o.id;
          opt.textContent = o.name;
          orderSelect.appendChild(opt);
        });

        if (typeof $ !== 'undefined' && $.fn.select2) {
          $('#order-select').select2({
            placeholder: 'Choisir une commande',
            allowClear : true
          });
        }
        cb?.(orders);
      })
      .catch(err => {
        Swal.fire({
          icon: 'error',
          title: 'Erreur de chargement',
          text : 'Impossible de charger les commandes.',
          confirmButtonColor: '#dc3545',
          confirmButtonText: 'OK'
        });
        cb?.([]);
      });
  }

  function loadLinesForOrder(orderId) {
    if (!orderId) {
      clearLines();
      return;
    }
    fetch(`/inventory/api/purchase_order_lines?order_id=${orderId}`)
      .then(r => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(json => {
        const lines = Array.isArray(json) ? json : json.lines || [];
        clearLines();
        if (!lines.length) {
          Swal.fire({
            icon: 'warning',
            title: 'Aucune ligne',
            text : 'Aucune ligne de commande trouvée.',
            confirmButtonColor: '#dc3545',
            confirmButtonText: 'OK'
          });
        } else {
          lines.forEach(l =>
            addLine(l.product_id, l.product_qty, l.product_uom_id, '')
          );
          updateLinesJson();
        }
      })
      .catch(err => {
        Swal.fire({
          icon: 'error',
          title: 'Erreur de chargement',
          text : 'Impossible de charger les lignes de commande.',
          confirmButtonColor: '#dc3545',
          confirmButtonText: 'OK'
        });
      });
  }

  /* ------------------------- Affichage conditionnel ------------------------ */

  function normalizeString(str) {
    return str
      .normalize('NFD') // décompose les accents
      .replace(/[\u0300-\u036f]/g, '') // enlève les accents
      .replace(/\s+/g, ' ') // remplace espaces multiples/insécables par espace simple
      .trim();
  }

  function toggleFields() {
    if (
      !opTypeSelect ||
      !sourceLocationCol ||
      !destLocationCol ||
      !departmentField ||
      !supplierField ||
      !orderField
    ) {
      return;
    }

    const label = normalizeString(opTypeSelect.options[opTypeSelect.selectedIndex].text.toLowerCase());
    const isReception = label.includes('reception') || label.includes('réception');
    const isConsommation = label.includes('consommation');
    const isTransfert = label.includes('transfert');

    // Masquer tous les champs conditionnels par défaut
    document.querySelectorAll('.field-conditional').forEach(field => {
      field.classList.remove('show');
    });

    // Masquer spécifiquement les champs de sélection
    sourceLocationCol.classList.remove('show');
    destLocationCol.classList.remove('show');
    departmentField.classList.remove('show');
    supplierField.classList.remove('show');
    if (orderField) orderField.classList.remove('show');

    // Afficher les champs selon le type d'opération
    if (isTransfert) {
      // Pour les transferts : afficher emplacements source et destination
      sourceLocationCol.classList.add('show');
      destLocationCol.classList.add('show');
    } else if (isConsommation) {
      // Pour les consommations : afficher emplacement source et département
      sourceLocationCol.classList.add('show');
      departmentField.classList.add('show');
    } else if (isReception) {
      // Pour les réceptions : afficher emplacement destination et fournisseur
      destLocationCol.classList.add('show');
      supplierField.classList.add('show');
      if (!isEdit && orderField) {
        orderField.classList.add('show');
      }
    }

    // Réinitialiser les sélecteurs inutiles
    if (!isReception) {
      if (orderSelect) {
        orderSelect.innerHTML = '<option value="">Choisir une commande</option>';
        clearLines();
      }
    }
  }

  /* ------------------------------ Listeners -------------------------------- */

  // Changement type d'opération
  opTypeSelect?.addEventListener('change', toggleFields);
  
  // Appeler toggleFields immédiatement pour masquer les champs par défaut
  if (opTypeSelect) {
    toggleFields(); // initial - masque tous les champs
  }

  // Gestion des placeholders et couleurs des champs de sélection
  function updateSelectStyles() {
    document.querySelectorAll('.form-select').forEach(select => {
      if (select.value === '') {
        select.setAttribute('data-selected', 'false');
        select.style.color = '#6c757d';
      } else {
        select.setAttribute('data-selected', 'true');
        select.style.color = '#212529';
      }
      
      // Gestion spéciale pour Select2
      if (typeof $ !== 'undefined' && $.fn.select2 && $(select).hasClass('select2-hidden-accessible')) {
        const select2Container = $(select).next('.select2-container');
        if (select.value === '') {
          select2Container.find('.select2-selection__rendered').css('color', '#6c757d');
        } else {
          select2Container.find('.select2-selection__rendered').css('color', '#212529');
        }
      }
    });
  }

  // Appliquer les styles initiaux
  updateSelectStyles();

  // Écouter les changements sur tous les selects
  document.querySelectorAll('.form-select').forEach(select => {
    select.addEventListener('change', updateSelectStyles);
  });

  // Changement fournisseur
  supplierSelect?.addEventListener('change', () => {
    loadOrdersForSupplier(supplierSelect.value, () => {
      orderSelect.value = '';
      clearLines();
    });
  });

  // Changement commande
  orderSelect?.addEventListener('change', () => {
    loadLinesForOrder(orderSelect.value);
  });

  // Ajout manuel de ligne
  addRowBtn?.addEventListener('click', e => {
    if (moveForm && moveForm.dataset.state === 'done') return;
    e.preventDefault();
    addLine();
  });

  /* -------------------- Pré‑remplissage (édition serveur) ------------------ */
  const moveLinesScript = document.getElementById('move-lines-data');
  if (moveLinesScript) {
    try {
      const moveLines = JSON.parse(moveLinesScript.textContent);
      if (Array.isArray(moveLines) && moveLines.length) {
        tbody.innerHTML = '';
        moveLines.forEach(l =>
          addLine(l.product_id, l.quantity_demanded, l.uom_id, l.quantity_arrived)
        );
      }
    } catch (e) {
      // Error handled silently
    }
  }

  // Si tableau vide, ajouter une ligne par défaut
  if (tbody && !tbody.querySelector('tr')) addLine();
  
  // Test SweetAlert
  console.log('Test SweetAlert...');
  if (typeof Swal !== 'undefined') {
    console.log('SweetAlert est disponible');
  } else {
    console.error('❌ SweetAlert n\'est pas disponible!');
  }

  /* ----------------------- Validation & soumission ------------------------- */
  moveForm?.addEventListener('submit', e => {
    let hasError = false;
    const seenProducts = new Set();

    const isConsommation = opTypeSelect?.selectedOptions[0].text.toLowerCase().includes('consommation');
    const isReception   = opTypeSelect?.selectedOptions[0].text.toLowerCase().includes('réception');
    const isTransfert = opTypeSelect?.selectedOptions[0].text.toLowerCase().includes('transfert');
    const sourceLocation = document.querySelector('[name="source_location"]')?.value;
    const destField   = document.querySelector('[name="dest_location"]');
    const sourceField = document.querySelector('[name="source_location"]');

    const data = Array.from(tbody.querySelectorAll('tr')).map(row => {
      const productSelect = row.querySelector('select[name="product"]');
      const qtyInput = row.querySelector('input[name="quantity_demanded"]');
      const uomInput = row.querySelector('input[name="uom"]');
      const qtyArrInput = row.querySelector('input[name="quantity_arrived"]');

      const product = productSelect ? productSelect.value : '';
      const qtyDem  = qtyInput ? parseFloat(qtyInput.value) : 0;
      const qtyArr  = qtyArrInput ? parseFloat(qtyArrInput.value) : 0;
      const uom     = uomInput ? uomInput.value : '';

      // Vérif produit sélectionné
      if (!product || !qtyDem || !uom) {
        hasError = true;
        productSelect?.classList.add('is-invalid');
        qtyInput?.classList.add('is-invalid');
        console.log('❌ Données manquantes - produit:', product, 'qty:', qtyDem, 'uom:', uom);
        // Ne pas afficher l'alerte ici, on va l'afficher à la fin
        return { product, quantity_demanded: qtyDem, uom, quantity_arrived: qtyArr, error: 'missing_data' };
      } else {
        productSelect?.classList.remove('is-invalid');
        qtyInput?.classList.remove('is-invalid');
      }

      // Duplication produit
      if (seenProducts.has(product)) {
        hasError = true;
        productSelect?.classList.add('is-invalid');
        console.log('❌ Produit dupliqué:', product);
        // Ne pas afficher l'alerte ici, on va l'afficher à la fin
        return { product, quantity_demanded: qtyDem, uom, quantity_arrived: qtyArr, error: 'duplicate' };
      } else {
        seenProducts.add(product);
      }

        // Vérif stock dispo (si défini globalement)
        console.log('=== VALIDATION STOCK INVENTORY ===');
        console.log('isConsommation:', isConsommation);
        console.log('isTransfert:', isTransfert);
        console.log('window.stockByProductLocation exists:', !!window.stockByProductLocation);
        console.log('sourceLocation:', sourceLocation);
        console.log('product:', product);
        console.log('qtyDem:', qtyDem);
        console.log('qtyArr:', qtyArr);
        
        if (
          (isConsommation || isTransfert) &&
          window.stockByProductLocation && sourceLocation && product
        ) {
          const stockKey = `${product}_${sourceLocation}`;
          const stockDispo = window.stockByProductLocation[stockKey] ?? null;
          
          if (stockDispo === null || stockDispo === undefined) {
            console.log('❌ Produit absent de l\'emplacement source');
            hasError = true;
            return { product, quantity_demanded: qtyDem, uom, quantity_arrived: qtyArr, error: 'absent' };
          } else {
            console.log('✅ Produit trouvé, stock disponible:', stockDispo);
            if (qtyDem > stockDispo) {
              console.log('❌ Quantité demandée dépasse le stock');
              hasError = true;
              qtyInput?.classList.add('is-invalid');
              return { product, quantity_demanded: qtyDem, uom, quantity_arrived: qtyArr, error: 'qty_demanded', stockDispo };
            }
            if (qtyArrInput && qtyArr > stockDispo) {
              console.log('❌ Quantité arrivée dépasse le stock');
              hasError = true;
              qtyArrInput.classList.add('is-invalid');
              return { product, quantity_demanded: qtyDem, uom, quantity_arrived: qtyArr, error: 'qty_arrived', stockDispo };
            }
          }
        } else {
          console.log('⚠️ Validation stock ignorée:', {
            isConsommation,
            isTransfert,
            hasStockData: !!window.stockByProductLocation,
            sourceLocation,
            product
          });
        }
        console.log('=== FIN VALIDATION STOCK ===');

        return { product, quantity_demanded: qtyDem, uom, quantity_arrived: qtyArr };
      });

      // Afficher les alertes appropriées selon les erreurs collectées
      const errors = data.filter(item => item.error);
      if (errors.length > 0) {
        const error = errors[0]; // Afficher la première erreur
        
        switch (error.error) {
          case 'missing_data':
            Swal.fire({
              icon: 'error',
              title: 'Données manquantes',
              text: 'Veuillez sélectionner un produit et saisir une quantité demandée.',
              confirmButtonColor: '#dc3545',
              confirmButtonText: 'OK'
            });
            break;
          case 'duplicate':
            Swal.fire({
              icon: 'error',
              title: 'Produit dupliqué',
              text: 'Un même produit ne peut pas être sélectionné plusieurs fois.',
              confirmButtonColor: '#dc3545',
              confirmButtonText: 'OK'
            });
            break;
          case 'absent':
            Swal.fire({
              icon: 'error',
              title: 'Produit absent de l\'emplacement source',
              text: "Ce produit n'existe pas dans l'emplacement d'origine.",
              confirmButtonColor: '#dc3545',
              confirmButtonText: 'OK'
            });
            break;
          case 'qty_demanded':
            Swal.fire({
              icon: 'warning',
              title: 'Stock insuffisant',
              text: `La quantité demandée (${error.quantity_demanded}) dépasse le stock disponible (${error.stockDispo}).`,
              confirmButtonColor: '#dc3545',
              confirmButtonText: 'OK'
            });
            break;
          case 'qty_arrived':
            Swal.fire({
              icon: 'warning',
              title: 'Stock insuffisant',
              text: `La quantité réellement transférée (${error.quantity_arrived}) dépasse le stock disponible (${error.stockDispo}).`,
              confirmButtonColor: '#dc3545',
              confirmButtonText: 'OK'
            });
            break;
        }
        
        e.preventDefault();
        return false;
      }

    // Vérif emplacements identiques (transfert)
    if (!isConsommation && !isReception && sourceField && destField &&
        sourceField.value && destField.value && sourceField.value === destField.value) {
      hasError = true;
        Swal.fire({
          icon: 'warning',
          title: 'Emplacements identiques',
        text : "L'emplacement de destination doit être différent de l'emplacement d'origine.",
          confirmButtonColor: '#dc3545',
          confirmButtonText: 'OK'
        });
        destField.classList.add('is-invalid');
        sourceField.classList.add('is-invalid');
      } else {
      destField?.classList.remove('is-invalid');
      sourceField?.classList.remove('is-invalid');
    }

    // Vérif destination obligatoire
    if (!isConsommation && destField && !destField.value) {
      hasError = true;
      Swal.fire({
        icon: 'warning',
        title: 'Emplacement manquant',
        text : 'Veuillez sélectionner un emplacement de destination.',
        confirmButtonColor: '#dc3545',
        confirmButtonText: 'OK'
      });
      destField.classList.add('is-invalid');
    }

    if (hasError) {
      e.preventDefault();
          return false;
    }

    // Sérialisation finale
    if (linesInput) linesInput.value = JSON.stringify(data);
  });

  /* ------------------------ Badges d'état dynamiques ----------------------- */
  if (moveForm) {
    // Init
    const currentState = moveForm.dataset.state || 'draft';
    updateBadgeStates(currentState);
    updateFormFields(currentState);

    // Mise à jour au clic sur les boutons
    moveForm.querySelectorAll('button[name="action"]').forEach(btn =>
      btn.addEventListener('click', () => {
        let newState = currentState;
        switch (btn.value) {
        case 'confirm': newState = 'confirmed'; break;
          case 'done'   : newState = 'done'     ; break;
          case 'cancel' : newState = 'canceled' ; break;
          case 'draft'  :
          case 'save'   :
          default       : newState = 'draft';
      }
      updateBadgeStates(newState);
        updateFormFields(newState);
      })
    );
  }

  document.querySelectorAll('.btn-delete-move').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const form = btn.closest('form');
      const ref = btn.getAttribute('data-ref');
      Swal.fire({
        title: 'Confirmer la suppression',
        text: `Êtes-vous sûr de vouloir supprimer le mouvement ${ref} ?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Oui, supprimer',
        cancelButtonText: 'Annuler',
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d'
      }).then((result) => {
        if (result.isConfirmed) {
          form.submit();
        }
      });
    });
  });

  // Interception du bouton "Valider"
  if (moveForm) {
    moveForm.querySelectorAll('button[name="action"]').forEach(btn => {
      if (btn.value === 'done') {
        btn.addEventListener('click', function(e) {
          // Si on est en mode saisie manuelle, on laisse passer la soumission sans alerte
          if (window.manualArriveeMode) {
            window.manualArriveeMode = false; // reset pour la prochaine fois
            return; // laisse la soumission normale se faire
          }
          // Empêche la boucle infinie si _auto_submit est présent
          if (moveForm.dataset.autoSubmit === "1") {
            // Nettoie le flag pour les prochaines fois
            delete moveForm.dataset.autoSubmit;
            return; // Laisse la soumission normale se faire
          }
          e.preventDefault();

          Swal.fire({
            title: "Validation des quantités",
            text: "La quantité arrivée est-elle identique à la quantité demandée pour tous les produits ?",
            icon: "question",
            showCancelButton: true,
            confirmButtonText: "Oui",
            cancelButtonText: "Non",
            reverseButtons: true,
            focusCancel: true,
            confirmButtonColor: '#28a745',
            cancelButtonColor: '#dc3545'
          }).then((result) => {
            if (result.isConfirmed) {
              // Copier quantité demandée -> quantité arrivée pour chaque ligne
              document.querySelectorAll('tbody#move-lines-tbody tr').forEach(row => {
                const qtyDemanded = row.querySelector('input[name="quantity_demanded"]');
                let qtyArrived = row.querySelector('input[name="quantity_arrived"]');
                if (!qtyArrived) {
                  qtyArrived = document.createElement('input');
                  qtyArrived.type = 'number';
                  qtyArrived.name = 'quantity_arrived';
                  qtyArrived.className = 'form-control';
                  qtyArrived.value = qtyDemanded.value;
                  qtyArrived.min = 0;
                  qtyArrived.step = '0.01';
                  const td = document.createElement('td');
                  td.className = 'arrived-cell';
                  td.appendChild(qtyArrived);
                  row.appendChild(td);
                } else {
                  qtyArrived.value = qtyDemanded.value;
                }
              });
              updateLinesJson();
              // Ajoute un flag pour éviter la boucle
              moveForm.dataset.autoSubmit = "1";
              // Ajoute un champ caché pour signaler la validation auto
              let autoRedirect = moveForm.querySelector('input[name="_auto_redirect"]');
              if (!autoRedirect) {
                autoRedirect = document.createElement('input');
                autoRedirect.type = 'hidden';
                autoRedirect.name = '_auto_redirect';
                autoRedirect.value = '1';
                moveForm.appendChild(autoRedirect);
              }
              btn.click(); // Relance le clic, mais cette fois on laisse passer
            } else if (result.dismiss === Swal.DismissReason.cancel) {
              // Affiche la colonne arrivée même si l'état n'est pas encore 'done'
              // 1. Afficher la colonne dans le header
              let arrivedCol = document.getElementById('arrived-column');
              if (!arrivedCol) {
                const th = document.createElement('th');
                th.id = 'arrived-column';
                th.textContent = 'Arrivée';
                const headerRow = document.querySelector('#products-table thead tr');
                if (headerRow) headerRow.insertBefore(th, headerRow.children[headerRow.children.length - 1]);
              } else {
                arrivedCol.style.display = 'table-cell';
              }
              // 2. Pour chaque ligne, ajouter input si besoin
              document.querySelectorAll('tbody#move-lines-tbody tr').forEach(row => {
                let qtyArrived = row.querySelector('input[name="quantity_arrived"]');
                if (!qtyArrived) {
                  qtyArrived = document.createElement('input');
                  qtyArrived.type = 'number';
                  qtyArrived.name = 'quantity_arrived';
                  qtyArrived.className = 'form-control';
                  qtyArrived.min = 0;
                  qtyArrived.step = '0.01';
                  const td = document.createElement('td');
                  td.setAttribute('data-label', 'Qté.A ');
                  td.className = 'arrived-cell';
                  td.appendChild(qtyArrived);
                  row.insertBefore(td, row.children[row.children.length - 1]);
                } else {
                  qtyArrived.parentElement.style.display = 'table-cell';
                }
              });
              window.manualArriveeMode = true; // active le mode manuel
              Swal.fire({
                icon: 'info',
                title: 'Saisissez les quantités réellement arrivées',
                text: 'Veuillez remplir la colonne "Arrivée" pour chaque produit, puis validez à nouveau.',
                confirmButtonColor: '#dc3545',
                confirmButtonText: 'OK'
              });
            }
          });
        });
      }
    });
  }
});