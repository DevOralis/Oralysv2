-- ============================================================================
-- Script SQL pour remplir les tables du module Maintenance (PostgreSQL)
-- ============================================================================
-- Ce script crée des données de test pour toutes les tables du module Maintenance
-- Base de données: PostgreSQL
-- ============================================================================

BEGIN;

-- Vider les tables maintenance existantes (dans l'ordre des dépendances)
TRUNCATE TABLE maintenance_intervention CASCADE;
TRUNCATE TABLE maintenance_incident CASCADE;
TRUNCATE TABLE maintenance_equipement CASCADE;
TRUNCATE TABLE maintenance_visiteur CASCADE;
TRUNCATE TABLE maintenance_convention CASCADE;
TRUNCATE TABLE maintenance_typemaintenance CASCADE;

-- ============================================================================
-- 1. TABLE: maintenance_typemaintenance (Types de maintenance)
-- ============================================================================
INSERT INTO maintenance_typemaintenance (id, code, libelle) VALUES
(1, 'PREV-001', 'Maintenance préventive systématique'),
(2, 'PREV-002', 'Maintenance préventive conditionnelle'),
(3, 'CORR-001', 'Maintenance corrective curative'),
(4, 'CORR-002', 'Maintenance corrective palliative'),
(5, 'PREV-003', 'Maintenance préventive prédictive'),
(6, 'VERIF-001', 'Vérification périodique'),
(7, 'CALIB-001', 'Calibration équipements'),
(8, 'HYGI-001', 'Nettoyage et hygiène'),
(9, 'SECU-001', 'Contrôle sécurité'),
(10, 'TECH-001', 'Mise à jour technique');

-- Réinitialiser la séquence
SELECT setval('maintenance_typemaintenance_id_seq', (SELECT MAX(id) FROM maintenance_typemaintenance));

-- ============================================================================
-- 2. TABLE: maintenance_convention (Conventions de maintenance)
-- ============================================================================
-- Note: Utilise les fournisseurs créés dans purchases_supplier
INSERT INTO maintenance_convention (
    id, supplier_id, type_convention, type_maintenance_id, date_debut, date_fin,
    description, cout_mensuel, active, created_at, updated_at
) VALUES
(1, 1, 'préventive', 1, '2024-01-01', '2024-12-31',
 'Convention de maintenance préventive annuelle pour équipements médicaux - MedEquip Maroc', 5000.00, true, NOW(), NOW()),
 
(2, 1, 'préventive', 2, '2024-01-01', '2024-06-30',
 'Convention de maintenance conditionnelle - Premier semestre - MedEquip Maroc', 3500.00, true, NOW(), NOW()),
 
(3, 4, 'corrective', 3, '2024-01-01', '2024-12-31',
 'Convention de maintenance corrective - Intervention sur panne - MediTech Europe', 4000.00, true, NOW(), NOW()),
 
(4, 1, 'préventive', 6, '2024-01-01', '2024-12-31',
 'Vérification périodique des équipements de sécurité - MedEquip Maroc', 2500.00, true, NOW(), NOW()),
 
(5, 4, 'corrective', 4, '2024-07-01', '2024-12-31',
 'Maintenance palliative - Deuxième semestre - MediTech Europe', 3000.00, false, NOW(), NOW());

-- Réinitialiser la séquence
SELECT setval('maintenance_convention_id_seq', (SELECT MAX(id) FROM maintenance_convention));

-- ============================================================================
-- 3. TABLE: maintenance_visiteur (Visiteurs)
-- ============================================================================
INSERT INTO maintenance_visiteur (
    id, nom, prenom, email, telephone, date_entree, date_sortie, motif_visite
) VALUES
(1, 'Alami', 'Hassan', 'hassan.alami@email.ma', '+212612345678', 
 '2024-01-15 09:00:00', '2024-01-15 11:30:00', 'Inspection des équipements médicaux'),
 
(2, 'Benani', 'Fatima', 'fatima.benani@email.ma', '+212623456789',
 '2024-01-15 10:00:00', '2024-01-15 12:00:00', 'Livraison de matériel médical'),
 
(3, 'El Fassi', 'Mohammed', 'mohammed.fassi@email.ma', '+212634567890',
 '2024-01-16 08:30:00', '2024-01-16 10:00:00', 'Maintenance préventive scanner'),
 
(4, 'Tazi', 'Amina', 'amina.tazi@email.ma', '+212645678901',
 '2024-01-16 14:00:00', '2024-01-16 16:30:00', 'Installation nouvel équipement'),
 
(5, 'Chraibi', 'Youssef', 'youssef.chraibi@email.ma', '+212656789012',
 '2024-01-17 09:00:00', NULL, 'Visite technique en cours'),
 
(6, 'Lahlou', 'Sara', 'sara.lahlou@email.ma', '+212667890123',
 '2024-01-17 11:00:00', NULL, 'Formation personnel technique'),
 
(7, 'Benjelloun', 'Karim', 'karim.benjelloun@email.ma', '+212678901234',
 '2024-01-18 08:00:00', '2024-01-18 17:00:00', 'Audit des équipements'),
 
(8, 'Ouazzani', 'Leila', 'leila.ouazzani@email.ma', '+212689012345',
 '2024-01-18 13:00:00', '2024-01-18 15:00:00', 'Contrôle qualité'),
 
(9, 'Berrada', 'Omar', 'omar.berrada@email.ma', '+212690123456',
 '2024-01-19 09:30:00', '2024-01-19 12:00:00', 'Calibration instruments'),
 
(10, 'Naciri', 'Nadia', 'nadia.naciri@email.ma', '+212601234567',
 '2024-01-19 14:00:00', '2024-01-19 16:00:00', 'Visite de suivi technique');

-- Réinitialiser la séquence
SELECT setval('maintenance_visiteur_id_seq', (SELECT MAX(id) FROM maintenance_visiteur));

-- ============================================================================
-- 4. TABLE: maintenance_equipement (Équipements)
-- ============================================================================
INSERT INTO maintenance_equipement (id, nom, reference, date_acquisition, emplacement, etat) VALUES
(1, 'Scanner IRM Siemens', 'IRM-001', '2020-01-15', 'Service Radiologie - Salle 1', 'bon'),
(2, 'Échographe GE Healthcare', 'ECHO-001', '2021-03-20', 'Service Radiologie - Salle 2', 'bon'),
(3, 'Moniteur Patient Philips', 'MON-001', '2022-05-10', 'Réanimation - Box 1', 'neuf'),
(4, 'Défibrillateur Zoll', 'DEF-001', '2021-08-15', 'Urgences - Salle 1', 'bon'),
(5, 'Ventilateur Médical Dräger', 'VENT-001', '2020-11-01', 'Réanimation - Box 2', 'moyen'),
(6, 'Électrocardiographe Fukuda', 'ECG-001', '2019-06-20', 'Cardiologie - Cabinet 1', 'bon'),
(7, 'Microscope Olympus', 'MICRO-001', '2021-02-14', 'Laboratoire - Section A', 'bon'),
(8, 'Centrifugeuse Eppendorf', 'CENTRI-001', '2020-09-25', 'Laboratoire - Section B', 'bon'),
(9, 'Incubateur Memmert', 'INCUB-001', '2022-01-10', 'Laboratoire - Section C', 'neuf'),
(10, 'Autoclave Tuttnauer', 'AUTO-001', '2019-04-18', 'Stérilisation', 'moyen'),
(11, 'Table Opératoire Maquet', 'TABLE-001', '2021-07-22', 'Bloc Opératoire - Salle 1', 'bon'),
(12, 'Lampe Scialytique Trumpf', 'LAMP-001', '2021-07-22', 'Bloc Opératoire - Salle 1', 'bon'),
(13, 'Pompe à Perfusion Braun', 'POMPE-001', '2022-03-15', 'Service Soins - Chambre 101', 'neuf'),
(14, 'Aspirateur Chirurgical Medela', 'ASPIR-001', '2020-12-05', 'Bloc Opératoire - Salle 2', 'bon'),
(15, 'Lit Médicalisé Hill-Rom', 'LIT-001', '2019-08-30', 'Service Soins - Chambre 102', 'moyen');

-- Réinitialiser la séquence
SELECT setval('maintenance_equipement_id_seq', (SELECT MAX(id) FROM maintenance_equipement));

-- ============================================================================
-- 5. TABLE: maintenance_incident (Incidents)
-- ============================================================================
INSERT INTO maintenance_incident (
    id, equipement_id, date_declaration, description, type, statut, gravite
) VALUES
(1, 1, '2024-01-10 08:30:00', 'Bruit anormal lors du fonctionnement du scanner', 'panne', 'resolu', 'moyenne'),
(2, 5, '2024-01-12 14:00:00', 'Alarme pression ventilateur défectueuse', 'defaillance', 'en_cours', 'haute'),
(3, 10, '2024-01-13 09:15:00', 'Température autoclave ne monte pas correctement', 'panne', 'ouvert', 'haute'),
(4, 6, '2024-01-14 11:00:00', 'Écran ECG présente des lignes parasites', 'defaillance', 'resolu', 'faible'),
(5, 13, '2024-01-15 16:30:00', 'Pompe à perfusion s''arrête de façon intermittente', 'panne', 'en_cours', 'haute'),
(6, 2, '2024-01-16 10:00:00', 'Image échographe floue', 'maintenance', 'ouvert', 'moyenne'),
(7, 11, '2024-01-17 07:45:00', 'Table opératoire bloquée en position haute', 'panne', 'en_cours', 'haute'),
(8, 15, '2024-01-18 13:20:00', 'Mécanisme électrique du lit ne fonctionne plus', 'panne', 'ouvert', 'moyenne'),
(9, 7, '2024-01-19 09:00:00', 'Objectif du microscope désaligné', 'accident', 'resolu', 'faible'),
(10, 4, '2024-01-19 15:30:00', 'Batterie du défibrillateur ne charge plus', 'defaillance', 'ouvert', 'haute');

-- Réinitialiser la séquence
SELECT setval('maintenance_incident_id_seq', (SELECT MAX(id) FROM maintenance_incident));

-- ============================================================================
-- 6. TABLE: maintenance_intervention (Interventions)
-- ============================================================================
INSERT INTO maintenance_intervention (
    id, equipement_id, supplier_id, date_intervention, type_intervention,
    criticite, description, statut
) VALUES
(1, 1, NULL, '2024-01-11 09:00:00', 'corrective', 'moyenne',
 'Remplacement roulement défectueux du scanner IRM', 'terminee'),
 
(2, 5, NULL, '2024-01-13 10:00:00', 'corrective', 'haute',
 'Intervention en cours sur alarme ventilateur', 'en_cours'),
 
(3, 6, NULL, '2024-01-15 08:30:00', 'corrective', 'faible',
 'Nettoyage des électrodes ECG', 'terminee'),
 
(4, 2, NULL, '2024-02-01 09:00:00', 'preventive', 'faible',
 'Maintenance préventive échographe - planifiée', 'planifiee'),
 
(5, 3, NULL, '2024-02-05 14:00:00', 'preventive', 'faible',
 'Vérification calibration moniteur patient', 'planifiee'),
 
(6, 7, NULL, '2024-01-20 08:00:00', 'corrective', 'faible',
 'Réalignement objectif microscope', 'terminee'),
 
(7, 11, NULL, '2024-01-18 08:00:00', 'corrective', 'haute',
 'Réparation mécanisme hydraulique table opératoire', 'en_cours'),
 
(8, 8, NULL, '2024-02-10 10:00:00', 'preventive', 'moyenne',
 'Contrôle et graissage centrifugeuse', 'planifiee'),
 
(9, 9, NULL, '2024-02-15 11:00:00', 'preventive', 'faible',
 'Vérification température et humidité incubateur', 'planifiee'),
 
(10, 12, NULL, '2024-02-20 09:00:00', 'preventive', 'moyenne',
 'Changement ampoules lampe scialytique', 'planifiee');

-- Réinitialiser la séquence
SELECT setval('maintenance_intervention_id_seq', (SELECT MAX(id) FROM maintenance_intervention));

COMMIT;

-- ============================================================================
-- MESSAGE DE CONFIRMATION
-- ============================================================================
SELECT 'DONNEES MAINTENANCE CREEES AVEC SUCCES!' as message;

-- ============================================================================
-- RÉSUMÉ DES DONNÉES CRÉÉES
-- ============================================================================
SELECT 
    'RÉSUMÉ DES DONNÉES CRÉÉES' as titre,
    (SELECT COUNT(*) FROM maintenance_typemaintenance) as "Types de maintenance",
    (SELECT COUNT(*) FROM maintenance_convention) as "Conventions",
    (SELECT COUNT(*) FROM maintenance_visiteur) as "Visiteurs",
    (SELECT COUNT(*) FROM maintenance_equipement) as "Équipements",
    (SELECT COUNT(*) FROM maintenance_incident) as "Incidents",
    (SELECT COUNT(*) FROM maintenance_intervention) as "Interventions";

