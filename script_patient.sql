-- ============================================================================
-- Script SQL pour remplir les tables du module Patient (PostgreSQL)
-- ============================================================================
-- Ce script crée des données de test pour toutes les tables du module Patient
-- Base de données: PostgreSQL
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. TABLE: patient_acte (Actes médicaux)
-- ============================================================================
INSERT INTO patient_acte (id, libelle, price) VALUES
(1, 'Consultation générale', 200.00),
(2, 'Consultation spécialisée', 300.00),
(3, 'Consultation urgente', 400.00),
(4, 'Échographie abdominale', 350.00),
(5, 'Échographie cardiaque', 400.00),
(6, 'Radiographie thorax', 150.00),
(7, 'Radiographie membre', 120.00),
(8, 'IRM cérébrale', 800.00),
(9, 'Scanner abdominal', 600.00),
(10, 'Électrocardiogramme', 100.00),
(11, 'Analyse sanguine complète', 180.00),
(12, 'Analyse urinaire', 50.00),
(13, 'Biopsie', 250.00),
(14, 'Endoscopie digestive', 500.00),
(15, 'Coloscopie', 600.00),
(16, 'Fibroscopie bronchique', 450.00),
(17, 'Échographie pelvienne', 280.00),
(18, 'Mammographie', 200.00),
(19, 'Densitométrie osseuse', 300.00),
(20, 'Holter ECG 24h', 200.00);

-- Réinitialiser la séquence
SELECT setval('patient_acte_id_seq', (SELECT MAX(id) FROM patient_acte));

