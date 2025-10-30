-- ============================================================================
-- Script SQL pour remplir les tables du module HR (PostgreSQL)
-- ============================================================================


BEGIN;

-- ============================================================================
-- 1. TABLE: hr_speciality (Spécialités médicales)
-- ============================================================================
INSERT INTO hr_speciality (id, name) VALUES
(1, 'Cardiologie'),
(2, 'Gynécologie'),
(3, 'Neurologie'),
(4, 'Dermatologie'),
(5, 'Diabétologie'),
(6, 'Pédiatrie'),
(7, 'Rhumatologie'),
(8, 'Ophtalmologie'),
(9, 'Orthopédie'),
(10, 'Endocrinologie'),
(11, 'Pneumologie'),
(12, 'Gastro-entérologie'),
(13, 'Psychiatrie'),
(14, 'Oncologie'),
(15, 'Urologie'),
(16, 'ORL (Oto-Rhino-Laryngologie)'),
(17, 'Néphrologie'),
(18, 'Radiologie'),
(19, 'Anesthésiologie'),
(20, 'Médecine générale'),
(21, 'Chirurgie générale'),
(22, 'Pharmacie'),
(23, 'Soins infirmiers'),
(24, 'Kinésithérapie'),
(25, 'Nutrition et diététique');

-- Réinitialiser la séquence
SELECT setval('hr_speciality_id_seq', (SELECT MAX(id) FROM hr_speciality));

-- ============================================================================
-- 2. TABLE: hr_department (Départements)
-- ============================================================================
INSERT INTO hr_department (id, name, description, parent_id, created_at, updated_at) VALUES
-- Départements principaux
(1, 'Direction Générale', 'Direction générale de l''établissement', NULL, NOW(), NOW()),
(2, 'Département Médical', 'Services médicaux et soins', NULL, NOW(), NOW()),
(3, 'Département Administratif', 'Services administratifs', NULL, NOW(), NOW()),
(4, 'Département Technique', 'Services techniques et maintenance', NULL, NOW(), NOW()),
(5, 'Département Logistique', 'Logistique et approvisionnement', NULL, NOW(), NOW()),

-- Sous-départements du Département Médical
(6, 'Service de Cardiologie', 'Consultations et soins cardiologiques', 2, NOW(), NOW()),
(7, 'Service de Pédiatrie', 'Consultations et soins pédiatriques', 2, NOW(), NOW()),
(8, 'Service de Chirurgie', 'Interventions chirurgicales', 2, NOW(), NOW()),
(9, 'Service des Urgences', 'Prise en charge des urgences', 2, NOW(), NOW()),
(10, 'Service de Radiologie', 'Imagerie médicale', 2, NOW(), NOW()),

-- Sous-départements du Département Administratif
(11, 'Ressources Humaines', 'Gestion du personnel', 3, NOW(), NOW()),
(12, 'Comptabilité', 'Gestion financière et comptable', 3, NOW(), NOW()),
(13, 'Accueil et Admission', 'Accueil des patients', 3, NOW(), NOW()),

-- Sous-départements du Département Technique
(14, 'Maintenance', 'Entretien des équipements', 4, NOW(), NOW()),
(15, 'Informatique', 'Support informatique et SI', 4, NOW(), NOW()),

-- Sous-départements du Département Logistique
(16, 'Pharmacie', 'Gestion des médicaments', 5, NOW(), NOW()),
(17, 'Approvisionnement', 'Achats et stocks', 5, NOW(), NOW()),
(18, 'Restauration', 'Service de restauration', 5, NOW(), NOW());

-- Réinitialiser la séquence
SELECT setval('hr_department_id_seq', (SELECT MAX(id) FROM hr_department));

