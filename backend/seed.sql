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

INSERT INTO users (username, name, last_name, email, password)
VALUES ('sarah', 'Sarah', 'Turner', 'sarah@gmail.com', 'password123');
INSERT INTO works (user_id, project_id, role_id)
VALUES (5, 2, 1);
INSERT INTO work (user_id, project_id, role_id)
VALUES (6, 1, 1);