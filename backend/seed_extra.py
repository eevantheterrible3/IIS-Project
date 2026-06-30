"""
Extra seed data for report testing.
Run: docker compose exec backend python seed_extra.py
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database import DATABASE_URL
from models.document import Document
from models.workflow import Workflow
from models.workflow_action import WorkflowAction
from models.workflow_has_action import WorkflowHasAction
from models.workflow_instance import WorkflowInstance
from models.workflow_instance_step import WorkflowInstanceStep

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Existing IDs
user_emma = "394ea76b-6ae8-4158-a8ee-03b1685c8572"
user_anna = "90347bf2-1504-427b-a734-e11ab1638e50"
user_mark = "f6847b1b-1e9c-4cc2-a5d1-7a57958c0fa4"
user_peter = "99343c4f-e7b2-4dbf-9c3c-1be5d2f9eb76"
user_sarah = "ba6f5b26-72bb-401b-acad-b9bbf706258f"

project_summer = "b37ed313-2e44-4fa2-b66c-e9c209e3f90e"
project_hiring = "4dbeb3d3-7a9a-43b2-8b0c-aef8e3a15c72"

type_cv = "0016c303-97ce-4b6e-8291-e44c1e tried"
type_contract = "71de58c6-7be7-498a-8a8c-4e08f6d7f5e3"
type_report = "aa15dc11-3b17-47a4-bf73-19468c84f6d3"
type_joboffer = "5baf81c6-f4f4-4c4e-b4e6-3c0e6e2f5a1b"

# Existing actions
action_draft = "7a3ad23f-d6e4-41b4-ba50-200df9c51d4d"
action_review = "bb6c8bf5-42a5-450c-8c03-458392479e08"
action_approval = "6ebc89bf-6dd7-47c9-890e-2379d6a0ed2f"
action_revise = "f0ca277a-1234-4567-890a-bcdef0123456"
action_publish = "be6d6620-abcd-4567-890a-bcdef0123456"

def uid():
    return str(uuid.uuid4())


async def main():
    async with AsyncSessionLocal() as db:
        # --- Fetch actual IDs for actions, doc types ---
        from sqlalchemy import select, text
        rows = await db.execute(text("SELECT action_id, name FROM workflow_actions"))
        actions = {r[1]: r[0] for r in rows.all()}
        print("Actions:", actions)

        rows = await db.execute(text("SELECT document_type_id, name FROM document_types"))
        dtypes = {r[1]: r[0] for r in rows.all()}
        print("Doc types:", dtypes)

        rows = await db.execute(text("SELECT user_id, name FROM users"))
        users = {r[1]: r[0] for r in rows.all()}
        print("Users:", users)

        rows = await db.execute(text("SELECT project_id, name FROM projects"))
        projects = {r[1]: r[0] for r in rows.all()}
        print("Projects:", projects)

        a_draft = actions["Draft"]
        a_review = actions["Peer Review"]
        a_approval = actions["Manager Approval"]
        a_revise = actions["Revise"]
        a_publish = actions["Publish"]

        t_cv = dtypes["CV / Resume"]
        t_contract = dtypes["Contract"]
        t_report = dtypes["Project Report"]
        t_joboffer = dtypes["Job Offer"]

        u_emma = users["Emma"]
        u_anna = users["Anna"]
        u_mark = users["Mark"]
        u_peter = users["Peter"]
        u_sarah = users["Sarah"]

        p_summer = projects["Summer Internship 2026"]
        p_hiring = projects["Employee Hiring Process"]

        now = datetime.now()

        # ============ NEW DOCUMENTS ============
        docs = []
        doc_data = [
            ("Backend Developer CV", t_cv, u_mark, p_hiring),
            ("QA Engineer CV", t_cv, u_anna, p_hiring),
            ("Ivan Ristic Employment Contract", t_contract, u_emma, p_hiring),
            ("Partner NDA Agreement", t_contract, u_sarah, p_summer),
            ("Sprint 1 Report", t_report, u_peter, p_summer),
            ("Sprint 2 Report", t_report, u_peter, p_summer),
            ("Junior Developer Offer", t_joboffer, u_anna, p_hiring),
            ("Senior Designer Offer", t_joboffer, u_emma, p_hiring),
            ("DevOps Engineer CV", t_cv, u_sarah, p_summer),
            ("Final Project Report", t_report, u_mark, p_summer),
        ]
        for name, dtype, user, project in doc_data:
            d = Document(
                document_id=uid(), name=name, document_type_id=dtype,
                user_id=user, project_id=project, status="draft",
            )
            db.add(d)
            docs.append(d)

        # ============ NEW WORKFLOWS ============
        wf_report_id = uid()
        wf_joboffer_id = uid()

        wf_report = Workflow(
            workflow_id=wf_report_id, name="Report Review Flow",
            document_type_id=t_report, created_by=u_emma,
        )
        wf_joboffer = Workflow(
            workflow_id=wf_joboffer_id, name="Job Offer Approval",
            document_type_id=t_joboffer, created_by=u_sarah,
        )
        db.add(wf_report)
        db.add(wf_joboffer)

        # Workflow actions linkage: Report Review Flow: Draft -> Review -> Approval -> Publish
        db.add(WorkflowHasAction(workflow_id=wf_report_id, action_id=a_draft, next_action=a_review, is_start_step=True, step_order=1))
        db.add(WorkflowHasAction(workflow_id=wf_report_id, action_id=a_review, next_action=a_approval, is_start_step=False, step_order=2))
        db.add(WorkflowHasAction(workflow_id=wf_report_id, action_id=a_approval, next_action=a_publish, is_start_step=False, step_order=3))
        db.add(WorkflowHasAction(workflow_id=wf_report_id, action_id=a_publish, next_action=None, is_start_step=False, step_order=4))

        # Job Offer Approval: Draft -> Approval -> Publish
        db.add(WorkflowHasAction(workflow_id=wf_joboffer_id, action_id=a_draft, next_action=a_approval, is_start_step=True, step_order=1))
        db.add(WorkflowHasAction(workflow_id=wf_joboffer_id, action_id=a_approval, next_action=a_publish, is_start_step=False, step_order=2))
        db.add(WorkflowHasAction(workflow_id=wf_joboffer_id, action_id=a_publish, next_action=None, is_start_step=False, step_order=3))

        await db.flush()

        # Existing workflow IDs
        rows = await db.execute(text("SELECT workflow_id, name, document_type_id FROM workflows"))
        wfs = {r[1]: (r[0], r[2]) for r in rows.all()}
        print("Workflows:", {k: v[0][:8] for k, v in wfs.items()})

        wf_cv_id = wfs["Document Review Flow"][0]
        wf_contract_id = wfs["Contract Approval Flow"][0]

        # ============ WORKFLOW INSTANCES WITH VARIED STATES ============
        instances_config = [
            # (doc_index, workflow_name, designated_user, started_days_ago, steps_config)
            # steps_config: list of (action_id, status, progress, assigned_user, updated_days_ago)

            # 1. Backend Developer CV - fully completed 5 days ago
            (0, "Document Review Flow", u_mark, 12, [
                (a_draft, "completed", 100, u_mark, 10),
                (a_review, "completed", 100, u_anna, 7),
                (a_approval, "completed", 100, u_sarah, 5),
            ], True, 5),

            # 2. QA Engineer CV - review in progress, 60%
            (1, "Document Review Flow", u_anna, 4, [
                (a_draft, "completed", 100, u_anna, 3),
                (a_review, "in_progress", 60, u_peter, 1),
                (a_approval, "pending", 0, None, None),
            ], False, None),

            # 3. Ugovor za Ivana - approval stage, 80%
            (2, "Contract Approval Flow", u_emma, 8, [
                (a_draft, "completed", 100, u_emma, 6),
                (a_approval, "in_progress", 80, u_sarah, 2),
            ], False, None),

            # 4. NDA Ugovor - completed 1 day ago
            (3, "Contract Approval Flow", u_sarah, 15, [
                (a_draft, "completed", 100, u_sarah, 12),
                (a_approval, "completed", 100, u_emma, 1),
            ], True, 1),

            # 5. Sprint 1 Izvestaj - completed 10 days ago
            (4, "Report Review Flow", u_peter, 20, [
                (a_draft, "completed", 100, u_peter, 18),
                (a_review, "completed", 100, u_mark, 15),
                (a_approval, "completed", 100, u_sarah, 12),
                (a_publish, "completed", 100, u_peter, 10),
            ], True, 10),

            # 6. Sprint 2 Izvestaj - in review, 30%
            (5, "Report Review Flow", u_peter, 6, [
                (a_draft, "completed", 100, u_peter, 5),
                (a_review, "in_progress", 30, u_anna, 3),
                (a_approval, "pending", 0, None, None),
                (a_publish, "pending", 0, None, None),
            ], False, None),

            # 7. Ponuda za Junior Dev - just started, draft in progress
            (6, "Job Offer Approval", u_anna, 1, [
                (a_draft, "in_progress", 25, u_anna, 0),
                (a_approval, "pending", 0, None, None),
                (a_publish, "pending", 0, None, None),
            ], False, None),

            # 8. Ponuda za Senior Designera - completed 3 days ago
            (7, "Job Offer Approval", u_emma, 10, [
                (a_draft, "completed", 100, u_emma, 8),
                (a_approval, "completed", 100, u_sarah, 5),
                (a_publish, "completed", 100, u_emma, 3),
            ], True, 3),

            # 9. DevOps CV - draft completed, waiting for review assignment
            (8, "Document Review Flow", u_sarah, 3, [
                (a_draft, "completed", 100, u_sarah, 2),
                (a_review, "in_progress", 10, u_mark, 1),
                (a_approval, "pending", 0, None, None),
            ], False, None),

            # 10. Zavrsni projektni izvestaj - almost done, publishing
            (9, "Report Review Flow", u_mark, 14, [
                (a_draft, "completed", 100, u_mark, 13),
                (a_review, "completed", 100, u_emma, 10),
                (a_approval, "completed", 100, u_sarah, 7),
                (a_publish, "in_progress", 90, u_mark, 0),
            ], False, None),
        ]

        for doc_idx, wf_name, designated, started_ago, steps_cfg, is_completed, completed_ago in instances_config:
            doc = docs[doc_idx]
            wf_id = wfs[wf_name][0]

            # Find current step (last in_progress, or last completed if all done)
            current_action = None
            for action_id, status, *_ in steps_cfg:
                if status == "in_progress":
                    current_action = action_id
                    break
            if is_completed:
                current_action = steps_cfg[-1][0]

            inst = WorkflowInstance(
                instance_id=uid(), workflow_id=wf_id, document_id=doc.document_id,
                current_step_id=current_action, designated_user_id=designated,
                note=None,
                started_at=now - timedelta(days=started_ago),
                completed_at=(now - timedelta(days=completed_ago)) if is_completed else None,
            )
            db.add(inst)
            await db.flush()

            for action_id, status, progress, assigned, updated_ago in steps_cfg:
                step = WorkflowInstanceStep(
                    instance_step_id=uid(), instance_id=inst.instance_id,
                    action_id=action_id, status=status, progress=progress,
                    assigned_user_id=assigned, note=None,
                    created_at=now - timedelta(days=started_ago),
                    updated_at=(now - timedelta(days=updated_ago)) if updated_ago is not None else None,
                )
                db.add(step)

        await db.commit()
        print("\nSeeded 10 documents, 2 workflows, 10 instances with varied steps.")


asyncio.run(main())
