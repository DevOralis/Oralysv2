// JavaScript spécifique pour le module de rendez-vous

document.addEventListener('DOMContentLoaded', function() {
    window.scrollTo(0, 0);
    // Initialisation du module de rendez-vous
    initializeAppointmentModule();
});

function initializeAppointmentModule() {
    // Gestion des messages de succès/erreur
    handleAppointmentMessages();
    
    // Initialisation des filtres de rendez-vous
    initializeAppointmentFilters();
    
    // Initialisation de la pagination
    initializeAppointmentPagination();
    
    // Liaison des événements du calendrier
    bindCalendarEvents();
    
    // Initialisation du formulaire de patient
    initializePatientForm();
    
    // Initialisation du calendrier
    initializeCalendar();
}

function handleAppointmentMessages() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Message de succès pour la création de rendez-vous
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
    
    // Message de succès pour l'ajout de rendez-vous
    if (urlParams.get('success') === 'add') {
        Swal.fire({
            icon: 'success',
            title: 'Succès',
            text: 'Rendez-vous enregistré avec succès !',
            timer: 2000,
            showConfirmButton: false
        });
        urlParams.delete('success');
        window.history.replaceState({}, document.title, window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : ''));
    }
    
    // Message d'erreur
    if (urlParams.get('error')) {
        Swal.fire({
            icon: 'error',
            title: 'Erreur',
            text: urlParams.get('error'),
            showConfirmButton: true
        });
        urlParams.delete('error');
        window.history.replaceState({}, document.title, window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : ''));
    }
    
    // Message d'erreur créneau occupé
    // Note: This would need to be handled differently since we're removing inline Django template code
}

function initializePatientForm() {
    const yesRadio = document.getElementById('isExistingYes');
    const noRadio = document.getElementById('isExistingNo');
    const patientSelectDiv = document.getElementById('patientSelectDiv');
    const patientSelect = document.getElementById('patientSelect');
    const nomInput = document.getElementById('nomInput');
    const prenomInput = document.getElementById('prenomInput');
    const telephoneInput = document.getElementById('telephoneInput');
    const emailInput = document.getElementById('emailInput');
    const sourceInput = document.getElementById('sourceInput');
    
    if (!yesRadio || !noRadio || !patientSelectDiv || !patientSelect || !nomInput || !prenomInput || !telephoneInput || !emailInput) {
        return;
    }

    function setFieldsDisabled(disabled) {
        nomInput.disabled = disabled;
        prenomInput.disabled = disabled;
        telephoneInput.disabled = disabled;
        emailInput.disabled = disabled;
    }

    function clearFields() {
        nomInput.value = '';
        prenomInput.value = '';
        telephoneInput.value = '';
        emailInput.value = '';
        if (sourceInput) sourceInput.value = '';
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
    
    // Initial state
    if (yesRadio.checked) {
        patientSelectDiv.style.display = '';
        setFieldsDisabled(true);
    } else {
        patientSelectDiv.style.display = 'none';
        setFieldsDisabled(false);
    }
    
    patientSelect.addEventListener('change', function() {
        const selected = patientSelect.options[patientSelect.selectedIndex];
        nomInput.value = selected.getAttribute('data-nom') || '';
        prenomInput.value = selected.getAttribute('data-prenom') || '';
        telephoneInput.value = selected.getAttribute('data-telephone') || '';
        emailInput.value = selected.getAttribute('data-email') || '';
        if (sourceInput) sourceInput.value = selected.getAttribute('data-source') || '';
    });
}

function initializeCalendar() {
    var calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;
    
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: window.innerWidth < 768 ? 'timeGridDay' : 'timeGridWeek',
        locale: 'fr',
        slotMinTime: '08:00:00',
        slotMaxTime: '20:00:00',
        allDaySlot: false,
        height: 'auto',
        contentHeight: 'auto',
        aspectRatio: window.innerWidth < 768 ? 0.8 : 1.35,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: window.innerWidth < 768 ? 'timeGridDay,dayGridMonth' : 'timeGridDay,timeGridWeek,dayGridMonth'
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
        },
        windowResize: function(view) {
            // Ajuster la vue selon la taille de l'écran
            if (window.innerWidth < 768) {
                calendar.changeView('timeGridDay');
            } else {
                calendar.changeView('timeGridWeek');
            }
        }
    });
    
    calendar.render();
    
    // Stocker le calendrier dans une variable globale pour y accéder depuis d'autres fonctions
    window.appointmentCalendar = calendar;
    
    // Charger les événements du médecin sélectionné
    var calendarMedecinSelect = document.getElementById('calendarDoctorFilter');
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

