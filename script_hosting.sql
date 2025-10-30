-- ============================================================================
-- Script SQL pour remplir les tables du module Hosting (PostgreSQL)
-- ============================================================================
-- Ce script crée des données de test pour toutes les tables du module Hosting
-- Base de données: PostgreSQL
-- ============================================================================

BEGIN;

-- Vider les tables hosting existantes (dans l'ordre des dépendances)
TRUNCATE TABLE hosting_companion CASCADE;
TRUNCATE TABLE hosting_reservation CASCADE;
TRUNCATE TABLE hosting_admission CASCADE;
TRUNCATE TABLE hosting_bed CASCADE;
TRUNCATE TABLE hosting_room CASCADE;
TRUNCATE TABLE hosting_bedstatus CASCADE;
TRUNCATE TABLE hosting_roomtype CASCADE;

-- ============================================================================
-- 1. TABLE: hosting_roomtype (Types de chambres)
-- ============================================================================
INSERT INTO hosting_roomtype (id, name, description, is_active) VALUES
(1, 'Chambre Simple', 'Chambre individuelle standard avec lit simple', true),
(2, 'Chambre Double', 'Chambre avec deux lits pour deux patients', true),
(3, 'Chambre VIP', 'Chambre haut standing avec équipements premium', true),
(4, 'Chambre Familiale', 'Chambre spacieuse pour famille avec accompagnants', true),
(5, 'Suite Médicale', 'Suite avec équipements médicaux spécialisés', true);

-- Réinitialiser la séquence
SELECT setval('hosting_roomtype_id_seq', (SELECT MAX(id) FROM hosting_roomtype));

-- ============================================================================
-- 2. TABLE: hosting_bedstatus (Statuts des lits)
-- ============================================================================
INSERT INTO hosting_bedstatus (id, name) VALUES
(1, 'available'),
(2, 'occupied'),
(3, 'reserved'),
(4, 'maintenance');

-- Réinitialiser la séquence
SELECT setval('hosting_bedstatus_id_seq', (SELECT MAX(id) FROM hosting_bedstatus));

-- ============================================================================
-- 3. TABLE: hosting_room (Chambres)
-- ============================================================================
INSERT INTO hosting_room (room_id, room_name, room_type_id, capacity, status, description) VALUES
('CH-101', 'Chambre 101', 1, 1, 'occupied', 'Chambre simple - Étage 1 - Aile A'),
('CH-102', 'Chambre 102', 1, 1, 'available', 'Chambre simple - Étage 1 - Aile A'),
('CH-103', 'Chambre 103', 1, 1, 'available', 'Chambre simple - Étage 1 - Aile A'),
('CH-104', 'Chambre 104', 2, 2, 'occupied', 'Chambre double - Étage 1 - Aile B'),
('CH-105', 'Chambre 105', 2, 2, 'available', 'Chambre double - Étage 1 - Aile B'),
('CH-201', 'Chambre 201', 1, 1, 'occupied', 'Chambre simple - Étage 2 - Aile A'),
('CH-202', 'Chambre 202', 1, 1, 'maintenance', 'Chambre simple - Étage 2 - Aile A - En rénovation'),
('CH-203', 'Chambre 203', 2, 2, 'available', 'Chambre double - Étage 2 - Aile B'),
('CH-VIP-01', 'Suite VIP 301', 3, 1, 'occupied', 'Suite VIP - Étage 3 - Vue panoramique'),
('CH-VIP-02', 'Suite VIP 302', 3, 1, 'available', 'Suite VIP - Étage 3 - Vue panoramique'),
('CH-FAM-01', 'Chambre Familiale 401', 4, 4, 'available', 'Chambre familiale - Étage 4'),
('CH-MED-01', 'Suite Médicale 501', 5, 1, 'occupied', 'Suite médicale spécialisée - Étage 5');

-- ============================================================================
-- 4. TABLE: hosting_bed (Lits)
-- ============================================================================
INSERT INTO hosting_bed (bed_id, room_id, bed_number, bed_status_id) VALUES
-- Chambres simples
('BED-101-01', 'CH-101', 'Lit 1', 2),  -- occupied
('BED-102-01', 'CH-102', 'Lit 1', 1),  -- available
('BED-103-01', 'CH-103', 'Lit 1', 1),  -- available
('BED-201-01', 'CH-201', 'Lit 1', 2),  -- occupied
('BED-202-01', 'CH-202', 'Lit 1', 4),  -- maintenance

-- Chambres doubles
('BED-104-01', 'CH-104', 'Lit 1', 2),  -- occupied
('BED-104-02', 'CH-104', 'Lit 2', 2),  -- occupied
('BED-105-01', 'CH-105', 'Lit 1', 1),  -- available
('BED-105-02', 'CH-105', 'Lit 2', 1),  -- available
('BED-203-01', 'CH-203', 'Lit 1', 1),  -- available
('BED-203-02', 'CH-203', 'Lit 2', 1),  -- available

-- Suites VIP
('BED-VIP-01-01', 'CH-VIP-01', 'Lit 1', 2),  -- occupied
('BED-VIP-02-01', 'CH-VIP-02', 'Lit 1', 1),  -- available

-- Chambre familiale
('BED-FAM-01-01', 'CH-FAM-01', 'Lit 1', 1),
('BED-FAM-01-02', 'CH-FAM-01', 'Lit 2', 1),
('BED-FAM-01-03', 'CH-FAM-01', 'Lit 3', 1),
('BED-FAM-01-04', 'CH-FAM-01', 'Lit 4', 1),

-- Suite médicale
('BED-MED-01-01', 'CH-MED-01', 'Lit 1', 2);  -- occupied

-- ============================================================================
-- 5. TABLE: hosting_admission (Admissions)
-- ============================================================================
-- Note: patient_id et consultation_id doivent référencer des enregistrements existants
INSERT INTO hosting_admission (
    admission_id, patient_id, consultation_id, admission_date, assignment_mode,
    room_id, bed_id, room_type, discharge_date, discharge_reason, notes, is_invoiced, created_at
) VALUES
(1, 1, 1, '2024-01-10', 'bed', 'CH-101', 'BED-101-01', 'Chambre Simple',
 '2024-01-15', 'end_of_stay', 'Séjour post-opératoire - Récupération complète', true, NOW()),
 
(2, 2, 2, '2024-01-12', 'bed', 'CH-104', 'BED-104-01', 'Chambre Double',
 NULL, NULL, 'Hospitalisation en cours - Observation cardiologique', false, NOW()),
 
(3, 3, 3, '2024-01-14', 'bed', 'CH-201', 'BED-201-01', 'Chambre Simple',
 NULL, NULL, 'Traitement diabète - Ajustement insuline', false, NOW()),
 
(4, 4, 4, '2024-01-15', 'bed', 'CH-VIP-01', 'BED-VIP-01-01', 'Chambre VIP',
 NULL, NULL, 'Séjour VIP - Convalescence', false, NOW()),
 
(5, 5, 5, '2024-01-08', 'bed', 'CH-MED-01', 'BED-MED-01-01', 'Suite Médicale',
 '2024-01-20', 'end_of_stay', 'Traitement intensif terminé avec succès', true, NOW());

-- Réinitialiser la séquence
SELECT setval('hosting_admission_admission_id_seq', (SELECT MAX(admission_id) FROM hosting_admission));

-- ============================================================================
-- 6. TABLE: hosting_reservation (Réservations)
-- ============================================================================
INSERT INTO hosting_reservation (
    reservation_id, patient_id, room_id, bed_id, start_date, end_date, reservation_status
) VALUES
(1, 6, 'CH-102', 'BED-102-01', '2024-02-01', '2024-02-05', 'confirmed'),
(2, 7, 'CH-103', 'BED-103-01', '2024-02-03', '2024-02-07', 'confirmed'),
(3, 8, 'CH-VIP-02', 'BED-VIP-02-01', '2024-02-10', '2024-02-15', 'pending'),
(4, 9, 'CH-105', 'BED-105-01', '2024-02-15', '2024-02-20', 'confirmed'),
(5, 10, 'CH-203', 'BED-203-01', '2024-01-25', '2024-01-28', 'cancelled');

-- Réinitialiser la séquence
SELECT setval('hosting_reservation_reservation_id_seq', (SELECT MAX(reservation_id) FROM hosting_reservation));

-- ============================================================================
-- 7. TABLE: hosting_companion (Accompagnants)
-- ============================================================================
INSERT INTO hosting_companion (
    companion_id, patient_id, companion_name, relationship, start_date, end_date,
    room_id, bed_id, accommodation_start_date, accommodation_end_date, notes
) VALUES
(1, 1, 'Fatima Alami', 'Épouse', '2024-01-10', '2024-01-15',
 'CH-101', 'BED-101-01', '2024-01-10', '2024-01-15', 'Accompagnement durant tout le séjour'),
 
(2, 2, 'Ahmed Benani', 'Fils', '2024-01-12', NULL,
 'CH-104', 'BED-104-01', '2024-01-12', NULL, 'Présence continue'),
 
(3, 3, 'Mohammed El Fassi', 'Frère', '2024-01-14', NULL,
 'CH-201', 'BED-201-01', '2024-01-14', NULL, 'Assistance médicale'),
 
(4, 4, 'Amina Tazi', 'Mère', '2024-01-15', NULL,
 'CH-VIP-01', 'BED-VIP-01-01', '2024-01-15', NULL, 'Accompagnement VIP'),
 
(5, 5, 'Youssef Chraibi', 'Père', '2024-01-08', '2024-01-20',
 'CH-MED-01', 'BED-MED-01-01', '2024-01-08', '2024-01-20', 'Présence durant traitement intensif');

-- Réinitialiser la séquence
SELECT setval('hosting_companion_companion_id_seq', (SELECT MAX(companion_id) FROM hosting_companion));

COMMIT;

-- ============================================================================
-- MESSAGE DE CONFIRMATION
-- ============================================================================
SELECT 'DONNEES HOSTING CREEES AVEC SUCCES!' as message;

-- ============================================================================
-- RÉSUMÉ DES DONNÉES CRÉÉES
-- ============================================================================
SELECT 
    'RÉSUMÉ DES DONNÉES CRÉÉES' as titre,
    (SELECT COUNT(*) FROM hosting_roomtype) as "Types de chambres",
    (SELECT COUNT(*) FROM hosting_bedstatus) as "Statuts de lits",
    (SELECT COUNT(*) FROM hosting_room) as "Chambres",
    (SELECT COUNT(*) FROM hosting_bed) as "Lits",
    (SELECT COUNT(*) FROM hosting_admission) as "Admissions",
    (SELECT COUNT(*) FROM hosting_reservation) as "Réservations",
    (SELECT COUNT(*) FROM hosting_companion) as "Accompagnants";

