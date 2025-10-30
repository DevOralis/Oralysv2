// JavaScript spécifique pour la page de complétion de consultation

document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les alertes pour la complétion de consultation
    initCompleteConsultationAlerts();
});

// Fonction pour initialiser les SweetAlert pour la complétion de consultation
function initCompleteConsultationAlerts() {
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.get('patient_incomplete') === '1') {
        const editUrl = urlParams.get('edit_url');
        Swal.fire({
            icon: 'warning',
            title: 'Informations incomplètes',
            text: 'Veuillez remplir les données du patient avant de poursuivre la consultation.',
            confirmButtonText: 'OK',
            allowOutsideClick: false
        }).then(() => {
            if (editUrl) {
                window.location.href = editUrl;
            }
        });
    } else if (urlParams.get('success') === 'completed') {
        Swal.fire({
            icon: 'success',
            title: 'Succès',
            text: 'Patient complété avec succès. Vous pouvez maintenant terminer la consultation.',
            timer: 2000,
            showConfirmButton: false
        });
        urlParams.delete('success');
        window.history.replaceState({}, document.title, window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : ''));
    } else if (urlParams.get('patient_completed') === '1') {
        Swal.fire({
            icon: 'success',
            title: 'Succès',
            text: 'Patient complété avec succès. Vous pouvez maintenant terminer la consultation.',
            timer: 2000,
            showConfirmButton: false
        });
        urlParams.delete('patient_completed');
        window.history.replaceState({}, document.title, window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : ''));
    } else if (urlParams.get('success') === 'update') {
        Swal.fire({
            icon: 'success',
            title: 'Succès',
            text: 'Mise à jour avec succès !',
            timer: 2000,
            showConfirmButton: false
        });
        urlParams.delete('success');
        window.history.replaceState({}, document.title, window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : ''));
    }
}
