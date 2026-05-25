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
            Project(project_id=project_intern_id,  name="Summer Internship 2026",  description="Project for organizing summer internship applications.", status=ProjectStatus.ACTIVE),
            Project(project_id=project_hiring_id,  name="Employee Hiring Process", description="Project for managing job applications and interviews.",  status=ProjectStatus.ACTIVE),
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

        await db.commit()
        print("Seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
