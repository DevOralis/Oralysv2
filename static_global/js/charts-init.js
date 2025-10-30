/**
 * Initialisation des graphiques Chart.js pour essential_components.html
 * Ce fichier initialise uniquement les graphiques existants dans la section Charts & Graphs
 */

document.addEventListener('DOMContentLoaded', function() {
    // Configuration commune pour tous les graphiques
    Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#666';

    // Graphique Linéaire - Évolution des Patients (ID: lineChart)
    const lineCtx = document.getElementById('lineChart');
    if (lineCtx) {
        new Chart(lineCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû'],
                datasets: [{
                    label: 'Nouveaux Patients',
                    data: [65, 78, 90, 81, 95, 105, 120, 140],
                    borderColor: '#1e90ff',
                    backgroundColor: 'rgba(30, 144, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Patients Sortants',
                    data: [45, 52, 68, 72, 85, 88, 95, 110],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Évolution mensuelle des patients'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Graphique en Barres - Consultations par Mois (ID: barChart)
    const barCtx = document.getElementById('barChart');
    if (barCtx) {
        new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû'],
                datasets: [{
                    label: 'Consultations',
                    data: [120, 190, 300, 500, 200, 300, 450, 380],
                    backgroundColor: [
                        'rgba(30, 144, 255, 0.8)',
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(220, 53, 69, 0.8)',
                        'rgba(23, 162, 184, 0.8)',
                        'rgba(108, 117, 125, 0.8)',
                        'rgba(102, 16, 242, 0.8)',
                        'rgba(255, 99, 132, 0.8)'
                    ],
                    borderColor: [
                        '#1e90ff',
                        '#28a745',
                        '#ffc107',
                        '#dc3545',
                        '#17a2b8',
                        '#6c757d',
                        '#6610f2',
                        '#ff6384'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Nombre de consultations par mois'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Graphique Secteurs - Répartition par Département (ID: pieChart)
    const pieCtx = document.getElementById('pieChart');
    if (pieCtx) {
        new Chart(pieCtx, {
            type: 'pie',
            data: {
                labels: ['Cardiologie', 'Pédiatrie', 'Chirurgie', 'Urgences', 'Autres'],
                datasets: [{
                    data: [35, 25, 20, 15, 5],
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF'
                    ],
                    borderColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Répartition des patients par département'
                    }
                }
            }
        });
    }

    // Graphique Donut - Statut des Rendez-vous (ID: doughnutChart)
    const donutCtx = document.getElementById('doughnutChart');
    if (donutCtx) {
        new Chart(donutCtx, {
            type: 'doughnut',
            data: {
                labels: ['Confirmés', 'En attente', 'Annulés', 'Reportés'],
                datasets: [{
                    data: [60, 25, 10, 5],
                    backgroundColor: [
                        '#28a745',
                        '#ffc107',
                        '#dc3545',
                        '#6c757d'
                    ],
                    borderColor: [
                        '#28a745',
                        '#ffc107',
                        '#dc3545',
                        '#6c757d'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Statut des rendez-vous'
                    }
                },
                cutout: '50%'
            }
        });
    }

    // Graphique en Aire - Occupation des Lits (ID: areaChart)
    const areaCtx = document.getElementById('areaChart');
    if (areaCtx) {
        new Chart(areaCtx, {
            type: 'line',
            data: {
                labels: ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
                datasets: [{
                    label: 'Lits Occupés',
                    data: [85, 92, 88, 95, 90, 78, 82],
                    borderColor: '#1e90ff',
                    backgroundColor: 'rgba(30, 144, 255, 0.3)',
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Capacité Totale',
                    data: [100, 100, 100, 100, 100, 100, 100],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    fill: false,
                    borderDash: [5, 5]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Taux d\'occupation des lits par jour'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 110
                    }
                }
            }
        });
    }

    // Graphique Mixte - Revenus vs Dépenses (ID: mixedChart)
    const mixedCtx = document.getElementById('mixedChart');
    if (mixedCtx) {
        new Chart(mixedCtx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun'],
                datasets: [{
                    type: 'bar',
                    label: 'Revenus',
                    data: [50000, 60000, 55000, 70000, 65000, 80000],
                    backgroundColor: 'rgba(30, 144, 255, 0.8)',
                    borderColor: '#1e90ff',
                    borderWidth: 1
                }, {
                    type: 'line',
                    label: 'Dépenses',
                    data: [35000, 45000, 40000, 50000, 48000, 55000],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    fill: false,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Analyse financière mensuelle'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString() + ' €';
                            }
                        }
                    }
                }
            }
        });
    }
});
