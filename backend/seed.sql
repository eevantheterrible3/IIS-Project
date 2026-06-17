INSERT INTO roles (role_id, name, description) VALUES
(1, 'ADMIN', 'System administrator'),
(2, 'PROJECT_MANAGER', 'Project manager'),
(3, 'TEAM_MEMBER', 'Project team member');

INSERT INTO users (user_id,username, name, last_name, email, password) VALUES
(1,'emma', 'Emma', 'Smith', 'milica@gmail.com', 'password123'),
(2,'anna', 'Anna', 'Smith', 'anna@gmail.com', 'password123'),
(3,'mark', 'Mark', 'Johnson', 'mark@gmail.com', 'password123'),
(4,'peter', 'Peter', 'Brown', 'peter@gmail.com', 'password123');

INSERT INTO projects (project_id, name, description, start_date, end_date, status) VALUES
(1, 'Document Digitalization', 'Project for managing organization documents', '2026-05-01', '2026-08-01', 'ACTIVE'),
(2, 'Environmental Campaign', 'Project for organizing environmental activities', '2026-06-01', '2026-09-01', 'ACTIVE');

INSERT INTO permissions (permission_id, name, description) VALUES
(1, 'VIEW', 'View document'),
(2, 'CREATE', 'Create document'),
(3, 'UPDATE', 'Update document'),
(4, 'DELETE', 'Delete document');

INSERT INTO works (user_id, project_id, role_id) VALUES
(1, 1, 2),
(2, 1, 3),
(3, 2, 2),
(4, 2, 3);

INSERT INTO documents (document_id, user_id, project_id, name, user_prompt, status, created_at, updated_at) VALUES
(1, 1, 1, 'Project Plan', 'Document describing the project plan and activities.', 'draft', NOW(), NOW()),
(2, 2, 1, 'Activity Report', 'Report about completed project activities.', 'published', NOW(), NOW()),
(3, 3, 2, 'Environmental Campaign Plan', 'Plan for organizing the environmental campaign.', 'draft', NOW(), NOW()),
(4, 1, 1, 'Budget Overview', 'Overview of planned and spent project budget.', 'published', NOW(), NOW()),
(5, 4, 2, 'Volunteer List', 'List of volunteers participating in the campaign.', 'draft', NOW(), NOW());

INSERT INTO metadata (meta_data_id, document_id, name, value) VALUES
(1, 1, 'author', 'Milica Salajic'),
(2, 1, 'year', '2026'),
(3, 1, 'category', 'planning'),
(4, 1, 'language', 'English'),

(5, 2, 'author', 'Anna Smith'),
(6, 2, 'year', '2026'),
(7, 2, 'category', 'report'),
(8, 2, 'version', '1.0'),

(9, 3, 'author', 'Mark Johnson'),
(10, 3, 'year', '2026'),
(11, 3, 'category', 'environment'),
(12, 3, 'priority', 'high'),

(13, 4, 'author', 'Milica Salajic'),
(14, 4, 'year', '2026'),
(15, 4, 'category', 'finance'),
(16, 4, 'currency', 'EUR'),

(17, 5, 'author', 'Peter Brown'),
(18, 5, 'year', '2026'),
(19, 5, 'category', 'volunteers'),
(20, 5, 'contains_personal_data', 'true');

INSERT INTO tags (tag_id, name) VALUES
(1, 'project'),
(2, 'report'),
(3, 'environment'),
(4, 'plan'),
(5, 'finance'),
(6, 'volunteers');

INSERT INTO is_marked (document_id, tag_id) VALUES
(1, 1),
(1, 4),
(2, 2),
(3, 3),
(3, 4),
(4, 5),
(5, 6);

INSERT INTO allows (user_id, document_id, permission_id) VALUES
(2, 1, 1),
(2, 1, 3),
(4, 1, 1),
(4, 2, 1),
(4, 2, 3),
(3, 4, 1),
(2, 5, 1);

