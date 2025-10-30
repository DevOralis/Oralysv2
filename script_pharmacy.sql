-- ============================================================================
-- Script SQL pour remplir les tables du module Pharmacy (PostgreSQL)
-- ============================================================================
-- Ce script crée des données de test pour toutes les tables du module Pharmacy
-- Base de données: PostgreSQL
-- ============================================================================

BEGIN;

-- Vider les tables pharmacy existantes (dans l'ordre des dépendances)
TRUNCATE TABLE pharmacy_order_line CASCADE;
TRUNCATE TABLE pharmacy_order CASCADE;
TRUNCATE TABLE pharmacy_product_location CASCADE;
TRUNCATE TABLE pharmacy_product CASCADE;
TRUNCATE TABLE pharmacy_supplier CASCADE;
TRUNCATE TABLE "pharmacy_stockLocation" CASCADE;
TRUNCATE TABLE "pharmacy_locationType" CASCADE;
TRUNCATE TABLE pharmacy_pharmacy CASCADE;
TRUNCATE TABLE pharmacy_product_category CASCADE;
TRUNCATE TABLE pharmacy_dci CASCADE;
TRUNCATE TABLE pharmacy_unitofmesure CASCADE;
TRUNCATE TABLE pharmacy_pharmaceutical_form CASCADE;
TRUNCATE TABLE pharmacy_operation_type CASCADE;

-- ============================================================================
-- 1. TABLE: pharmacy_pharmaceutical_form (Formes pharmaceutiques)
-- ============================================================================
INSERT INTO pharmacy_pharmaceutical_form (id, name, description) VALUES
(1, 'Comprimé', 'Forme solide destinée à être avalée'),
(2, 'Gélule', 'Enveloppe gélatineuse contenant une poudre'),
(3, 'Sirop', 'Solution sucrée pour administration orale'),
(4, 'Injection', 'Solution stérile pour administration parentérale'),
(5, 'Crème', 'Émulsion pour application cutanée'),
(6, 'Pommade', 'Préparation grasse pour application cutanée'),
(7, 'Suppositoire', 'Forme solide pour administration rectale'),
(8, 'Gouttes', 'Solution concentrée pour administration orale'),
(9, 'Patch', 'Dispositif transdermique'),
(10, 'Aérosol', 'Forme inhalée sous pression'),
(11, 'Inhalateur', 'Dispositif pour administration pulmonaire'),
(12, 'Collyre', 'Solution pour application oculaire'),
(13, 'Solution buvable', 'Solution pour administration orale'),
(14, 'Poudre', 'Forme sèche pour reconstitution'),
(15, 'Granulé', 'Petits grains pour suspension');

-- Réinitialiser la séquence
SELECT setval('pharmacy_pharmaceutical_form_id_seq', (SELECT MAX(id) FROM pharmacy_pharmaceutical_form));

-- ============================================================================
-- 2. TABLE: pharmacy_unitofmesure (Unités de mesure)
-- ============================================================================
INSERT INTO pharmacy_unitofmesure (uom_id, label, symbole) VALUES
(1, 'Comprimé', 'cp'),
(2, 'Gélule', 'gél'),
(3, 'Millilitre', 'ml'),
(4, 'Litre', 'L'),
(5, 'Milligramme', 'mg'),
(6, 'Gramme', 'g'),
(7, 'Kilogramme', 'kg'),
(8, 'Unité', 'U'),
(9, 'Flacon', 'fl'),
(10, 'Ampoule', 'amp'),
(11, 'Seringue', 'syr'),
(12, 'Tube', 'tub'),
(13, 'Boîte', 'boîte'),
(14, 'Sachet', 'sach'),
(15, 'Patch', 'patch');

-- Réinitialiser la séquence
SELECT setval('pharmacy_unitofmesure_uom_id_seq', (SELECT MAX(uom_id) FROM pharmacy_unitofmesure));

-- ============================================================================
-- 3. TABLE: pharmacy_dci (Dénominations Communes Internationales)
-- ============================================================================
INSERT INTO pharmacy_dci (dci_id, label, description) VALUES
(1, 'Paracétamol', 'Antalgique et antipyrétique'),
(2, 'Ibuprofène', 'Anti-inflammatoire non stéroïdien'),
(3, 'Amoxicilline', 'Antibiotique de la famille des pénicillines'),
(4, 'Céfalexine', 'Antibiotique de la famille des céphalosporines'),
(5, 'Métronidazole', 'Antibiotique et antiprotozoaire'),
(6, 'Diclofénac', 'Anti-inflammatoire non stéroïdien'),
(7, 'Oméprazole', 'Inhibiteur de la pompe à protons'),
(8, 'Lansoprazole', 'Inhibiteur de la pompe à protons'),
(9, 'Ranitidine', 'Antihistaminique H2'),
(10, 'Loratadine', 'Antihistaminique H1'),
(11, 'Diphenhydramine', 'Antihistaminique H1 sédatif'),
(12, 'Salbutamol', 'Bronchodilatateur'),
(13, 'Budesonide', 'Corticoïde inhalé'),
(14, 'Insuline', 'Hormone antidiabétique'),
(15, 'Métformine', 'Antidiabétique oral'),
(16, 'Simvastatine', 'Hypolipémiant'),
(17, 'Atorvastatine', 'Hypolipémiant'),
(18, 'Amlodipine', 'Antihypertenseur'),
(19, 'Lisinopril', 'Inhibiteur de l''enzyme de conversion'),
(20, 'Hydrochlorothiazide', 'Diurétique thiazidique'),
(21, 'Furosémide', 'Diurétique de l''anse'),
(22, 'Digoxine', 'Glycoside cardiaque'),
(23, 'Warfarine', 'Anticoagulant oral'),
(24, 'Aspirine', 'Antiplaquettaire et antalgique'),
(25, 'Morphine', 'Analgésique opioïde');

-- Réinitialiser la séquence
SELECT setval('pharmacy_dci_dci_id_seq', (SELECT MAX(dci_id) FROM pharmacy_dci));

-- ============================================================================
-- 4. TABLE: pharmacy_product_category (Catégories de produits)
-- ============================================================================
INSERT INTO pharmacy_product_category (categ_id, label, description) VALUES
(1, 'Antalgiques', 'Médicaments contre la douleur'),
(2, 'Antibiotiques', 'Traitement des infections bactériennes'),
(3, 'Anti-inflammatoires', 'Réduction de l''inflammation'),
(4, 'Antihypertenseurs', 'Traitement de l''hypertension artérielle'),
(5, 'Antidiabétiques', 'Traitement du diabète'),
(6, 'Antihistaminiques', 'Traitement des allergies'),
(7, 'Bronchodilatateurs', 'Traitement de l''asthme et des bronchites'),
(8, 'Corticoïdes', 'Anti-inflammatoires stéroïdiens'),
(9, 'Diurétiques', 'Élimination de l''eau et du sel'),
(10, 'Hypolipémiants', 'Réduction du cholestérol'),
(11, 'Anticoagulants', 'Prévention des caillots sanguins'),
(12, 'Vitamines', 'Compléments vitaminiques'),
(13, 'Soins externes', 'Désinfectants, crèmes, etc.'),
(14, 'Gastro-entérologie', 'Traitement des troubles digestifs'),
(15, 'Cardiologie', 'Médicaments pour le cœur'),
(16, 'Neurologie', 'Traitement des troubles neurologiques'),
(17, 'Psychiatrie', 'Médicaments psychotropes'),
(18, 'Dermatologie', 'Traitement des maladies de peau'),
(19, 'Ophtalmologie', 'Traitement des troubles oculaires'),
(20, 'ORL', 'Traitement des troubles ORL');

-- Réinitialiser la séquence
SELECT setval('pharmacy_product_category_categ_id_seq', (SELECT MAX(categ_id) FROM pharmacy_product_category));

-- ============================================================================
-- 5. TABLE: pharmacy_pharmacy (Pharmacies)
-- ============================================================================
INSERT INTO pharmacy_pharmacy (pharmacy_id, label, adress) VALUES
(1, 'Pharmacie Centrale', 'Avenue Mohammed V, Centre-ville, Casablanca'),
(2, 'Pharmacie de l''Hôpital', 'Hôpital Oralys, Service Pharmacie, Rabat'),
(3, 'Pharmacie du Quartier', 'Rue Hassan II, Hay Riad, Rabat'),
(4, 'Pharmacie Express', 'Boulevard Zerktouni, Casablanca'),
(5, 'Pharmacie de Garde', 'Place des Nations Unies, Rabat');

-- Réinitialiser la séquence
SELECT setval('pharmacy_pharmacy_pharmacy_id_seq', (SELECT MAX(pharmacy_id) FROM pharmacy_pharmacy));

-- ============================================================================
-- 6. TABLE: pharmacy_locationType (Types d'emplacement)
-- ============================================================================
INSERT INTO "pharmacy_locationType" (location_type_id, name, description) VALUES
(1, 'Étagère', 'Étagère de stockage standard'),
(2, 'Réfrigérateur', 'Stockage au froid (2-8°C)'),
(3, 'Congélateur', 'Stockage en congélation (-20°C)'),
(4, 'Armoire sécurisée', 'Stockage des substances contrôlées'),
(5, 'Zone de préparation', 'Zone pour la préparation des médicaments'),
(6, 'Quarantaine', 'Zone pour produits en attente de contrôle'),
(7, 'Retour', 'Zone pour produits retournés'),
(8, 'Destruction', 'Zone pour produits à détruire'),
(9, 'Urgence', 'Zone d''accès rapide pour urgences'),
(10, 'Contrôle qualité', 'Zone de contrôle et validation');

-- Réinitialiser la séquence
SELECT setval('"pharmacy_locationType_location_type_id_seq"', (SELECT MAX(location_type_id) FROM "pharmacy_locationType"));

-- ============================================================================
-- 7. TABLE: pharmacy_stockLocation (Emplacements de stockage)
-- ============================================================================
INSERT INTO "pharmacy_stockLocation" (location_id, name, parent_location_id, location_type_id, pharmacy_id) VALUES
(1, 'Étagère A - Antalgiques', NULL, 1, 2),
(2, 'Étagère B - Antibiotiques', NULL, 1, 2),
(3, 'Étagère C - Cardiologie', NULL, 1, 2),
(4, 'Réfrigérateur Principal', NULL, 2, 2),
(5, 'Armoire Contrôlée', NULL, 4, 2),
(6, 'Zone Urgence', NULL, 9, 2),
(7, 'Zone Préparation', NULL, 5, 2),
(8, 'Quarantaine', NULL, 6, 2),
(9, 'Sous-étagère A1', 1, 1, 2),
(10, 'Sous-étagère A2', 1, 1, 2),
(11, 'Sous-étagère B1', 2, 1, 2),
(12, 'Sous-étagère C1', 3, 1, 2),
(13, 'Étagère D - Vitamines', NULL, 1, 2),
(14, 'Étagère E - Soins externes', NULL, 1, 2),
(15, 'Zone Contrôle Qualité', NULL, 10, 2);

-- Réinitialiser la séquence
SELECT setval('"pharmacy_stockLocation_location_id_seq"', (SELECT MAX(location_id) FROM "pharmacy_stockLocation"));

-- ============================================================================
-- 8. TABLE: pharmacy_supplier (Fournisseurs)
-- ============================================================================
INSERT INTO pharmacy_supplier (
    id, name, is_company, street, street2, zip, city_id, country_id, lang_id,
    email, phone, mobile, "ICE", "RC", "IF", vat, "RIB", comment
) VALUES
(1, 'Laboratoires Pharmatech', true, 'Zone Industrielle', 'Lot 45', '20000', NULL, NULL, NULL,
 'contact@pharmatech.ma', '+212522334455', '+212612345678', '12345678901234', 12345678, 87654321, '123456789', '12345678901234567890', 'Fournisseur principal de médicaments génériques'),
 
(2, 'MediCorp International', true, 'Avenue Hassan II', 'Immeuble 200', '10000', NULL, NULL, NULL,
 'info@medicorp.ma', '+212537445566', '+212623456789', '23456789012345', 23456789, 98765432, '234567890', '23456789012345678901', 'Spécialisé dans les médicaments de spécialité'),
 
(3, 'BioPharma Distribution', true, 'Boulevard Zerktouni', 'Tour A', '30000', NULL, NULL, NULL,
 'ventes@biopharma.ma', '+212524556677', '+212634567890', '34567890123456', 34567890, 19876543, '345678901', '34567890123456789012', 'Distribution de produits biologiques'),
 
(4, 'Pharmacie Grossiste Maroc', true, 'Rue de la Pharmacie', 'Entrepôt 50', '40000', NULL, NULL, NULL,
 'grossiste@pharmacie.ma', '+212535667788', '+212645678901', '45678901234567', 45678901, 21987654, '456789012', '45678901234567890123', 'Grossiste en produits pharmaceutiques'),
 
(5, 'Laboratoires Sanofi', true, 'Zone Franche', 'Usine 100', '50000', NULL, NULL, NULL,
 'maroc@sanofi.com', '+212543889900', '+212656789012', '56789012345678', 56789012, 32109876, '567890123', '56789012345678901234', 'Laboratoire international - Vaccins et spécialités');

-- Réinitialiser la séquence
SELECT setval('pharmacy_supplier_id_seq', (SELECT MAX(id) FROM pharmacy_supplier));

-- ============================================================================
-- 9. TABLE: pharmacy_operation_type (Types d'opération)
-- ============================================================================
INSERT INTO pharmacy_operation_type (operation_type_id, label) VALUES
(1, 'Réception'),
(2, 'Sortie'),
(3, 'Transfert'),
(4, 'Inventaire'),
(5, 'Retour'),
(6, 'Perte'),
(7, 'Vol'),
(8, 'Détérioration'),
(9, 'Expiration'),
(10, 'Don'),
(11, 'Prêt'),
(12, 'Vente'),
(13, 'Échantillon'),
(14, 'Ajustement'),
(15, 'Réapprovisionnement');

-- Réinitialiser la séquence
SELECT setval('pharmacy_operation_type_operation_type_id_seq', (SELECT MAX(operation_type_id) FROM pharmacy_operation_type));

-- ============================================================================
-- 10. TABLE: pharmacy_product (Produits pharmaceutiques)
-- ============================================================================
INSERT INTO pharmacy_product (
    product_id, code, short_label, brand, full_label, dci_id, pharmaceutical_form_id,
    dosage, barcode, ppm_price, unit_price, supplier_price, internal_purchase_price,
    refund_price, refund_rate, uom_id, categ_id, total_quantity_cached, nombrepiece
) VALUES
-- Antalgiques
(1, 'PARA500', 'Paracétamol 500mg', 'Doliprane', 'Paracétamol 500mg - Comprimé', 1, 1,
 '500mg', '1234567890123', 2.50, 2.00, 1.50, 1.80, 2.00, 80.00, 1, 1, 1000, 20),
 
(2, 'PARA1000', 'Paracétamol 1g', 'Doliprane', 'Paracétamol 1g - Comprimé', 1, 1,
 '1000mg', '1234567890124', 3.50, 3.00, 2.00, 2.50, 3.00, 85.00, 1, 1, 500, 16),
 
(3, 'IBU400', 'Ibuprofène 400mg', 'Nurofen', 'Ibuprofène 400mg - Comprimé', 2, 1,
 '400mg', '1234567890125', 4.00, 3.50, 2.50, 3.00, 3.50, 87.50, 1, 3, 800, 20),
 
(4, 'ASP500', 'Aspirine 500mg', 'Aspégic', 'Aspirine 500mg - Comprimé', 24, 1,
 '500mg', '1234567890126', 2.80, 2.30, 1.60, 2.00, 2.30, 82.00, 1, 1, 600, 20),

-- Antibiotiques
(5, 'AMOX500', 'Amoxicilline 500mg', 'Clamoxyl', 'Amoxicilline 500mg - Gélule', 3, 2,
 '500mg', '1234567890127', 8.50, 7.00, 5.00, 6.00, 7.00, 82.00, 2, 2, 300, 21),
 
(6, 'AMOX1G', 'Amoxicilline 1g', 'Clamoxyl', 'Amoxicilline 1g - Gélule', 3, 2,
 '1000mg', '1234567890128', 12.00, 10.00, 7.00, 8.50, 10.00, 83.00, 2, 2, 200, 14),
 
(7, 'CEFA500', 'Céfalexine 500mg', 'Keforal', 'Céfalexine 500mg - Gélule', 4, 2,
 '500mg', '1234567890129', 9.00, 7.50, 5.50, 6.50, 7.50, 83.00, 2, 2, 250, 21),

-- Anti-inflammatoires
(8, 'DICO50', 'Diclofénac 50mg', 'Voltaren', 'Diclofénac 50mg - Comprimé', 6, 1,
 '50mg', '1234567890130', 3.50, 3.00, 2.00, 2.50, 3.00, 85.00, 1, 3, 400, 20),
 
(9, 'DICO75', 'Diclofénac 75mg', 'Voltaren', 'Diclofénac 75mg - Comprimé', 6, 1,
 '75mg', '1234567890131', 4.20, 3.60, 2.40, 3.00, 3.60, 85.00, 1, 3, 350, 20),

-- Gastro-entérologie
(10, 'OME20', 'Oméprazole 20mg', 'Mopral', 'Oméprazole 20mg - Gélule', 7, 2,
 '20mg', '1234567890132', 6.50, 5.50, 3.80, 4.50, 5.50, 84.00, 2, 14, 300, 28),
 
(11, 'LAN30', 'Lansoprazole 30mg', 'Lanzor', 'Lansoprazole 30mg - Gélule', 8, 2,
 '30mg', '1234567890133', 7.00, 6.00, 4.20, 5.00, 6.00, 85.00, 2, 14, 280, 28),

-- Cardiologie
(12, 'AML5', 'Amlodipine 5mg', 'Amlor', 'Amlodipine 5mg - Comprimé', 18, 1,
 '5mg', '1234567890134', 4.50, 3.80, 2.70, 3.20, 3.80, 84.00, 1, 4, 450, 30),
 
(13, 'LIS10', 'Lisinopril 10mg', 'Prinivil', 'Lisinopril 10mg - Comprimé', 19, 1,
 '10mg', '1234567890135', 5.00, 4.20, 3.00, 3.50, 4.20, 84.00, 1, 4, 400, 30),
 
(14, 'HYD25', 'Hydrochlorothiazide 25mg', 'Esidrex', 'Hydrochlorothiazide 25mg - Comprimé', 20, 1,
 '25mg', '1234567890136', 3.00, 2.50, 1.80, 2.20, 2.50, 83.00, 1, 9, 500, 30),

-- Antidiabétiques
(15, 'MET500', 'Métformine 500mg', 'Glucophage', 'Métformine 500mg - Comprimé', 15, 1,
 '500mg', '1234567890137', 2.80, 2.30, 1.60, 2.00, 2.30, 82.00, 1, 5, 600, 30),
 
(16, 'MET850', 'Métformine 850mg', 'Glucophage', 'Métformine 850mg - Comprimé', 15, 1,
 '850mg', '1234567890138', 3.20, 2.70, 1.90, 2.30, 2.70, 84.00, 1, 5, 500, 30),

-- Soins externes
(17, 'BETADINE', 'Bétadine Solution', 'Bétadine', 'Bétadine 10% - Solution', NULL, 13,
 '10%', '1234567890139', 8.50, 7.00, 5.00, 6.00, 7.00, 82.00, 3, 13, 100, 1),
 
(18, 'HYDROCORT', 'Hydrocortisone Crème', 'Locoid', 'Hydrocortisone 1% - Crème', NULL, 5,
 '1%', '1234567890140', 12.00, 10.00, 7.00, 8.50, 10.00, 83.00, 8, 13, 80, 1),

-- Vitamines
(19, 'VITC1000', 'Vitamine C 1000mg', 'Redoxon', 'Vitamine C 1000mg - Comprimé', NULL, 1,
 '1000mg', '1234567890141', 15.00, 12.00, 8.50, 10.00, 12.00, 80.00, 1, 12, 200, 20),
 
(20, 'VITD3', 'Vitamine D3', 'Zyma', 'Vitamine D3 1000 UI - Gélule', NULL, 2,
 '1000 UI', '1234567890142', 18.00, 15.00, 10.50, 12.00, 15.00, 83.00, 2, 12, 150, 30);

-- Réinitialiser la séquence
SELECT setval('pharmacy_product_product_id_seq', (SELECT MAX(product_id) FROM pharmacy_product));

-- ============================================================================
-- 11. TABLE: pharmacy_product_location (Emplacements des produits)
-- ============================================================================
INSERT INTO pharmacy_product_location (id, product_id, location_id, quantity_stored, quantity_counted) VALUES
-- Répartition des produits dans les emplacements
(1, 1, 9, 500, 500),   -- Paracétamol 500mg dans Sous-étagère A1
(2, 1, 10, 500, 500),  -- Paracétamol 500mg dans Sous-étagère A2
(3, 2, 9, 250, 250),   -- Paracétamol 1g dans Sous-étagère A1
(4, 2, 10, 250, 250),  -- Paracétamol 1g dans Sous-étagère A2
(5, 3, 9, 400, 400),   -- Ibuprofène 400mg dans Sous-étagère A1
(6, 3, 10, 400, 400),  -- Ibuprofène 400mg dans Sous-étagère A2
(7, 4, 9, 300, 300),   -- Aspirine 500mg dans Sous-étagère A1
(8, 4, 10, 300, 300),  -- Aspirine 500mg dans Sous-étagère A2

(9, 5, 11, 150, 150),  -- Amoxicilline 500mg dans Sous-étagère B1
(10, 6, 11, 100, 100), -- Amoxicilline 1g dans Sous-étagère B1
(11, 7, 11, 125, 125), -- Céfalexine 500mg dans Sous-étagère B1

(12, 8, 9, 200, 200),  -- Diclofénac 50mg dans Sous-étagère A1
(13, 8, 10, 200, 200), -- Diclofénac 50mg dans Sous-étagère A2
(14, 9, 9, 175, 175),  -- Diclofénac 75mg dans Sous-étagère A1
(15, 9, 10, 175, 175), -- Diclofénac 75mg dans Sous-étagère A2

(16, 10, 12, 150, 150), -- Oméprazole 20mg dans Sous-étagère C1
(17, 11, 12, 140, 140), -- Lansoprazole 30mg dans Sous-étagère C1

(18, 12, 12, 225, 225), -- Amlodipine 5mg dans Sous-étagère C1
(19, 13, 12, 200, 200), -- Lisinopril 10mg dans Sous-étagère C1
(20, 14, 12, 250, 250), -- Hydrochlorothiazide 25mg dans Sous-étagère C1

(21, 15, 13, 300, 300), -- Métformine 500mg dans Étagère D
(22, 16, 13, 250, 250), -- Métformine 850mg dans Étagère D

(23, 17, 14, 50, 50),  -- Bétadine dans Étagère E
(24, 18, 14, 40, 40),  -- Hydrocortisone dans Étagère E

(25, 19, 13, 100, 100), -- Vitamine C dans Étagère D
(26, 20, 13, 75, 75);  -- Vitamine D3 dans Étagère D

-- ============================================================================
-- 12. TABLE: pharmacy_order (Commandes) - SUPPRIMÉ (dépendances externes)
-- ============================================================================
-- Les commandes nécessitent des tables externes (currency, payment_mode, tax)
-- qui ne sont pas disponibles dans cette base de données

-- ============================================================================
-- 13. TABLE: pharmacy_order_line (Lignes de commande) - SUPPRIMÉ (dépendances externes)
-- ============================================================================
-- Les lignes de commande nécessitent des commandes qui ne sont pas créées

COMMIT;

-- ============================================================================
-- MESSAGE DE CONFIRMATION
-- ============================================================================
SELECT 'DONNEES PHARMACY CREEES AVEC SUCCES!' as message;

-- ============================================================================
-- RÉSUMÉ DES DONNÉES CRÉÉES
-- ============================================================================
SELECT 
    'RÉSUMÉ DES DONNÉES CRÉÉES' as titre,
    (SELECT COUNT(*) FROM pharmacy_pharmaceutical_form) as "Formes pharmaceutiques",
    (SELECT COUNT(*) FROM pharmacy_unitofmesure) as "Unités de mesure", 
    (SELECT COUNT(*) FROM pharmacy_dci) as "DCI",
    (SELECT COUNT(*) FROM pharmacy_product_category) as "Catégories",
    (SELECT COUNT(*) FROM pharmacy_pharmacy) as "Pharmacies",
    (SELECT COUNT(*) FROM "pharmacy_locationType") as "Types d'emplacement",
    (SELECT COUNT(*) FROM "pharmacy_stockLocation") as "Emplacements de stockage",
    (SELECT COUNT(*) FROM pharmacy_supplier) as "Fournisseurs",
    (SELECT COUNT(*) FROM pharmacy_operation_type) as "Types d'opération",
    (SELECT COUNT(*) FROM pharmacy_product) as "Produits pharmaceutiques",
    (SELECT COUNT(*) FROM pharmacy_product_location) as "Emplacements produits",
    0 as "Commandes (non créées - dépendances externes)",
    0 as "Lignes de commande (non créées - dépendances externes)";
