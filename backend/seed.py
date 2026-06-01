"""
Run: docker compose exec backend python seed.py
"""
import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database import DATABASE_URL
from models.user import User
from models.role import Role
from datetime import datetime
from models.project import Project, ProjectStatus
from models.permission import Permission
from models.work import Work
from models.document_type import DocumentType
from models.section_template import SectionTemplate
from models.document import Document
from models.metadata import DocumentMetadata
from models.tag import Tag
from models.is_marked import IsMarked
from models.allows import Allows
from models.activity import Activity, ActivityType
from models.task_workflow import TaskWorkflow
from models.task_workflow_step import TaskWorkflowStep
from models.task import Task, TaskPriority
from models.subtask import Subtask, SubtaskStatus
from models.resource import Resource, ResourceStatus
from models.task_resource import TaskResource, TaskResourceStatus
from models.workflow_action import WorkflowAction
from models.workflow import Workflow
from models.workflow_has_action import WorkflowHasAction
from models.workflow_instance import WorkflowInstance
from models.workflow_instance_step import WorkflowInstanceStep
from models.condition_type import ConditionType
from models.condition import Condition
from models.document_rating import DocumentRating
from core.security import hash_password

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Pre-generate IDs so FK references are consistent
role_admin_id       = str(uuid.uuid4())
role_manager_id     = str(uuid.uuid4())
role_member_id      = str(uuid.uuid4())

user_emma_id        = str(uuid.uuid4())
user_anna_id        = str(uuid.uuid4())
user_mark_id        = str(uuid.uuid4())
user_peter_id       = str(uuid.uuid4())
user_sarah_id       = str(uuid.uuid4())

project_intern_id   = str(uuid.uuid4())
project_hiring_id   = str(uuid.uuid4())

perm_view_id        = str(uuid.uuid4())
perm_create_id      = str(uuid.uuid4())
perm_update_id      = str(uuid.uuid4())
perm_delete_id      = str(uuid.uuid4())

dt_cv_id            = str(uuid.uuid4())
dt_offer_id         = str(uuid.uuid4())
dt_contract_id      = str(uuid.uuid4())
dt_report_id        = str(uuid.uuid4())

doc_cv_id           = str(uuid.uuid4())
doc_interview_id    = str(uuid.uuid4())
doc_contract_id     = str(uuid.uuid4())
doc_website_id      = str(uuid.uuid4())
doc_invoice_id      = str(uuid.uuid4())

tag_project_id      = str(uuid.uuid4())
tag_report_id       = str(uuid.uuid4())
tag_env_id          = str(uuid.uuid4())
tag_plan_id         = str(uuid.uuid4())
tag_finance_id      = str(uuid.uuid4())
tag_volunteers_id   = str(uuid.uuid4())

# Workflows
wf_intern_id        = str(uuid.uuid4())
wf_hiring_id        = str(uuid.uuid4())

# Workflow steps — intern
step_i1_id = str(uuid.uuid4())
step_i2_id = str(uuid.uuid4())
step_i3_id = str(uuid.uuid4())

# Workflow steps — hiring
step_h1_id = str(uuid.uuid4())
step_h2_id = str(uuid.uuid4())
step_h3_id = str(uuid.uuid4())
step_h4_id = str(uuid.uuid4())

# Resources
res_laptop_id       = str(uuid.uuid4())
res_meeting_room_id = str(uuid.uuid4())
res_projector_id    = str(uuid.uuid4())

# Tasks
task_setup_id       = str(uuid.uuid4())
task_onboarding_id  = str(uuid.uuid4())
task_screening_id   = str(uuid.uuid4())
task_interviews_id  = str(uuid.uuid4())
task_offers_id      = str(uuid.uuid4())

# ── Archive Digitalization project ──────────────────────────────────────────
project_archive_id         = str(uuid.uuid4())
resource_scanner_id        = str(uuid.uuid4())

workflow_technical_id      = str(uuid.uuid4())
workflow_fieldwork_id      = str(uuid.uuid4())
workflow_administrative_id = str(uuid.uuid4())

# Technical workflow steps: Created → Development → Testing → Under Review → Done
step_tech_created_id     = str(uuid.uuid4())
step_tech_development_id = str(uuid.uuid4())
step_tech_testing_id     = str(uuid.uuid4())
step_tech_review_id      = str(uuid.uuid4())
step_tech_done_id        = str(uuid.uuid4())

# Field Work workflow steps: Created → In Progress → Under Review → Done
step_field_created_id    = str(uuid.uuid4())
step_field_inprogress_id = str(uuid.uuid4())
step_field_review_id     = str(uuid.uuid4())
step_field_done_id       = str(uuid.uuid4())

# Administrative workflow steps: Created → In Progress → Done
step_admin_created_id    = str(uuid.uuid4())
step_admin_inprogress_id = str(uuid.uuid4())
step_admin_done_id       = str(uuid.uuid4())