INSERT INTO activities (activity_id, document_id, user_id, type, date) VALUES
(1, 1, 1, 'CREATE', NOW()),
(2, 1, 2, 'VIEW', NOW()),
(3, 2, 2, 'CREATE', NOW()),
(4, 2, 4, 'UPDATE', NOW()),
(5, 3, 3, 'CREATE', NOW()),
(6, 4, 1, 'CREATE', NOW()),
(7, 5, 4, 'CREATE', NOW());
INSERT INTO task_workflow (task_workflow_id, name, created_by, created_at) VALUES
(1, 'Terenski', 1, NOW()),
(2, 'Tehnički', 1, NOW()),
(3, 'Hitan',    1, NOW());

INSERT INTO task_workflow_step (step_id, task_workflow_id, status_name, next_step_id, is_first, is_last) VALUES
-- Terenski: Kreiran → U toku → Na reviziji → Završeno
(1,  1, 'Kreiran',     NULL, true,  false),
(2,  1, 'U toku',      NULL, false, false),
(3,  1, 'Na reviziji', NULL, false, false),
(4,  1, 'Završeno',    NULL, false, true),
-- Tehnički: Kreiran → Razvoj → Testiranje → Na reviziji → Završeno
(5,  2, 'Kreiran',     NULL, true,  false),
(6,  2, 'Razvoj',      NULL, false, false),
(7,  2, 'Testiranje',  NULL, false, false),
(8,  2, 'Na reviziji', NULL, false, false),
(9,  2, 'Završeno',    NULL, false, true),
-- Hitan: Kreiran → U toku → Završeno
(10, 3, 'Kreiran',     NULL, true,  false),
(11, 3, 'U toku',      NULL, false, false),
(12, 3, 'Završeno',    NULL, false, true);

UPDATE task_workflow_step SET next_step_id = 2  WHERE step_id = 1;
UPDATE task_workflow_step SET next_step_id = 3  WHERE step_id = 2;
UPDATE task_workflow_step SET next_step_id = 4  WHERE step_id = 3;
UPDATE task_workflow_step SET next_step_id = 6  WHERE step_id = 5;
UPDATE task_workflow_step SET next_step_id = 7  WHERE step_id = 6;
UPDATE task_workflow_step SET next_step_id = 8  WHERE step_id = 7;
UPDATE task_workflow_step SET next_step_id = 9  WHERE step_id = 8;
UPDATE task_workflow_step SET next_step_id = 11 WHERE step_id = 10;
UPDATE task_workflow_step SET next_step_id = 12 WHERE step_id = 11;

INSERT INTO resource (resource_id, name, resource_type, description, status, total_quantity) VALUES
(1, 'Skener Fujitsu fi-7160', 'Oprema',  'Skener za digitalizaciju dokumenata', 'active',     3),
(2, 'Adobe Acrobat Pro',      'Softver', 'Softver za rad sa PDF fajlovima',      'active',     5),
(3, 'Laptop Dell Latitude',   'Oprema',  'Laptop za terenski rad',               'active',     4),
(4, 'Projektor Epson EB-X51', 'Oprema',  'Projektor za prezentacije',            'not_active', 2),
(5, 'Microsoft 365',          'Softver', 'Office paket licenci',                 'active',     10);

INSERT INTO task (task_id, name, description, priority, task_workflow_id, current_step_id, deadline, assigned_user_id, project_id, created_at, last_updated_at) VALUES
(1, 'Nabavka skenera',           'Nabaviti skener visoke rezolucije za digitalizaciju arhive',                     'high',   2, 9, '2026-04-10', 4, 1, '2026-04-01 09:00:00', '2026-04-10 12:00:00'),
(2, 'Skeniranje dok. 2010-2015', 'Skenirati sve papirne dokumente iz arhivskog registra 2010-2015. Min. 300 DPI.', 'high',   1, 2, '2026-05-01', 2, 1, '2026-04-20 09:00:00', '2026-04-22 10:32:00'),
(3, 'Indeksiranje fajlova',      'Indeksirati sve skenirane fajlove i uneti ih u digitalni registar',             'high',   3, 10,'2026-04-20', 4, 1, '2026-04-10 08:00:00', '2026-04-10 08:00:00'),
(4, 'Priprema izveštaja',        'Pripremiti izveštaj o napretku digitalizacije za menadžment',                   'low',    2, 5, '2026-06-01', 3, 2, '2026-05-01 09:00:00', '2026-05-01 09:00:00');

