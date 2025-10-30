// configuratio_sweetalert.js
function showAlert(title, text, icon) {
  Swal.fire(title, text, icon);
}

function showAlertConfirm(title, text, icon = 'warning') {
  return Swal.fire({
    title,
    text,
    icon,
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6',
    confirmButtonText: 'Oui, confirmer',
    cancelButtonText: 'Annuler'
  });
}