-- ============================================================================
-- 2. TABLE: patient_emergencycontact (Contacts d'urgence)
-- ============================================================================
INSERT INTO patient_emergencycontact (id, name, phone, relationship) VALUES
(1, 'Fatima Alami', '+212612345678', 'Épouse'),
(2, 'Hassan Bennani', '+212623456789', 'Mari'),
(3, 'Khadija Tazi', '+212634567890', 'Sœur'),
(4, 'Omar El Fassi', '+212645678901', 'Mari'),
(5, 'Aicha Idrissi', '+212656789012', 'Épouse'),
(6, 'Youssef Amrani', '+212667890123', 'Père'),
(7, 'Zineb Senhaji', '+212678901234', 'Mère'),
(8, 'Ahmed Ouazzani', '+212689012345', 'Frère'),
(9, 'Khadija Naciri', '+212690123456', 'Sœur'),
(10, 'Mohamed Khalil', '+212601234567', 'Oncle'),
(11, 'Aicha Chraibi', '+212612345678', 'Tante'),
(12, 'Hassan El Mansouri', '+212623456789', 'Cousin'),
(13, 'Fatima Benjelloun', '+212634567890', 'Cousine'),
(14, 'Omar Alaoui', '+212645678901', 'Ami'),
(15, 'Khadija Bennis', '+212656789012', 'Amie'),
(16, 'Youssef Rifi', '+212667890123', 'Collègue'),
(17, 'Zineb Skalli', '+212678901234', 'Collègue'),
(18, 'Ahmed Benslimane', '+212689012345', 'Voisin'),
(19, 'Khadija Tazi', '+212690123456', 'Voisine'),
(20, 'Mohamed Berrada', '+212601234567', 'Ami de famille');

-- Réinitialiser la séquence
SELECT setval('patient_emergencycontact_id_seq', (SELECT MAX(id) FROM patient_emergencycontact));

-- ============================================================================
-- 3. TABLE: patient_patient (Patients)
-- ============================================================================
INSERT INTO patient_patient (
    id, patient_identifier, cin, passport_number, last_name, first_name, 
    gender, birth_date, nationality, profession, city, email, 
    phone, mobile_number, spouse_name, treating_physician, referring_physician, 
    disease_speciality, has_insurance, insurance_number, affiliation_number, 
    relationship, insured_name
) VALUES
-- Patient 1
(1, 'PAT-001', 'AB123456', NULL, 'Alami', 'Hassan', 'M', '1965-03-15', 'MA', 
 'Enseignant', 'Casablanca', 'hassan.alami@email.ma', '+212522334455', '+212612345678', 
 'Fatima Alami', 'Dr. Bennani Mohammed', 'Dr. Tazi Ahmed', 'Cardiologie', true, 
 'CNSS123456', 'AFF001', 'Adhérent', 'Hassan Alami'),

-- Patient 2
(2, 'PAT-002', 'CD234567', NULL, 'Bennani', 'Fatima', 'F', '1970-07-22', 'MA', 
 'Infirmière', 'Rabat', 'fatima.bennani@email.ma', '+212537445566', '+212623456789', 
 'Hassan Bennani', 'Dr. El Fassi Karim', 'Dr. Idrissi Leila', 'Gynécologie', true, 
 'CNSS234567', 'AFF002', 'Adhérente', 'Fatima Bennani'),

-- Patient 3
(3, 'PAT-003', 'EF345678', NULL, 'Tazi', 'Ahmed', 'M', '1980-11-30', 'MA', 
 'Ingénieur', 'Marrakech', 'ahmed.tazi@email.ma', '+212524556677', '+212634567890', 
 '', 'Dr. Amrani Nadia', 'Dr. Chraibi Said', 'Neurologie', false, 
 NULL, NULL, NULL, NULL),

-- Patient 4
(4, 'PAT-004', 'GH456789', NULL, 'El Fassi', 'Samira', 'F', '1988-05-18', 'MA', 
 'Avocate', 'Fès', 'samira.elfassi@email.ma', '+212535667788', '+212645678901', 
 'Omar El Fassi', 'Dr. Senhaji Rachid', 'Dr. Ouazzani Fatima', 'Dermatologie', true, 
 'CNSS345678', 'AFF003', 'Adhérente', 'Samira El Fassi'),

-- Patient 5
(5, 'PAT-005', 'IJ567890', NULL, 'Idrissi', 'Mohamed', 'M', '1975-09-25', 'MA', 
 'Commerçant', 'Tanger', 'mohamed.idrissi@email.ma', '+212539778899', '+212656789012', 
 'Khadija Idrissi', 'Dr. Naciri Youssef', 'Dr. Khalil Zineb', 'Diabétologie', true, 
 'CNSS456789', 'AFF004', 'Adhérent', 'Mohamed Idrissi'),

-- Patient 6
(6, 'PAT-006', 'KL678901', NULL, 'Amrani', 'Khadija', 'F', '1992-12-08', 'MA', 
 'Étudiante', 'Agadir', 'khadija.amrani@email.ma', '+212543889900', '+212667890123', 
 '', 'Dr. Berrada Mohamed', 'Dr. Skalli Ahmed', 'Pédiatrie', true, 
 'CNSS567890', 'AFF005', 'Adhérente', 'Khadija Amrani'),

-- Patient 7
(7, 'PAT-007', 'MN789012', NULL, 'Senhaji', 'Youssef', 'M', '1985-04-12', 'MA', 
 'Médecin', 'Meknès', 'youssef.senhaji@email.ma', '+212548990011', '+212678901234', 
 'Zineb Senhaji', 'Dr. Benslimane Karim', 'Dr. Tazi Leila', 'Rhumatologie', true, 
 'CNSS678901', 'AFF006', 'Adhérent', 'Youssef Senhaji'),

-- Patient 8
(8, 'PAT-008', 'OP890123', NULL, 'Ouazzani', 'Leila', 'F', '1978-08-30', 'MA', 
 'Pharmacienne', 'Oujda', 'leila.ouazzani@email.ma', '+212552001122', '+212689012345', 
 'Ahmed Ouazzani', 'Dr. Naciri Fatima', 'Dr. Khalil Youssef', 'Ophtalmologie', true, 
 'CNSS789012', 'AFF007', 'Adhérente', 'Leila Ouazzani'),

-- Patient 9
(9, 'PAT-009', 'QR901234', NULL, 'Naciri', 'Karim', 'M', '1982-01-20', 'MA', 
 'Architecte', 'Tétouan', 'karim.naciri@email.ma', '+212556112233', '+212690123456', 
 'Khadija Naciri', 'Dr. Chraibi Ahmed', 'Dr. El Mansouri Fatima', 'Orthopédie', false, 
 NULL, NULL, NULL, NULL),

-- Patient 10
(10, 'PAT-010', 'ST012345', NULL, 'Khalil', 'Zineb', 'F', '1990-06-14', 'MA', 
 'Psychologue', 'Kénitra', 'zineb.khalil@email.ma', '+212561223344', '+212601234567', 
 'Mohamed Khalil', 'Dr. Benjelloun Youssef', 'Dr. Alaoui Karim', 'Endocrinologie', true, 
 'CNSS890123', 'AFF008', 'Adhérente', 'Zineb Khalil'),

-- Patient 11
(11, 'PAT-011', 'UV123456', NULL, 'Chraibi', 'Said', 'M', '1973-10-05', 'MA', 
 'Avocat', 'Safi', 'said.chraibi@email.ma', '+212565334455', '+212612345678', 
 'Aicha Chraibi', 'Dr. Bennis Omar', 'Dr. Rifi Khadija', 'Pneumologie', true, 
 'CNSS901234', 'AFF009', 'Adhérent', 'Said Chraibi'),

-- Patient 12
(12, 'PAT-012', 'WX234567', NULL, 'El Mansouri', 'Fatima', 'F', '1987-02-28', 'MA', 
 'Ingénieure', 'El Jadida', 'fatima.elmansouri@email.ma', '+212569445566', '+212623456789', 
 'Hassan El Mansouri', 'Dr. Skalli Youssef', 'Dr. Benslimane Leila', 'Gastro-entérologie', true, 
 'CNSS012345', 'AFF010', 'Adhérente', 'Fatima El Mansouri'),

-- Patient 13
(13, 'PAT-013', 'YZ345678', NULL, 'Benjelloun', 'Omar', 'M', '1984-11-16', 'MA', 
 'Comptable', 'Larache', 'omar.benjelloun@email.ma', '+212573556677', '+212634567890', 
 'Zineb Benjelloun', 'Dr. Tazi Ahmed', 'Dr. Berrada Karim', 'Psychiatrie', false, 
 NULL, NULL, NULL, NULL),

-- Patient 14
(14, 'PAT-014', 'AB456789', NULL, 'Alaoui', 'Khadija', 'F', '1995-09-03', 'MA', 
 'Étudiante', 'Nador', 'khadija.alaoui@email.ma', '+212577667788', '+212645678901', 
 '', 'Dr. Bennis Youssef', 'Dr. Rifi Fatima', 'Oncologie', true, 
 'CNSS123450', 'AFF011', 'Adhérente', 'Khadija Alaoui'),

-- Patient 15
(15, 'PAT-015', 'CD567890', NULL, 'Bennis', 'Youssef', 'M', '1979-12-25', 'MA', 
 'Enseignant', 'Settat', 'youssef.bennis@email.ma', '+212581778899', '+212656789012', 
 'Zineb Bennis', 'Dr. Skalli Omar', 'Dr. Benslimane Khadija', 'Urologie', true, 
 'CNSS234560', 'AFF012', 'Adhérent', 'Youssef Bennis');

-- Réinitialiser la séquence
SELECT setval('patient_patient_id_seq', (SELECT MAX(id) FROM patient_patient));

-- ============================================================================
-- 4. TABLE DE LIAISON: patient_patient_emergency_contacts
-- ============================================================================
INSERT INTO patient_patient_emergency_contacts (id, patient_id, emergencycontact_id) VALUES
(1, 1, 1),   -- Hassan Alami -> Fatima Alami (épouse)
(2, 2, 2),   -- Fatima Bennani -> Hassan Bennani (mari)
(3, 3, 3),   -- Ahmed Tazi -> Khadija Tazi (sœur)
(4, 4, 4),   -- Samira El Fassi -> Omar El Fassi (mari)
(5, 5, 5),   -- Mohamed Idrissi -> Aicha Idrissi (épouse)
(6, 6, 6),   -- Khadija Amrani -> Youssef Amrani (père)
(7, 7, 7),   -- Youssef Senhaji -> Zineb Senhaji (épouse)
(8, 8, 8),   -- Leila Ouazzani -> Ahmed Ouazzani (mari)
(9, 9, 9),   -- Karim Naciri -> Khadija Naciri (épouse)
(10, 10, 10), -- Zineb Khalil -> Mohamed Khalil (oncle)
(11, 11, 11), -- Said Chraibi -> Aicha Chraibi (épouse)
(12, 12, 12), -- Fatima El Mansouri -> Hassan El Mansouri (mari)
(13, 13, 13), -- Omar Benjelloun -> Zineb Benjelloun (épouse)
(14, 14, 14), -- Khadija Alaoui -> Omar Alaoui (ami)
(15, 15, 15); -- Youssef Bennis -> Zineb Bennis (épouse)

-- ============================================================================
-- 5. TABLE: patient_consultation (Consultations)
-- ============================================================================
INSERT INTO patient_consultation (
    id, patient_id, medecin_id, speciality_id, date, commentaires, traitement,
    temperature, pression, rythme_cardiaque, hospitalisation, demande_patient,
    type_admission, date_admission_programmee, consigne_alimentaire, 
    consigne_hebergement, is_invoiced
) VALUES
-- Consultation 1
(1, 1, 1, 1, '2024-01-15 09:30:00', 'Patient se plaint de douleurs thoraciques. Tension artérielle élevée.', 
 'Repos, régime sans sel, médicaments antihypertenseurs.', 37.2, '140/90', 85, false, 
 'consultation_normale', NULL, NULL, 'Régime sans sel', 'Repos à domicile', true),

-- Consultation 2
(2, 2, 2, 2, '2024-01-16 10:15:00', 'Consultation de routine gynécologique. Tout va bien.', 
 'Continuation du traitement habituel.', 36.8, '120/80', 72, false, 
 'consultation_normale', NULL, NULL, 'Alimentation normale', 'Domicile', true),

-- Consultation 3
(3, 3, 1, 3, '2024-01-17 14:00:00', 'Maux de tête persistants, examen neurologique demandé.', 
 'IRM cérébrale, traitement antalgique.', 36.5, '130/85', 78, true, 
 'hospitalisation', 'immediate', '2024-01-17', 'Alimentation légère', 'Hospitalisation en neurologie', false),

-- Consultation 4
(4, 4, 2, 4, '2024-01-18 11:30:00', 'Éruption cutanée, possible allergie.', 
 'Crème corticoïde, éviction des allergènes.', 37.0, '115/75', 70, false, 
 'consultation_normale', NULL, NULL, 'Éviter les aliments allergènes', 'Domicile', true),

-- Consultation 5
(5, 5, 1, 5, '2024-01-19 08:45:00', 'Diabète de type 2, contrôle glycémique.', 
 'Ajustement de l''insuline, régime diabétique.', 36.9, '125/80', 82, false, 
 'consultation_normale', NULL, NULL, 'Régime diabétique strict', 'Domicile', true),

-- Consultation 6
(6, 6, 2, 6, '2024-01-20 15:20:00', 'Enfant de 5 ans, fièvre et toux.', 
 'Antibiotiques, antipyrétiques.', 38.5, '100/60', 95, false, 
 'consultation_normale', NULL, NULL, 'Liquides abondants', 'Domicile', true),

-- Consultation 7
(7, 7, 1, 7, '2024-01-21 13:10:00', 'Douleurs articulaires, possible arthrose.', 
 'Anti-inflammatoires, kinésithérapie.', 36.7, '118/78', 75, false, 
 'consultation_normale', NULL, NULL, 'Alimentation anti-inflammatoire', 'Domicile', true),

-- Consultation 8
(8, 8, 2, 8, '2024-01-22 09:00:00', 'Problèmes de vision, examen ophtalmologique.', 
 'Nouvelle prescription de lunettes.', 36.8, '122/82', 68, false, 
 'consultation_normale', NULL, NULL, 'Alimentation normale', 'Domicile', true),

-- Consultation 9
(9, 9, 1, 9, '2024-01-23 16:30:00', 'Fracture du bras, contrôle post-opératoire.', 
 'Physiothérapie, rééducation.', 37.1, '135/88', 80, false, 
 'consultation_normale', NULL, NULL, 'Alimentation riche en calcium', 'Domicile', true),

-- Consultation 10
(10, 10, 2, 10, '2024-01-24 12:15:00', 'Problèmes thyroïdiens, dosage hormonal.', 
 'Ajustement du traitement thyroïdien.', 36.6, '128/84', 76, false, 
 'consultation_normale', NULL, NULL, 'Alimentation équilibrée', 'Domicile', true);

-- Réinitialiser la séquence
SELECT setval('patient_consultation_id_seq', (SELECT MAX(id) FROM patient_consultation));

-- ============================================================================
-- 6. TABLE DE LIAISON: patient_consultation_actes
-- ============================================================================
INSERT INTO patient_consultation_actes (id, consultation_id, acte_id) VALUES
-- Consultation 1 (Hassan Alami)
(1, 1, 1),   -- Consultation générale
(2, 1, 10),  -- Électrocardiogramme

-- Consultation 2 (Fatima Bennani)
(3, 2, 2),   -- Consultation spécialisée
(4, 2, 17),  -- Échographie pelvienne

-- Consultation 3 (Ahmed Tazi)
(5, 3, 3),   -- Consultation urgente
(6, 3, 8),   -- IRM cérébrale
(7, 3, 1),   -- Consultation générale

-- Consultation 4 (Samira El Fassi)
(8, 4, 2),   -- Consultation spécialisée
(9, 4, 13),  -- Biopsie

-- Consultation 5 (Mohamed Idrissi)
(10, 5, 1),  -- Consultation générale
(11, 5, 11), -- Analyse sanguine complète

-- Consultation 6 (Khadija Amrani)
(12, 6, 2),  -- Consultation spécialisée
(13, 6, 12), -- Analyse urinaire

-- Consultation 7 (Youssef Senhaji)
(14, 7, 1),  -- Consultation générale
(15, 7, 6),  -- Radiographie membre

-- Consultation 8 (Leila Ouazzani)
(16, 8, 2),  -- Consultation spécialisée

-- Consultation 9 (Karim Naciri)
(17, 9, 1),  -- Consultation générale
(18, 9, 7),  -- Radiographie membre

-- Consultation 10 (Zineb Khalil)
(19, 10, 2), -- Consultation spécialisée
(20, 10, 11); -- Analyse sanguine complète

-- ============================================================================
-- 7. TABLE: patient_appointment (Rendez-vous)
-- ============================================================================
INSERT INTO patient_appointment (
    id, patient_id, medecin_id, date_heure, 
    statut, motif, nom, prenom, telephone, email, mode
) VALUES
-- Rendez-vous futurs
(1, 1, 1, '2024-02-15 09:30:00', 'à venir', 'Contrôle tension artérielle', 'Alami', 'Hassan', '+212612345678', 'hassan.alami@email.ma', 'direct'),
(2, 2, 2, '2024-02-16 10:15:00', 'à venir', 'Consultation de routine', 'Bennani', 'Fatima', '+212623456789', 'fatima.bennani@email.ma', 'direct'),
(3, 3, 1, '2024-02-17 14:00:00', 'à venir', 'Contrôle post-hospitalisation', 'Tazi', 'Ahmed', '+212634567890', 'ahmed.tazi@email.ma', 'direct'),
(4, 4, 2, '2024-02-18 11:30:00', 'à venir', 'Suivi dermatologique', 'El Fassi', 'Samira', '+212645678901', 'samira.elfassi@email.ma', 'direct'),
(5, 5, 1, '2024-02-19 08:45:00', 'à venir', 'Contrôle diabète', 'Idrissi', 'Mohamed', '+212656789012', 'mohamed.idrissi@email.ma', 'direct'),
(6, 6, 2, '2024-02-20 15:20:00', 'à venir', 'Contrôle pédiatrique', 'Amrani', 'Khadija', '+212667890123', 'khadija.amrani@email.ma', 'direct'),
(7, 7, 1, '2024-02-21 13:10:00', 'à venir', 'Suivi rhumatologique', 'Senhaji', 'Youssef', '+212678901234', 'youssef.senhaji@email.ma', 'direct'),
(8, 8, 2, '2024-02-22 09:00:00', 'à venir', 'Contrôle ophtalmologique', 'Ouazzani', 'Leila', '+212689012345', 'leila.ouazzani@email.ma', 'direct'),
(9, 9, 1, '2024-02-23 16:30:00', 'à venir', 'Contrôle orthopédique', 'Naciri', 'Karim', '+212690123456', 'karim.naciri@email.ma', 'direct'),
(10, 10, 2, '2024-02-24 12:15:00', 'à venir', 'Contrôle endocrinologique', 'Khalil', 'Zineb', '+212601234567', 'zineb.khalil@email.ma', 'direct');

-- Réinitialiser la séquence
SELECT setval('patient_appointment_id_seq', (SELECT MAX(id) FROM patient_appointment));

-- ============================================================================
-- 8. TABLE: patient_invoice (Factures)
-- ============================================================================
INSERT INTO patient_invoice (
    id, patient_id, consultation_id, invoice_number, invoice_date, 
    total_amount, paid_amount, status, created_date, notes
) VALUES
-- Factures des consultations
(1, 1, 1, 'FACT-2024-001', '2024-01-15', 300.00, 300.00, 'paid', NOW(), 'Facture consultation générale'),
(2, 2, 2, 'FACT-2024-002', '2024-01-16', 650.00, 650.00, 'paid', NOW(), 'Facture consultation spécialisée'),
(3, 4, 4, 'FACT-2024-003', '2024-01-18', 550.00, 550.00, 'paid', NOW(), 'Facture consultation dermatologie'),
(4, 5, 5, 'FACT-2024-004', '2024-01-19', 380.00, 380.00, 'paid', NOW(), 'Facture consultation diabétologie'),
(5, 6, 6, 'FACT-2024-005', '2024-01-20', 250.00, 250.00, 'paid', NOW(), 'Facture consultation pédiatrique'),
(6, 7, 7, 'FACT-2024-006', '2024-01-21', 270.00, 270.00, 'paid', NOW(), 'Facture consultation rhumatologie'),
(7, 8, 8, 'FACT-2024-007', '2024-01-22', 300.00, 300.00, 'paid', NOW(), 'Facture consultation ophtalmologie'),
(8, 9, 9, 'FACT-2024-008', '2024-01-23', 370.00, 370.00, 'paid', NOW(), 'Facture consultation orthopédie'),
(9, 10, 10, 'FACT-2024-009', '2024-01-24', 480.00, 480.00, 'paid', NOW(), 'Facture consultation endocrinologie');

-- Réinitialiser la séquence
SELECT setval('patient_invoice_id_seq', (SELECT MAX(id) FROM patient_invoice));

-- ============================================================================
-- 9. TABLE: patient_billinghistory (Historique de facturation)
-- ============================================================================
INSERT INTO patient_billinghistory (
    id, patient_id, generated_by_id, generated_at, total_amount, billing_date, notes
) VALUES
-- Historique des paiements
(1, 1, 1, NOW(), 300.00, '2024-01-15', 'Paiement consultation générale + ECG'),
(2, 2, 1, NOW(), 650.00, '2024-01-16', 'Paiement consultation spécialisée + échographie'),
(3, 4, 1, NOW(), 550.00, '2024-01-18', 'Paiement consultation + biopsie'),
(4, 5, 1, NOW(), 380.00, '2024-01-19', 'Paiement consultation + analyses'),
(5, 6, 1, NOW(), 250.00, '2024-01-20', 'Paiement consultation pédiatrique'),
(6, 7, 1, NOW(), 270.00, '2024-01-21', 'Paiement consultation + radiographie'),
(7, 8, 1, NOW(), 300.00, '2024-01-22', 'Paiement consultation ophtalmologique'),
(8, 9, 1, NOW(), 370.00, '2024-01-23', 'Paiement consultation + radiographie'),
(9, 10, 1, NOW(), 480.00, '2024-01-24', 'Paiement consultation + analyses');

-- Réinitialiser la séquence
SELECT setval('patient_billinghistory_id_seq', (SELECT MAX(id) FROM patient_billinghistory));

-- ============================================================================
-- 10. TABLE: patient_medicationprescription (Prescriptions de médicaments)
-- ============================================================================
-- Note: Cette table nécessite des produits de pharmacie qui seront créés plus tard
-- Les prescriptions seront ajoutées après la création des données de pharmacie

COMMIT;

-- ============================================================================
-- MESSAGE DE CONFIRMATION
-- ============================================================================
SELECT 'DONNEES PATIENT CREEES AVEC SUCCES!' as message;

-- ============================================================================
-- RÉSUMÉ DES DONNÉES CRÉÉES
-- ============================================================================
SELECT 
    'RÉSUMÉ DES DONNÉES CRÉÉES' as titre,
    (SELECT COUNT(*) FROM patient_acte) as "Actes médicaux",
    (SELECT COUNT(*) FROM patient_emergencycontact) as "Contacts d'urgence", 
    (SELECT COUNT(*) FROM patient_patient) as "Patients",
    (SELECT COUNT(*) FROM patient_consultation) as "Consultations",
    (SELECT COUNT(*) FROM patient_appointment) as "Rendez-vous",
    (SELECT COUNT(*) FROM patient_invoice) as "Factures",
    (SELECT COUNT(*) FROM patient_billinghistory) as "Historique facturation",
    (SELECT COUNT(*) FROM patient_medicationprescription) as "Prescriptions";