-- ============================================================================
-- 3. TABLE: hr_position (Postes/Fonctions)
-- ============================================================================
INSERT INTO hr_position (id, name, description, created_at, updated_at) VALUES
(1, 'Directeur Général', 'Direction générale de l''établissement', NOW(), NOW()),
(2, 'Directeur Médical', 'Direction des services médicaux', NOW(), NOW()),
(3, 'Directeur Administratif', 'Direction des services administratifs', NOW(), NOW()),
(4, 'Médecin Chef de Service', 'Responsable d''un service médical', NOW(), NOW()),
(5, 'Médecin Spécialiste', 'Médecin spécialisé dans un domaine', NOW(), NOW()),
(6, 'Médecin Généraliste', 'Médecin de médecine générale', NOW(), NOW()),
(7, 'Infirmier(ère) Chef', 'Responsable du personnel infirmier', NOW(), NOW()),
(8, 'Infirmier(ère)', 'Soins infirmiers aux patients', NOW(), NOW()),
(9, 'Aide-soignant(e)', 'Assistance aux soins', NOW(), NOW()),
(10, 'Pharmacien Chef', 'Responsable de la pharmacie', NOW(), NOW()),
(11, 'Pharmacien', 'Gestion des médicaments', NOW(), NOW()),
(12, 'Préparateur en pharmacie', 'Préparation des médicaments', NOW(), NOW()),
(13, 'Kinésithérapeute', 'Rééducation fonctionnelle', NOW(), NOW()),
(14, 'Radiologue', 'Imagerie médicale', NOW(), NOW()),
(15, 'Technicien de radiologie', 'Assistance radiologie', NOW(), NOW()),
(16, 'Secrétaire Médicale', 'Secrétariat médical', NOW(), NOW()),
(17, 'Responsable RH', 'Gestion des ressources humaines', NOW(), NOW()),
(18, 'Assistant(e) RH', 'Assistance RH', NOW(), NOW()),
(19, 'Chef Comptable', 'Responsable comptabilité', NOW(), NOW()),
(20, 'Comptable', 'Gestion comptable', NOW(), NOW()),
(21, 'Agent d''accueil', 'Accueil des patients', NOW(), NOW()),
(22, 'Technicien de maintenance', 'Maintenance des équipements', NOW(), NOW()),
(23, 'Informaticien', 'Support informatique', NOW(), NOW()),
(24, 'Agent de sécurité', 'Sécurité de l''établissement', NOW(), NOW()),
(25, 'Agent d''entretien', 'Nettoyage et entretien', NOW(), NOW());

-- Réinitialiser la séquence
SELECT setval('hr_position_id_seq', (SELECT MAX(id) FROM hr_position));

-- ============================================================================
-- 4. TABLE: hr_contracttype (Types de contrat)
-- ============================================================================
INSERT INTO hr_contracttype (id, name, description, created_at, updated_at) VALUES
(1, 'CDI', 'Contrat à Durée Indéterminée', NOW(), NOW()),
(2, 'CDD', 'Contrat à Durée Déterminée', NOW(), NOW()),
(3, 'Stage', 'Convention de stage', NOW(), NOW()),
(4, 'Interim', 'Contrat d''intérim', NOW(), NOW()),
(5, 'Vacation', 'Contrat de vacation', NOW(), NOW()),
(6, 'Apprentissage', 'Contrat d''apprentissage', NOW(), NOW());

-- Réinitialiser la séquence
SELECT setval('hr_contracttype_id_seq', (SELECT MAX(id) FROM hr_contracttype));

-- ============================================================================
-- 5. TABLE: hr_socialcontribution (Cotisations sociales)
-- ============================================================================
INSERT INTO hr_socialcontribution (id, label, rate, ceiling) VALUES
(1, 'CNSS', 3.96, 6000.00),
(2, 'AMO', 2.26, NULL),
(3, 'CIMR', 3.00, NULL),
(4, 'Mutuelle', 2.50, NULL);

-- Réinitialiser la séquence
SELECT setval('hr_socialcontribution_id_seq', (SELECT MAX(id) FROM hr_socialcontribution));

