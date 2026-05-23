-- Roles
INSERT INTO roles (role_id, name, description) VALUES
(1, 'ADMIN',           'System administrator'),
(2, 'PROJECT_MANAGER', 'Project manager'),
(3, 'TEAM_MEMBER',     'Project team member');

-- Users (password: password123, bcrypt-hashed)
INSERT INTO users (user_id, username, name, last_name, email, password) VALUES
(1, 'emma',  'Emma',  'Smith',   'emma@gmail.com',  '$2b$10$PFp9V8MSwWSTTuVNXY2CZeygNj5McmSNBMwDXOmoNAfiMXUm7akyO'),
(2, 'anna',  'Anna',  'Smith',   'anna@gmail.com',  '$2b$10$PFp9V8MSwWSTTuVNXY2CZeygNj5McmSNBMwDXOmoNAfiMXUm7akyO'),
(3, 'mark',  'Mark',  'Johnson', 'mark@gmail.com',  '$2b$10$PFp9V8MSwWSTTuVNXY2CZeygNj5McmSNBMwDXOmoNAfiMXUm7akyO'),
(4, 'peter', 'Peter', 'Brown',   'peter@gmail.com', '$2b$10$PFp9V8MSwWSTTuVNXY2CZeygNj5McmSNBMwDXOmoNAfiMXUm7akyO'),
(5, 'sarah', 'Sarah', 'Turner',  'sarah@gmail.com', '$2b$10$PFp9V8MSwWSTTuVNXY2CZeygNj5McmSNBMwDXOmoNAfiMXUm7akyO');

-- Projects
INSERT INTO projects (project_id, name, description, start_date, end_date, status) VALUES
(1, 'Summer Internship 2026',  'Project for organizing summer internship applications.', '2026-05-01', '2026-08-01', 'ACTIVE'),
(2, 'Employee Hiring Process', 'Project for managing job applications and interviews.',  '2026-04-15', '2026-09-01', 'ACTIVE');

-- Permissions
INSERT INTO permissions (permission_id, name, description) VALUES
(1, 'VIEW',   'View document'),
(2, 'CREATE', 'Create document'),
(3, 'UPDATE', 'Update document'),
(4, 'DELETE', 'Delete document');

-- Works (user → project → role)
INSERT INTO works (user_id, project_id, role_id) VALUES
(1, 1, 2),  -- emma  → Summer Internship    → PROJECT_MANAGER
(2, 1, 3),  -- anna  → Summer Internship    → TEAM_MEMBER
(3, 2, 2),  -- mark  → Employee Hiring      → PROJECT_MANAGER
(4, 2, 3),  -- peter → Employee Hiring      → TEAM_MEMBER
(5, 2, 1);  -- sarah → Employee Hiring      → ADMIN

-- Documents
INSERT INTO documents (document_id, user_id, project_id, name, user_prompt, file_path, status, created_at, updated_at) VALUES
(1, 1, 1, 'Frontend Developer CV',  'Frontend internship application',       'uploads/documents/frontend_cv.pdf',          'draft',     NOW(), NOW()),
(2, 2, 1, 'Interview Schedule',     'Interview planning document',           'uploads/documents/interview_schedule.pdf',   'published', NOW(), NOW()),
(3, 3, 2, 'Employment Contract',    'Employee contract document',            'uploads/documents/employment_contract.pdf',  'published', NOW(), NOW()),
(4, 1, 1, 'Website Specification',  'Website redesign requirements',         'uploads/documents/website_specification.pdf','draft',     NOW(), NOW()),
(5, 4, 2, 'Laptop Invoice',         'Office equipment purchase invoice',     'uploads/documents/laptop_invoice.pdf',       'published', NOW(), NOW());

-- Metadata
INSERT INTO metadata (meta_data_id, document_id, name, value) VALUES
(1,  1, 'author',   'Emma Smith'),
(2,  1, 'year',     '2026'),
(3,  1, 'category', 'planning'),
(4,  1, 'language', 'English'),
(5,  2, 'author',   'Anna Smith'),
(6,  2, 'year',     '2026'),
(7,  2, 'category', 'report'),
(8,  2, 'version',  '1.0'),
(9,  3, 'author',   'Mark Johnson'),
(10, 3, 'year',     '2026'),
(11, 3, 'category', 'environment'),
(12, 3, 'priority', 'high'),
(13, 4, 'author',   'Emma Smith'),
(14, 4, 'year',     '2026'),
(15, 4, 'category', 'finance'),
(16, 4, 'currency', 'EUR'),
(17, 5, 'author',   'Peter Brown'),
(18, 5, 'year',     '2026'),
(19, 5, 'category', 'volunteers'),
(20, 5, 'contains_personal_data', 'true');

-- Tags
INSERT INTO tags (tag_id, name) VALUES
(1, 'project'),
(2, 'report'),
(3, 'environment'),
(4, 'plan'),
(5, 'finance'),
(6, 'volunteers');

-- Document–tag links
INSERT INTO is_marked (document_id, tag_id) VALUES
(1, 1),
(1, 4),
(2, 2),
(3, 3),
(3, 4),
(4, 5),
(5, 6);

-- Document permissions per user
INSERT INTO allows (user_id, document_id, permission_id) VALUES
(2, 1, 1),
(2, 1, 3),
(4, 1, 1),
(4, 2, 1),
(4, 2, 3),
(3, 4, 1),
(2, 5, 1);

-- Activities
INSERT INTO activities (activity_id, document_id, user_id, type, date) VALUES
(1, 1, 1, 'CREATE', NOW()),
(2, 1, 2, 'VIEW',   NOW()),
(3, 2, 2, 'CREATE', NOW()),
(4, 2, 4, 'UPDATE', NOW()),
(5, 3, 3, 'CREATE', NOW()),
(6, 4, 1, 'CREATE', NOW()),
(7, 5, 4, 'CREATE', NOW());
