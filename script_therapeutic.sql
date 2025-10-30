-- Script Therapeutic Activities
BEGIN;
-- Vider uniquement les tables existantes
DELETE FROM therapeutic_activities_activity;
DELETE FROM therapeutic_activities_activitylocation;
DELETE FROM therapeutic_activities_activitytype;

INSERT INTO therapeutic_activities_activitytype (id, name, description, is_active, created_at, updated_at) VALUES
(1, 'Sport', 'Activités sportives', true, NOW(), NOW()),
(2, 'Art thérapie', 'Activités artistiques thérapeutiques', true, NOW(), NOW()),
(3, 'Relaxation', 'Séances de relaxation', true, NOW(), NOW());

INSERT INTO therapeutic_activities_activitylocation (id, name, address, capacity, is_active, created_at, updated_at) VALUES
(1, 'Salle A', 'Étage 1', 20, true, NOW(), NOW()),
(2, 'Salle B', 'Étage 2', 15, true, NOW(), NOW());

INSERT INTO therapeutic_activities_activity (id, title, description, type_id, coach_id, is_active, created_at, updated_at) VALUES
(1, 'Yoga thérapeutique', 'Séances de yoga adaptées', 3, 1, true, NOW(), NOW()),
(2, 'Peinture', 'Atelier peinture', 2, 2, true, NOW(), NOW());

-- Sessions et participants non créés (tables inexistantes)

COMMIT;
SELECT 'DONNEES THERAPEUTIC ACTIVITIES CREEES!' as message;

