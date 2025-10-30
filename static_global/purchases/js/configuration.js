document.addEventListener('DOMContentLoaded', () => {
  const { showAlert, showAlertConfirm } = window;

  function getCSRFToken() {
    const cookieValue = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    if (!cookieValue) {
      console.error('CSRF token not found in cookies');
      return '';
    }
    return cookieValue.split('=')[1];
  }

  const entityConfig = {
    country: {
      url: '/purchases/countries',
      fields: [{ id: 'country-name-input', key: 'name', type: 'text' }],
      table: 'country-table',
      columns: [{ key: 'name', class: 'country-name' }],
      searchColumns: [0],
      title: 'Pays'
    },
    city: {
      url: '/purchases/cities',
      fields: [
        { id: 'city-name-input', key: 'name', type: 'text' },
        { id: 'city-country-select', key: 'country', type: 'select' }
      ],
      table: 'city-table',
      columns: [
        { key: 'name', class: 'city-name' },
        { key: 'country_name', class: 'city-country-name' }
      ],
      searchColumns: [0, 1],
      title: 'Ville'
    },
    language: {
      url: '/purchases/languages',
      fields: [{ id: 'lang-name-input', key: 'name', type: 'text' }],
      table: 'language-table',
      columns: [{ key: 'name', class: 'language-name' }],
      searchColumns: [0],
      title: 'Langue'
    },
    tax: {
      url: '/purchases/taxes',
      fields: [
        { id: 'tax-libelle-input', key: 'libelle', type: 'text' },
        { id: 'tax-valeur-input', key: 'valeur', type: 'number' }
      ],
      table: 'tax-table',
      columns: [
        { key: 'libelle', class: 'tax-libelle' },
        { key: 'valeur', class: 'tax-valeur' }
      ],
      searchColumns: [0, 1],
      title: 'Taxe'
    },
    currency: {
      url: '/purchases/currencies',
      fields: [
        { id: 'currency-libelle-input', key: 'libelle', type: 'text' },
        { id: 'currency-abreviation-input', key: 'abreviation', type: 'text', transform: v => v.toUpperCase() }
      ],
      table: 'currency-table',
      columns: [
        { key: 'libelle', class: 'currency-libelle' },
        { key: 'abreviation', class: 'currency-abreviation' }
      ],
      searchColumns: [0, 1],
      title: 'Devise'
    },
    'payment-mode': {
      url: '/purchases/payment-modes', // Updated to match Django URL structure
      fields: [
        { id: 'payment-mode-name-input', key: 'name', type: 'text' },
        { id: 'payment-mode-description-input', key: 'description', type: 'text' }
      ],
      table: 'payment-mode-table',
      columns: [
        { key: 'name', class: 'payment-mode-name' },
        { key: 'description', class: 'payment-mode-description' }
      ],
      searchColumns: [0, 1],
      title: 'Mode de paiement'
    },
    'convention-type': {
      url: '/configuration/type-convention', // URL du premier code adaptée
      fields: [{ id: 'convention-type-libelle-input', key: 'libelle', type: 'text' }],
      table: 'convention-type-table',
      columns: [{ key: 'libelle', class: 'convention-type-libelle' }],
      searchColumns: [0],
      title: 'Type de convention'
    }
  };

  function deleteEntity(entity, id) {
    const config = entityConfig[entity];
    if (!config) {
      showAlert('Erreur', 'Entité non reconnue.', 'error');
      return;
    }

    showAlertConfirm(
      `Confirmer la suppression`,
      `Voulez-vous vraiment supprimer ce ${config.title.toLowerCase()} ?`,
      'warning'
    ).then(result => {
      if (result.isConfirmed) {
        // Use consistent URL pattern for all entities
        const deleteUrl = `${config.url}/delete/${id}/`;

        fetch(deleteUrl, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
          }
        })
          .then(response => {
            if (!response.ok) {
              return response.json().then(err => {
                throw new Error(err.message || `Échec de la suppression du ${config.title.toLowerCase()}`);
              });
            }
            showAlert('Succès', `${config.title} supprimé.`, 'success');
            setTimeout(() => location.reload(), 800);
          })
          .catch(error => {
            showAlert('Erreur', error.message || 'Erreur réseau.', 'error');
            console.error(`Delete ${entity} error:`, error);
          });
      }
    });
  }

  function setupFormToggle(entity) {
    const addBtn = document.querySelector(`.add-entity-btn[data-entity="${entity}"]`);
    const form = document.getElementById(`${entity}-form`);
    const cancelBtn = document.querySelector(`.cancel-entity-btn[data-entity="${entity}"]`);

    if (!addBtn || !form || !cancelBtn) {
      console.warn(`Form elements missing for ${entity}`);
      return;
    }

    addBtn.addEventListener('click', () => {
      form.classList.remove('d-none');
      const container = addBtn.closest('.col-12.col-md-6.text-md-end');
      if (container) {
        container.classList.add('d-none');
      }
    });

    cancelBtn.addEventListener('click', () => {
      form.classList.add('d-none');
      const addContainer = addBtn.closest('.d-flex') || addBtn.closest('.col-12.col-md-6.text-md-end');
      if (addContainer) {
        addContainer.classList.remove('d-none');
      }
      form.querySelectorAll('input, select').forEach(el => (el.value = ''));
    });
  }

  function setupEntityAdd(entity) {
    const config = entityConfig[entity];
    if (!config.fields) return;

    const saveBtn = document.querySelector(`.save-entity-btn[data-entity="${entity}"]`);
    if (!saveBtn) {
      console.warn(`Save button not found for ${entity}`);
      return;
    }

    saveBtn.addEventListener('click', () => {
      const data = {};
      let valid = true;

      config.fields.forEach(field => {
        const element = document.getElementById(field.id);
        let value = element?.value;
        if (field.type === 'text') value = value.trim();
        if (field.type === 'number') value = parseFloat(value);
        if (field.transform) value = field.transform(value);
        if (!value) valid = false;
        data[field.key] = value;
      });

      if (!valid) {
        showAlert('Erreur', 'Tous les champs sont requis.', 'error');
        return;
      }

      fetch(`${config.url}/create/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
      })
        .then(res => {
          if (!res.ok) {
            return res.json().then(err => {
              throw new Error(err.message || 'Erreur serveur');
            });
          }
          return res.json();
        })
        .then(() => {
          showAlert('Succès', `${config.title} ajouté.`, 'success');
          setTimeout(() => location.reload(), 800);
        })
        .catch(error => {
          showAlert('Erreur', `Erreur lors de l'ajout: ${error.message}`, 'error');
          console.error(`${config.title} add error:`, error);
        });
    });
  }

  function filterTable(tableId, columnIndices, searchValue) {
    const rows = document.querySelectorAll(`#${tableId} tbody tr`);
    const filter = searchValue.toLowerCase();
    rows.forEach(row => {
      const match = columnIndices.some(i => row.cells[i]?.textContent.toLowerCase().includes(filter));
      row.style.display = match ? '' : 'none';
    });
  }

  function setupSearch() {
    document.querySelectorAll('.search-input').forEach(input => {
      input.addEventListener('input', e => {
        const tableId = e.target.getAttribute('data-table');
        const entity = Object.keys(entityConfig).find(key => entityConfig[key].table === tableId);
        if (entity) {
          filterTable(tableId, entityConfig[entity].searchColumns, e.target.value);
        }
      });
    });
  }

  function setupDeleteButtons() {
    document.querySelectorAll('.btn-delete-entity').forEach(btn => {
      btn.addEventListener('click', () => {
        const entity = btn.getAttribute('data-entity');
        const id = btn.getAttribute('data-id');
        deleteEntity(entity, id);
      });
    });
  }

  Object.keys(entityConfig).forEach(entity => {
    setupFormToggle(entity);
    setupEntityAdd(entity);
  });

  setupSearch();
  setupDeleteButtons();
});