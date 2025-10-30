-- ============================================================================
-- Script SQL pour remplir les tables du module Restauration (PostgreSQL)
-- ============================================================================
-- Ce script crée des données de test pour toutes les tables du module Restauration
-- Base de données: PostgreSQL
-- ============================================================================

BEGIN;

-- Vider les tables restauration existantes (dans l'ordre des dépendances)
TRUNCATE TABLE "Restauration_menusupplementaire" CASCADE;
TRUNCATE TABLE "Restauration_menupersonnalise_plats" CASCADE;
TRUNCATE TABLE "Restauration_menupersonnalise" CASCADE;
TRUNCATE TABLE "Restauration_programmejourmenu_plats" CASCADE;
TRUNCATE TABLE "Restauration_programmejourmenu" CASCADE;
TRUNCATE TABLE "Restauration_programmejour" CASCADE;
TRUNCATE TABLE "Restauration_programme" CASCADE;
TRUNCATE TABLE "Restauration_menustandard_plats" CASCADE;
TRUNCATE TABLE "Restauration_menustandard" CASCADE;
TRUNCATE TABLE "Restauration_lignerecette" CASCADE;
TRUNCATE TABLE "Restauration_recette" CASCADE;
TRUNCATE TABLE "Restauration_ingredient" CASCADE;
TRUNCATE TABLE "Restauration_ingredientcategorie" CASCADE;
TRUNCATE TABLE "Restauration_plat" CASCADE;

-- ============================================================================
-- 1. TABLE: Restauration_ingredientcategorie (Catégories d'ingrédients)
-- ============================================================================
INSERT INTO "Restauration_ingredientcategorie" (id, nom) VALUES
(1, 'Légumes'),
(2, 'Viandes'),
(3, 'Poissons'),
(4, 'Féculents'),
(5, 'Produits laitiers'),
(6, 'Fruits'),
(7, 'Épices et condiments'),
(8, 'Huiles et matières grasses'),
(9, 'Céréales'),
(10, 'Légumineuses');

-- Réinitialiser la séquence
SELECT setval('"Restauration_ingredientcategorie_id_seq"', (SELECT MAX(id) FROM "Restauration_ingredientcategorie"));

-- ============================================================================
-- 2. TABLE: Restauration_ingredient (Ingrédients)
-- ============================================================================
INSERT INTO "Restauration_ingredient" (id, nom, unite, categorie_id) VALUES
-- Légumes
(1, 'Tomates', 'kg', 1),
(2, 'Carottes', 'kg', 1),
(3, 'Oignons', 'kg', 1),
(4, 'Pommes de terre', 'kg', 1),
(5, 'Courgettes', 'kg', 1),
-- Viandes
(6, 'Poulet', 'kg', 2),
(7, 'Bœuf', 'kg', 2),
(8, 'Agneau', 'kg', 2),
-- Poissons
(9, 'Sole', 'kg', 3),
(10, 'Cabillaud', 'kg', 3),
-- Féculents
(11, 'Riz', 'kg', 4),
(12, 'Pâtes', 'kg', 4),
(13, 'Semoule', 'kg', 4),
-- Produits laitiers
(14, 'Lait', 'L', 5),
(15, 'Yaourt', 'unité', 5),
-- Fruits
(16, 'Pommes', 'kg', 6),
(17, 'Oranges', 'kg', 6),
(18, 'Bananes', 'kg', 6),
-- Épices
(19, 'Sel', 'g', 7),
(20, 'Poivre', 'g', 7);

-- Réinitialiser la séquence
SELECT setval('"Restauration_ingredient_id_seq"', (SELECT MAX(id) FROM "Restauration_ingredient"));

-- ============================================================================
-- 3. TABLE: Restauration_plat (Plats)
-- ============================================================================
INSERT INTO "Restauration_plat" (id, nom) VALUES
(1, 'Tajine de poulet aux légumes'),
(2, 'Couscous royal'),
(3, 'Poisson grillé'),
(4, 'Salade composée'),
(5, 'Soupe de légumes'),
(6, 'Riz au poulet'),
(7, 'Purée de pommes de terre'),
(8, 'Légumes vapeur'),
(9, 'Yaourt nature'),
(10, 'Fruits frais'),
(11, 'Omelette nature'),
(12, 'Pain complet'),
(13, 'Confiture'),
(14, 'Fromage blanc'),
(15, 'Jus d''orange');

-- Réinitialiser la séquence
SELECT setval('"Restauration_plat_id_seq"', (SELECT MAX(id) FROM "Restauration_plat"));

-- ============================================================================
-- 4. TABLE: Restauration_recette (Recettes)
-- ============================================================================
INSERT INTO "Restauration_recette" (id, plat_id) VALUES
(1, 1),  -- Recette Tajine de poulet
(2, 2),  -- Recette Couscous royal
(3, 3),  -- Recette Poisson grillé
(4, 5),  -- Recette Soupe de légumes
(5, 6);  -- Recette Riz au poulet

-- Réinitialiser la séquence
SELECT setval('"Restauration_recette_id_seq"', (SELECT MAX(id) FROM "Restauration_recette"));

-- ============================================================================
-- 5. TABLE: Restauration_lignerecette (Lignes de recette)
-- ============================================================================
INSERT INTO "Restauration_lignerecette" (id, recette_id, ingredient_id, quantite_par_portion) VALUES
-- Tajine de poulet
(1, 1, 6, 0.200),  -- 200g poulet
(2, 1, 1, 0.100),  -- 100g tomates
(3, 1, 2, 0.050),  -- 50g carottes
(4, 1, 3, 0.030),  -- 30g oignons
-- Couscous royal
(5, 2, 13, 0.150), -- 150g semoule
(6, 2, 6, 0.100),  -- 100g poulet
(7, 2, 8, 0.100),  -- 100g agneau
(8, 2, 1, 0.080),  -- 80g tomates
-- Poisson grillé
(9, 3, 9, 0.200),  -- 200g sole
(10, 3, 19, 0.002), -- 2g sel
-- Soupe de légumes
(11, 4, 2, 0.100), -- 100g carottes
(12, 4, 4, 0.100), -- 100g pommes de terre
(13, 4, 3, 0.050), -- 50g oignons
-- Riz au poulet
(14, 5, 11, 0.100), -- 100g riz
(15, 5, 6, 0.150);  -- 150g poulet

-- Réinitialiser la séquence
SELECT setval('"Restauration_lignerecette_id_seq"', (SELECT MAX(id) FROM "Restauration_lignerecette"));

-- ============================================================================
-- 6. TABLE: Restauration_menustandard (Menus standards)
-- ============================================================================
INSERT INTO "Restauration_menustandard" (id, date, repas) VALUES
(1, '2024-01-20', 'Petit déjeuner'),
(2, '2024-01-20', 'Déjeuner'),
(3, '2024-01-20', 'Collation'),
(4, '2024-01-20', 'Dîner'),
(5, '2024-01-21', 'Petit déjeuner');

-- Réinitialiser la séquence
SELECT setval('"Restauration_menustandard_id_seq"', (SELECT MAX(id) FROM "Restauration_menustandard"));

-- ============================================================================
-- 7. TABLE: Restauration_menustandard_plats (Liaison menu-plats)
-- ============================================================================
INSERT INTO "Restauration_menustandard_plats" (id, menustandard_id, plat_id) VALUES
-- Petit déjeuner
(1, 1, 11), -- Omelette
(2, 1, 12), -- Pain
(3, 1, 15), -- Jus orange
-- Déjeuner
(4, 2, 1),  -- Tajine
(5, 2, 7),  -- Purée
(6, 2, 10), -- Fruits
-- Collation
(7, 3, 9),  -- Yaourt
(8, 3, 10), -- Fruits frais
-- Dîner
(9, 4, 5),  -- Soupe
(10, 4, 6), -- Riz poulet
(11, 4, 9); -- Yaourt

-- Réinitialiser la séquence
SELECT setval('"Restauration_menustandard_plats_id_seq"', (SELECT MAX(id) FROM "Restauration_menustandard_plats"));

-- ============================================================================
-- 8. TABLE: Restauration_programme (Programmes)
-- ============================================================================
INSERT INTO "Restauration_programme" (id, nom, date_debut, date_fin, lieu, population) VALUES
(1, 'Programme Janvier 2024', '2024-01-15', '2024-01-31', 'Hôpital Principal', 'patients'),
(2, 'Programme Février 2024', '2024-02-01', '2024-02-15', 'Hôpital Principal', 'patients'),
(3, 'Programme Diététique', '2024-01-20', '2024-02-20', 'Service Nutrition', 'patients diabétiques');

-- Réinitialiser la séquence
SELECT setval('"Restauration_programme_id_seq"', (SELECT MAX(id) FROM "Restauration_programme"));

-- ============================================================================
-- 9. TABLE: Restauration_menupersonnalise (Menus personnalisés)
-- ============================================================================
INSERT INTO "Restauration_menupersonnalise" (id, client_id, num_chambre, date, repas, quantite, description) VALUES
(1, 1, 'CH-101', '2024-01-20', 'Déjeuner', 1, 'Régime sans sel'),
(2, 2, 'CH-104', '2024-01-20', 'Déjeuner', 1, 'Régime diabétique'),
(3, 3, 'CH-201', '2024-01-20', 'Dîner', 1, 'Menu standard');

-- Réinitialiser la séquence
SELECT setval('"Restauration_menupersonnalise_id_seq"', (SELECT MAX(id) FROM "Restauration_menupersonnalise"));

-- ============================================================================
-- 10. TABLE: Restauration_menupersonnalise_plats (Liaison menu personnalisé-plats)
-- ============================================================================
INSERT INTO "Restauration_menupersonnalise_plats" (id, menupersonnalise_id, plat_id) VALUES
(1, 1, 3),  -- Poisson grillé
(2, 1, 8),  -- Légumes vapeur
(3, 2, 6),  -- Riz poulet (sans sauce)
(4, 2, 4),  -- Salade
(5, 3, 1),  -- Tajine
(6, 3, 7);  -- Purée

-- Réinitialiser la séquence
SELECT setval('"Restauration_menupersonnalise_plats_id_seq"', (SELECT MAX(id) FROM "Restauration_menupersonnalise_plats"));

-- ============================================================================
-- 11. TABLE: Restauration_menusupplementaire (Menus supplémentaires)
-- ============================================================================
INSERT INTO "Restauration_menusupplementaire" (id, client_id, num_chambre, date, repas, quantite) VALUES
(1, 1, 'CH-101', '2024-01-20', 'Collation', 1),
(2, 2, 'CH-104', '2024-01-20', 'Collation', 1),
(3, 4, 'CH-VIP-01', '2024-01-20', 'Déjeuner', 2);

-- Réinitialiser la séquence
SELECT setval('"Restauration_menusupplementaire_id_seq"', (SELECT MAX(id) FROM "Restauration_menusupplementaire"));

COMMIT;

-- ============================================================================
-- MESSAGE DE CONFIRMATION
-- ============================================================================
SELECT 'DONNEES RESTAURATION CREEES AVEC SUCCES!' as message;

-- ============================================================================
-- RÉSUMÉ DES DONNÉES CRÉÉES
-- ============================================================================
SELECT 
    'RÉSUMÉ DES DONNÉES CRÉÉES' as titre,
    (SELECT COUNT(*) FROM "Restauration_ingredientcategorie") as "Catégories ingrédients",
    (SELECT COUNT(*) FROM "Restauration_ingredient") as "Ingrédients",
    (SELECT COUNT(*) FROM "Restauration_plat") as "Plats",
    (SELECT COUNT(*) FROM "Restauration_recette") as "Recettes",
    (SELECT COUNT(*) FROM "Restauration_menustandard") as "Menus standards",
    (SELECT COUNT(*) FROM "Restauration_programme") as "Programmes",
    (SELECT COUNT(*) FROM "Restauration_menupersonnalise") as "Menus personnalisés",
    (SELECT COUNT(*) FROM "Restauration_menusupplementaire") as "Menus supplémentaires";

