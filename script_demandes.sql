-- ============================================================================
-- Script SQL pour remplir les tables du module Demandes (PostgreSQL)
-- ============================================================================


BEGIN;

-- Vider les tables demandes existantes (dans l'ordre des dépendances)
TRUNCATE TABLE demandes_demandeproduit CASCADE;
TRUNCATE TABLE demandes_demandepatient CASCADE;
TRUNCATE TABLE demandes_demandeinterne CASCADE;
TRUNCATE TABLE demandes_demandepatientmodel CASCADE;
TRUNCATE TABLE demandes_produit CASCADE;
TRUNCATE TABLE demandes_statut CASCADE;
TRUNCATE TABLE demandes_priorite CASCADE;

-- ============================================================================
-- 1. TABLE: demandes_priorite (Priorités)
-- ============================================================================
INSERT INTO demandes_priorite (id, nom, niveau) VALUES
(1, 'Urgente', 1),
(2, 'Haute', 2),
(3, 'Normale', 3),
(4, 'Basse', 4);

-- Réinitialiser la séquence
SELECT setval('demandes_priorite_id_seq', (SELECT MAX(id) FROM demandes_priorite));

-- ============================================================================
-- 2. TABLE: demandes_statut (Statuts)
-- ============================================================================
INSERT INTO demandes_statut (id, nom, couleur, category) VALUES
(1, 'En attente', 'warning', 'pending'),
(2, 'En cours', 'info', 'active'),
(3, 'Validée', 'success', 'active'),
(4, 'Livrée', 'success', 'terminated'),
(5, 'Rejetée', 'danger', 'cancelled'),
(6, 'Annulée', 'secondary', 'cancelled');

-- Réinitialiser la séquence
SELECT setval('demandes_statut_id_seq', (SELECT MAX(id) FROM demandes_statut));

-- ============================================================================
-- 3. TABLE: demandes_produit (Produits)
-- ============================================================================
INSERT INTO demandes_produit (id, nom, description, type_demande, disponible) VALUES
-- Produits Internes
(1, 'Papier A4', 'Ramette de papier blanc A4 80g', 'Interne', true),
(2, 'Stylos bille', 'Lot de 10 stylos bille bleus', 'Interne', true),
(3, 'Classeurs', 'Classeurs à levier 8cm', 'Interne', true),
(4, 'Toner imprimante', 'Toner noir pour imprimante HP LaserJet', 'Interne', true),
(5, 'Gants jetables', 'Boîte de 100 gants latex', 'Interne', true),
-- Produits Patients
(6, 'Repas standard', 'Repas complet standard', 'Patient', true),
(7, 'Repas diabétique', 'Repas adapté diabète', 'Patient', true),
(8, 'Repas sans sel', 'Repas régime sans sel', 'Patient', true),
(9, 'Fauteuil roulant', 'Fauteuil roulant standard', 'Patient', true),
(10, 'Béquilles', 'Paire de béquilles réglables', 'Patient', true),
(11, 'Coussin anti-escarres', 'Coussin médical anti-escarres', 'Patient', true),
(12, 'Plateau repas', 'Plateau pour service en chambre', 'Patient', true),
(13, 'Oreiller ergonomique', 'Oreiller médical ergonomique', 'Patient', true),
(14, 'Couverture chauffante', 'Couverture chauffante médicale', 'Patient', true),
(15, 'Kit hygiène', 'Kit hygiène complet patient', 'Patient', true);

-- Réinitialiser la séquence
SELECT setval('demandes_produit_id_seq', (SELECT MAX(id) FROM demandes_produit));

-- ============================================================================
-- 4. TABLE: demandes_demandepatientmodel (Patients des demandes)
-- ============================================================================
INSERT INTO demandes_demandepatientmodel (id, nom, prenom, date_naissance, sexe, chambre, telephone, created_at, updated_at) VALUES
(1, 'Alami', 'Hassan', '1965-03-15', 'M', 'CH-101', '+212612345678', NOW(), NOW()),
(2, 'Benani', 'Fatima', '1972-07-20', 'F', 'CH-104', '+212623456789', NOW(), NOW()),
(3, 'El Fassi', 'Mohammed', '1958-11-10', 'M', 'CH-201', '+212634567890', NOW(), NOW()),
(4, 'Tazi', 'Amina', '1980-05-25', 'F', 'CH-VIP-01', '+212645678901', NOW(), NOW()),
(5, 'Chraibi', 'Youssef', '1945-12-08', 'M', 'CH-MED-01', '+212656789012', NOW(), NOW());


-- ============================================================================
-- 5. TABLE: demandes_demandeinterne (Demandes internes)
-- ============================================================================
INSERT INTO demandes_demandeinterne (
    id, priorite_id, statut_id, description, prestataire_id, created_at, updated_at,
    date_souhaitee, departement_source_id, departement_destinataire_id
) VALUES
(1, 1, 2, 'Besoin urgent de fournitures de bureau', NULL, NOW(), NOW(),
 '2024-01-20 09:00:00', 1, 2),

(2, 2, 3, 'Commande de gants pour service médical', NULL, NOW(), NOW(),
 '2024-01-22 10:00:00', 1, 5),

(3, 3, 2, 'Renouvellement stock papier', NULL, NOW(), NOW(),
 '2024-01-25 14:00:00', 2, 5),

(4, 2, 1, 'Toner imprimante service RH', NULL, NOW(), NOW(),
 '2024-01-28 08:00:00', 2, 5),

(5, 3, 4, 'Classeurs pour archivage', NULL, NOW(), NOW(),
 '2024-01-15 11:00:00', 3, 5);

-- Réinitialiser la séquence
SELECT setval('demandes_demandeinterne_id_seq', (SELECT MAX(id) FROM demandes_demandeinterne));

-- ============================================================================
-- 6. TABLE: demandes_demandepatient (Demandes patients)
-- ============================================================================
INSERT INTO demandes_demandepatient (
    id, priorite_id, statut_id, description, prestataire_id, created_at, updated_at,
    date_souhaitee, patient_id
) VALUES
(1, 1, 2, 'Fauteuil roulant pour patient CH-101', NULL, NOW(), NOW(),
 '2024-01-18 14:00:00', 1),

(2, 2, 3, 'Repas diabétique pour CH-104', NULL, NOW(), NOW(),
 '2024-01-19 12:00:00', 2),

(3, 1, 2, 'Repas sans sel urgent CH-201', NULL, NOW(), NOW(),
 '2024-01-20 11:30:00', 3),

(4, 3, 4, 'Oreiller ergonomique CH-VIP-01', NULL, NOW(), NOW(),
 '2024-01-16 15:00:00', 4),

(5, 2, 1, 'Béquilles pour sortie patient CH-MED-01', NULL, NOW(), NOW(),
 '2024-01-21 09:00:00', 5);

-- Réinitialiser la séquence
SELECT setval('demandes_demandepatient_id_seq', (SELECT MAX(id) FROM demandes_demandepatient));

-- ============================================================================
-- 7. TABLE: demandes_demandeproduit (Produits dans demandes)
-- ============================================================================
INSERT INTO demandes_demandeproduit (id, demande_interne_id, demande_patient_id, produit_id, quantite) VALUES
-- Produits pour demandes internes
(1, 1, NULL, 1, 5),  -- 5 ramettes papier
(2, 1, NULL, 2, 3),  -- 3 lots stylos
(3, 2, NULL, 5, 10), -- 10 boîtes gants
(4, 3, NULL, 1, 10), -- 10 ramettes papier
(5, 4, NULL, 4, 2),  -- 2 toners
(6, 5, NULL, 3, 5),  -- 5 classeurs

-- Produits pour demandes patients
(7, NULL, 1, 9, 1),  -- 1 fauteuil roulant
(8, NULL, 2, 7, 3),  -- 3 repas diabétiques
(9, NULL, 3, 8, 3),  -- 3 repas sans sel
(10, NULL, 4, 13, 1), -- 1 oreiller ergonomique
(11, NULL, 5, 10, 1); -- 1 paire béquilles

-- Réinitialiser la séquence
SELECT setval('demandes_demandeproduit_id_seq', (SELECT MAX(id) FROM demandes_demandeproduit));

COMMIT;

-- ============================================================================
-- MESSAGE DE CONFIRMATION
-- ============================================================================
SELECT 'DONNEES DEMANDES CREEES AVEC SUCCES!' as message;

-- ============================================================================
-- RÉSUMÉ DES DONNÉES CRÉÉES
-- ============================================================================
SELECT 
    'RÉSUMÉ DES DONNÉES CRÉÉES' as titre,
    (SELECT COUNT(*) FROM demandes_priorite) as "Priorités",
    (SELECT COUNT(*) FROM demandes_statut) as "Statuts",
    (SELECT COUNT(*) FROM demandes_produit) as "Produits",
    (SELECT COUNT(*) FROM demandes_demandepatientmodel) as "Patients demandes",
    (SELECT COUNT(*) FROM demandes_demandeinterne) as "Demandes internes",
    (SELECT COUNT(*) FROM demandes_demandepatient) as "Demandes patients",
    (SELECT COUNT(*) FROM demandes_demandeproduit) as "Produits dans demandes";