-- ============================================================================
-- 6. TABLE: hr_prime (Primes)
-- ============================================================================
INSERT INTO hr_prime (id, libelle, rate, amount) VALUES
(1, 'Prime de transport', NULL, 300.00),
(2, 'Prime de repas', NULL, 300.00),
(3, 'Prime de logement', NULL, 500.00),
(4, 'Prime d''ancienneté', NULL, NULL),
(5, 'Prime de rendement', 10.00, NULL),
(6, 'Prime de responsabilité', NULL, 1000.00),
(7, 'Prime de garde', NULL, 800.00),
(8, 'Prime de risque', 5.00, NULL),
(9, 'Prime de disponibilité', NULL, 600.00),
(10, 'Prime exceptionnelle', NULL, NULL);

-- Réinitialiser la séquence
SELECT setval('hr_prime_id_seq', (SELECT MAX(id) FROM hr_prime));

-- ============================================================================
-- 7. TABLE: hr_modelcalcul (Modèles de calcul de paie)
-- ============================================================================
INSERT INTO hr_modelcalcul (id, libelle) VALUES
(1, 'Modèle Standard Médecin'),
(2, 'Modèle Standard Personnel Soignant'),
(3, 'Modèle Standard Administratif'),
(4, 'Modèle Cadre Supérieur'),
(5, 'Modèle Stage/Apprenti');

-- Réinitialiser la séquence
SELECT setval('hr_modelcalcul_id_seq', (SELECT MAX(id) FROM hr_modelcalcul));

-- ============================================================================
-- 8. TABLE: hr_modelcalcul_social_contributions (Relation M2M)
-- ============================================================================
INSERT INTO hr_modelcalcul_social_contributions (id, modelcalcul_id, socialcontribution_id) VALUES
-- Modèle Standard Médecin
(1, 1, 1), -- CNSS
(2, 1, 2), -- AMO
(3, 1, 3), -- CIMR
(4, 1, 4), -- Mutuelle

-- Modèle Standard Personnel Soignant
(5, 2, 1), -- CNSS
(6, 2, 2), -- AMO
(7, 2, 4), -- Mutuelle

-- Modèle Standard Administratif
(8, 3, 1), -- CNSS
(9, 3, 2), -- AMO

-- Modèle Cadre Supérieur
(10, 4, 1), -- CNSS
(11, 4, 2), -- AMO
(12, 4, 3), -- CIMR
(13, 4, 4), -- Mutuelle

-- Modèle Stage/Apprenti
(14, 5, 2); -- AMO seulement

-- Réinitialiser la séquence
SELECT setval('hr_modelcalcul_social_contributions_id_seq', (SELECT MAX(id) FROM hr_modelcalcul_social_contributions));

-- ============================================================================
-- 9. TABLE: hr_modelcalcul_primes (Relation M2M)
-- ============================================================================
INSERT INTO hr_modelcalcul_primes (id, modelcalcul_id, prime_id) VALUES
-- Modèle Standard Médecin
(1, 1, 1), -- Transport
(2, 1, 2), -- Repas
(3, 1, 4), -- Ancienneté
(4, 1, 6), -- Responsabilité
(5, 1, 7), -- Garde

-- Modèle Standard Personnel Soignant
(6, 2, 1), -- Transport
(7, 2, 2), -- Repas
(8, 2, 4), -- Ancienneté

-- Modèle Standard Administratif
(9, 3, 1), -- Transport
(10, 3, 2), -- Repas
(11, 3, 4), -- Ancienneté

-- Modèle Cadre Supérieur
(12, 4, 1), -- Transport
(13, 4, 2), -- Repas
(14, 4, 3), -- Logement
(15, 4, 4), -- Ancienneté
(16, 4, 6), -- Responsabilité

-- Modèle Stage/Apprenti
(17, 5, 1); -- Transport seulement

-- Réinitialiser la séquence
SELECT setval('hr_modelcalcul_primes_id_seq', (SELECT MAX(id) FROM hr_modelcalcul_primes));

