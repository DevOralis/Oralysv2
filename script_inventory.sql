-- ============================================================================
-- Script SQL pour remplir les tables du module Inventory (PostgreSQL)
-- ============================================================================

BEGIN;

-- Vider les tables (ordre des dépendances - enfants avant parents)
TRUNCATE TABLE inventory_line_stock_move CASCADE;
TRUNCATE TABLE "inventory_stockMove" CASCADE;
TRUNCATE TABLE inventory_product_location CASCADE;
TRUNCATE TABLE inventory_product_department CASCADE;
TRUNCATE TABLE inventory_product CASCADE;
TRUNCATE TABLE "inventory_stockLocation" CASCADE;
TRUNCATE TABLE "inventory_locationType" CASCADE;
TRUNCATE TABLE inventory_unitofmesure CASCADE;
TRUNCATE TABLE inventory_category CASCADE;
TRUNCATE TABLE "inventory_operationType" CASCADE;
TRUNCATE TABLE "inventory_productType" CASCADE;

-- ============================================================================
-- 1. Catégories de produits
-- ============================================================================
INSERT INTO inventory_category (label, description) VALUES
('Consommables médicaux', 'Produits consommables à usage médical'),
('Équipements médicaux', 'Équipements et instruments médicaux'),
('Fournitures bureau', 'Fournitures de bureau et administratives'),
('Produits d''hygiène', 'Produits d''hygiène et désinfection'),
('Matériel diagnostic', 'Matériel pour diagnostic médical'),
('Équipements protection', 'Équipements de protection individuelle'),
('Consommables laboratoire', 'Consommables pour laboratoire'),
('Mobilier médical', 'Mobilier et équipements d''hospitalisation');

-- ============================================================================
-- 2. Unités de mesure
-- ============================================================================
INSERT INTO inventory_unitofmesure (label, symbole) VALUES
('Unité', 'U'),
('Boîte', 'Boîte'),
('Carton', 'Carton'),
('Kilogramme', 'kg'),
('Gramme', 'g'),
('Litre', 'L'),
('Millilitre', 'ml'),
('Mètre', 'm'),
('Paire', 'paire'),
('Lot', 'lot');

-- ============================================================================
-- 3. Types de produits
-- ============================================================================
INSERT INTO "inventory_productType" (label) VALUES
('Stockable'),
('Consommable'),
('Service');

-- ============================================================================
-- 4. Types d''emplacement
-- ============================================================================
INSERT INTO "inventory_locationType" (label, description) VALUES
('Entrepôt principal', 'Zone de stockage principale'),
('Réserve', 'Zone de réserve secondaire'),
('Salle de stockage', 'Salle dédiée au stockage'),
('Armoire', 'Armoire de rangement'),
('Étagère', 'Étagère de stockage'),
('Réfrigérateur', 'Zone réfrigérée'),
('Zone stérile', 'Zone de stockage stérile'),
('Quarantaine', 'Zone de quarantaine');

-- ============================================================================
-- 5. Emplacements de stockage (utilise SELECT pour les IDs)
-- ============================================================================
INSERT INTO "inventory_stockLocation" (name, parent_location_id, location_type_id)
SELECT 'Entrepôt Central', NULL, location_type_id FROM "inventory_locationType" WHERE label = 'Entrepôt principal';

INSERT INTO "inventory_stockLocation" (name, parent_location_id, location_type_id)
SELECT 'Réserve A', NULL, location_type_id FROM "inventory_locationType" WHERE label = 'Réserve';

INSERT INTO "inventory_stockLocation" (name, parent_location_id, location_type_id)
SELECT 'Réserve B', NULL, location_type_id FROM "inventory_locationType" WHERE label = 'Réserve';

INSERT INTO "inventory_stockLocation" (name, parent_location_id, location_type_id)
SELECT 'Armoire Médical 1', 
    (SELECT location_id FROM "inventory_stockLocation" WHERE name = 'Entrepôt Central' LIMIT 1),
    location_type_id 
FROM "inventory_locationType" WHERE label = 'Armoire';

