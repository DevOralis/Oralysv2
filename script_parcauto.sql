-- ============================================================================
-- Script SQL pour remplir les tables du module Parc Auto (PostgreSQL)
-- ============================================================================

BEGIN;

-- Vider les tables
TRUNCATE TABLE parcauto_contract CASCADE;
TRUNCATE TABLE parcauto_affectation CASCADE;
TRUNCATE TABLE parcauto_entretien CASCADE;
TRUNCATE TABLE parcauto_vehicule CASCADE;
TRUNCATE TABLE parcauto_modele CASCADE;
TRUNCATE TABLE parcauto_marque CASCADE;
TRUNCATE TABLE parcauto_typeentretien CASCADE;
TRUNCATE TABLE parcauto_contracttype CASCADE;
TRUNCATE TABLE parcauto_provider CASCADE;

-- ============================================================================
-- 1. Marques
-- ============================================================================
INSERT INTO parcauto_marque (id, nom) VALUES
(1, 'Renault'),
(2, 'Peugeot'),
(3, 'Dacia'),
(4, 'Mercedes'),
(5, 'Toyota');

SELECT setval('parcauto_marque_id_seq', (SELECT MAX(id) FROM parcauto_marque));

-- ============================================================================
-- 2. Modèles
-- ============================================================================
INSERT INTO parcauto_modele (id, nom, marque_id) VALUES
(1, 'Kangoo', 1),
(2, 'Master', 1),
(3, 'Partner', 2),
(4, 'Boxer', 2),
(5, 'Dokker', 3),
(6, 'Sprinter', 4),
(7, 'Hiace', 5);

SELECT setval('parcauto_modele_id_seq', (SELECT MAX(id) FROM parcauto_modele));

-- ============================================================================
-- 3. Types d'entretien
-- ============================================================================
INSERT INTO parcauto_typeentretien (id, nom, description, is_active, created_at) VALUES
(1, 'Vidange', 'Vidange moteur et filtre à huile', true, NOW()),
(2, 'Révision complète', 'Révision générale du véhicule', true, NOW()),
(3, 'Contrôle technique', 'Contrôle technique obligatoire', true, NOW()),
(4, 'Pneumatiques', 'Changement ou vérification pneus', true, NOW()),
(5, 'Freinage', 'Vérification système de freinage', true, NOW());

SELECT setval('parcauto_typeentretien_id_seq', (SELECT MAX(id) FROM parcauto_typeentretien));

-- ============================================================================
-- 4. Véhicules
-- ============================================================================
INSERT INTO parcauto_vehicule (
    id, immatriculation, marque_id, modele_id, annee, type, statut,
    kilometrage_actuel, date_achat, date_mise_service
) VALUES
(1, '12345-A-20', 1, 1, 2020, 'utilitaire', 'en_service', 45000, '2020-01-15', '2020-02-01'),
(2, '67890-B-21', 2, 3, 2021, 'utilitaire', 'disponible', 32000, '2021-03-10', '2021-03-15'),
(3, '11111-C-22', 3, 5, 2022, 'utilitaire', 'en_service', 18000, '2022-05-20', '2022-06-01'),
(4, '22222-D-19', 4, 6, 2019, 'camion', 'maintenance', 95000, '2019-08-15', '2019-09-01'),
(5, '33333-E-23', 5, 7, 2023, 'utilitaire', 'disponible', 5000, '2023-01-10', '2023-01-15');

SELECT setval('parcauto_vehicule_id_seq', (SELECT MAX(id) FROM parcauto_vehicule));

-- ============================================================================
-- 5. Entretiens
-- ============================================================================
INSERT INTO parcauto_entretien (
    id, vehicle_id, type_entretien_id, date_planifiee, "StatutEntretien",
    remarque, created_at, updated_at
) VALUES
(1, 1, 1, '2024-02-15', 'effectué', 'Vidange effectuée avec succès', NOW(), NOW()),
(2, 1, 3, '2024-06-20', 'planifié', 'Contrôle technique à prévoir', NOW(), NOW()),
(3, 2, 2, '2024-01-25', 'effectué', 'Révision 30000 km OK', NOW(), NOW()),
(4, 3, 1, '2024-03-10', 'planifié', 'Prochaine vidange', NOW(), NOW()),
(5, 4, 4, '2024-01-30', 'en_retard', 'Changement pneus urgent', NOW(), NOW());