-- ============================================================================
-- 10. TABLE: hr_child (Enfants des employés)
-- ============================================================================
INSERT INTO hr_child (id, name, gender, birth_date, is_scolarise, created_at, updated_at) VALUES
(1, 'Yasmine Bennani', 'F', '2015-03-15', true, NOW(), NOW()),
(2, 'Adam Bennani', 'M', '2018-06-20', true, NOW(), NOW()),
(3, 'Sara El Fassi', 'F', '2016-09-10', true, NOW(), NOW()),
(4, 'Omar Idrissi', 'M', '2017-12-05', true, NOW(), NOW()),
(5, 'Amina Idrissi', 'F', '2020-04-18', false, NOW(), NOW()),
(6, 'Mehdi Amrani', 'M', '2014-07-22', true, NOW(), NOW()),
(7, 'Leila Benkirane', 'F', '2016-11-30', true, NOW(), NOW()),
(8, 'Youssef Benkirane', 'M', '2019-02-14', false, NOW(), NOW()),
(9, 'Khalid Senhaji', 'M', '2015-05-25', true, NOW(), NOW()),
(10, 'Fatima Ouazzani', 'F', '2017-08-12', true, NOW(), NOW()),
(11, 'Hassan Naciri', 'M', '2018-10-03', true, NOW(), NOW()),
(12, 'Nadia Khalil', 'F', '2016-01-20', true, NOW(), NOW()),
(13, 'Karim Berrada', 'M', '2015-12-08', true, NOW(), NOW()),
(14, 'Amal Ziani', 'F', '2019-06-15', false, NOW(), NOW()),
(15, 'Rachid Mansouri', 'M', '2017-04-28', true, NOW(), NOW());

-- Réinitialiser la séquence
SELECT setval('hr_child_id_seq', (SELECT MAX(id) FROM hr_child));

-- ============================================================================
-- 11. TABLE: hr_employee (Employés)
-- ============================================================================
INSERT INTO hr_employee (
    id, employee_id, national_id, full_name, birth_date, photo, marital_status, 
    gender, email, personal_phone, work_phone, personal_address, work_address,
    children_count, status, position_id, department_id, speciality_id,
    work_certificate, legalized_contract, doctor_agreement, temporary_agreement,
    base_salary, model_calcul_id, career_evolution, skills, is_supervisor, supervisor_id
) VALUES
-- Directeur Général
(1, 'EMP-001', 'AB123456', 'Dr. Mohammed Bennani', '1975-03-15', NULL, 'M', 'M',
 'm.bennani@oralys.ma', '+212661234567', '+212522334455', 
 '15 Rue des Hôpitaux, Casablanca', 'Direction Générale, ORALYS',
 2, 'A', 1, 1, 20, NULL, NULL, NULL, NULL,
 45000.00, 4, 'Directeur depuis 2015', 'Management, Gestion hospitalière, Leadership', 1, NULL),

-- Directeur Médical
(2, 'EMP-002', 'CD234567', 'Dr. Karim El Fassi', '1978-06-20', NULL, 'M', 'M',
 'k.elfassi@oralys.ma', '+212662345678', '+212537445566',
 '22 Avenue Hassan II, Rabat', 'Direction Médicale, ORALYS',
 1, 'A', 2, 2, 1, NULL, NULL, NULL, NULL,
 40000.00, 4, 'Chef de service cardiologie puis Directeur médical', 'Cardiologie, Gestion médicale', 1, 1),

-- Médecins spécialistes
(3, 'EMP-003', 'EF345678', 'Dr. Nadia Amrani', '1980-09-10', NULL, 'F', 'F',
 'n.amrani@oralys.ma', '+212663456789', '+212524556677',
 '45 Rue de Fès, Marrakech', 'Service de Neurologie, ORALYS',
 0, 'A', 5, 2, 3, NULL, NULL, NULL, NULL,
 25000.00, 1, NULL, 'Neurologie, IRM, Diagnostic', 0, 2),

(4, 'EMP-004', 'GH456789', 'Dr. Rachid Senhaji', '1982-12-05', NULL, 'M', 'M',
 'r.senhaji@oralys.ma', '+212664567890', '+212535667788',
 '12 Boulevard Mohamed V, Fès', 'Service de Dermatologie, ORALYS',
 2, 'A', 5, 2, 4, NULL, NULL, NULL, NULL,
 24000.00, 1, NULL, 'Dermatologie, Allergologie', 0, 2),

