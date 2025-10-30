// Gestion des documents médicaux
let documentsToUpload = [];

function addDocument() {
    const documentType = document.getElementById('documentType');
    const documentFile = document.getElementById('documentFile');
    
    if (!documentType.value) {
        Swal.fire({
            icon: 'warning',
            title: 'Attention',
            text: 'Veuillez sélectionner le type de document',
            confirmButtonColor: '#ffc107'
        });
        return;
    }
    
    if (!documentFile.files || documentFile.files.length === 0) {
        Swal.fire({
            icon: 'warning',
            title: 'Attention',
            text: 'Veuillez sélectionner un fichier',
            confirmButtonColor: '#ffc107'
        });
        return;
    }
    
    const file = documentFile.files[0];
    const typeLabel = documentType.options[documentType.selectedIndex].text;
    
    // Ajouter le document à la liste temporaire
    documentsToUpload.push({
        type: documentType.value,
        typeLabel: typeLabel,
        file: file
    });
    
    // Mettre à jour le compteur
    updateDocumentCount();
    
    // Afficher le document dans la liste
    displayPendingDocuments();
    
    // Réinitialiser les champs
    documentType.value = '';
    documentFile.value = '';
    
    Swal.fire({
        icon: 'success',
        title: 'Document ajouté',
        text: 'Le document sera uploadé lors de la sauvegarde du patient',
        timer: 2000,
        showConfirmButton: false
    });
}

function updateDocumentCount() {
    const countElement = document.getElementById('docCount');
    if (countElement) {
        countElement.textContent = documentsToUpload.length;
    }
}

function displayPendingDocuments() {
    const documentsList = document.getElementById('documentsList');
    if (!documentsList) return;
    
    // Créer ou récupérer la section des documents en attente
    let pendingSection = document.getElementById('pendingDocuments');
    if (!pendingSection && documentsToUpload.length > 0) {
        pendingSection = document.createElement('div');
        pendingSection.id = 'pendingDocuments';
        pendingSection.className = 'card mt-3';
        documentsList.insertBefore(pendingSection, documentsList.firstChild);
    }
    
    if (documentsToUpload.length === 0 && pendingSection) {
        pendingSection.remove();
        return;
    }
    
    if (!pendingSection) return;
    
    // Construire le HTML de la section
    let html = `
        <div class="card-header text-white" style="background-color: #1e90ff;">
            <i class="fas fa-file-medical me-2"></i>Documents téléchargés (${documentsToUpload.length})
        </div>
        <div class="card-body">
            <div class="list-group">
    `;
    
    documentsToUpload.forEach((doc, index) => {
        html += `
            <div class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    <i class="fas fa-file-alt me-2 text-warning"></i>
                    <span class="badge bg-info me-2">${doc.typeLabel}</span>
                    <span>${doc.file.name}</span>
                    <small class="text-muted ms-2">(${formatFileSize(doc.file.size)})</small>
                </div>
                <button type="button" class="btn btn-sm btn-danger" onclick="removePendingDocument(${index})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    });
    
    html += `
            </div>
        </div>
    `;
    
    pendingSection.innerHTML = html;
}

function removePendingDocument(index) {
    documentsToUpload.splice(index, 1);
    updateDocumentCount();
    displayPendingDocuments();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function deleteDocument(documentId) {
    Swal.fire({
        title: 'Êtes-vous sûr ?',
        text: "Cette action supprimera définitivement le document",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Oui, supprimer',
        cancelButtonText: 'Annuler'
    }).then((result) => {
        if (result.isConfirmed) {
            // Envoyer la requête de suppression
            fetch(`/patient/delete-medical-document/${documentId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Supprimé !',
                        text: 'Le document a été supprimé',
                        timer: 2000,
                        showConfirmButton: false
                    }).then(() => {
                        location.reload();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erreur',
                        text: data.message || 'Impossible de supprimer le document'
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Erreur',
                    text: 'Une erreur est survenue'
                });
            });
        }
    });
}

// Fonction pour obtenir le cookie CSRF
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

// Gérer la soumission du formulaire pour inclure les documents
document.addEventListener('DOMContentLoaded', function() {
    const patientForm = document.querySelector('form[action*="patient_list_create"]');
    if (patientForm) {
        patientForm.addEventListener('submit', function(e) {
            if (documentsToUpload.length > 0) {
                e.preventDefault();
                
                // Créer un FormData pour inclure les fichiers
                const formData = new FormData(this);
                
                // Ajouter les documents à uploader
                documentsToUpload.forEach((doc, index) => {
                    formData.append(`medical_document_type_${index}`, doc.type);
                    formData.append(`medical_document_file_${index}`, doc.file);
                });
                
                formData.append('medical_documents_count', documentsToUpload.length);
                
                // Envoyer le formulaire via AJAX avec les fichiers
                fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => {
                    if (response.ok) {
                        // Rediriger vers la page de succès
                        window.location.href = response.url;
                    } else {
                        throw new Error('Erreur lors de la sauvegarde');
                    }
                })
                .catch(error => {
                    console.error('Erreur:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Erreur',
                        text: 'Une erreur est survenue lors de la sauvegarde'
                    });
                });
            }
            // Si pas de documents, laisser la soumission normale se faire
        });
    }
});

