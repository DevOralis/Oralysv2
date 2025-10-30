document.addEventListener('DOMContentLoaded', function() {
  const employeeSelect = document.querySelector('#id_employee');
  const nomInput = document.querySelector('#id_nom');
  const prenomInput = document.querySelector('#id_prenom');
  const updateEmployeeSelect = document.querySelector('#update_employee');
  const updateNomInput = document.querySelector('#update_nom');
  const updatePrenomInput = document.querySelector('#update_prenom');
  const employeesData = JSON.parse(document.getElementById('employees-data').textContent);

  // Pre-fill for create form
  if (employeeSelect) {
    employeeSelect.addEventListener('change', function() {
      const selectedEmployeeId = this.value;
      const employee = employeesData.find(emp => emp.id == selectedEmployeeId);
      if (employee) {
        const nameParts = employee.full_name.trim().split(' ');
        const prenom = nameParts[0] || '';
        const nom = nameParts.slice(1).join(' ') || '';
        prenomInput.value = prenom;
        nomInput.value = nom;
      } else {
        prenomInput.value = '';
        nomInput.value = '';
      }
    });
  }

  // Pre-fill for update modal
  if (updateEmployeeSelect) {
    updateEmployeeSelect.addEventListener('change', function() {
      const selectedEmployeeId = this.value;
      const employee = employeesData.find(emp => emp.id == selectedEmployeeId);
      if (employee) {
        const nameParts = employee.full_name.trim().split(' ');
        const prenom = nameParts[0] || '';
        const nom = nameParts.slice(1).join(' ') || '';
        updatePrenomInput.value = prenom;
        updateNomInput.value = nom;
      } else {
        updatePrenomInput.value = '';
        updateNomInput.value = '';
      }
    });
  }

  // Handle update form submission
  document.querySelector('#update-user-submit').addEventListener('click', () => {
    const form = document.querySelector('#update-user-form');
    const formData = new FormData(form);
    const userId = document.querySelector('#update_user_id').value;
    fetch(`/users/${userId}/update/`, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
      }
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          Swal.fire({
            title: 'Succès',
            text: 'Utilisateur modifié avec succès.',
            icon: 'success',
            timer: 1500,
            showConfirmButton: false
          }).then(() => {
            // Refresh table
            fetch('/users/ajax/')
              .then(response => response.text())
              .then(html => {
                document.querySelector('#user-table tbody').innerHTML = html;
                bootstrap.Modal.getInstance(document.getElementById('updateUserModal')).hide();
                reattachButtonListeners();
              });
          });
        } else {
          const errorDiv = document.querySelector('#update-error');
          errorDiv.innerHTML = '<ul class="errorlist">' + Object.values(data.errors).flat().map(err => `<li>${err}</li>`).join('') + '</ul>';
          errorDiv.classList.remove('d-none');
        }
      })
      .catch(error => {
        console.error('Error updating user:', error);
        Swal.fire({
          title: 'Erreur',
          text: 'Une erreur est survenue lors de la modification.',
          icon: 'error'
        });
      });
  });

  function reattachButtonListeners() {
    // Reattach delete button event listeners
    document.querySelectorAll('.btn-delete-user').forEach(button => {
      button.addEventListener('click', () => {
        const userId = button.dataset.id;
        const userName = button.dataset.name;
        Swal.fire({
          title: 'Confirmer la suppression',
          html: `Voulez-vous vraiment supprimer l'utilisateur <strong>${userName}</strong> ?`,
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Supprimer',
          cancelButtonText: 'Annuler'
        }).then(result => {
          if (result.isConfirmed) {
            const form = document.getElementById('delete-user-form');
            form.action = `/users/delete/${userId}/`;
            form.submit();
          }
        });
      });
    });

    // Reattach update button event listeners
    document.querySelectorAll('.btn-update-user').forEach(button => {
      button.addEventListener('click', () => {
        const userId = button.dataset.id;
        fetch(`/users/${userId}/get/`)
          .then(response => response.json())
          .then(data => {
            document.querySelector('#update_user_id').value = data.id;
            document.querySelector('#update_nom').value = data.nom;
            document.querySelector('#update_prenom').value = data.prenom;
            document.querySelector('#update_username').value = data.username;
            document.querySelector('#update_is_activated').checked = data.is_activated;
            document.querySelector('#update_employee').value = data.employee || '';
            // Populate permissions
            document.querySelectorAll('.update-permissions').forEach(checkbox => {
              const [app, perm] = checkbox.name.match(/permissions\[(.+)\]\[(.+)\]/).slice(1);
              checkbox.checked = data.permissions[app][perm];
            });
            document.querySelector('#update-error').classList.add('d-none');
            const modal = new bootstrap.Modal(document.getElementById('updateUserModal'));
            modal.show();
          })
          .catch(error => {
            console.error('Error fetching user data:', error);
            Swal.fire({
              title: 'Erreur',
              text: 'Impossible de charger les données de l\'utilisateur.',
              icon: 'error'
            });
          });
      });
    });

    // Reattach toggle button event listeners
    document.querySelectorAll('.btn-toggle-user').forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const userId = button.dataset.id;
        fetch(`/users/${userId}/toggle-activation/`, {
          method: 'GET',
          headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          }
        })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              Swal.fire({
                title: 'Succès',
                text: data.message,
                icon: 'success',
                timer: 1500,
                showConfirmButton: false
              }).then(() => {
                // Refresh table
                fetch('/users/ajax/')
                  .then(response => response.text())
                  .then(html => {
                    document.querySelector('#user-table tbody').innerHTML = html;
                    reattachButtonListeners();
                  });
              });
            } else {
              Swal.fire({
                title: 'Erreur',
                text: 'Une erreur est survenue lors de la modification du statut.',
                icon: 'error'
              });
            }
          })
          .catch(error => {
            console.error('Error toggling user:', error);
            Swal.fire({
              title: 'Erreur',
              text: 'Une erreur est survenue lors de la modification du statut.',
              icon: 'error'
            });
          });
      });
    });
  }

  // Initial attachment of button listeners
  reattachButtonListeners();
});