(5, 'EMP-005', 'IJ567890', 'Dr. Leila Idrissi', '1985-04-18', NULL, 'F', 'F',
 'l.idrissi@oralys.ma', '+212665678901', '+212539778899',
 '8 Rue Ibn Batouta, Tanger', 'Service de Gynécologie, ORALYS',
 0, 'A', 5, 2, 2, NULL, NULL, NULL, NULL,
 26000.00, 1, NULL, 'Gynécologie, Obstétrique', 0, 2),

-- Personnel infirmier
(6, 'EMP-006', 'KL678901', 'Fatima Amrani', '1988-07-22', NULL, 'F', 'F',
 'f.amrani@oralys.ma', '+212666789012', '+212528889900',
 '30 Avenue de la Liberté, Agadir', 'Service de Pédiatrie, ORALYS',
 1, 'A', 7, 7, 23, NULL, NULL, NULL, NULL,
 12000.00, 2, 'Infirmière puis Chef infirmière', 'Soins pédiatriques, Management', 1, 2),

(7, 'EMP-007', 'MN789012', 'Hassan Benkirane', '1990-11-30', NULL, 'M', 'M',
 'h.benkirane@oralys.ma', '+212667890123', '+212535990011',
 '18 Rue Al Massira, Meknès', 'Service des Urgences, ORALYS',
 2, 'A', 8, 9, 23, NULL, NULL, NULL, NULL,
 10000.00, 2, NULL, 'Soins d''urgence, Réanimation', 0, 6),

(8, 'EMP-008', 'OP890123', 'Samira Chraibi', '1992-02-14', NULL, 'F', 'F',
 's.chraibi@oralys.ma', '+212668901234', '+212536001122',
 '25 Boulevard Zerktouni, Oujda', 'Service de Cardiologie, ORALYS',
 0, 'A', 8, 6, 23, NULL, NULL, NULL, NULL,
 9500.00, 2, NULL, 'Soins cardiologiques', 0, 6),

(9, 'EMP-009', 'QR901234', 'Youssef Senhaji', '1993-05-25', NULL, 'M', 'M',
 'y.senhaji@oralys.ma', '+212669012345', '+212522112233',
 '40 Rue Oued Sebou, Casablanca', 'Service de Chirurgie, ORALYS',
 1, 'A', 8, 8, 23, NULL, NULL, NULL, NULL,
 9800.00, 2, NULL, 'Soins chirurgicaux', 0, 6),

-- Pharmaciens
(10, 'EMP-010', 'ST012345', 'Dr. Zineb Ouazzani', '1986-08-12', NULL, 'F', 'F',
 'z.ouazzani@oralys.ma', '+212660123456', '+212537223344',
 '5 Avenue des FAR, Rabat', 'Pharmacie, ORALYS',
 1, 'A', 10, 16, 22, NULL, NULL, NULL, NULL,
 18000.00, 3, 'Pharmacienne chef depuis 2018', 'Pharmacie clinique, Gestion des stocks', 1, 1),

(11, 'EMP-011', 'UV123456', 'Mehdi Naciri', '1991-10-03', NULL, 'M', 'M',
 'm.naciri@oralys.ma', '+212661122334', '+212524334455',
 '33 Rue Yacoub El Mansour, Marrakech', 'Pharmacie, ORALYS',
 1, 'A', 11, 16, 22, NULL, NULL, NULL, NULL,
 13000.00, 3, NULL, 'Pharmacie hospitalière', 0, 10),

-- Personnel administratif
(12, 'EMP-012', 'WX234567', 'Salma Berrada', '1987-01-20', NULL, 'F', 'F',
 's.berrada@oralys.ma', '+212662233445', '+212535445566',
 '20 Rue de la Paix, Fès', 'Ressources Humaines, ORALYS',
 1, 'A', 17, 11, NULL, NULL, NULL, NULL, NULL,
 15000.00, 3, 'Responsable RH', 'GRH, Recrutement, Paie', 1, 3),

