-- ============================================================================
-- Script SQL pour remplir les tables du module Recruitment (PostgreSQL)
-- ============================================================================
-- Ce script crée des données de test pour toutes les tables du module Recruitment
-- Base de données: PostgreSQL
-- ============================================================================

BEGIN;

-- Vider les tables recruitment existantes (dans l'ordre des dépendances)
TRUNCATE TABLE recruitment_evaluation CASCADE;
TRUNCATE TABLE recruitment_pointage CASCADE;
TRUNCATE TABLE recruitment_interview CASCADE;
TRUNCATE TABLE recruitment_application CASCADE;
TRUNCATE TABLE recruitment_candidate CASCADE;
TRUNCATE TABLE recruitment_offer CASCADE;

-- ============================================================================
-- 1. TABLE: recruitment_offer (Offres d'emploi)
-- ============================================================================
INSERT INTO recruitment_offer (
    id, title, description, publication_date, end_date, skills, profile,
    department_id, positions_available, archived
) VALUES
(1, 'Médecin Généraliste', 'Nous recherchons un médecin généraliste expérimenté pour rejoindre notre équipe médicale.', 
 '2024-01-01', '2024-03-31', 'Diplôme de médecine, 3 ans d''expérience minimum', 'Médecin généraliste diplômé avec excellentes compétences en communication', 
 1, 2, false),

(2, 'Infirmier(ère) en Cardiologie', 'Poste d''infirmier(ère) spécialisé(e) en cardiologie dans notre service.', 
 '2024-01-05', '2024-04-05', 'Diplôme d''infirmier, spécialisation cardiologie', 'Infirmier diplômé avec expérience en cardiologie', 
 1, 1, false),

(3, 'Pharmacien Hospitalier', 'Pharmacien pour gestion de la pharmacie hospitalière et conseils pharmaceutiques.', 
 '2024-01-10', '2024-04-10', 'Diplôme de pharmacien, connaissance réglementation', 'Pharmacien expérimenté avec sens de l''organisation', 
 3, 1, false),

(4, 'Technicien de Maintenance', 'Technicien pour la maintenance des équipements médicaux.', 
 '2024-01-15', '2024-04-15', 'Formation technique, électrotechnique', 'Technicien avec expérience en maintenance d''équipements médicaux', 
 5, 2, false),

(5, 'Responsable RH', 'Responsable des ressources humaines pour gestion du personnel.', 
 '2023-12-01', '2024-02-28', 'Diplôme RH, 5 ans d''expérience', 'Manager RH avec compétences en recrutement et gestion', 
 2, 1, true);

-- Réinitialiser la séquence
SELECT setval('recruitment_offer_id_seq', (SELECT MAX(id) FROM recruitment_offer));

-- ============================================================================
-- 2. TABLE: recruitment_candidate (Candidats)
-- ============================================================================
INSERT INTO recruitment_candidate (
    id, last_name, first_name, email, phone, birth_date, address, gender, linkedin_profile, archived
) VALUES
(1, 'Bennani', 'Ahmed', 'ahmed.bennani@email.ma', '+212612345678', '1990-05-15', 'Casablanca', 'M', 'https://linkedin.com/in/ahmed-bennani', false),
(2, 'El Amrani', 'Fatima', 'fatima.elamrani@email.ma', '+212623456789', '1992-08-20', 'Rabat', 'F', 'https://linkedin.com/in/fatima-elamrani', false),
(3, 'Chakir', 'Hassan', 'hassan.chakir@email.ma', '+212634567890', '1988-03-10', 'Fès', 'M', NULL, false),
(4, 'Tazi', 'Amina', 'amina.tazi@email.ma', '+212645678901', '1995-11-25', 'Marrakech', 'F', 'https://linkedin.com/in/amina-tazi', false),
(5, 'Idrissi', 'Mohammed', 'mohammed.idrissi@email.ma', '+212656789012', '1987-06-30', 'Tanger', 'M', NULL, false),
(6, 'Berrada', 'Nadia', 'nadia.berrada@email.ma', '+212667890123', '1993-09-05', 'Casablanca', 'F', 'https://linkedin.com/in/nadia-berrada', false),
(7, 'Alaoui', 'Youssef', 'youssef.alaoui@email.ma', '+212678901234', '1991-02-14', 'Rabat', 'M', NULL, false),
(8, 'Ziani', 'Sara', 'sara.ziani@email.ma', '+212689012345', '1994-07-18', 'Agadir', 'F', 'https://linkedin.com/in/sara-ziani', false),
(9, 'Fassi', 'Karim', 'karim.fassi@email.ma', '+212690123456', '1989-12-22', 'Fès', 'M', NULL, false),
(10, 'Lahlou', 'Leila', 'leila.lahlou@email.ma', '+212601234567', '1996-04-08', 'Casablanca', 'F', 'https://linkedin.com/in/leila-lahlou', false);

-- Réinitialiser la séquence
SELECT setval('recruitment_candidate_id_seq', (SELECT MAX(id) FROM recruitment_candidate));

-- ============================================================================
-- 3. TABLE: recruitment_application (Candidatures)
-- ============================================================================
INSERT INTO recruitment_application (
    id, offer_id, candidate_id, submission_date, source, always_available,
    availability_start, availability_end, status, archived
) VALUES
(1, 1, 1, '2024-01-10 09:00:00', 'LinkedIn', false, '2024-03-01', '2024-03-31', 'in_review', false),
(2, 1, 2, '2024-01-12 14:30:00', 'Site web', true, NULL, NULL, 'accepted', false),
(3, 2, 3, '2024-01-15 11:00:00', 'Email direct', false, '2024-02-15', NULL, 'in_review', false),
(4, 2, 4, '2024-01-18 16:00:00', 'LinkedIn', false, '2024-03-01', NULL, 'received', false),
(5, 3, 5, '2024-01-20 10:30:00', 'Site web', true, NULL, NULL, 'in_review', false),
(6, 3, 6, '2024-01-22 13:00:00', 'Recommandation', false, '2024-02-01', NULL, 'accepted', false),
(7, 4, 7, '2024-01-25 09:30:00', 'LinkedIn', true, NULL, NULL, 'in_review', false),
(8, 4, 8, '2024-01-28 15:00:00', 'Site web', false, '2024-03-15', NULL, 'received', false),
(9, 5, 9, '2023-12-15 10:00:00', 'Email direct', false, '2024-01-01', NULL, 'rejected', false),
(10, 5, 10, '2023-12-20 14:00:00', 'LinkedIn', true, NULL, NULL, 'rejected', false);

-- Réinitialiser la séquence
SELECT setval('recruitment_application_id_seq', (SELECT MAX(id) FROM recruitment_application));

-- ============================================================================
-- 4. TABLE: recruitment_interview (Entretiens)
-- ============================================================================
INSERT INTO recruitment_interview (
    id, application_id, start, "end", duration, location, videcall_url,
    organizer_id, description, notes, result, stage, archived
) VALUES
(1, 1, '2024-01-20 10:00:00', '2024-01-20 11:00:00', '01:00:00', 'Salle de réunion A', NULL,
 1, 'Premier entretien technique', 'Bon profil, compétences solides', 'positive', 'a', false),

(2, 2, '2024-01-22 14:00:00', '2024-01-22 15:30:00', '01:30:00', NULL, 'https://meet.google.com/abc-defg-hij',
 1, 'Entretien visio avec le chef de service', 'Excellente candidate, recrutement recommandé', 'positive', 'b', false),

(3, 3, '2024-01-25 09:00:00', '2024-01-25 10:00:00', '01:00:00', 'Bureau RH', NULL,
 2, 'Entretien RH préliminaire', 'Profil intéressant, à suivre', 'pending', 'a', false),

(4, 5, '2024-01-30 11:00:00', '2024-01-30 12:00:00', '01:00:00', 'Salle de réunion B', NULL,
 2, 'Entretien technique pharmacie', 'Compétences techniques validées', 'positive', 'a', false),

(5, 6, '2024-02-01 15:00:00', '2024-02-01 16:30:00', '01:30:00', NULL, 'https://meet.google.com/xyz-abcd-efg',
 1, 'Entretien final direction', 'Candidat retenu pour le poste', 'positive', 'b', false),

(6, 7, '2024-02-05 10:00:00', '2024-02-05 11:00:00', '01:00:00', 'Atelier maintenance', NULL,
 3, 'Test pratique maintenance', 'Bon niveau technique', 'positive', 'a', false);

-- Réinitialiser la séquence
SELECT setval('recruitment_interview_id_seq', (SELECT MAX(id) FROM recruitment_interview));

-- ============================================================================
-- 5. TABLE: recruitment_pointage (Pointages employés)
-- ============================================================================
INSERT INTO recruitment_pointage (
    id, employee_id, date, jour, heure_arrivee, heure_depart, heure_travaillee
) VALUES
(1, 1, '2024-01-15', 'Lundi', '08:00:00', '17:00:00', '08:00:00'),
(2, 1, '2024-01-16', 'Mardi', '08:05:00', '17:10:00', '08:05:00'),
(3, 1, '2024-01-17', 'Mercredi', '07:55:00', '16:55:00', '08:00:00'),
(4, 2, '2024-01-15', 'Lundi', '08:30:00', '17:30:00', '08:00:00'),
(5, 2, '2024-01-16', 'Mardi', '08:25:00', '17:25:00', '08:00:00'),
(6, 3, '2024-01-15', 'Lundi', '08:00:00', '17:00:00', '08:00:00'),
(7, 3, '2024-01-16', 'Mardi', '08:10:00', '17:15:00', '08:05:00'),
(8, 4, '2024-01-15', 'Lundi', '07:50:00', '16:50:00', '08:00:00'),
(9, 5, '2024-01-15', 'Lundi', '08:15:00', '17:15:00', '08:00:00'),
(10, 5, '2024-01-16', 'Mardi', '08:00:00', '17:00:00', '08:00:00');

-- Réinitialiser la séquence
SELECT setval('recruitment_pointage_id_seq', (SELECT MAX(id) FROM recruitment_pointage));

-- ============================================================================
-- 6. TABLE: recruitment_evaluation (Évaluations employés)
-- ============================================================================
INSERT INTO recruitment_evaluation (
    id, employee_id, evaluator_id, evaluation_date, work_quality, deadline_respect,
    team_spirit, autonomy, initiative, overall_score, comments, improvement_plan,
    status, hr_validation, hr_validator_id, hr_validation_date, employee_notified,
    notification_date, created_at, updated_at
) VALUES
(1, 1, 2, '2024-01-20', 5, 5, 4, 5, 4, 4.60,
 'Excellent travail, très professionnel et ponctuel', 'Continuer dans cette voie',
 'validated', true, 2, '2024-01-21 10:00:00', true, '2024-01-21 11:00:00',
 '2024-01-20 14:00:00', '2024-01-21 10:00:00'),

(2, 2, 1, '2024-01-20', 4, 4, 5, 4, 4, 4.20,
 'Très bon esprit d''équipe, travail de qualité', 'Développer l''autonomie sur certains dossiers',
 'validated', true, 2, '2024-01-21 10:00:00', true, '2024-01-21 11:00:00',
 '2024-01-20 15:00:00', '2024-01-21 10:00:00'),

(3, 3, 1, '2024-01-20', 4, 3, 4, 4, 3, 3.60,
 'Bon niveau technique, amélioration à faire sur les délais', 'Mieux planifier les tâches',
 'submitted', false, NULL, NULL, false, NULL,
 '2024-01-20 16:00:00', '2024-01-20 16:00:00'),

(4, 4, 2, '2024-01-21', 5, 4, 5, 5, 5, 4.80,
 'Employé exemplaire, grande initiative et autonomie', 'Aucun plan nécessaire',
 'validated', true, 2, '2024-01-22 09:00:00', true, '2024-01-22 10:00:00',
 '2024-01-21 14:00:00', '2024-01-22 09:00:00'),

(5, 5, 1, '2024-01-21', 3, 4, 3, 4, 3, 3.40,
 'Travail correct mais manque de régularité', 'Améliorer la constance dans la qualité',
 'draft', false, NULL, NULL, false, NULL,
 '2024-01-21 15:00:00', '2024-01-21 15:00:00');

-- Réinitialiser la séquence
SELECT setval('recruitment_evaluation_id_seq', (SELECT MAX(id) FROM recruitment_evaluation));

COMMIT;

-- ============================================================================
-- MESSAGE DE CONFIRMATION
-- ============================================================================
SELECT 'DONNEES RECRUITMENT CREEES AVEC SUCCES!' as message;

-- ============================================================================
-- RÉSUMÉ DES DONNÉES CRÉÉES
-- ============================================================================
SELECT 
    'RÉSUMÉ DES DONNÉES CRÉÉES' as titre,
    (SELECT COUNT(*) FROM recruitment_offer) as "Offres d'emploi",
    (SELECT COUNT(*) FROM recruitment_candidate) as "Candidats",
    (SELECT COUNT(*) FROM recruitment_application) as "Candidatures",
    (SELECT COUNT(*) FROM recruitment_interview) as "Entretiens",
    (SELECT COUNT(*) FROM recruitment_pointage) as "Pointages",
    (SELECT COUNT(*) FROM recruitment_evaluation) as "Évaluations";


