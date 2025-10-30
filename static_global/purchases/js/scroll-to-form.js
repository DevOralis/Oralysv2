document.addEventListener('DOMContentLoaded', function() {
  const scrollToFormButton = document.getElementById('scrollToForm');
  if (scrollToFormButton) {
    scrollToFormButton.addEventListener('click', function() {
      const form = document.getElementById('formulaire-fournisseur');
      if (form) {
        form.scrollIntoView({ behavior: 'smooth' });
      }
    });
  }
});