(13, 'EMP-013', 'YZ345678', 'Karim Ziani', '1989-12-08', NULL, 'M', 'M',
 'k.ziani@oralys.ma', '+212663344556', '+212539556677',
 '10 Boulevard Mohammed VI, Tanger', 'Comptabilité, ORALYS',
 1, 'A', 19, 12, NULL, NULL, NULL, NULL, NULL,
 14000.00, 3, 'Chef comptable', 'Comptabilité, Fiscalité', 1, 3),

(14, 'EMP-014', 'AB456789', 'Nadia Mansouri', '1994-06-15', NULL, 'F', 'F',
 'n.mansouri@oralys.ma', '+212664455667', '+212528667788',
 '7 Rue Oqba, Agadir', 'Accueil et Admission, ORALYS',
 0, 'A', 21, 13, NULL, NULL, NULL, NULL, NULL,
 7500.00, 3, NULL, 'Accueil, Gestion des admissions', 0, 3),

(15, 'EMP-015', 'CD567890', 'Omar Rami', '1995-04-28', NULL, 'M', 'M',
 'o.rami@oralys.ma', '+212665566778', '+212535778899',
 '14 Avenue Allal Ben Abdellah, Meknès', 'Accueil et Admission, ORALYS',
 0, 'A', 21, 13, NULL, NULL, NULL, NULL, NULL,
 7500.00, 3, NULL, 'Accueil, Orientation patients', 0, 3),

-- Personnel technique
(16, 'EMP-016', 'EF678901', 'Hicham Fassi', '1988-09-11', NULL, 'M', 'M',
 'h.fassi@oralys.ma', '+212666677889', '+212522998877',
 '50 Rue Prince Moulay Abdellah, Casablanca', 'Informatique, ORALYS',
 2, 'A', 23, 15, NULL, NULL, NULL, NULL, NULL,
 11000.00, 3, NULL, 'Systèmes d''information, Réseau', 0, 3),

(17, 'EMP-017', 'GH789012', 'Laila Tazi', '1990-12-05', NULL, 'F', 'F',
 'l.tazi@oralys.ma', '+212667788990', '+212537887766',
 '28 Rue Patrice Lumumba, Rabat', 'Maintenance, ORALYS',
 1, 'A', 22, 14, NULL, NULL, NULL, NULL, NULL,
 9500.00, 3, NULL, 'Maintenance biomédicale', 0, 3),

-- Stagiaires
(18, 'EMP-018', 'IJ890123', 'Sara Alaoui', '1999-03-20', NULL, 'S', 'F',
 's.alaoui@oralys.ma', '+212668899001', '+212524776655',
 '15 Rue Souika, Marrakech', 'Service de Cardiologie, ORALYS',
 0, 'A', 8, 6, 23, NULL, NULL, NULL, NULL,
 3500.00, 5, NULL, 'Formation en soins infirmiers', 0, 8),

(19, 'EMP-019', 'KL901234', 'Amine Berrada', '1998-07-10', NULL, 'S', 'M',
 'a.berrada@oralys.ma', '+212669900112', '+212535665544',
 '9 Avenue Hassan II, Fès', 'Pharmacie, ORALYS',
 0, 'A', 12, 16, 22, NULL, NULL, NULL, NULL,
 3000.00, 5, NULL, 'Stage en pharmacie', 0, 11),

(20, 'EMP-020', 'MN012345', 'Soumaya Mansouri', '2000-11-18', NULL, 'S', 'F',
 's.mansouri@oralys.ma', '+212660011223', '+212539554433',
 '6 Rue de Tétouan, Tanger', 'Ressources Humaines, ORALYS',
 0, 'A', 18, 11, NULL, NULL, NULL, NULL, NULL,
 3200.00, 5, NULL, 'Stage RH', 0, 12);

-- Réinitialiser la séquence
SELECT setval('hr_employee_id_seq', (SELECT MAX(id) FROM hr_employee));