INSERT INTO "inventory_stockLocation" (name, parent_location_id, location_type_id)
SELECT 'Armoire Médical 2',
    (SELECT location_id FROM "inventory_stockLocation" WHERE name = 'Entrepôt Central' LIMIT 1),
    location_type_id
FROM "inventory_locationType" WHERE label = 'Armoire';

INSERT INTO "inventory_stockLocation" (name, parent_location_id, location_type_id)
SELECT 'Étagère Consommables',
    (SELECT location_id FROM "inventory_stockLocation" WHERE name = 'Réserve A' LIMIT 1),
    location_type_id
FROM "inventory_locationType" WHERE label = 'Étagère';

INSERT INTO "inventory_stockLocation" (name, parent_location_id, location_type_id)
SELECT 'Réfrigérateur Médicaments',
    (SELECT location_id FROM "inventory_stockLocation" WHERE name = 'Entrepôt Central' LIMIT 1),
    location_type_id
FROM "inventory_locationType" WHERE label = 'Réfrigérateur';

INSERT INTO "inventory_stockLocation" (name, parent_location_id, location_type_id)
SELECT 'Zone Stérile 1',
    (SELECT location_id FROM "inventory_stockLocation" WHERE name = 'Entrepôt Central' LIMIT 1),
    location_type_id
FROM "inventory_locationType" WHERE label = 'Zone stérile';

INSERT INTO "inventory_stockLocation" (name, parent_location_id, location_type_id)
SELECT 'Quarantaine Produits',
    (SELECT location_id FROM "inventory_stockLocation" WHERE name = 'Réserve B' LIMIT 1),
    location_type_id
FROM "inventory_locationType" WHERE label = 'Quarantaine';

-- ============================================================================
-- 6. Types d''opération
-- ============================================================================
INSERT INTO "inventory_operationType" (label) VALUES
('Réception'),
('Sortie'),
('Transfert'),
('Inventaire'),
('Ajustement'),
('Retour'),
('Perte'),
('Destruction');

-- ============================================================================
-- 7. Produits d''inventaire
-- ============================================================================
INSERT INTO inventory_product (name, default_code, active, standard_price, weight, volume, stock_minimal, total_quantity_cached, description) VALUES
-- Consommables médicaux
('Gants latex stériles', 'INV-GLAT-001', true, 5.00, 0.1, 0.01, 100, 500, 'Boîte de 100 gants latex stériles'),
('Masques chirurgicaux', 'INV-MASK-001', true, 3.00, 0.05, 0.005, 200, 1000, 'Boîte de 50 masques chirurgicaux'),
('Compresses stériles', 'INV-COMP-001', true, 8.00, 0.2, 0.02, 50, 300, 'Paquet de 100 compresses stériles'),
('Seringues 5ml', 'INV-SER-001', true, 12.00, 0.15, 0.015, 100, 400, 'Boîte de 100 seringues jetables 5ml'),
('Cathéters IV', 'INV-CATH-001', true, 25.00, 0.3, 0.03, 50, 200, 'Boîte de 50 cathéters intraveineux'),

-- Équipements médicaux
('Thermomètre digital', 'INV-THER-001', true, 15.00, 0.2, 0.02, 10, 50, 'Thermomètre digital médical'),
('Tensiomètre', 'INV-TENS-001', true, 45.00, 0.5, 0.05, 5, 25, 'Tensiomètre automatique'),
('Stéthoscope', 'INV-STET-001', true, 35.00, 0.3, 0.03, 10, 30, 'Stéthoscope médical professionnel'),
('Otoscope', 'INV-OTOS-001', true, 55.00, 0.4, 0.04, 5, 15, 'Otoscope avec éclairage LED'),

-- Fournitures bureau
('Papier A4', 'INV-PAP-001', true, 4.50, 2.5, 0.25, 50, 200, 'Ramette 500 feuilles papier A4'),
('Stylos bille', 'INV-STYL-001', true, 0.50, 0.01, 0.001, 100, 500, 'Stylo bille bleu'),
('Classeurs', 'INV-CLAS-001', true, 2.50, 0.4, 0.04, 30, 150, 'Classeur à levier dos 8cm'),

