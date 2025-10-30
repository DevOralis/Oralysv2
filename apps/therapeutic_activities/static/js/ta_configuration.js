// Therapeutic Activities Configuration JS
// Handles AJAX operations for creating and deleting Activity Types and Locations
// Requires SweetAlert2 (already included in template)

(function () {
  // Helper to get CSRF token from cookies (Django)
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie("csrftoken");

  // Generic fetch helper
  async function postJson(url, payload) {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify(payload),
    });
    return response.json();
  }

  // ------- Activity Type Create/Update -------
  const activityTypeForm = document.getElementById("activity-type-form");
  if (activityTypeForm) {
    activityTypeForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const submitBtn = activityTypeForm.querySelector("button[type='submit']");
      submitBtn.disabled = true;

      const formData = new FormData(activityTypeForm);
      const payload = Object.fromEntries(formData.entries());
      // Convert checkbox value to boolean
      payload.is_active = activityTypeForm.querySelector('[name="is_active"]').checked;

      // Récupérer l'ID directement du champ caché
      const idField = activityTypeForm.querySelector('input[name="id"]');
      const activityTypeId = idField ? idField.value : '';
      const isUpdate = activityTypeId && activityTypeId !== '' && activityTypeId !== '0' && !isNaN(parseInt(activityTypeId));
      
      // Choisir l'URL appropriée
      const url = isUpdate 
        ? `/therapeutic_activities/api/activity-types/${activityTypeId}/update/`
        : "/therapeutic_activities/api/activity-types/create/";

      console.log('=== ACTIVITY TYPE DEBUG ===');
      console.log('ID Field Element:', idField);
      console.log('ID Field Value:', activityTypeId);
      console.log('Is Update:', isUpdate);
      console.log('URL:', url);
      console.log('Payload:', payload);
      
      // Forcer l'URL de modification si ID présent
      if (activityTypeId && activityTypeId !== '' && activityTypeId !== '0') {
        console.log('ID DÉTECTÉ - FORÇAGE URL DE MODIFICATION');
        url = `/therapeutic_activities/api/activity-types/${activityTypeId}/update/`;
        console.log('URL FORCÉE:', url);
      }

      try {
        const data = await postJson(url, payload);
        if (data.success) {
          Swal.fire({
            icon: "success",
            title: "Succès",
            text: data.message,
            timer: 2000,
            showConfirmButton: false,
          }).then(() => window.location.reload());
        } else {
          Swal.fire({ icon: "error", title: "Erreur", text: data.message || "Veuillez vérifier les champs." });
          submitBtn.disabled = false;
        }
      } catch (err) {
        console.error('Erreur AJAX:', err);
        Swal.fire({ icon: "error", title: "Erreur", text: "Une erreur est survenue." });
        submitBtn.disabled = false;
      }
    });
  }

  // ------- Location Create/Update -------
  const locationForm = document.getElementById("location-form");
  if (locationForm) {
    locationForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const submitBtn = locationForm.querySelector("button[type='submit']");
      submitBtn.disabled = true;

      const formData = new FormData(locationForm);
      const payload = Object.fromEntries(formData.entries());
      payload.is_active = locationForm.querySelector('[name="is_active"]').checked;

      // Convert capacity to integer if provided, otherwise remove to avoid validation error
      if (payload.capacity === "") {
        delete payload.capacity;
      } else {
        payload.capacity = parseInt(payload.capacity, 10);
      }

      // Récupérer l'ID directement du champ caché
      const idField = locationForm.querySelector('input[name="id"]');
      const locationId = idField ? idField.value : '';
      const isUpdate = locationId && locationId !== '' && locationId !== '0' && !isNaN(parseInt(locationId));
      
      // Choisir l'URL appropriée
      const url = isUpdate 
        ? `/therapeutic_activities/api/activity-locations/${locationId}/update/`
        : "/therapeutic_activities/ajax/create-activity-location/";

      console.log('=== LOCATION DEBUG ===');
      console.log('ID Field Value:', locationId);
      console.log('Is Update:', isUpdate);
      console.log('URL:', url);
      console.log('Payload:', payload);

      try {
        const data = await postJson(url, payload);
        if (data.success) {
          Swal.fire({ icon: "success", title: "Succès", text: data.message, timer: 2000, showConfirmButton: false }).then(() => window.location.reload());
        } else {
          Swal.fire({ icon: "error", title: "Erreur", text: data.message || "Veuillez vérifier les champs." });
          submitBtn.disabled = false;
        }
      } catch (err) {
        console.error('Erreur AJAX:', err);
        Swal.fire({ icon: "error", title: "Erreur", text: "Une erreur est survenue." });
        submitBtn.disabled = false;
      }
    });
  }

  // ------- Delete Activity Type -------
  window.deleteActivityType = async function (id, name) {
    const confirm = await Swal.fire({
      title: `Supprimer le type "${name}" ?`,
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Oui, supprimer",
      cancelButtonText: "Annuler",
    });
    if (!confirm.isConfirmed) return;

    try {
      const data = await postJson("/therapeutic_activities/ajax/delete-activity-type/", { id });
      if (data.success) {
        Swal.fire({ icon: "success", title: "Supprimé", text: data.message, timer: 2000, showConfirmButton: false }).then(() => window.location.reload());
      } else {
        Swal.fire({ icon: "error", title: "Erreur", text: data.message });
      }
    } catch (err) {
      console.error(err);
      Swal.fire({ icon: "error", title: "Erreur", text: "Une erreur est survenue." });
    }
  };

  // ------- Delete Activity Location -------
  window.deleteActivityLocation = async function (id, name) {
    const confirm = await Swal.fire({
      title: `Supprimer la salle "${name}" ?`,
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Oui, supprimer",
      cancelButtonText: "Annuler",
    });
    if (!confirm.isConfirmed) return;

    try {
      const data = await postJson("/therapeutic_activities/ajax/delete-activity-location/", { id });
      if (data.success) {
        Swal.fire({ icon: "success", title: "Supprimé", text: data.message, timer: 2000, showConfirmButton: false }).then(() => window.location.reload());
      } else {
        Swal.fire({ icon: "error", title: "Erreur", text: data.message });
      }
    } catch (err) {
      console.error(err);
      Swal.fire({ icon: "error", title: "Erreur", text: "Une erreur est survenue." });
    }
  };
  // ------- Form Card Management -------
  
  // Activity Type Form Card
  const btnAddActivityType = document.getElementById('btn-add-activity-type');
  const activityTypeFormCard = document.getElementById('activity-type-form-card');
  const activityTypeFormTitle = document.getElementById('activity-type-form-title');
  const activityTypeFormElement = document.getElementById('activity-type-form');
  
  // Location Form Card  
  const btnAddLocation = document.getElementById('btn-add-location');
  const locationFormCard = document.getElementById('location-form-card');
  const locationFormTitle = document.getElementById('location-form-title');
  const locationFormElement = document.getElementById('location-form');

  // Show Activity Type Form Card
  function showActivityTypeForm(isEdit = false, data = {}) {
    activityTypeFormTitle.textContent = isEdit ? 'Modifier le type d\'activité' : 'Ajouter un type d\'activité';
    
    // Reset form
    activityTypeFormElement.reset();
    
    console.log('=== SHOW ACTIVITY TYPE FORM DEBUG ===');
    console.log('isEdit:', isEdit);
    console.log('data:', data);
    console.log('data.id:', data.id);
    
    // Définir l'ID dans le champ caché
    const idField = activityTypeFormElement.querySelector('[name="id"]');
    if (idField) {
      idField.value = data.id || '';
      console.log('ID field set to:', idField.value);
    } else {
      console.error('ID field not found!');
    }
    
    if (isEdit && data) {
      activityTypeFormElement.querySelector('[name="name"]').value = data.name || '';
      activityTypeFormElement.querySelector('[name="description"]').value = data.description || '';
      activityTypeFormElement.querySelector('[name="is_active"]').checked = data.is_active === 'true';
    } else {
      activityTypeFormElement.querySelector('[name="is_active"]').checked = true;
    }
    
    activityTypeFormCard.classList.remove('d-none');
    activityTypeFormCard.scrollIntoView({ behavior: 'smooth' });
  }

  // Show Location Form Card
  function showLocationForm(isEdit = false, data = {}) {
    locationFormTitle.textContent = isEdit ? 'Modifier la salle' : 'Ajouter une salle';
    
    // Reset form
    locationFormElement.reset();
    locationFormElement.querySelector('[name="id"]').value = data.id || '';
    
    if (isEdit && data) {
      locationFormElement.querySelector('[name="name"]').value = data.name || '';
      locationFormElement.querySelector('[name="address"]').value = data.address || '';
      locationFormElement.querySelector('[name="capacity"]').value = data.capacity || '';
      locationFormElement.querySelector('[name="is_active"]').checked = data.is_active === 'true';
    } else {
      locationFormElement.querySelector('[name="is_active"]').checked = true;
    }
    
    locationFormCard.classList.remove('d-none');
    locationFormCard.scrollIntoView({ behavior: 'smooth' });
  }

  // Hide all form cards
  function hideAllFormCards() {
    if (activityTypeFormCard) activityTypeFormCard.classList.add('d-none');
    if (locationFormCard) locationFormCard.classList.add('d-none');
  }

  // Event listeners for "Nouveau" buttons
  if (btnAddActivityType) {
    btnAddActivityType.addEventListener('click', function() {
      hideAllFormCards();
      showActivityTypeForm(false);
    });
  }

  if (btnAddLocation) {
    btnAddLocation.addEventListener('click', function() {
      hideAllFormCards();
      showLocationForm(false);
    });
  }

  // Event listeners for "Modifier" buttons
  document.addEventListener('click', function(e) {
    if (e.target.closest('.edit-activity-type-btn')) {
      const btn = e.target.closest('.edit-activity-type-btn');
      const data = {
        id: btn.dataset.id,
        name: btn.dataset.name,
        description: btn.dataset.description,
        is_active: btn.dataset.isActive
      };
      hideAllFormCards();
      showActivityTypeForm(true, data);
    }
    
    if (e.target.closest('.edit-location-btn')) {
      const btn = e.target.closest('.edit-location-btn');
      const data = {
        id: btn.dataset.id,
        name: btn.dataset.name,
        address: btn.dataset.address,
        capacity: btn.dataset.capacity,
        is_active: btn.dataset.isActive
      };
      hideAllFormCards();
      showLocationForm(true, data);
    }
  });

  // Event listeners for "Annuler" buttons
  document.addEventListener('click', function(e) {
    if (e.target.closest('.btn-cancel-form')) {
      hideAllFormCards();
    }
  });

})();
