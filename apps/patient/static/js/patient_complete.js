// Scripts spécifiques à l'application patient

// Données des médecins passées depuis le template Django
// Cette variable sera définie dans le template avec les données réelles
window.medecinsData = window.medecinsData || [];

// Initialisation du formulaire de rendez-vous
function initAppointmentForm() {
    const yesRadio = document.getElementById('isExistingYes');
    const noRadio = document.getElementById('isExistingNo');
    const patientSelectDiv = document.getElementById('patientSelectDiv');
    const patientSelect = document.getElementById('patientSelect');
    const nomInput = document.getElementById('nomInput');
    const prenomInput = document.getElementById('prenomInput');
    const telephoneInput = document.getElementById('telephoneInput');
    const emailInput = document.getElementById('emailInput');

    if (!yesRadio || !noRadio || !patientSelectDiv) return;

    function setFieldsDisabled(disabled) {
        if (nomInput) nomInput.disabled = disabled;
        if (prenomInput) prenomInput.disabled = disabled;
        if (telephoneInput) telephoneInput.disabled = disabled;
        if (emailInput) emailInput.disabled = disabled;
    }

    function clearFields() {
        if (nomInput) nomInput.value = '';
        if (prenomInput) prenomInput.value = '';
        if (telephoneInput) telephoneInput.value = '';
        if (emailInput) emailInput.value = '';
    }

    yesRadio.addEventListener('change', function() {
        if (yesRadio.checked) {
            patientSelectDiv.style.display = '';
            setFieldsDisabled(true);
            clearFields();
        }
    });
    
    noRadio.addEventListener('change', function() {
        if (noRadio.checked) {
            patientSelectDiv.style.display = 'none';
            setFieldsDisabled(false);
            clearFields();
        }
    });
    
    if (patientSelect) {
        patientSelect.addEventListener('change', function() {
            const selected = patientSelect.options[patientSelect.selectedIndex];
            if (nomInput) nomInput.value = selected.getAttribute('data-nom') || '';
            if (prenomInput) prenomInput.value = selected.getAttribute('data-prenom') || '';
            if (telephoneInput) telephoneInput.value = selected.getAttribute('data-telephone') || '';
            if (emailInput) emailInput.value = selected.getAttribute('data-email') || '';
        });
    }

    // Initial state
    if (yesRadio.checked) {
        patientSelectDiv.style.display = '';
        setFieldsDisabled(true);
    } else {
        patientSelectDiv.style.display = 'none';
        setFieldsDisabled(false);
    }
}

