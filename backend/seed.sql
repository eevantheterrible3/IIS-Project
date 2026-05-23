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

-- Document types
INSERT INTO document_types (document_type_id, name, description, system_prompt) VALUES
(1, 'CV / Resume',     'Candidate curriculum vitae for job applications.',         'You are an expert HR assistant. Generate a professional CV section based on the provided candidate information. Use clear, concise language and highlight relevant experience and skills.'),
(2, 'Job Offer',       'Formal job offer letter sent to selected candidates.',      'You are an HR specialist. Write a formal, friendly job offer section. Be precise about terms, conditions, and next steps.'),
(3, 'Contract',        'Employment or service contract between two parties.',       'You are a legal document assistant. Write a clear, formal contract section. Use precise legal language while keeping it readable.'),
(4, 'Project Report',  'Periodic or final report documenting project progress.',    'You are a project management assistant. Write a structured project report section based on the provided data. Be factual and concise.');

-- Section templates
INSERT INTO section_templates (section_template_id, document_type_id, name, content_structure, system_prompt, order_index) VALUES
-- CV / Resume
(1,  1, 'Personal Information',  'Full name, contact details, address, LinkedIn, portfolio links.',                                          'Extract and format the candidate''s personal and contact information in a clean, professional layout.',                    1),
(2,  1, 'Professional Summary',  'A 3-5 sentence overview of the candidate''s career, key skills, and goals.',                               'Write a compelling professional summary that highlights the candidate''s strongest qualifications for the target role.',   2),
(3,  1, 'Work Experience',       'List of previous positions: company, title, dates, and key responsibilities/achievements per role.',        'Describe each work experience entry with action verbs and measurable achievements where possible.',                       3),
(4,  1, 'Education',             'Degrees, institutions, graduation years, and relevant coursework or honors.',                               'Format the education section clearly, listing the most recent degree first.',                                             4),
(5,  1, 'Skills',                'Technical and soft skills grouped by category (e.g. Languages, Tools, Frameworks).',                       'List skills in a scannable format grouped by category. Prioritize skills most relevant to the job.',                    5),

-- Job Offer
(6,  2, 'Position Details',      'Job title, department, reporting line, work location, and start date.',                                    'Describe the offered position clearly and formally, including all key details about the role and team.',                  1),
(7,  2, 'Compensation & Benefits','Salary, bonus structure, benefits (health, pension, vacation days), and any other perks.',                 'Present the compensation package in a transparent and attractive way.',                                                   2),
(8,  2, 'Requirements',          'Required qualifications, experience, and skills expected from the candidate.',                             'List the requirements concisely. Distinguish between mandatory and preferred qualifications.',                           3),
(9,  2, 'Application Process',   'Next steps: deadline, documents needed, interview stages, and contact person.',                            'Explain the next steps clearly so the candidate knows exactly what to do and when to expect a response.',                 4),

-- Contract
(10, 3, 'Parties',               'Full legal names, addresses, and roles of all parties entering the agreement.',                            'State the contracting parties precisely using their full legal names and relevant identifiers.',                          1),
(11, 3, 'Terms & Duration',      'Contract type (fixed/permanent), start date, end date if applicable, and probation period.',               'Define the contractual terms and duration clearly, specifying any probation or notice period conditions.',                 2),
(12, 3, 'Obligations',           'Responsibilities and obligations of each party: deliverables, working hours, confidentiality, etc.',        'List obligations for each party in a balanced and enforceable way. Include confidentiality and IP clauses if applicable.', 3),
(13, 3, 'Signatures',            'Signature block with name, title, date, and space for signatures of all parties.',                         'Format the signature section formally with fields for all required signatories.',                                         4),

-- Project Report
(14, 4, 'Executive Summary',     'High-level overview of the project status, key achievements, and blockers in 1-2 paragraphs.',             'Summarize the project state concisely for a non-technical audience. Highlight what was achieved and what is at risk.',    1),
(15, 4, 'Progress Update',       'Detailed update on completed tasks, milestones reached, and current work in progress.',                    'Describe progress against the project plan. Reference milestones and deliverables by name.',                             2),
(16, 4, 'Risks & Issues',        'Current risks, their likelihood and impact, mitigation actions, and any open blockers.',                   'List each risk or issue clearly with its status and the action being taken to address it.',                              3),
(17, 4, 'Next Steps',            'Planned activities for the next reporting period with owners and target dates.',                           'Outline upcoming work in a structured list with clear owners and deadlines.',                                            4);

-- Link existing seed documents to document types
UPDATE documents SET document_type_id = 1 WHERE document_id = 1;  -- Frontend Developer CV  → CV/Resume
UPDATE documents SET document_type_id = 4 WHERE document_id = 2;  -- Interview Schedule     → Project Report
UPDATE documents SET document_type_id = 3 WHERE document_id = 3;  -- Employment Contract    → Contract
UPDATE documents SET document_type_id = 4 WHERE document_id = 4;  -- Website Specification  → Project Report
UPDATE documents SET document_type_id = 2 WHERE document_id = 5;  -- Laptop Invoice         → Job Offer

-- Activities
INSERT INTO activities (activity_id, document_id, user_id, type, date) VALUES
(1, 1, 1, 'CREATE', NOW()),
(2, 1, 2, 'VIEW',   NOW()),
(3, 2, 2, 'CREATE', NOW()),
(4, 2, 4, 'UPDATE', NOW()),
(5, 3, 3, 'CREATE', NOW()),
(6, 4, 1, 'CREATE', NOW()),
(7, 5, 4, 'CREATE', NOW());