INSERT INTO subtask (subtask_id, task_id, name, deadline, current_status, assigned_user_id, created_at) VALUES
-- Nabavka skenera (task 1) - završen 2/2
(1, 1, 'Odabir modela skenera', '2026-04-05', 'done',        4, '2026-04-01 09:00:00'),
(2, 1, 'Nabavka i instalacija', '2026-04-10', 'done',        4, '2026-04-01 09:00:00'),
-- Skeniranje (task 2) - u toku 3/5
(3, 2, 'Pregled dokumenata',    '2026-04-22', 'done',        2, '2026-04-20 09:00:00'),
(4, 2, 'Skeniranje batch 1',    '2026-04-25', 'done',        2, '2026-04-20 09:00:00'),
(5, 2, 'Skeniranje batch 2',    '2026-04-28', 'done',        2, '2026-04-20 09:00:00'),
(6, 2, 'Skeniranje batch 3',    '2026-05-01', 'todo',        2, '2026-04-20 09:00:00'),
(7, 2, 'Verifikacija kvaliteta','2026-05-02', 'todo',        4, '2026-04-20 09:00:00'),
-- Priprema izveštaja (task 4)
(8, 4, 'Prikupiti statistike',  '2026-05-20', 'todo',        3, '2026-05-01 09:00:00'),
(9, 4, 'Napisati izveštaj',     '2026-05-28', 'todo',        3, '2026-05-01 09:00:00');

INSERT INTO task_resource (task_id, resource_id, quantity, reserved_from, reserved_until, status) VALUES
(1, 1, 1, '2026-04-01', '2026-04-10', 'free'),
(2, 3, 1, '2026-04-20', '2026-05-01', 'in_use'),
(2, 2, 1, '2026-04-20', '2026-05-01', 'reserved');

UPDATE projects
SET name = 'Summer Internship 2026',
    description = 'Project for organizing summer internship applications.',
    start_date = '2026-05-01',
    end_date = '2026-08-01',
    status = 'ACTIVE'
WHERE project_id = 1;
commit;
UPDATE projects
SET name = 'Employee Hiring Process',
    description = 'Project for managing job applications and interviews.',
    start_date = '2026-04-15',
    end_date = '2026-09-01',
    status = 'ACTIVE'
WHERE project_id = 2;
UPDATE documents
SET name = 'Frontend Developer CV',
    user_prompt = 'Frontend internship application',
    file_path = 'uploads/documents/frontend_cv.pdf',
    status = 'draft'
WHERE document_id = 1;
commit;
UPDATE documents
SET name = 'Interview Schedule',
    user_prompt = 'Interview planning document',
    file_path = 'uploads/documents/interview_schedule.pdf',
    status = 'published'
WHERE document_id = 2;
commit;
UPDATE documents
SET name = 'Employment Contract',
    user_prompt = 'Employee contract document',
    file_path = 'uploads/documents/employment_contract.pdf',
    status = 'published'
WHERE document_id = 3;
commit;
UPDATE documents
SET name = 'Website Specification',
    user_prompt = 'Website redesign requirements',
    file_path = 'uploads/documents/website_specification.pdf',
    status = 'draft'
WHERE document_id = 4;
commit;
UPDATE documents
SET name = 'Laptop Invoice',
    user_prompt = 'Office equipment purchase invoice',
    file_path = 'uploads/documents/laptop_invoice.pdf',
    status = 'published'
WHERE document_id = 5;
commit;