# Archive project tasks
task_scanner_purchase_id  = str(uuid.uuid4())
task_doc_scanning_id      = str(uuid.uuid4())
task_file_indexing_id     = str(uuid.uuid4())
task_quality_review_id    = str(uuid.uuid4())
task_server_setup_id      = str(uuid.uuid4())
task_staff_training_id    = str(uuid.uuid4())
task_documentation_id     = str(uuid.uuid4())
task_final_report_id      = str(uuid.uuid4())
wa_draft_id         = str(uuid.uuid4())
wa_review_id        = str(uuid.uuid4())
wa_approve_id       = str(uuid.uuid4())
wa_revise_id        = str(uuid.uuid4())
wa_publish_id       = str(uuid.uuid4())

wf_doc_review_id    = str(uuid.uuid4())
wf_contract_id      = str(uuid.uuid4())

ct_role_id          = str(uuid.uuid4())
ct_doctype_id       = str(uuid.uuid4())
ct_approval_id      = str(uuid.uuid4())

cond_mgr_review_id  = str(uuid.uuid4())
cond_contract_id    = str(uuid.uuid4())
cond_admin_approve_id = str(uuid.uuid4())

wi_cv_review_id     = str(uuid.uuid4())
wi_contract_flow_id = str(uuid.uuid4())

wis1_id             = str(uuid.uuid4())
wis2_id             = str(uuid.uuid4())
wis3_id             = str(uuid.uuid4())
wis4_id             = str(uuid.uuid4())
wis5_id             = str(uuid.uuid4())

PWD = hash_password("password123")


