document.addEventListener('DOMContentLoaded', function() {
  const form = document.querySelector('#formulaire-fournisseur form');
  if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      let isValid = true;
      this.querySelectorAll('[required]').forEach(field => {
        if (!field.value.trim()) {
          isValid = false;
          field.classList.add('is-invalid');
        } else {
          field.classList.remove('is-invalid');
        }
      });

      if (!isValid) {
        Swal.fire({
          icon: 'error',
          title: 'Erreur',
          text: 'Veuillez remplir tous les champs obligatoires.',
        });
        return;
      }

      Swal.fire({
        icon: 'question',
        title: 'Confirmer',
        text: 'Voulez-vous vraiment enregistrer ce fournisseur ?',
        showCancelButton: true,
        confirmButtonText: 'Oui, enregistrer',
        cancelButtonText: 'Annuler'
      }).then((result) => {
        if (result.isConfirmed) {
          const formData = new FormData(this);
          Swal.fire({
            title: 'Traitement en cours...',
            text: 'Veuillez patienter',
            allowOutsideClick: false,
            didOpen: () => {
              Swal.showLoading();
            }
          });

          fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
              'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
            }
          })
          .then(response => {
            Swal.close();
            if (response.ok) {
              const redirectUrl = document.getElementById('supplier-list-url').dataset.url;
              window.location.href = redirectUrl;
            } else {
              return response.json().then(data => {
                Swal.fire({
                  icon: 'error',
                  title: 'Erreur',
                  text: data.error || 'Une erreur s\'est produite lors de l\'enregistrement.',
                });
              });
            }
          })
          .catch(error => {
            Swal.close();
            Swal.fire({
              icon: 'error',
              title: 'Erreur',
              text: 'Une erreur réseau est survenue. Veuillez réessayer.',
            });
            console.error('Error:', error);
          });
        }
      });
    });
  }
});