-- ============================================================================
-- 12. TABLE: hr_employee_children (Relation M2M Employés-Enfants)
-- ============================================================================
INSERT INTO hr_employee_children (id, employee_id, child_id) VALUES
(1, 1, 1),   -- Mohammed Bennani -> Yasmine Bennani
(2, 1, 2),   -- Mohammed Bennani -> Adam Bennani
(3, 4, 3),   -- Rachid Senhaji -> Sara El Fassi
(4, 4, 9),   -- Rachid Senhaji -> Khalid Senhaji
(5, 2, 4),   -- Karim El Fassi -> Omar Idrissi
(6, 6, 5),   -- Fatima Amrani -> Amina Idrissi
(7, 6, 6),   -- Fatima Amrani -> Mehdi Amrani
(8, 7, 7),   -- Hassan Benkirane -> Leila Benkirane
(9, 7, 8),   -- Hassan Benkirane -> Youssef Benkirane
(10, 9, 10), -- Youssef Senhaji -> Fatima Ouazzani
(11, 10, 11),-- Zineb Ouazzani -> Hassan Naciri
(12, 11, 12),-- Mehdi Naciri -> Nadia Khalil
(13, 12, 13),-- Salma Berrada -> Karim Berrada
(14, 13, 14),-- Karim Ziani -> Amal Ziani
(15, 16, 15);-- Hicham Fassi -> Rachid Mansouri

-- Réinitialiser la séquence
SELECT setval('hr_employee_children_id_seq', (SELECT MAX(id) FROM hr_employee_children));

-- ============================================================================
-- 13. TABLE: hr_contract (Contrats)
-- ============================================================================
INSERT INTO hr_contract (id, employee_id, start_date, end_date, contract_type_id, created_at, updated_at) VALUES
(1, 1, '2015-01-15', NULL, 1, NOW(), NOW()),  -- CDI
(2, 2, '2016-03-01', NULL, 1, NOW(), NOW()),  -- CDI
(3, 3, '2018-06-15', NULL, 1, NOW(), NOW()),  -- CDI
(4, 4, '2019-09-01', NULL, 1, NOW(), NOW()),  -- CDI
(5, 5, '2020-02-01', NULL, 1, NOW(), NOW()),  -- CDI
(6, 6, '2017-04-10', NULL, 1, NOW(), NOW()),  -- CDI
(7, 7, '2019-11-15', NULL, 1, NOW(), NOW()),  -- CDI
(8, 8, '2020-05-20', NULL, 1, NOW(), NOW()),  -- CDI
(9, 9, '2021-01-10', NULL, 1, NOW(), NOW()),  -- CDI
(10, 10, '2018-03-01', NULL, 1, NOW(), NOW()), -- CDI
(11, 11, '2020-07-15', NULL, 1, NOW(), NOW()), -- CDI
(12, 12, '2019-02-01', NULL, 1, NOW(), NOW()), -- CDI
(13, 13, '2020-04-15', NULL, 1, NOW(), NOW()), -- CDI
(14, 14, '2022-06-01', NULL, 1, NOW(), NOW()), -- CDI
(15, 15, '2022-06-01', NULL, 1, NOW(), NOW()), -- CDI
(16, 16, '2021-03-15', NULL, 1, NOW(), NOW()), -- CDI
(17, 17, '2021-08-01', NULL, 1, NOW(), NOW()), -- CDI
(18, 18, '2024-09-01', '2025-08-31', 3, NOW(), NOW()), -- Stage
(19, 19, '2024-09-01', '2025-08-31', 3, NOW(), NOW()), -- Stage
(20, 20, '2024-10-01', '2025-03-31', 3, NOW(), NOW()); -- Stage

-- Réinitialiser la séquence
SELECT setval('hr_contract_id_seq', (SELECT MAX(id) FROM hr_contract));

-- ============================================================================
-- 14. TABLE: hr_leavetype (Types de congés)
-- ============================================================================
INSERT INTO hr_leavetype (
    type_id, name, default_days, accrual_method, year, active,
    monday, tuesday, wednesday, thursday, friday, saturday, sunday, description
) VALUES
(1, 'Congé annuel', 22.00, 'annual', 2024, true, true, true, true, true, true, false, false, 
 'Congé annuel légal de 22 jours ouvrables par an'),

