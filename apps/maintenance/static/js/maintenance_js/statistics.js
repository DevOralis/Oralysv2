/**
 * Gestion des graphiques des statistiques - Maintenance
 * Gère l'affichage de tous les graphiques Chart.js
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initialisation des graphiques...');
    
    // Attendre que Chart.js soit chargé
    if (typeof Chart === 'undefined') {
        console.error('Chart.js n\'est pas chargé');
        return;
    }
    
    // Initialiser tous les graphiques
    initializeAllCharts();
});

function initializeAllCharts() {
    try {
        // Graphiques des conventions
        initializeConventionCharts();
        
        // Graphiques des visiteurs
        initializeVisiteurCharts();
        
        // Graphiques des incidents
        initializeIncidentCharts();
        
        // Graphiques des interventions
        initializeInterventionCharts();
        
    } catch (error) {
        console.error('Erreur lors de l\'initialisation des graphiques:', error);
    }
}

function initializeConventionCharts() {
    try {
        // Conventions par prestataire (supplier)
        const conventionsPrestataireData = window.conventionsPrestataireData || [];
        if (conventionsPrestataireData && conventionsPrestataireData.length > 0) {
            createBarChart('conventionsPrestataireChart', 
                conventionsPrestataireData.map(item => item.supplier__nom || 'N/A'),
                conventionsPrestataireData.map(item => item.count),
                'Nombre de Conventions'
            );
        }
        
        // Conventions par type
        const conventionsTypeData = window.conventionsTypeData || [];
        if (conventionsTypeData && conventionsTypeData.length > 0) {
            createDoughnutChart('conventionsTypeChart',
                conventionsTypeData.map(item => item.type_convention === 'préventive' ? 'Préventive' : 'Corrective'),
                conventionsTypeData.map(item => item.count)
            );
        }
        
        // Conventions par période
        const conventionsPeriodeData = window.conventionsPeriodeData || [];
        if (conventionsPeriodeData && conventionsPeriodeData.length > 0) {
            createLineChart('conventionsPeriodeChart',
                conventionsPeriodeData.map(item => {
                    const date = new Date(item.mois);
                    return date.toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' });
                }),
                conventionsPeriodeData.map(item => item.count),
                'Conventions créées'
            );
        }
    } catch (error) {
        console.error('Erreur dans initializeConventionCharts:', error);
    }
}

function initializeVisiteurCharts() {
    try {
        // Visiteurs par motif
        const visiteursMotifData = window.visiteursMotifData || [];
        if (visiteursMotifData && visiteursMotifData.length > 0) {
            createBarChart('visiteursMotifChart',
                visiteursMotifData.map(item => item.motif_visite || 'N/A'),
                visiteursMotifData.map(item => item.count),
                'Nombre de Visiteurs'
            );
        }
        
        // Durée moyenne des visites
        const visiteursDureeData = window.visiteursDureeData || [];
        if (visiteursDureeData && visiteursDureeData.length > 0) {
            createLineChart('visiteursDureeChart',
                visiteursDureeData.map(item => {
                    const date = new Date(item.date);
                    return date.toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' });
                }),
                visiteursDureeData.map(item => item.duree_moyenne),
                'Durée Moyenne (minutes)'
            );
        }
    } catch (error) {
        console.error('Erreur dans initializeVisiteurCharts:', error);
    }
}

function initializeIncidentCharts() {
    try {
        // Incidents par statut
        const incidentsStatutData = window.incidentsStatutData || [];
        if (incidentsStatutData && incidentsStatutData.length > 0) {
            createDoughnutChart('incidentsStatutChart',
                incidentsStatutData.map(item => item.statut || 'N/A'),
                incidentsStatutData.map(item => item.count)
            );
        }
        
        // Incidents par type
        const incidentsTypeData = window.incidentsTypeData || [];
        if (incidentsTypeData && incidentsTypeData.length > 0) {
            createBarChart('incidentsTypeChart',
                incidentsTypeData.map(item => item.type || 'N/A'),
                incidentsTypeData.map(item => item.count),
                'Nombre d\'Incidents'
            );
        }
        
        // Incidents par gravité
        const incidentsGraviteData = window.incidentsGraviteData || [];
        if (incidentsGraviteData && incidentsGraviteData.length > 0) {
            createPieChart('incidentsGraviteChart',
                incidentsGraviteData.map(item => item.gravite || 'N/A'),
                incidentsGraviteData.map(item => item.count)
            );
        }
        
        // Incidents par équipement
        const incidentsEquipementData = window.incidentsEquipementData || [];
        if (incidentsEquipementData && incidentsEquipementData.length > 0) {
            createBarChart('incidentsEquipementChart',
                incidentsEquipementData.map(item => item.equipement__nom || 'N/A'),
                incidentsEquipementData.map(item => item.count),
                'Nombre d\'Incidents'
            );
        }
        
        // Incidents par année
        const incidentsAnneeData = window.incidentsAnneeData || [];
        if (incidentsAnneeData && incidentsAnneeData.length > 0) {
            createLineChart('incidentsAnneeChart',
                incidentsAnneeData.map(item => item.annee),
                incidentsAnneeData.map(item => item.count),
                'Incidents'
            );
        }
    } catch (error) {
        console.error('Erreur dans initializeIncidentCharts:', error);
    }
}

function initializeInterventionCharts() {
    try {
        // Interventions par statut
        const interventionsStatutData = window.interventionsStatutData || [];
        if (interventionsStatutData && interventionsStatutData.length > 0) {
            createDoughnutChart('interventionsStatutChart',
                interventionsStatutData.map(item => item.statut || 'N/A'),
                interventionsStatutData.map(item => item.count)
            );
        }
        
        // Interventions par type
        const interventionsTypeData = window.interventionsTypeData || [];
        if (interventionsTypeData && interventionsTypeData.length > 0) {
            createPieChart('interventionsTypeChart',
                interventionsTypeData.map(item => item.type_intervention === 'preventive' ? 'Préventive' : 'Corrective'),
                interventionsTypeData.map(item => item.count)
            );
        }
        
        // Interventions par criticité
        const interventionsCriticiteData = window.interventionsCriticiteData || [];
        if (interventionsCriticiteData && interventionsCriticiteData.length > 0) {
            createBarChart('interventionsCriticiteChart',
                interventionsCriticiteData.map(item => {
                    const criticite = item.criticite || 'N/A';
                    return criticite === 'faible' ? 'Faible' : 
                           criticite === 'moyenne' ? 'Moyenne' : 
                           criticite === 'haute' ? 'Haute' : criticite;
                }),
                interventionsCriticiteData.map(item => item.count),
                'Nombre d\'Interventions'
            );
        }
        
        // Interventions par prestataire
        const interventionsPrestataireData = window.interventionsPrestataireData || [];
        if (interventionsPrestataireData && interventionsPrestataireData.length > 0) {
            createBarChart('interventionsPrestataireChart',
                interventionsPrestataireData.map(item => item.supplier__nom || 'N/A'),
                interventionsPrestataireData.map(item => item.count),
                'Nombre d\'Interventions'
            );
        }
        
        // Interventions par équipement
        const interventionsEquipementData = window.interventionsEquipementData || [];
        if (interventionsEquipementData && interventionsEquipementData.length > 0) {
            createBarChart('interventionsEquipementChart',
                interventionsEquipementData.map(item => item.equipement__nom || 'N/A'),
                interventionsEquipementData.map(item => item.count),
                'Nombre d\'Interventions'
            );
        }
        
        // Interventions par période
        const interventionsPeriodeData = window.interventionsPeriodeData || [];
        if (interventionsPeriodeData && interventionsPeriodeData.length > 0) {
            createLineChart('interventionsPeriodeChart',
                interventionsPeriodeData.map(item => {
                    const date = new Date(item.mois);
                    return date.toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' });
                }),
                interventionsPeriodeData.map(item => item.count),
                'Interventions créées'
            );
        }
        
        // Interventions par période détaillée
        const aujourd_hui = window.interventionsAujourdHui || 0;
        const semaine = window.interventionsSemaine || 0;
        const mois = window.interventionsMois || 0;
        
        if (aujourd_hui > 0 || semaine > 0 || mois > 0) {
            createBarChart('interventionsPeriodeDetailChart',
                ['Aujourd\'hui', 'Cette Semaine', 'Ce Mois'],
                [aujourd_hui, semaine, mois],
                'Nombre d\'Interventions'
            );
        }
        
        // Interventions par type et criticité
        const preventivesFaible = window.interventionsPreventivesFaible || 0;
        const preventivesMoyenne = window.interventionsPreventivesMoyenne || 0;
        const preventivesHaute = window.interventionsPreventivesHaute || 0;
        const correctivesFaible = window.interventionsCorrectivesFaible || 0;
        const correctivesMoyenne = window.interventionsCorrectivesMoyenne || 0;
        const correctivesHaute = window.interventionsCorrectivesHaute || 0;
        
        if (preventivesFaible > 0 || preventivesMoyenne > 0 || preventivesHaute > 0 || 
            correctivesFaible > 0 || correctivesMoyenne > 0 || correctivesHaute > 0) {
            
            createStackedBarChart('interventionsTypeCriticiteChart',
                ['Préventives', 'Correctives'],
                [
                    {
                        label: 'Faible',
                        data: [preventivesFaible, correctivesFaible],
                        backgroundColor: 'rgba(75, 192, 192, 0.8)'
                    },
                    {
                        label: 'Moyenne',
                        data: [preventivesMoyenne, correctivesMoyenne],
                        backgroundColor: 'rgba(255, 206, 86, 0.8)'
                    },
                    {
                        label: 'Haute',
                        data: [preventivesHaute, correctivesHaute],
                        backgroundColor: 'rgba(255, 99, 132, 0.8)'
                    }
                ]
            );
        }
    } catch (error) {
        console.error('Erreur dans initializeInterventionCharts:', error);
    }
}

// Fonctions utilitaires pour créer les graphiques
function createBarChart(canvasId, labels, data, label) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.warn(`Canvas ${canvasId} non trouvé`);
        return;
    }
    
    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.warn(`Contexte 2D non disponible pour ${canvasId}`);
        return;
    }
    
    const colors = [
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 99, 132, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)'
    ];
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: colors.slice(0, labels.length).map(color => color.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function createDoughnutChart(canvasId, labels, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const colors = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(255, 206, 86, 0.8)'
    ];
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: colors.slice(0, labels.length).map(color => color.replace('0.8', '1')),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function createPieChart(canvasId, labels, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const colors = [
        'rgba(75, 192, 192, 0.8)',
        'rgba(255, 99, 132, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(153, 102, 255, 0.8)'
    ];
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: colors.slice(0, labels.length).map(color => color.replace('0.8', '1')),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function createLineChart(canvasId, labels, data, label) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const color = 'rgba(75, 192, 192, 1)';
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                borderColor: color,
                backgroundColor: color.replace('1', '0.2'),
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: color,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

function createStackedBarChart(canvasId, labels, datasets) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

