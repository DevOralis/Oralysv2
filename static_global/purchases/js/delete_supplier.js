document.addEventListener("DOMContentLoaded", () => {
  const deleteButtons = document.querySelectorAll(".btn-delete");

  deleteButtons.forEach(button => {
    button.addEventListener("click", (e) => {
      e.preventDefault();
      const supplierId = button.getAttribute("data-id");

      Swal.fire({
        title: 'Êtes-vous sûr ?',
        text: "Cette action est irréversible !",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Oui, supprimer',
        cancelButtonText: 'Annuler'
      }).then((result) => {
        if (result.isConfirmed) {
          fetch(`/purchases/suppliers/${supplierId}/delete/`, {
            method: 'POST',
            headers: {
              'X-CSRFToken': getCookie('csrftoken'),
              'Content-Type': 'application/json'
            },
          })
          .then(response => {
            if (response.ok) {
              Swal.fire({
                title: 'Supprimé!',
                text: 'Le fournisseur a été supprimé avec succès.',
                icon: 'success',
                timer: 2000,
                showConfirmButton: false
              }).then(() => {
                location.reload();
              });
            } else {
              Swal.fire('Erreur', 'Une erreur est survenue.', 'error');
            }
          });
        }
      });
    });
  });

  // Fonction pour obtenir le token CSRF
  function getCookie(name) {
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
});