-- Produits hygiène
('Solution hydroalcoolique', 'INV-SHA-001', true, 8.50, 0.5, 0.5, 50, 300, 'Flacon 500ml gel hydroalcoolique'),
('Savon liquide', 'INV-SAV-001', true, 6.00, 1.0, 1.0, 40, 200, 'Flacon 1L savon liquide antibactérien'),
('Lingettes désinfectantes', 'INV-LING-001', true, 5.50, 0.3, 0.03, 60, 250, 'Boîte de 100 lingettes désinfectantes'),

-- Matériel diagnostic
('Bandelettes glucose', 'INV-BAND-001', true, 18.00, 0.05, 0.005, 30, 120, 'Boîte de 50 bandelettes test glucose'),
('Kit test urinaire', 'INV-URIN-001', true, 22.00, 0.1, 0.01, 20, 80, 'Boîte de 100 bandelettes test urinaire'),

-- Équipements protection
('Surblouses jetables', 'INV-SURB-001', true, 15.00, 0.8, 0.08, 50, 200, 'Paquet de 50 surblouses'),
('Charlotte', 'INV-CHAR-001', true, 4.00, 0.1, 0.01, 100, 400, 'Boîte de 100 charlottes jetables'),
('Surchaussures', 'INV-SURCH-001', true, 3.50, 0.15, 0.015, 100, 350, 'Paquet de 100 surchaussures'),

-- Consommables laboratoire
('Tubes à essai', 'INV-TUBE-001', true, 12.00, 0.2, 0.02, 40, 150, 'Boîte de 100 tubes à essai'),
('Pipettes Pasteur', 'INV-PIP-001', true, 8.00, 0.1, 0.01, 50, 200, 'Boîte de 500 pipettes Pasteur');

-- ============================================================================
-- 8. Emplacements des produits (utilise SELECT pour les IDs)
-- ============================================================================
-- Gants dans Entrepôt Central
INSERT INTO inventory_product_location (product_id, location_id, quantity_stored, quantity_counted, last_count_date)
SELECT p.product_id, l.location_id, 300, 300, '2024-01-15'
FROM inventory_product p, "inventory_stockLocation" l
WHERE p.default_code = 'INV-GLAT-001' AND l.name = 'Entrepôt Central';

-- Masques dans Entrepôt Central
INSERT INTO inventory_product_location (product_id, location_id, quantity_stored, quantity_counted, last_count_date)
SELECT p.product_id, l.location_id, 500, 500, '2024-01-15'
FROM inventory_product p, "inventory_stockLocation" l
WHERE p.default_code = 'INV-MASK-001' AND l.name = 'Entrepôt Central';

-- Compresses dans Entrepôt Central
INSERT INTO inventory_product_location (product_id, location_id, quantity_stored, quantity_counted, last_count_date)
SELECT p.product_id, l.location_id, 200, 200, '2024-01-15'
FROM inventory_product p, "inventory_stockLocation" l
WHERE p.default_code = 'INV-COMP-001' AND l.name = 'Entrepôt Central';

-- Seringues dans Réserve A
INSERT INTO inventory_product_location (product_id, location_id, quantity_stored, quantity_counted, last_count_date)
SELECT p.product_id, l.location_id, 250, 250, '2024-01-15'
FROM inventory_product p, "inventory_stockLocation" l
WHERE p.default_code = 'INV-SER-001' AND l.name = 'Réserve A';

-- Thermomètres dans Armoire Médical 1
INSERT INTO inventory_product_location (product_id, location_id, quantity_stored, quantity_counted, last_count_date)
SELECT p.product_id, l.location_id, 30, 30, '2024-01-16'
FROM inventory_product p, "inventory_stockLocation" l
WHERE p.default_code = 'INV-THER-001' AND l.name = 'Armoire Médical 1';

