// Gestion du formulaire d'employé avec SweetAlert
document.addEventListener('DOMContentLoaded', function() {
  // Vérifier si nous sommes sur la page employé
  const employeeForm = document.querySelector('form[action*="add_employee"]');
  if (!employeeForm) {
    // Pas sur la page employé, arrêter l'exécution
    return;
  }
  
  // Ajouter l'event listener au formulaire
  employeeForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Créer un objet FormData à partir du formulaire
      const formData = new FormData(this);
      
      // Afficher un indicateur de chargement
      Swal.fire({
        title: 'Traitement en cours...',
        html: 'Veuillez patienter pendant que nous traitons votre demande.',
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        }
      });
      
      // Envoyer les données via AJAX
      fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => {
        return response.json();
      })
      .then(data => {
        if (data.status === 'success') {
          // Afficher un message de succès sans redirection
          Swal.fire({
            icon: 'success',
            title: 'Succès!',
            text: 'Employé modifié avec succès.'
          });
        } else {
          // Afficher un message d'erreur
          Swal.fire({
            icon: 'error',
            title: 'Erreur',
            text: data.message || 'Une erreur est survenue lors de la modification de l\'employé.'
          });
        }
      })
      .catch(error => {
        console.error('Erreur:', error);
        Swal.fire({
          icon: 'error',
          title: 'Erreur',
          text: 'Une erreur est survenue lors de la communication avec le serveur.'
        });
      });
  });
}); 