(2, 'Congé maladie', 90.00, 'annual', 2024, true, true, true, true, true, true, false, false,
 'Congé maladie sur présentation de certificat médical (max 90 jours/an)'),

(3, 'Congé maternité', 98.00, 'annual', 2024, true, true, true, true, true, true, true, true,
 'Congé de maternité de 14 semaines (98 jours)'),

(4, 'Congé paternité', 3.00, 'annual', 2024, true, true, true, true, true, true, false, false,
 'Congé de paternité de 3 jours'),

(5, 'Congé sans solde', NULL, 'annual', 2024, true, true, true, true, true, true, false, false,
 'Congé sans solde sur autorisation'),

(6, 'Congé exceptionnel', 5.00, 'annual', 2024, true, true, true, true, true, true, false, false,
 'Congé pour événements familiaux (mariage, décès, etc.)'),

(7, 'Récupération', NULL, 'monthly', 2024, true, true, true, true, true, true, false, false,
 'Jour de récupération pour heures supplémentaires'),

(8, 'Formation', NULL, 'annual', 2024, true, true, true, true, true, true, false, false,
 'Congé de formation professionnelle');

-- Réinitialiser la séquence
SELECT setval('hr_leavetype_type_id_seq', (SELECT MAX(type_id) FROM hr_leavetype));

COMMIT;

-- ============================================================================
-- Vérification des données insérées
-- ============================================================================
SELECT '=== RÉSUMÉ DES INSERTIONS MODULE HR ===' as info;
SELECT 'Nombre de spécialités: ' || COUNT(*) as resultat FROM hr_speciality;
SELECT 'Nombre de départements: ' || COUNT(*) as resultat FROM hr_department;
SELECT 'Nombre de postes: ' || COUNT(*) as resultat FROM hr_position;
SELECT 'Nombre de types de contrat: ' || COUNT(*) as resultat FROM hr_contracttype;
SELECT 'Nombre de cotisations sociales: ' || COUNT(*) as resultat FROM hr_socialcontribution;
SELECT 'Nombre de primes: ' || COUNT(*) as resultat FROM hr_prime;
SELECT 'Nombre de modèles de calcul: ' || COUNT(*) as resultat FROM hr_modelcalcul;
SELECT 'Nombre d''enfants: ' || COUNT(*) as resultat FROM hr_child;
SELECT 'Nombre d''employés: ' || COUNT(*) as resultat FROM hr_employee;
SELECT 'Nombre de contrats: ' || COUNT(*) as resultat FROM hr_contract;
SELECT 'Nombre de types de congés: ' || COUNT(*) as resultat FROM hr_leavetype;

-- Statistiques par département
SELECT '=== RÉPARTITION DES EMPLOYÉS PAR DÉPARTEMENT ===' as info;
SELECT d.name, COUNT(e.id) as nombre_employes
FROM hr_department d
LEFT JOIN hr_employee e ON e.department_id = d.id
GROUP BY d.id, d.name
ORDER BY nombre_employes DESC;

-- Statistiques par type de contrat
SELECT '=== RÉPARTITION DES CONTRATS PAR TYPE ===' as info;
SELECT ct.name, COUNT(c.id) as nombre_contrats
FROM hr_contracttype ct
LEFT JOIN hr_contract c ON c.contract_type_id = ct.id
GROUP BY ct.id, ct.name
ORDER BY nombre_contrats DESC;

-- Masse salariale
SELECT '=== MASSE SALARIALE ===' as info;
SELECT 'Masse salariale totale: ' || SUM(base_salary) || ' DH/mois' as resultat FROM hr_employee WHERE status = 'A';
SELECT 'Salaire moyen: ' || ROUND(AVG(base_salary), 2) || ' DH/mois' as resultat FROM hr_employee WHERE status = 'A';
SELECT 'Salaire minimum: ' || MIN(base_salary) || ' DH/mois' as resultat FROM hr_employee WHERE status = 'A';
SELECT 'Salaire maximum: ' || MAX(base_salary) || ' DH/mois' as resultat FROM hr_employee WHERE status = 'A';