-- Papier A4 dans Étagère Consommables
INSERT INTO inventory_product_location (product_id, location_id, quantity_stored, quantity_counted, last_count_date)
SELECT p.product_id, l.location_id, 150, 150, '2024-01-17'
FROM inventory_product p, "inventory_stockLocation" l
WHERE p.default_code = 'INV-PAP-001' AND l.name = 'Étagère Consommables';

-- Solution hydroalcoolique dans Zone Stérile
INSERT INTO inventory_product_location (product_id, location_id, quantity_stored, quantity_counted, last_count_date)
SELECT p.product_id, l.location_id, 200, 200, '2024-01-18'
FROM inventory_product p, "inventory_stockLocation" l
WHERE p.default_code = 'INV-SHA-001' AND l.name = 'Zone Stérile 1';

-- ============================================================================
-- 9. Mouvements de stock
-- ============================================================================
INSERT INTO "inventory_stockMove" (reference, state, scheduled_date, effective_date, operation_type_id, source_location_id, dest_location_id, supplier_id, department_id, notes, created_by, date_created)
SELECT 'MOV-REC-001', 'done', '2024-01-10', '2024-01-10',
    ot.operation_type_id,
    NULL,
    sl.location_id,
    1,
    NULL,
    'Réception commande fournisseur - Gants et masques',
    1,
    NOW()
FROM "inventory_operationType" ot, "inventory_stockLocation" sl
WHERE ot.label = 'Réception' AND sl.name = 'Entrepôt Central'
LIMIT 1;

INSERT INTO "inventory_stockMove" (reference, state, scheduled_date, effective_date, operation_type_id, source_location_id, dest_location_id, supplier_id, department_id, notes, created_by, date_created)
SELECT 'MOV-OUT-001', 'done', '2024-01-12', '2024-01-12',
    ot.operation_type_id,
    sl1.location_id,
    NULL,
    NULL,
    1,
    'Sortie produits pour service médical',
    1,
    NOW()
FROM "inventory_operationType" ot, "inventory_stockLocation" sl1
WHERE ot.label = 'Sortie' AND sl1.name = 'Entrepôt Central'
LIMIT 1;

INSERT INTO "inventory_stockMove" (reference, state, scheduled_date, effective_date, operation_type_id, source_location_id, dest_location_id, supplier_id, department_id, notes, created_by, date_created)
SELECT 'MOV-TRF-001', 'done', '2024-01-15', '2024-01-15',
    ot.operation_type_id,
    sl1.location_id,
    sl2.location_id,
    NULL,
    NULL,
    'Transfert entre entrepôt et réserve',
    1,
    NOW()
FROM "inventory_operationType" ot, "inventory_stockLocation" sl1, "inventory_stockLocation" sl2
WHERE ot.label = 'Transfert' AND sl1.name = 'Entrepôt Central' AND sl2.name = 'Réserve A'
LIMIT 1;

INSERT INTO "inventory_stockMove" (reference, state, scheduled_date, operation_type_id, source_location_id, dest_location_id, supplier_id, department_id, notes, created_by, date_created)
SELECT 'MOV-REC-002', 'confirmed', '2024-02-01',
    ot.operation_type_id,
    NULL,
    sl.location_id,
    2,
    NULL,
    'Réception prévue - Commande février',
    1,
    NOW()
FROM "inventory_operationType" ot, "inventory_stockLocation" sl
WHERE ot.label = 'Réception' AND sl.name = 'Entrepôt Central'
LIMIT 1;

INSERT INTO "inventory_stockMove" (reference, state, scheduled_date, operation_type_id, source_location_id, dest_location_id, supplier_id, department_id, notes, created_by, date_created)
SELECT 'MOV-OUT-002', 'draft', '2024-02-05',
    ot.operation_type_id,
    sl.location_id,
    NULL,
    NULL,
    2,
    'Sortie prévue pour RH',
    1,
    NOW()
FROM "inventory_operationType" ot, "inventory_stockLocation" sl
WHERE ot.label = 'Sortie' AND sl.name = 'Réserve A'
LIMIT 1;