function loadMedecinEvents(medecinId) {
    // Si aucun médecin sélectionné, retirer tous les événements
    if (!medecinId) {
        if (window.appointmentCalendar) {
            window.appointmentCalendar.removeAllEvents();
        }
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
            if (window.appointmentCalendar) {
                window.appointmentCalendar.removeAllEvents();
                events.forEach(appointment => {
                    // Calculer la fin du rendez-vous (+ 1 heure) avec JavaScript natif
                    const startDate = new Date(appointment.date_heure);
                    const endDate = new Date(startDate.getTime() + 60 * 60000); // +1 heure
                    
                    window.appointmentCalendar.addEvent({
                        id: appointment.id,
                        title: appointment.patient_nom || 'Anonyme', // Nom du patient seulement
                        start: appointment.date_heure,
                        end: endDate.toISOString(),
                        backgroundColor: '#007bff', // Couleur bleue
                        borderColor: '#007bff', // Couleur bleue
                        extendedProps: appointment
                    });
                });
            }
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

function initializeAppointmentFilters() {
    // Cette fonction peut être étendue pour gérer les filtres de rendez-vous
    // si nécessaire
    bindRdvFilters();
}

function initializeAppointmentPagination() {
    // Gestion de la pagination AJAX pour les rendez-vous
    const appointmentTableBlock = document.getElementById('appointment-table-block');
    
    if (appointmentTableBlock) {
        appointmentTableBlock.addEventListener('click', function(e) {
            if (e.target.classList.contains('page-ajax')) {
                e.preventDefault();
                fetchAppointmentPage(e.target.href);
            }
        });
    }
    
    // Initialiser la pagination pour les rendez-vous récents
    bindRdvPagination();
}

function fetchAppointmentPage(url) {
    const appointmentTableBlock = document.getElementById('appointment-table-block');
    if (!appointmentTableBlock) return;
    
    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(response => response.json())
        .then(data => {
            appointmentTableBlock.innerHTML = data.html;
            // Réattacher les événements après mise à jour du contenu
            bindRdvPagination();
            bindRdvFilters();
        })
        .catch(error => {
            console.error('Error loading appointment page:', error);
        });
}

function bindCalendarEvents() {
    // Cette fonction peut être étendue pour gérer les événements du calendrier
    // si nécessaire
}

// Pagination AJAX pour rendez-vous récents
function bindRdvPagination() {
    const appointmentsTable = document.getElementById('appointments-table');
    if (!appointmentsTable) return;
    
    document.querySelectorAll('#appointments-table .page-ajax').forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            // Extraire les paramètres de l'URL
            const url = new URL(this.href);
            const params = new URLSearchParams(url.search);
            // Ajouter l'en-tête pour indiquer que c'est une requête AJAX
            fetch('/patient/appointments/table/?' + params.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('appointments-table').innerHTML = data.html;
                    bindRdvPagination();
                    bindRdvFilters(); // Réattacher les événements pour les filtres
                })
                .catch(error => {
                    console.error('Error loading appointment page:', error);
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
        })
        .catch(error => {
            console.error('Error loading appointment data:', error);
        });
}

function bindRdvFilters() {
    const searchInput = document.getElementById('search-appointment');
    const medecinSelect = document.getElementById('filter-appointment-medecin');
    const statutSelect = document.getElementById('filter-appointment-statut');
    
    if (searchInput) {
        // Supprimer l'event listener existant s'il y en a un
        searchInput.removeEventListener('input', triggerRdvAjax);
        searchInput.addEventListener('input', triggerRdvAjax);
    }
    
    if (medecinSelect) {
        // Supprimer l'event listener existant s'il y en a un
        medecinSelect.removeEventListener('change', triggerRdvAjax);
        medecinSelect.addEventListener('change', triggerRdvAjax);
    }
    
    if (statutSelect) {
        // Supprimer l'event listener existant s'il y en a un
        statutSelect.removeEventListener('change', triggerRdvAjax);
        statutSelect.addEventListener('change', triggerRdvAjax);
    }
}

// Fonction utilitaire pour obtenir un cookie
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