// Initialisation du calendrier FullCalendar
function initCalendar() {
    var calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;
    
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        locale: 'fr',
        slotMinTime: '08:00:00',
        slotMaxTime: '20:00:00',
        allDaySlot: false,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'timeGridDay,timeGridWeek,dayGridMonth'
        },
        buttonText: {
            today: 'Aujourd\'hui',
            month: 'Mois',
            week: 'Semaine',
            day: 'Jour',
            list: 'Liste'
        },
        dayHeaderFormat: { weekday: 'long', month: 'numeric', day: 'numeric' },
        events: [],
        eventDidMount: function(info) {
            if (info.event.extendedProps.description) {
                info.el.title = info.event.extendedProps.description;
            }
        }
    });
    
    calendar.render();
    
    function loadMedecinEvents(medecinId) {
        if (!medecinId) {
            calendar.removeAllEvents();
            return;
        }
        
        // Utilisation de la bonne URL d'API avec le préfixe patient/ et le paramètre medecin_id
        fetch(`/patient/api/medecin-appointments/?medecin_id=${medecinId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur lors du chargement des rendez-vous');
                }
                return response.json();
            })
            .then(events => {
                calendar.removeAllEvents();
                events.forEach(appointment => {
                    // Calculer la fin du rendez-vous (+ 1 heure) avec JavaScript natif
                    const startDate = new Date(appointment.date_heure);
                    const endDate = new Date(startDate.getTime() + 60 * 60000); // +1 heure
                    
                    calendar.addEvent({
                        id: appointment.id,
                        title: appointment.patient_nom || 'Anonyme', // Nom du patient seulement
                        start: appointment.date_heure,
                        end: endDate.toISOString(),
                        backgroundColor: '#007bff', // Couleur bleue
                        borderColor: '#007bff', // Couleur bleue
                        extendedProps: appointment
                    });
                });
            })
            .catch(error => {
                console.error('Erreur:', error);
                // Afficher un message d'erreur à l'utilisateur
                Swal.fire({
                    icon: 'error',
                    title: 'Erreur',
                    text: 'Impossible de charger les rendez-vous. Veuillez réessayer.',
                    timer: 3000
                });
            });
    }
    
    // Filtre dynamique pour le calendrier
    var calendarMedecinSelect = document.getElementById('calendarMedecinSelect');
    if (calendarMedecinSelect) {
        calendarMedecinSelect.addEventListener('change', function() {
            loadMedecinEvents(this.value);
        });
        // Charger au chargement si déjà sélectionné
        if (calendarMedecinSelect.value) {
            loadMedecinEvents(calendarMedecinSelect.value);
        }
    }
}

// Pagination AJAX pour rendez-vous récents
function bindRdvPagination() {
    const appointmentsTable = document.getElementById('appointments-table');
    if (!appointmentsTable) return;
    
    appointmentsTable.querySelectorAll('.page-ajax').forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            // Extraire les paramètres de l'URL
            const url = new URL(this.href);
            const params = new URLSearchParams(url.search);
            // Ajouter l'en-tête pour indiquer que c'est une requête AJAX
            fetch('/patient/appointments/table/?' + params.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(response => response.json())
                .then(data => {
                    appointmentsTable.innerHTML = data.html;
                    bindRdvPagination();
                    bindRdvFilters(); // Réattacher les événements pour les filtres
                });
        });
    });
}

// Recherche et filtres AJAX rendez-vous récents
function triggerRdvAjax() {
    const searchInput = document.getElementById('search-appointment');
    const medecinSelect = document.getElementById('filter-appointment-medecin');
    const statutSelect = document.getElementById('filter-appointment-statut');
    
    if (!searchInput || !medecinSelect || !statutSelect) return;
    
    const search = searchInput.value;
    const medecin = medecinSelect.value;
    const statut = statutSelect.value;
    const params = new URLSearchParams({search_rdv: search, filter_rdv_medecin: medecin, filter_rdv_statut: statut});
    
    fetch('/patient/appointments/table/?' + params.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(response => response.json())
        .then(data => {
            const appointmentsTable = document.getElementById('appointments-table');
            if (appointmentsTable) {
                appointmentsTable.innerHTML = data.html;
                bindRdvPagination();
                bindRdvFilters();
            }
        });
}

function bindRdvFilters() {
    const searchInput = document.getElementById('search-appointment');
    const medecinSelect = document.getElementById('filter-appointment-medecin');
    const statutSelect = document.getElementById('filter-appointment-statut');
    
    if (searchInput) searchInput.addEventListener('input', triggerRdvAjax);
    if (medecinSelect) medecinSelect.addEventListener('change', triggerRdvAjax);
    if (statutSelect) statutSelect.addEventListener('change', triggerRdvAjax);
}

// Gestion des messages SweetAlert pour les rendez-vous
function handleAppointmentMessages() {
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.get('success') === 'rdv_created') {
        Swal.fire({
            icon: 'success',
            title: 'Rendez-vous créé !',
            text: 'Le rendez-vous a été créé avec succès.',
            timer: 3000,
            showConfirmButton: false
        });
        // Nettoyer l'URL
        urlParams.delete('success');
        window.history.replaceState({}, document.title, window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : ''));
    }
}

// Initialisation du formulaire patient
function initPatientForm() {
    // Navigation entre les onglets avec les boutons personnalisés
    document.querySelectorAll('.next-tab-btn').forEach(button => {
        button.addEventListener('click', function() {
            // Trouver l'onglet actif
            const activeTab = document.querySelector('.tab-pane.active');
            if (activeTab) {
                // Trouver le prochain onglet
                const nextTab = activeTab.nextElementSibling;
                if (nextTab && nextTab.classList.contains('tab-pane')) {
                    // Activer le prochain onglet en déclenchant le clic sur son bouton
                    const nextTabButton = document.querySelector(`[data-bs-target="#${nextTab.id}"]`);
                    if (nextTabButton) {
                        nextTabButton.click();
                    }
                }
            }
        });
    });
    
    document.querySelectorAll('.prev-tab-btn').forEach(button => {
        button.addEventListener('click', function() {
            // Trouver l'onglet actif
            const activeTab = document.querySelector('.tab-pane.active');
            if (activeTab) {
                // Trouver l'onglet précédent
                const prevTab = activeTab.previousElementSibling;
                if (prevTab && prevTab.classList.contains('tab-pane')) {
                    // Activer l'onglet précédent en déclenchant le clic sur son bouton
                    const prevTabButton = document.querySelector(`[data-bs-target="#${prevTab.id}"]`);
                    if (prevTabButton) {
                        prevTabButton.click();
                    }
                }
            }
        });
    });
    
    // Gestion de l'affichage des champs d'assurance
    const yesRadio = document.getElementById('hasInsuranceYes');
    const noRadio = document.getElementById('hasInsuranceNo');
    const insuranceFields = document.getElementById('insuranceFields');
    
    function toggleInsuranceFields() {
        if (insuranceFields) {
            insuranceFields.style.display = yesRadio && yesRadio.checked ? 'block' : 'none';
        }
    }
    
    if (yesRadio && noRadio) {
        yesRadio.addEventListener('change', toggleInsuranceFields);
        noRadio.addEventListener('change', toggleInsuranceFields);
        toggleInsuranceFields();
    }
    
    // Sécurité : forcer la valeur du champ gender à M, F ou O avant soumission
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const genderSelect = document.getElementById('genderSelect');
            if (genderSelect) {
                let val = genderSelect.value;
                // Si jamais une valeur longue est sélectionnée, on la mappe
                if (val.toLowerCase().includes('homme') || val.toLowerCase().includes('masculin')) {
                    genderSelect.value = 'M';
                } else if (val.toLowerCase().includes('femme') || val.toLowerCase().includes('féminin')) {
                    genderSelect.value = 'F';
                } else if (val.toLowerCase().includes('autre')) {
                    genderSelect.value = 'O';
                }
            }
        });
    }
}

// Gestion des messages SweetAlert pour les patients
function handlePatientMessages() {
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.get('success') === 'patient_updated') {
        Swal.fire({
            icon: 'success',
            title: 'Patient modifié !',
            text: 'Les informations du patient ont été mises à jour avec succès.',
            timer: 3000,
            showConfirmButton: false
        });
        // Nettoyer l'URL
        urlParams.delete('success');
        window.history.replaceState({}, document.title, window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : ''));
    } else if (urlParams.get('success') === 'patient_created') {
        Swal.fire({
            icon: 'success',
            title: 'Patient créé !',
            text: 'Le nouveau patient a été enregistré avec succès.',
            timer: 3000,
            showConfirmButton: false
        });
        // Nettoyer l'URL
        urlParams.delete('success');
        window.history.replaceState({}, document.title, window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : ''));
    }
}

// Gestion de la suppression de patient
function handlePatientDeletion() {
    document.querySelectorAll('.delete-patient-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const patientId = this.getAttribute('data-patient-id');
            const patientName = this.getAttribute('data-patient-name');
            
            Swal.fire({
                title: 'Êtes-vous sûr ?',
                text: `Voulez-vous vraiment supprimer ${patientName} ?`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Oui, supprimer',
                cancelButtonText: 'Annuler'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Utiliser fetch pour supprimer sans rechargement de page ni alerte navigateur
                    fetch(`/patient/delete/${patientId}/`, { method: 'GET' })
                        .then(() => {
                            Swal.fire({
                                icon: 'success',
                                title: 'Supprimé',
                                text: 'Patient supprimé avec succès !',
                                timer: 1500,
                                showConfirmButton: false
                            });
                            setTimeout(() => { window.location.reload(); }, 1500);
                        });
                }
            });
        });
    });
}

// Scroll automatique vers le formulaire lors du clic sur modifier
function handleEditScroll() {
    document.querySelectorAll('.edit-patient-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            // Lien déjà avec #new-patient, on force le scroll smooth
            setTimeout(function() {
                const form = document.getElementById('new-patient');
                if (form) {
                    form.scrollIntoView({ behavior: 'smooth' });
                }
            }, 100);
        });
    });
}

// Générer la liste des médecins avec leur spécialité (donnée Django -> JS)
function initMedecinSelects() {
    // Récupérer les données des médecins à partir de l'attribut data-
    const medecinsDataElement = document.getElementById('medecins-data');
    if (!medecinsDataElement) return;
    
    let medecinsData;
    try {
        medecinsData = JSON.parse('[' + medecinsDataElement.dataset.medecins + ']');
    } catch (e) {
        console.error('Erreur lors du parsing des données des médecins:', e);
        return;
    }

    function updateMedecinSelectsBySpeciality() {
        const specialitySelect = document.getElementById('diseaseSpecialitySelect');
        const treatingSelect = document.getElementById('treatingPhysicianSelect');
        const referringSelect = document.getElementById('referringPhysicianSelect');
        const selectedSpeciality = specialitySelect.value;

        // Filtrer les médecins par spécialité
        const filteredMedecins = selectedSpeciality 
            ? medecinsData.filter(med => med.speciality === selectedSpeciality)
            : medecinsData;

        // Mettre à jour les selects de médecins
        [treatingSelect, referringSelect].forEach(select => {
            if (select) {
                const currentValue = select.value;
                select.innerHTML = '<option value="">Sélectionnez un médecin</option>';
                
                filteredMedecins.forEach(med => {
                    const option = document.createElement('option');
                    option.value = med.full_name;
                    option.textContent = med.display;
                    if (med.full_name === currentValue) {
                        option.selected = true;
                    }
                    select.appendChild(option);
                });
            }
        });
    }

    // Attacher l'événement de changement de spécialité
    document.addEventListener('DOMContentLoaded', function() {
        const specialitySelect = document.getElementById('diseaseSpecialitySelect');
        if (specialitySelect) {
            specialitySelect.addEventListener('change', updateMedecinSelectsBySpeciality);
            // Initialiser au chargement de la page
            updateMedecinSelectsBySpeciality();
        }
    });
}

// Pagination AJAX pour les patients
function initPatientPagination() {
    const filtersForm = document.getElementById('patientFilters');
    const tableBlock = document.getElementById('patient-table-block');
    
    if (!filtersForm || !tableBlock) return;
    
    function fetchPatientsAJAX() {
        const params = new URLSearchParams(new FormData(filtersForm)).toString();
        fetch(`?${params}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.json())
        .then(data => {
            tableBlock.innerHTML = data.html;
        });
    }
    
    const searchInput = filtersForm.querySelector('input[name="search"]');
    const medecinSelect = filtersForm.querySelector('select[name="medecin"]');
    
    if (searchInput) searchInput.addEventListener('input', fetchPatientsAJAX);
    if (medecinSelect) medecinSelect.addEventListener('change', fetchPatientsAJAX);
    
    // Pagination AJAX
    tableBlock.addEventListener('click', function(e) {
        if (e.target.classList.contains('page-ajax')) {
            e.preventDefault();
            fetch(e.target.href, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(response => response.json())
                .then(data => {
                    tableBlock.innerHTML = data.html;
                });
        }
    });
}

// Initialisation générale
document.addEventListener('DOMContentLoaded', function() {
    // Initialisation du formulaire de rendez-vous
    initAppointmentForm();
    
    // Initialisation du calendrier
    initCalendar();
    
    // Initialisation de la pagination des rendez-vous
    bindRdvPagination();
    
    // Initialisation des filtres de rendez-vous
    bindRdvFilters();
    
    // Gestion des messages de rendez-vous
    handleAppointmentMessages();
    
    // Initialisation du formulaire patient
    initPatientForm();
    
    // Gestion des messages patient
    handlePatientMessages();
    
    // Gestion de la suppression de patient
    handlePatientDeletion();
    
    // Gestion du scroll d'édition
    handleEditScroll();
    
    // Initialisation de la pagination des patients
    initPatientPagination();
    
    // Initialisation des selects de médecins
    initMedecinSelects();
    
    // Gestion du bouton d'ajout de patient
    const newPatientBtn = document.querySelector('a[href="#new-patient"]');
    if (newPatientBtn) {
        newPatientBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // Nettoyer l'URL pour enlever ?patient_id=... et scroller sur le formulaire
            window.location.href = window.location.pathname + '#new-patient';
        });
    }
});