-- ============================================================================
-- 10. Lignes de mouvements de stock
-- ============================================================================
-- Lignes pour MOV-REC-001 (Réception)
INSERT INTO inventory_line_stock_move (move_id, product_id, quantity_demanded, quantity_arrived, uom_id)
SELECT 
    sm.move_id,
    p.product_id,
    500,
    500,
    uom.uom_id
FROM "inventory_stockMove" sm, inventory_product p, inventory_unitofmesure uom
WHERE sm.reference = 'MOV-REC-001' AND p.default_code = 'INV-GLAT-001' AND uom.label = 'Boîte'
LIMIT 1;

INSERT INTO inventory_line_stock_move (move_id, product_id, quantity_demanded, quantity_arrived, uom_id)
SELECT 
    sm.move_id,
    p.product_id,
    1000,
    1000,
    uom.uom_id
FROM "inventory_stockMove" sm, inventory_product p, inventory_unitofmesure uom
WHERE sm.reference = 'MOV-REC-001' AND p.default_code = 'INV-MASK-001' AND uom.label = 'Boîte'
LIMIT 1;

-- Lignes pour MOV-OUT-001 (Sortie)
INSERT INTO inventory_line_stock_move (move_id, product_id, quantity_demanded, quantity_arrived, uom_id)
SELECT 
    sm.move_id,
    p.product_id,
    100,
    100,
    uom.uom_id
FROM "inventory_stockMove" sm, inventory_product p, inventory_unitofmesure uom
WHERE sm.reference = 'MOV-OUT-001' AND p.default_code = 'INV-GLAT-001' AND uom.label = 'Boîte'
LIMIT 1;

-- Lignes pour MOV-TRF-001 (Transfert)
INSERT INTO inventory_line_stock_move (move_id, product_id, quantity_demanded, quantity_arrived, uom_id)
SELECT 
    sm.move_id,
    p.product_id,
    200,
    200,
    uom.uom_id
FROM "inventory_stockMove" sm, inventory_product p, inventory_unitofmesure uom
WHERE sm.reference = 'MOV-TRF-001' AND p.default_code = 'INV-COMP-001' AND uom.label = 'Boîte'
LIMIT 1;

-- Lignes pour MOV-REC-002 (Réception prévue)
INSERT INTO inventory_line_stock_move (move_id, product_id, quantity_demanded, quantity_arrived, uom_id)
SELECT 
    sm.move_id,
    p.product_id,
    300,
    NULL,
    uom.uom_id
FROM "inventory_stockMove" sm, inventory_product p, inventory_unitofmesure uom
WHERE sm.reference = 'MOV-REC-002' AND p.default_code = 'INV-SER-001' AND uom.label = 'Boîte'
LIMIT 1;

COMMIT;

-- ============================================================================
-- MESSAGE DE CONFIRMATION
-- ============================================================================
SELECT 'DONNEES INVENTORY CREEES AVEC SUCCES!' as message;

-- ============================================================================
-- RÉSUMÉ DES DONNÉES CRÉÉES
-- ============================================================================
SELECT 
    'RÉSUMÉ DES DONNÉES CRÉÉES' as titre,
    (SELECT COUNT(*) FROM inventory_category) as "Catégories",
    (SELECT COUNT(*) FROM inventory_unitofmesure) as "Unités de mesure",
    (SELECT COUNT(*) FROM "inventory_productType") as "Types de produits",
    (SELECT COUNT(*) FROM "inventory_locationType") as "Types d'emplacement",
    (SELECT COUNT(*) FROM "inventory_stockLocation") as "Emplacements",
    (SELECT COUNT(*) FROM "inventory_operationType") as "Types d'opération",
    (SELECT COUNT(*) FROM inventory_product) as "Produits",
    (SELECT COUNT(*) FROM inventory_product_location) as "Emplacements produits",
    (SELECT COUNT(*) FROM "inventory_stockMove") as "Mouvements de stock",
    (SELECT COUNT(*) FROM inventory_line_stock_move) as "Lignes de mouvements";

