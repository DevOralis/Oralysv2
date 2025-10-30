-- ============================================================================
-- Script SQL pour remplir les tables du module Purchases (PostgreSQL)
-- ============================================================================
-- Ce script crée des données de test pour toutes les tables du module Purchases
-- Base de données: PostgreSQL
-- ============================================================================

BEGIN;

-- Vider les tables purchases existantes (dans l'ordre des dépendances)
TRUNCATE TABLE purchases_supplier CASCADE;
TRUNCATE TABLE purchases_city CASCADE;
TRUNCATE TABLE purchases_country CASCADE;
TRUNCATE TABLE purchases_language CASCADE;
TRUNCATE TABLE purchases_currency CASCADE;
TRUNCATE TABLE purchases_tax CASCADE;
TRUNCATE TABLE purchases_payment_mode CASCADE;

-- ============================================================================
-- 1. TABLE: purchases_country (Pays)
-- ============================================================================
INSERT INTO purchases_country (id, name) VALUES
(1, 'Maroc'),
(2, 'France'),
(3, 'Espagne'),
(4, 'Allemagne'),
(5, 'Italie'),
(6, 'Belgique'),
(7, 'Suisse'),
(8, 'Tunisie'),
(9, 'Algérie'),
(10, 'Égypte');

-- Réinitialiser la séquence
SELECT setval('purchases_country_id_seq', (SELECT MAX(id) FROM purchases_country));

-- ============================================================================
-- 2. TABLE: purchases_city (Villes)
-- ============================================================================
INSERT INTO purchases_city (id, name, country_id) VALUES
(1, 'Casablanca', 1),
(2, 'Rabat', 1),
(3, 'Fès', 1),
(4, 'Marrakech', 1),
(5, 'Tanger', 1),
(6, 'Paris', 2),
(7, 'Lyon', 2),
(8, 'Madrid', 3),
(9, 'Barcelone', 3),
(10, 'Berlin', 4),
(11, 'Munich', 4),
(12, 'Rome', 5),
(13, 'Milan', 5),
(14, 'Bruxelles', 6),
(15, 'Genève', 7);

-- Réinitialiser la séquence
SELECT setval('purchases_city_id_seq', (SELECT MAX(id) FROM purchases_city));

-- ============================================================================
-- 3. TABLE: purchases_language (Langues)
-- ============================================================================
INSERT INTO purchases_language (id, name) VALUES
(1, 'Français'),
(2, 'Arabe'),
(3, 'Anglais'),
(4, 'Espagnol'),
(5, 'Allemand'),
(6, 'Italien'),
(7, 'Néerlandais');

-- Réinitialiser la séquence
SELECT setval('purchases_language_id_seq', (SELECT MAX(id) FROM purchases_language));

-- ============================================================================
-- 4. TABLE: purchases_currency (Devises)
-- ============================================================================
INSERT INTO purchases_currency (id, libelle, abreviation) VALUES
(1, 'Dirham Marocain', 'MAD'),
(2, 'Euro', 'EUR'),
(3, 'Dollar Américain', 'USD'),
(4, 'Livre Sterling', 'GBP'),
(5, 'Franc Suisse', 'CHF'),
(6, 'Dinar Tunisien', 'TND'),
(7, 'Dinar Algérien', 'DZD');

-- Réinitialiser la séquence
SELECT setval('purchases_currency_id_seq', (SELECT MAX(id) FROM purchases_currency));

-- ============================================================================
-- 5. TABLE: purchases_tax (Taxes)
-- ============================================================================
INSERT INTO purchases_tax (id, libelle, valeur) VALUES
(1, 'TVA 20%', 20.00),
(2, 'TVA 10%', 10.00),
(3, 'TVA 5.5%', 5.50),
(4, 'TVA 0%', 0.00),
(5, 'TVA 7%', 7.00),
(6, 'TVA 14%', 14.00);

-- Réinitialiser la séquence
SELECT setval('purchases_tax_id_seq', (SELECT MAX(id) FROM purchases_tax));

-- ============================================================================
-- 6. TABLE: purchases_payment_mode (Modes de paiement)
-- ============================================================================
INSERT INTO purchases_payment_mode (id, name, description) VALUES
(1, 'Virement bancaire', 'Paiement par virement bancaire'),
(2, 'Chèque', 'Paiement par chèque'),
(3, 'Espèces', 'Paiement en espèces'),
(4, 'Carte bancaire', 'Paiement par carte bancaire'),
(5, 'Effet de commerce', 'Paiement par effet de commerce'),
(6, 'Prélèvement automatique', 'Paiement par prélèvement automatique'),
(7, 'Crédit fournisseur', 'Paiement différé avec crédit fournisseur');

-- Réinitialiser la séquence
SELECT setval('purchases_payment_mode_id_seq', (SELECT MAX(id) FROM purchases_payment_mode));

-- ============================================================================
-- 7. TABLE: purchases_supplier (Fournisseurs)
-- ============================================================================
INSERT INTO purchases_supplier (
    id, name, is_company, street, street2, zip, city_id, country_id, lang_id,
    email, phone, mobile, "ICE", "RC", "IF", vat, "RIB", comment
) VALUES
(1, 'MedEquip Maroc', true, 'Zone Industrielle Aïn Sebaâ', 'Lot 45', '20250', 1, 1, 1,
 'contact@medequip.ma', '+212522334455', '+212612345678', '001234567890001', 12345678, 87654321, 'MAR123456', '230610000123456789012345', 'Fournisseur principal équipements médicaux'),
 
(2, 'PharmaDistrib', true, 'Avenue Hassan II', 'Immeuble Al Amal', '10000', 2, 1, 1,
 'info@pharmadistrib.ma', '+212537445566', '+212623456789', '001234567890002', 23456789, 98765432, 'MAR234567', '230610000234567890123456', 'Distributeur produits pharmaceutiques'),
 
(3, 'Sanofi Maroc', true, 'Zone Franche Tanger', 'Usine 100', '90000', 5, 1, 1,
 'maroc@sanofi.com', '+212539667788', '+212634567890', '001234567890003', 34567890, 19876543, 'MAR345678', '230610000345678901234567', 'Laboratoire pharmaceutique international'),
 
(4, 'MediTech Europe', true, 'Rue de la Santé', 'Bâtiment B', '75013', 6, 2, 1,
 'contact@meditech.fr', '+33142334455', '+33612345678', '', NULL, NULL, 'FR12345678901', 'FR76123456789012345678901234', 'Importateur équipements européens'),
 
(5, 'BioSupplies International', true, 'Avenida de la Salud', 'Piso 3', '28001', 8, 3, 4,
 'info@biosupplies.es', '+34912334455', '+34612345678', '', NULL, NULL, 'ES12345678901', 'ES76123456789012345678901234', 'Fournitures biologiques et consommables');

-- Réinitialiser la séquence
SELECT setval('purchases_supplier_id_seq', (SELECT MAX(id) FROM purchases_supplier));

-- ============================================================================
-- 8. TABLE: purchases_convention_type et purchases_convention - NON CRÉÉES
-- ============================================================================
-- Ces tables n'existent pas encore dans la base de données

COMMIT;

-- ============================================================================
-- MESSAGE DE CONFIRMATION
-- ============================================================================
SELECT 'DONNEES PURCHASES CREEES AVEC SUCCES!' as message;

-- ============================================================================
-- RÉSUMÉ DES DONNÉES CRÉÉES
-- ============================================================================
SELECT 
    'RÉSUMÉ DES DONNÉES CRÉÉES' as titre,
    (SELECT COUNT(*) FROM purchases_country) as "Pays",
    (SELECT COUNT(*) FROM purchases_city) as "Villes",
    (SELECT COUNT(*) FROM purchases_language) as "Langues",
    (SELECT COUNT(*) FROM purchases_currency) as "Devises",
    (SELECT COUNT(*) FROM purchases_tax) as "Taxes",
    (SELECT COUNT(*) FROM purchases_payment_mode) as "Modes de paiement",
    (SELECT COUNT(*) FROM purchases_supplier) as "Fournisseurs",
    0 as "Types de convention (non créés)",
    0 as "Conventions (non créées)";