SELECT setval('parcauto_entretien_id_seq', (SELECT MAX(id) FROM parcauto_entretien));

-- ============================================================================
-- 6. Affectations
-- ============================================================================
INSERT INTO parcauto_affectation (
    id, vehicle_id, driver_id, date_debut, date_fin, statut,
    kilometrage_debut, kilometrage_fin, distance_parcourue, duree_jours,
    created_at, updated_at
) VALUES
(1, 1, 1, '2024-01-15', NULL, 'A', 45000, NULL, NULL, NULL, NOW(), NOW()),
(2, 3, 2, '2024-01-20', NULL, 'A', 18000, NULL, NULL, NULL, NOW(), NOW()),
(3, 2, 3, '2024-01-10', '2024-01-25', 'T', 30000, 32000, 2000, 15, NOW(), NOW());

SELECT setval('parcauto_affectation_id_seq', (SELECT MAX(id) FROM parcauto_affectation));

-- ============================================================================
-- 7. Types de contrat
-- ============================================================================
INSERT INTO parcauto_contracttype (id, name, code, description) VALUES
(1, 'Assurance', 'ASS', 'Contrat d''assurance véhicule'),
(2, 'Maintenance', 'MAINT', 'Contrat de maintenance'),
(3, 'Leasing', 'LEASE', 'Contrat de location longue durée');

SELECT setval('parcauto_contracttype_id_seq', (SELECT MAX(id) FROM parcauto_contracttype));

-- ============================================================================
-- 8. Fournisseurs
-- ============================================================================
INSERT INTO parcauto_provider (id, name, email, phone, address) VALUES
(1, 'Assurance Wafa', 'contact@wafa.ma', '+212522334455', 'Casablanca'),
(2, 'Garage Central', 'garage@central.ma', '+212537445566', 'Rabat'),
(3, 'Leasing Maroc', 'info@leasing.ma', '+212524556677', 'Marrakech');

SELECT setval('parcauto_provider_id_seq', (SELECT MAX(id) FROM parcauto_provider));

-- ============================================================================
-- 9. Contrats (sans fichier)
-- ============================================================================
INSERT INTO parcauto_contract (
    id, vehicle_id, contract_type_id, provider_id, reference_number,
    start_date, expiration_date, contract_file, notes, is_active,
    created_at, updated_at
) VALUES
(1, 1, 1, 1, 'ASS-2024-001', '2024-01-01', '2024-12-31', '', 'Assurance tous risques', true, NOW(), NOW()),
(2, 2, 1, 1, 'ASS-2024-002', '2024-01-01', '2024-12-31', '', 'Assurance tous risques', true, NOW(), NOW()),
(3, 4, 2, 2, 'MAINT-2024-001', '2024-01-01', '2024-12-31', '', 'Maintenance annuelle', true, NOW(), NOW());

SELECT setval('parcauto_contract_id_seq', (SELECT MAX(id) FROM parcauto_contract));

COMMIT;

SELECT 'DONNEES PARC AUTO CREEES AVEC SUCCES!' as message;

SELECT 
    'RÉSUMÉ' as titre,
    (SELECT COUNT(*) FROM parcauto_marque) as "Marques",
    (SELECT COUNT(*) FROM parcauto_modele) as "Modèles",
    (SELECT COUNT(*) FROM parcauto_vehicule) as "Véhicules",
    (SELECT COUNT(*) FROM parcauto_typeentretien) as "Types entretien",
    (SELECT COUNT(*) FROM parcauto_entretien) as "Entretiens",
    (SELECT COUNT(*) FROM parcauto_affectation) as "Affectations",
    (SELECT COUNT(*) FROM parcauto_contract) as "Contrats";


