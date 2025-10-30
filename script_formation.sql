-- Script Formation
BEGIN;

-- Vider toutes les tables d'abord
DELETE FROM formation_evaluation;
DELETE FROM formation_inscription;
DELETE FROM formation_session;
DELETE FROM formation_formation;
DELETE FROM formation_collaborateur;
DELETE FROM formation_formateur;

-- Formateurs (d'abord)
INSERT INTO formation_formateur (nom, prenom, service) VALUES
('Alami', 'Hassan', 'Développement web'),
('Bennani', 'Fatima', 'Ressources Humaines'),
('El Fassi', 'Mohammed', 'Sécurité au travail');

-- Formations
INSERT INTO formation_formation (code, titre, description, type, domaine, duree_heures, supplier_id) VALUES
('FORM001', 'Formation Django', 'Formation développement web Django', 'interne', 'IT', 40, 1),
('FORM002', 'Gestion RH', 'Formation gestion des ressources humaines', 'externe', 'HR', 24, 2),
('FORM003', 'E-learning Sécurité', 'Formation en ligne sécurité au travail', 'e_learning', 'securite', 8, 1),
('FORM004', 'Formation Premiers Secours', 'Formation aux gestes de premiers secours', 'interne', 'medecine', 16, 1),
('FORM005', 'Management d''équipe', 'Formation au management et leadership', 'externe', 'management', 32, 2);

-- Sessions de formation (utilise les codes des formations)
INSERT INTO formation_session (formation_id, date_debut, date_fin, lieu, places_totales, statut, formateur_id) VALUES
('FORM001', '2024-03-01', '2024-03-08', 'Salle Formation A', 20, 'planifiee', (SELECT id FROM formation_formateur WHERE nom='Alami' LIMIT 1)),
('FORM002', '2024-03-15', '2024-03-18', 'Centre Formation Externe', 15, 'planifiee', (SELECT id FROM formation_formateur WHERE nom='Bennani' LIMIT 1)),
('FORM003', '2024-02-10', '2024-02-10', 'En ligne', 50, 'terminee', (SELECT id FROM formation_formateur WHERE nom='El Fassi' LIMIT 1)),
('FORM004', '2024-04-01', '2024-04-02', 'Salle Formation B', 25, 'planifiee', (SELECT id FROM formation_formateur WHERE nom='Alami' LIMIT 1)),
('FORM005', '2024-04-10', '2024-04-17', 'Centre Formation Externe', 12, 'planifiee', (SELECT id FROM formation_formateur WHERE nom='Bennani' LIMIT 1));

-- Collaborateurs
INSERT INTO formation_collaborateur (nom, prenom, service) VALUES
('Tazi', 'Amina', 'IT'),
('Chraibi', 'Youssef', 'RH'),
('Lahlou', 'Sara', 'Medical'),
('Benjelloun', 'Karim', 'Administration'),
('Ouazzani', 'Leila', 'RH');

-- Inscriptions (utilise les IDs dynamiques)
INSERT INTO formation_inscription (session_id, employee_id, statut, date_inscription) 
SELECT s.id, 1, 'confirmee', NOW()
FROM formation_session s WHERE s.formation_id = 'FORM001' LIMIT 1;

INSERT INTO formation_inscription (session_id, employee_id, statut, date_inscription) 
SELECT s.id, 2, 'confirmee', NOW()
FROM formation_session s WHERE s.formation_id = 'FORM001' LIMIT 1;

INSERT INTO formation_inscription (session_id, employee_id, statut, date_inscription) 
SELECT s.id, 2, 'confirmee', NOW()
FROM formation_session s WHERE s.formation_id = 'FORM002' LIMIT 1;

INSERT INTO formation_inscription (session_id, employee_id, statut, date_inscription) 
SELECT s.id, 3, 'terminee', NOW()
FROM formation_session s WHERE s.formation_id = 'FORM003' LIMIT 1;

INSERT INTO formation_inscription (session_id, employee_id, statut, date_inscription) 
SELECT s.id, 5, 'terminee', NOW()
FROM formation_session s WHERE s.formation_id = 'FORM003' LIMIT 1;

-- Évaluations (utilise les IDs d'inscriptions réelles)
INSERT INTO formation_evaluation (inscription_id, score, commentaires, date_evaluation)
SELECT i.id, 18, 'Excellente formation, très utile', '2024-02-11'
FROM formation_inscription i
JOIN formation_session s ON i.session_id = s.id
WHERE s.formation_id = 'FORM003' AND i.employee_id = 3 LIMIT 1;

INSERT INTO formation_evaluation (inscription_id, score, commentaires, date_evaluation)
SELECT i.id, 16, 'Bonne formation, contenu intéressant', '2024-02-11'
FROM formation_inscription i
JOIN formation_session s ON i.session_id = s.id
WHERE s.formation_id = 'FORM003' AND i.employee_id = 5 LIMIT 1;

COMMIT;
SELECT 'DONNEES FORMATION CREEES!' as message;