async def seed():
    async with AsyncSessionLocal() as db:
        # Roles
        db.add_all([
            Role(role_id=role_admin_id,   name="ADMIN",           description="System administrator"),
            Role(role_id=role_manager_id, name="PROJECT_MANAGER", description="Project manager"),
            Role(role_id=role_member_id,  name="TEAM_MEMBER",     description="Project team member"),
        ])

        # Users
        db.add_all([
            User(user_id=user_emma_id,  username="emma",  name="Emma",  last_name="Smith",   email="emma@gmail.com",  password=PWD),
            User(user_id=user_anna_id,  username="anna",  name="Anna",  last_name="Smith",   email="anna@gmail.com",  password=PWD),
            User(user_id=user_mark_id,  username="mark",  name="Mark",  last_name="Johnson", email="mark@gmail.com",  password=PWD),
            User(user_id=user_peter_id, username="peter", name="Peter", last_name="Brown",   email="peter@gmail.com", password=PWD),
            User(user_id=user_sarah_id, username="sarah", name="Sarah", last_name="Turner",  email="sarah@gmail.com", password=PWD),
        ])

        # Projects
        db.add_all([
            Project(project_id=project_intern_id,  name="Summer Internship 2026",  description="Project for organizing summer internship applications.", status=ProjectStatus.ACTIVE,   start_date=datetime(2026, 3, 1),  end_date=datetime(2026, 8, 31)),
            Project(project_id=project_hiring_id,  name="Employee Hiring Process", description="Project for managing job applications and interviews.",  status=ProjectStatus.ACTIVE,   start_date=datetime(2026, 1, 15), end_date=datetime(2026, 6, 30)),
        ])

        # Permissions
        db.add_all([
            Permission(permission_id=perm_view_id,   name="VIEW",   description="View document"),
            Permission(permission_id=perm_create_id, name="CREATE", description="Create document"),
            Permission(permission_id=perm_update_id, name="UPDATE", description="Update document"),
            Permission(permission_id=perm_delete_id, name="DELETE", description="Delete document"),
        ])

        await db.flush()

        # Works
        db.add_all([
            Work(user_id=user_emma_id,  project_id=project_intern_id,  role_id=role_manager_id),
            Work(user_id=user_anna_id,  project_id=project_intern_id,  role_id=role_member_id),
            Work(user_id=user_mark_id,  project_id=project_hiring_id,  role_id=role_manager_id),
            Work(user_id=user_peter_id, project_id=project_hiring_id,  role_id=role_member_id),
            Work(user_id=user_sarah_id, project_id=project_hiring_id,  role_id=role_admin_id),
        ])

        # Document types
        db.add_all([
            DocumentType(document_type_id=dt_cv_id,       name="CV / Resume",    description="Candidate curriculum vitae for job applications.",        system_prompt="You are an expert HR assistant. Generate a professional CV section based on the provided candidate information. Use clear, concise language and highlight relevant experience and skills."),
            DocumentType(document_type_id=dt_offer_id,    name="Job Offer",      description="Formal job offer letter sent to selected candidates.",     system_prompt="You are an HR specialist. Write a formal, friendly job offer section. Be precise about terms, conditions, and next steps."),
            DocumentType(document_type_id=dt_contract_id, name="Contract",       description="Employment or service contract between two parties.",      system_prompt="You are a legal document assistant. Write a clear, formal contract section. Use precise legal language while keeping it readable."),
            DocumentType(document_type_id=dt_report_id,   name="Project Report", description="Periodic or final report documenting project progress.",   system_prompt="You are a project management assistant. Write a structured project report section based on the provided data. Be factual and concise."),
        ])

        await db.flush()

        # Section templates
        db.add_all([
            # CV / Resume
            SectionTemplate(document_type_id=dt_cv_id, name="Personal Information",  order_index=1, content_structure="Full name, contact details, address, LinkedIn, portfolio links.",                        system_prompt="Extract and format the candidate's personal and contact information in a clean, professional layout."),
            SectionTemplate(document_type_id=dt_cv_id, name="Professional Summary",  order_index=2, content_structure="A 3-5 sentence overview of the candidate's career, key skills, and goals.",              system_prompt="Write a compelling professional summary that highlights the candidate's strongest qualifications for the target role."),
            SectionTemplate(document_type_id=dt_cv_id, name="Work Experience",       order_index=3, content_structure="List of previous positions: company, title, dates, and key responsibilities/achievements.", system_prompt="Describe each work experience entry with action verbs and measurable achievements where possible."),
            SectionTemplate(document_type_id=dt_cv_id, name="Education",             order_index=4, content_structure="Degrees, institutions, graduation years, and relevant coursework or honors.",             system_prompt="Format the education section clearly, listing the most recent degree first."),
            SectionTemplate(document_type_id=dt_cv_id, name="Skills",                order_index=5, content_structure="Technical and soft skills grouped by category (e.g. Languages, Tools, Frameworks).",     system_prompt="List skills in a scannable format grouped by category. Prioritize skills most relevant to the job."),
            # Job Offer
            SectionTemplate(document_type_id=dt_offer_id, name="Position Details",       order_index=1, content_structure="Job title, department, reporting line, work location, and start date.",                           system_prompt="Describe the offered position clearly and formally, including all key details about the role and team."),
            SectionTemplate(document_type_id=dt_offer_id, name="Compensation & Benefits", order_index=2, content_structure="Salary, bonus structure, benefits (health, pension, vacation days), and any other perks.",       system_prompt="Present the compensation package in a transparent and attractive way."),
            SectionTemplate(document_type_id=dt_offer_id, name="Requirements",            order_index=3, content_structure="Required qualifications, experience, and skills expected from the candidate.",                    system_prompt="List the requirements concisely. Distinguish between mandatory and preferred qualifications."),
            SectionTemplate(document_type_id=dt_offer_id, name="Application Process",     order_index=4, content_structure="Next steps: deadline, documents needed, interview stages, and contact person.",                  system_prompt="Explain the next steps clearly so the candidate knows exactly what to do and when to expect a response."),
            # Contract
            SectionTemplate(document_type_id=dt_contract_id, name="Parties",         order_index=1, content_structure="Full legal names, addresses, and roles of all parties entering the agreement.",                 system_prompt="State the contracting parties precisely using their full legal names and relevant identifiers."),
            SectionTemplate(document_type_id=dt_contract_id, name="Terms & Duration", order_index=2, content_structure="Contract type (fixed/permanent), start date, end date if applicable, and probation period.",   system_prompt="Define the contractual terms and duration clearly, specifying any probation or notice period conditions."),
            SectionTemplate(document_type_id=dt_contract_id, name="Obligations",      order_index=3, content_structure="Responsibilities and obligations of each party: deliverables, working hours, confidentiality.", system_prompt="List obligations for each party in a balanced and enforceable way. Include confidentiality and IP clauses if applicable."),
            SectionTemplate(document_type_id=dt_contract_id, name="Signatures",       order_index=4, content_structure="Signature block with name, title, date, and space for signatures of all parties.",             system_prompt="Format the signature section formally with fields for all required signatories."),
            # Project Report
            SectionTemplate(document_type_id=dt_report_id, name="Executive Summary", order_index=1, content_structure="High-level overview of the project status, key achievements, and blockers in 1-2 paragraphs.", system_prompt="Summarize the project state concisely for a non-technical audience. Highlight what was achieved and what is at risk."),
            SectionTemplate(document_type_id=dt_report_id, name="Progress Update",   order_index=2, content_structure="Detailed update on completed tasks, milestones reached, and current work in progress.",        system_prompt="Describe progress against the project plan. Reference milestones and deliverables by name."),
            SectionTemplate(document_type_id=dt_report_id, name="Risks & Issues",    order_index=3, content_structure="Current risks, their likelihood and impact, mitigation actions, and any open blockers.",       system_prompt="List each risk or issue clearly with its status and the action being taken to address it."),
            SectionTemplate(document_type_id=dt_report_id, name="Next Steps",        order_index=4, content_structure="Planned activities for the next reporting period with owners and target dates.",               system_prompt="Outline upcoming work in a structured list with clear owners and deadlines."),
        ])

        # Documents
        db.add_all([
            Document(document_id=doc_cv_id,        user_id=user_emma_id,  project_id=project_intern_id,  document_type_id=dt_cv_id,       name="Frontend Developer CV",  user_prompt="Frontend internship application",         file_path="uploads/documents/frontend_cv.pdf",           status="draft"),
            Document(document_id=doc_interview_id, user_id=user_anna_id,  project_id=project_intern_id,  document_type_id=dt_report_id,   name="Interview Schedule",     user_prompt="Interview planning document",             file_path="uploads/documents/interview_schedule.pdf",    status="published"),
            Document(document_id=doc_contract_id,  user_id=user_mark_id,  project_id=project_hiring_id,  document_type_id=dt_contract_id, name="Employment Contract",    user_prompt="Employee contract document",              file_path="uploads/documents/employment_contract.pdf",   status="published"),
            Document(document_id=doc_website_id,   user_id=user_emma_id,  project_id=project_intern_id,  document_type_id=dt_report_id,   name="Website Specification",  user_prompt="Website redesign requirements",           file_path="uploads/documents/website_specification.pdf", status="draft"),
            Document(document_id=doc_invoice_id,   user_id=user_peter_id, project_id=project_hiring_id,  document_type_id=dt_offer_id,    name="Laptop Invoice",         user_prompt="Office equipment purchase invoice",       file_path="uploads/documents/laptop_invoice.pdf",        status="published"),
        ])

        await db.flush()

        # Metadata
        db.add_all([
            DocumentMetadata(document_id=doc_cv_id,        name="author",                value="Emma Smith"),
            DocumentMetadata(document_id=doc_cv_id,        name="year",                  value="2026"),
            DocumentMetadata(document_id=doc_cv_id,        name="category",              value="planning"),
            DocumentMetadata(document_id=doc_cv_id,        name="language",              value="English"),
            DocumentMetadata(document_id=doc_interview_id, name="author",                value="Anna Smith"),
            DocumentMetadata(document_id=doc_interview_id, name="year",                  value="2026"),
            DocumentMetadata(document_id=doc_interview_id, name="category",              value="report"),
            DocumentMetadata(document_id=doc_interview_id, name="version",               value="1.0"),
            DocumentMetadata(document_id=doc_contract_id,  name="author",                value="Mark Johnson"),
            DocumentMetadata(document_id=doc_contract_id,  name="year",                  value="2026"),
            DocumentMetadata(document_id=doc_contract_id,  name="category",              value="legal"),
            DocumentMetadata(document_id=doc_contract_id,  name="priority",              value="high"),
            DocumentMetadata(document_id=doc_website_id,   name="author",                value="Emma Smith"),
            DocumentMetadata(document_id=doc_website_id,   name="year",                  value="2026"),
            DocumentMetadata(document_id=doc_website_id,   name="category",              value="finance"),
            DocumentMetadata(document_id=doc_website_id,   name="currency",              value="EUR"),
            DocumentMetadata(document_id=doc_invoice_id,   name="author",                value="Peter Brown"),
            DocumentMetadata(document_id=doc_invoice_id,   name="year",                  value="2026"),
            DocumentMetadata(document_id=doc_invoice_id,   name="category",              value="procurement"),
            DocumentMetadata(document_id=doc_invoice_id,   name="contains_personal_data",value="false"),
        ])

        # Tags
        db.add_all([
            Tag(tag_id=tag_project_id,   name="project"),
            Tag(tag_id=tag_report_id,    name="report"),
            Tag(tag_id=tag_env_id,       name="environment"),
            Tag(tag_id=tag_plan_id,      name="plan"),
            Tag(tag_id=tag_finance_id,   name="finance"),
            Tag(tag_id=tag_volunteers_id,name="volunteers"),
        ])

        await db.flush()

        # Document–tag links
        db.add_all([
            IsMarked(document_id=doc_cv_id,        tag_id=tag_project_id),
            IsMarked(document_id=doc_cv_id,        tag_id=tag_plan_id),
            IsMarked(document_id=doc_interview_id, tag_id=tag_report_id),
            IsMarked(document_id=doc_contract_id,  tag_id=tag_plan_id),
            IsMarked(document_id=doc_website_id,   tag_id=tag_finance_id),
            IsMarked(document_id=doc_invoice_id,   tag_id=tag_volunteers_id),
        ])

        # Document permissions
        db.add_all([
            Allows(user_id=user_anna_id,  document_id=doc_cv_id,        permission_id=perm_view_id),
            Allows(user_id=user_anna_id,  document_id=doc_cv_id,        permission_id=perm_update_id),
            Allows(user_id=user_peter_id, document_id=doc_cv_id,        permission_id=perm_view_id),
            Allows(user_id=user_peter_id, document_id=doc_interview_id, permission_id=perm_view_id),
            Allows(user_id=user_peter_id, document_id=doc_interview_id, permission_id=perm_update_id),
            Allows(user_id=user_mark_id,  document_id=doc_website_id,   permission_id=perm_view_id),
            Allows(user_id=user_anna_id,  document_id=doc_invoice_id,   permission_id=perm_view_id),
        ])

        # Activities
        db.add_all([
            Activity(document_id=doc_cv_id,        user_id=user_emma_id,  type=ActivityType.CREATE),
            Activity(document_id=doc_cv_id,        user_id=user_anna_id,  type=ActivityType.VIEW),
            Activity(document_id=doc_interview_id, user_id=user_anna_id,  type=ActivityType.CREATE),
            Activity(document_id=doc_interview_id, user_id=user_peter_id, type=ActivityType.UPDATE),
            Activity(document_id=doc_contract_id,  user_id=user_mark_id,  type=ActivityType.CREATE),
            Activity(document_id=doc_website_id,   user_id=user_emma_id,  type=ActivityType.CREATE),
            Activity(document_id=doc_invoice_id,   user_id=user_peter_id, type=ActivityType.CREATE),
        ])

        # Task workflows
        db.add_all([
            TaskWorkflow(task_workflow_id=wf_intern_id,  name="Internship Task Flow",  created_by=user_emma_id),
            TaskWorkflow(task_workflow_id=wf_hiring_id,  name="Hiring Process Flow",   created_by=user_mark_id),
        ])

        # Workflow steps — insert without next_step_id first (self-referential FK)
        steps = [
            TaskWorkflowStep(step_id=step_i1_id, task_workflow_id=wf_intern_id, status_name="To Do",       is_first=True,  is_last=False),
            TaskWorkflowStep(step_id=step_i2_id, task_workflow_id=wf_intern_id, status_name="In Progress", is_first=False, is_last=False),
            TaskWorkflowStep(step_id=step_i3_id, task_workflow_id=wf_intern_id, status_name="Done",        is_first=False, is_last=True),
            TaskWorkflowStep(step_id=step_h1_id, task_workflow_id=wf_hiring_id, status_name="New",         is_first=True,  is_last=False),
            TaskWorkflowStep(step_id=step_h2_id, task_workflow_id=wf_hiring_id, status_name="Screening",   is_first=False, is_last=False),
            TaskWorkflowStep(step_id=step_h3_id, task_workflow_id=wf_hiring_id, status_name="Interview",   is_first=False, is_last=False),
            TaskWorkflowStep(step_id=step_h4_id, task_workflow_id=wf_hiring_id, status_name="Decision",    is_first=False, is_last=True),
        ]
        db.add_all(steps)
        await db.flush()

        # Now set next_step links
        steps[0].next_step_id = step_i2_id
        steps[1].next_step_id = step_i3_id
        steps[3].next_step_id = step_h2_id
        steps[4].next_step_id = step_h3_id
        steps[5].next_step_id = step_h4_id
        await db.flush()

        # Resources
        db.add_all([
            Resource(resource_id=res_laptop_id,       name="Developer Laptop",  resource_type="Equipment", description="MacBook Pro 14 for developers", status=ResourceStatus.active, total_quantity=5),
            Resource(resource_id=res_meeting_room_id, name="Meeting Room A",    resource_type="Room",      description="Conference room with whiteboard", status=ResourceStatus.active, total_quantity=1),
            Resource(resource_id=res_projector_id,    name="Projector",         resource_type="Equipment", description="HDMI projector for presentations", status=ResourceStatus.active, total_quantity=2),
        ])
          # Workflow Actions
        db.add_all([
            WorkflowAction(action_id=wa_draft_id,   name="Draft",           type="create",  description="Initial document drafting"),
            WorkflowAction(action_id=wa_review_id,   name="Peer Review",     type="review",  description="Review by a team member"),
            WorkflowAction(action_id=wa_approve_id,  name="Manager Approval", type="approve", description="Approval by project manager"),
            WorkflowAction(action_id=wa_revise_id,   name="Revise",          type="edit",    description="Revise document based on feedback"),
            WorkflowAction(action_id=wa_publish_id,  name="Publish",         type="publish", description="Final publish of the document"),
        ])

        # Condition Types
        db.add_all([
            ConditionType(condition_type_id=ct_role_id,     name="Role-based"),
            ConditionType(condition_type_id=ct_doctype_id,  name="Document-type"),
            ConditionType(condition_type_id=ct_approval_id, name="Approval-required"),
        ])

        await db.flush()

        # Tasks
        db.add_all([
            Task(task_id=task_setup_id,      name="Set Up Dev Environment",     description="Configure local dev environment for interns.",       priority=TaskPriority.high,   task_workflow_id=wf_intern_id,  current_step_id=step_i2_id, assigned_user_id=user_anna_id,  project_id=project_intern_id),
            Task(task_id=task_onboarding_id, name="Prepare Onboarding Materials", description="Create onboarding docs and welcome package.",      priority=TaskPriority.medium, task_workflow_id=wf_intern_id,  current_step_id=step_i1_id, assigned_user_id=user_emma_id,  project_id=project_intern_id),
            Task(task_id=task_screening_id,  name="Screen Applications",        description="Review and score received job applications.",         priority=TaskPriority.high,   task_workflow_id=wf_hiring_id,  current_step_id=step_h2_id, assigned_user_id=user_mark_id,  project_id=project_hiring_id),
            Task(task_id=task_interviews_id, name="Schedule Interviews",        description="Coordinate interview slots with all candidates.",     priority=TaskPriority.medium, task_workflow_id=wf_hiring_id,  current_step_id=step_h3_id, assigned_user_id=user_peter_id, project_id=project_hiring_id),
            Task(task_id=task_offers_id,     name="Send Job Offers",            description="Prepare and send offer letters to selected candidates.", priority=TaskPriority.low, task_workflow_id=wf_hiring_id,  current_step_id=step_h4_id, assigned_user_id=user_mark_id,  project_id=project_hiring_id),
        ])

        await db.flush()

        # Subtasks
        db.add_all([
            Subtask(task_id=task_setup_id,      name="Install required tools",       description="Install Node, Python, Docker on intern laptops.", assigned_user_id=user_anna_id),
            Subtask(task_id=task_setup_id,      name="Set up Git repositories",      description="Clone repos and configure SSH keys.",             assigned_user_id=user_anna_id),
            Subtask(task_id=task_onboarding_id, name="Write welcome guide",          description="One-page guide with links and contacts.",         assigned_user_id=user_emma_id),
            Subtask(task_id=task_screening_id,  name="Define scoring criteria",      description="Create scoring rubric for CV evaluation.",        assigned_user_id=user_mark_id),
            Subtask(task_id=task_screening_id,  name="Review 20 applications",       description="First batch of CVs received.",                    assigned_user_id=user_peter_id),
            Subtask(task_id=task_interviews_id, name="Send calendar invites",        description="Email candidates with interview time slots.",     assigned_user_id=user_peter_id),
        ])

        # ── Archive Digitalization project ──────────────────────────────────────
        db.add(Resource(resource_id=resource_scanner_id, name="Scanner", resource_type="Equipment",
                        description="High-speed document scanner", status=ResourceStatus.active, total_quantity=3))

        db.add(Project(project_id=project_archive_id, name="Archive Digitalization",
                       description="Digitization of all company archive documents.",
                       status=ProjectStatus.ACTIVE,
                       start_date=datetime(2026, 2, 1), end_date=datetime(2026, 6, 15)))

        db.add_all([
            TaskWorkflow(task_workflow_id=workflow_technical_id,      name="Technical",       created_by=user_emma_id),
            TaskWorkflow(task_workflow_id=workflow_fieldwork_id,       name="Field Work",      created_by=user_emma_id),
            TaskWorkflow(task_workflow_id=workflow_administrative_id,  name="Administrative",  created_by=user_emma_id),
        ])
        # Conditions
        db.add_all([
            Condition(condition_id=cond_mgr_review_id,    condition_type_id=ct_role_id,     document_type_id=None,          role_id=role_manager_id, description="Only project managers can review"),
            Condition(condition_id=cond_contract_id,      condition_type_id=ct_doctype_id,  document_type_id=dt_contract_id, role_id=None,           description="Applies only to contract documents"),
            Condition(condition_id=cond_admin_approve_id, condition_type_id=ct_approval_id, document_type_id=None,          role_id=role_admin_id,   description="Admin approval required before publish"),
        ])

        # Workflows
        db.add_all([
            Workflow(workflow_id=wf_doc_review_id, name="Document Review Flow", document_type_id=dt_cv_id, created_by=user_emma_id),
            Workflow(workflow_id=wf_contract_id,   name="Contract Approval Flow", document_type_id=dt_contract_id, created_by=user_mark_id),
        ])

        await db.flush()

        db.add_all([
            Work(user_id=user_emma_id,  project_id=project_archive_id, role_id=role_manager_id),
            Work(user_id=user_anna_id,  project_id=project_archive_id, role_id=role_member_id),
            Work(user_id=user_mark_id,  project_id=project_archive_id, role_id=role_member_id),
            Work(user_id=user_peter_id, project_id=project_archive_id, role_id=role_member_id),
        ])

        # Insert steps without next_step_id (self-referential FK)
        archive_steps = [
            # Technical (indices 0-4)
            TaskWorkflowStep(step_id=step_tech_created_id,     task_workflow_id=workflow_technical_id, status_name="Created",      is_first=True,  is_last=False),
            TaskWorkflowStep(step_id=step_tech_development_id, task_workflow_id=workflow_technical_id, status_name="Development",  is_first=False, is_last=False),
            TaskWorkflowStep(step_id=step_tech_testing_id,     task_workflow_id=workflow_technical_id, status_name="Testing",      is_first=False, is_last=False),
            TaskWorkflowStep(step_id=step_tech_review_id,      task_workflow_id=workflow_technical_id, status_name="Under Review", is_first=False, is_last=False),
            TaskWorkflowStep(step_id=step_tech_done_id,        task_workflow_id=workflow_technical_id, status_name="Done",         is_first=False, is_last=True),
            # Field Work (indices 5-8)
            TaskWorkflowStep(step_id=step_field_created_id,    task_workflow_id=workflow_fieldwork_id,  status_name="Created",      is_first=True,  is_last=False),
            TaskWorkflowStep(step_id=step_field_inprogress_id, task_workflow_id=workflow_fieldwork_id,  status_name="In Progress",  is_first=False, is_last=False),
            TaskWorkflowStep(step_id=step_field_review_id,     task_workflow_id=workflow_fieldwork_id,  status_name="Under Review", is_first=False, is_last=False),
            TaskWorkflowStep(step_id=step_field_done_id,       task_workflow_id=workflow_fieldwork_id,  status_name="Done",         is_first=False, is_last=True),
            # Administrative (indices 9-11)
            TaskWorkflowStep(step_id=step_admin_created_id,    task_workflow_id=workflow_administrative_id, status_name="Created",     is_first=True,  is_last=False),
            TaskWorkflowStep(step_id=step_admin_inprogress_id, task_workflow_id=workflow_administrative_id, status_name="In Progress", is_first=False, is_last=False),
            TaskWorkflowStep(step_id=step_admin_done_id,       task_workflow_id=workflow_administrative_id, status_name="Done",        is_first=False, is_last=True),
        ]
        db.add_all(archive_steps)
        await db.flush()

        # Set next_step links (self-ref FK safe after flush)
        archive_steps[0].next_step_id = step_tech_development_id
        archive_steps[1].next_step_id = step_tech_testing_id
        archive_steps[2].next_step_id = step_tech_review_id
        archive_steps[3].next_step_id = step_tech_done_id
        archive_steps[5].next_step_id = step_field_inprogress_id
        archive_steps[6].next_step_id = step_field_review_id
        archive_steps[7].next_step_id = step_field_done_id
        archive_steps[9].next_step_id  = step_admin_inprogress_id
        archive_steps[10].next_step_id = step_admin_done_id
        await db.flush()

        # Tasks (today=2026-05-26; late = deadline past + not done)
        db.add_all([
            Task(task_id=task_scanner_purchase_id, name="Scanner Purchase",
                 description="Procure document scanners for the archive team.",
                 priority=TaskPriority.high,   task_workflow_id=workflow_technical_id,
                 current_step_id=step_tech_done_id,        assigned_user_id=user_peter_id,
                 project_id=project_archive_id, deadline=datetime(2026, 4, 10)),

            Task(task_id=task_doc_scanning_id, name="Document Scanning 2010–2015",
                 description="Scan all archive documents from the period 2010–2015.",
                 priority=TaskPriority.high,   task_workflow_id=workflow_fieldwork_id,
                 current_step_id=step_field_inprogress_id, assigned_user_id=user_mark_id,
                 project_id=project_archive_id, deadline=datetime(2026, 5, 30)),

            Task(task_id=task_file_indexing_id, name="File Indexing",
                 description="Index all scanned files in the document management system.",
                 priority=TaskPriority.high,   task_workflow_id=workflow_administrative_id,
                 current_step_id=step_admin_inprogress_id, assigned_user_id=user_peter_id,
                 project_id=project_archive_id, deadline=datetime(2026, 4, 20)),  # LATE

            Task(task_id=task_quality_review_id, name="Quality Review",
                 description="Review digitized documents for quality and completeness.",
                 priority=TaskPriority.medium, task_workflow_id=workflow_administrative_id,
                 current_step_id=step_admin_done_id,        assigned_user_id=user_anna_id,
                 project_id=project_archive_id, deadline=datetime(2026, 5, 10)),

            Task(task_id=task_server_setup_id, name="Server Setup",
                 description="Configure document storage server and backup system.",
                 priority=TaskPriority.high,   task_workflow_id=workflow_technical_id,
                 current_step_id=step_tech_done_id,        assigned_user_id=user_peter_id,
                 project_id=project_archive_id, deadline=datetime(2026, 4, 30)),

            Task(task_id=task_staff_training_id, name="Staff Training",
                 description="Train archive staff on the new digitization workflow.",
                 priority=TaskPriority.medium, task_workflow_id=workflow_fieldwork_id,
                 current_step_id=step_field_done_id,        assigned_user_id=user_anna_id,
                 project_id=project_archive_id, deadline=datetime(2026, 6, 1)),

            Task(task_id=task_documentation_id, name="Documentation",
                 description="Write system and process documentation.",
                 priority=TaskPriority.low,    task_workflow_id=workflow_administrative_id,
                 current_step_id=step_admin_created_id,    assigned_user_id=user_emma_id,
                 project_id=project_archive_id, deadline=datetime(2026, 6, 10)),

            Task(task_id=task_final_report_id, name="Final Report",
                 description="Compile and submit the final project report.",
                 priority=TaskPriority.low,    task_workflow_id=workflow_administrative_id,
                 current_step_id=step_admin_created_id,    assigned_user_id=user_emma_id,
                 project_id=project_archive_id, deadline=datetime(2026, 6, 15)),
        ])
        # Workflow Has Actions (steps)
        db.add_all([
            WorkflowHasAction(workflow_id=wf_doc_review_id, action_id=wa_draft_id,   next_action=wa_review_id,  is_start_step=True,  condition_id=None),
            WorkflowHasAction(workflow_id=wf_doc_review_id, action_id=wa_review_id,  next_action=wa_approve_id, is_start_step=False, condition_id=cond_mgr_review_id),
            WorkflowHasAction(workflow_id=wf_doc_review_id, action_id=wa_approve_id, next_action=wa_publish_id, is_start_step=False, condition_id=None),
            WorkflowHasAction(workflow_id=wf_doc_review_id, action_id=wa_publish_id, next_action=None,          is_start_step=False, condition_id=None),
            WorkflowHasAction(workflow_id=wf_contract_id,   action_id=wa_draft_id,   next_action=wa_review_id,  is_start_step=True,  condition_id=cond_contract_id),
            WorkflowHasAction(workflow_id=wf_contract_id,   action_id=wa_review_id,  next_action=wa_approve_id, is_start_step=False, condition_id=None),
            WorkflowHasAction(workflow_id=wf_contract_id,   action_id=wa_approve_id, next_action=None,          is_start_step=False, condition_id=cond_admin_approve_id),
        ])

        # Workflow Instances
        db.add_all([
            WorkflowInstance(instance_id=wi_cv_review_id,    workflow_id=wf_doc_review_id, document_id=doc_cv_id,       current_step_id=wa_review_id,  designated_user_id=user_anna_id,  note="CV under peer review"),
            WorkflowInstance(instance_id=wi_contract_flow_id, workflow_id=wf_contract_id,  document_id=doc_contract_id, current_step_id=wa_approve_id, designated_user_id=user_sarah_id, note="Contract awaiting admin approval"),
        ])

        await db.flush()

        db.add_all([
            Subtask(task_id=task_scanner_purchase_id, name="Model selection",
                    description="Compare and select scanner model.", assigned_user_id=user_peter_id,
                    current_status=SubtaskStatus.done, deadline=datetime(2026, 4, 5)),
            Subtask(task_id=task_scanner_purchase_id, name="Purchase order",
                    description="Submit purchase order to finance.", assigned_user_id=user_peter_id,
                    current_status=SubtaskStatus.done, deadline=datetime(2026, 4, 10)),
            Subtask(task_id=task_doc_scanning_id, name="Scanning batch 1 (2010–2012)",
                    description="Scan documents from 2010 to 2012.", assigned_user_id=user_mark_id,
                    current_status=SubtaskStatus.done, deadline=datetime(2026, 4, 25)),
            Subtask(task_id=task_doc_scanning_id, name="Scanning batch 2 (2013–2015)",
                    description="Scan documents from 2013 to 2015.", assigned_user_id=user_mark_id,
                    current_status=SubtaskStatus.in_progress, deadline=datetime(2026, 5, 30)),
            Subtask(task_id=task_quality_review_id, name="Review batch 1",
                    description="Quality check for documents 2010–2012.", assigned_user_id=user_anna_id,
                    current_status=SubtaskStatus.done, deadline=datetime(2026, 5, 5)),
            Subtask(task_id=task_quality_review_id, name="Review batch 2",
                    description="Quality check for documents 2013–2015.", assigned_user_id=user_anna_id,
                    current_status=SubtaskStatus.done, deadline=datetime(2026, 5, 10)),
            Subtask(task_id=task_file_indexing_id, name="Create index structure",
                    description="Define folder and metadata structure.", assigned_user_id=user_peter_id,
                    current_status=SubtaskStatus.done, deadline=datetime(2026, 4, 15)),
            Subtask(task_id=task_file_indexing_id, name="Index batch 1",
                    description="Index scanned files from first batch.", assigned_user_id=user_peter_id,
                    current_status=SubtaskStatus.in_progress, deadline=datetime(2026, 4, 20)),
        ])

        db.add_all([
            TaskResource(task_id=task_scanner_purchase_id, resource_id=resource_scanner_id, quantity=2, status=TaskResourceStatus.in_use),
            TaskResource(task_id=task_doc_scanning_id,     resource_id=res_laptop_id,        quantity=1, status=TaskResourceStatus.in_use),
            TaskResource(task_id=task_server_setup_id,     resource_id=resource_scanner_id,  quantity=1, status=TaskResourceStatus.reserved),
        ])
        # Workflow Instance Steps (with progress)
        db.add_all([
            WorkflowInstanceStep(instance_step_id=wis1_id, instance_id=wi_cv_review_id, action_id=wa_draft_id,   status="completed",   progress=100, assigned_user_id=user_emma_id, note="Draft completed"),
            WorkflowInstanceStep(instance_step_id=wis2_id, instance_id=wi_cv_review_id, action_id=wa_review_id,  status="in_progress", progress=60,  assigned_user_id=user_anna_id, note="Review in progress"),
            WorkflowInstanceStep(instance_step_id=wis3_id, instance_id=wi_cv_review_id, action_id=wa_approve_id, status="pending",     progress=0,   assigned_user_id=None,         note=None),
            WorkflowInstanceStep(instance_step_id=wis4_id, instance_id=wi_contract_flow_id, action_id=wa_draft_id,   status="completed",   progress=100, assigned_user_id=user_mark_id,  note="Contract drafted"),
            WorkflowInstanceStep(instance_step_id=wis5_id, instance_id=wi_contract_flow_id, action_id=wa_approve_id, status="in_progress", progress=30,  assigned_user_id=user_sarah_id, note="Under admin review"),
        ])

        # Document Ratings
        db.add_all([
            DocumentRating(document_id=doc_cv_id,        user_id=user_anna_id,  score=4, comment="Well structured CV, minor formatting issues"),
            DocumentRating(document_id=doc_cv_id,        user_id=user_peter_id, score=5, comment="Excellent candidate profile"),
            DocumentRating(document_id=doc_contract_id,  user_id=user_sarah_id, score=3, comment="Needs clarification on termination clause"),
            DocumentRating(document_id=doc_contract_id,  user_id=user_emma_id,  score=4, comment="Solid contract, well written"),
            DocumentRating(document_id=doc_interview_id, user_id=user_emma_id,  score=5, comment="Great interview plan"),
            DocumentRating(document_id=doc_invoice_id,   user_id=user_anna_id,  score=2, comment="Missing vendor details"),
        ])

        await db.commit()
        print("Seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
