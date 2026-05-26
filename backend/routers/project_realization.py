from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.dependencies import get_current_user
from database import get_db
from models.project import Project
from models.resource import Resource
from models.role import Role
from models.subtask import Subtask
from models.task import Task
from models.task_resource import TaskResource, TaskResourceStatus
from models.task_workflow import TaskWorkflow
from models.task_workflow_step import TaskWorkflowStep
from models.user import User
from models.work import Work

router = APIRouter(prefix="/project-realization", tags=["Project Realization"])


# ── helpers ──────────────────────────────────────────────────────────────────

async def _get_member_role(db: AsyncSession) -> Role:
    result = await db.execute(select(Role).where(Role.name == "TEAM_MEMBER"))
    role = result.scalars().first()
    if not role:
        raise HTTPException(status_code=500, detail="TEAM_MEMBER role not found")
    return role


def _is_manager(project: Project, user_id: str) -> bool:
    return any(
        w.user_id == user_id and w.role and w.role.name == "PROJECT_MANAGER"
        for w in project.works
    )


def _order_steps(steps):
    if not steps:
        return []
    step_map = {s.step_id: s for s in steps}
    first = next((s for s in steps if s.is_first), steps[0])
    ordered, visited = [], set()
    current = first
    while current and current.step_id not in visited:
        ordered.append(current)
        visited.add(current.step_id)
        current = step_map.get(current.next_step_id)
    return ordered


# ── GET /projects ─────────────────────────────────────────────────────────────

@router.get("/projects")
async def get_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project).options(
            selectinload(Project.works).selectinload(Work.role),
            selectinload(Project.works).selectinload(Work.user),
        )
    )
    projects = result.scalars().all()

    output = []
    for project in projects:
        manager = next(
            (w.user for w in project.works if w.role and w.role.name == "PROJECT_MANAGER"),
            None,
        )
        output.append({
            "project_id": project.project_id,
            "name": project.name,
            "description": project.description,
            "status": project.status.value if project.status else None,
            "start_date": project.start_date.strftime("%d.%m.%y") if project.start_date else None,
            "end_date": project.end_date.strftime("%d.%m.%y") if project.end_date else None,
            "manager_name": f"{manager.name} {manager.last_name[0]}." if manager else None,
        })

    return output


# ── GET /projects/{project_id} ────────────────────────────────────────────────

@router.get("/projects/{project_id}")
async def get_project_detail(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.project_id == project_id)
        .options(
            selectinload(Project.works).selectinload(Work.role),
            selectinload(Project.works).selectinload(Work.user),
        )
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # tasks with eager-loaded relations
    tasks_result = await db.execute(
        select(Task)
        .where(Task.project_id == project_id)
        .options(
            selectinload(Task.current_step),
            selectinload(Task.assigned_user),
            selectinload(Task.subtasks).selectinload(
                __import__("models.subtask", fromlist=["Subtask"]).Subtask.assigned_user
            ),
            selectinload(Task.resources).selectinload(TaskResource.resource),
        )
    )
    tasks = tasks_result.scalars().all()

    now = datetime.now()

    total = len(tasks)
    completed = sum(1 for t in tasks if t.current_step and t.current_step.is_last)
    late = sum(
        1 for t in tasks
        if t.deadline and t.deadline < now and not (t.current_step and t.current_step.is_last)
    )
    progress = round(completed / total * 100) if total else 0

    # end_date for display
    project_deadline = project.end_date.strftime("%d.%m.%Y") if project.end_date else None

    tasks_data = []
    for t in tasks:
        is_late = bool(t.deadline and t.deadline < now and not (t.current_step and t.current_step.is_last))
        subtasks_data = [
            {
                "subtask_id": s.subtask_id,
                "name": s.name,
                "description": s.description,
                "status": s.current_status.value if s.current_status else None,
                "deadline": s.deadline.strftime("%d.%m.%Y") if s.deadline else None,
                "assigned_user": (
                    f"{s.assigned_user.name} {s.assigned_user.last_name}"
                    if s.assigned_user else None
                ),
            }
            for s in t.subtasks
        ]
        tasks_data.append({
            "task_id": t.task_id,
            "name": t.name,
            "description": t.description,
            "priority": t.priority.value if t.priority else None,
            "status": t.current_step.status_name if t.current_step else None,
            "is_completed": t.current_step.is_last if t.current_step else False,
            "is_late": is_late,
            "deadline": t.deadline.strftime("%d.%m.%Y") if t.deadline else None,
            "assigned_user": (
                f"{t.assigned_user.name} {t.assigned_user.last_name}"
                if t.assigned_user else None
            ),
            "assigned_user_id": t.assigned_user_id,
            "subtasks": subtasks_data,
            "resources": [
                {
                    "resource_id": tr.resource_id,
                    "name": tr.resource.name if tr.resource else tr.resource_id,
                    "resource_type": tr.resource.resource_type if tr.resource else None,
                    "quantity": tr.quantity,
                    "status": tr.status.value if tr.status else None,
                }
                for tr in t.resources
            ],
        })

    members_data = [
        {
            "user_id": w.user_id,
            "name": w.user.name if w.user else "",
            "last_name": w.user.last_name if w.user else "",
            "role": w.role.name if w.role else None,
        }
        for w in project.works
        if w.user
    ]

    return {
        "project_id": project.project_id,
        "name": project.name,
        "description": project.description,
        "status": project.status.value if project.status else None,
        "start_date": project.start_date.strftime("%d.%m.%Y") if project.start_date else None,
        "end_date": project_deadline,
        "is_manager": _is_manager(project, current_user.user_id),
        "stats": {
            "total": total,
            "completed": completed,
            "late": late,
            "progress": progress,
            "deadline": project_deadline,
        },
        "members": members_data,
        "tasks": tasks_data,
    }


# ── GET /users ────────────────────────────────────────────────────────────────

@router.get("/users")
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [
        {
            "user_id": u.user_id,
            "name": u.name,
            "last_name": u.last_name,
            "email": u.email,
        }
        for u in users
    ]


# ── POST /projects/{project_id}/members ───────────────────────────────────────

@router.post("/projects/{project_id}/members", status_code=201)
async def add_member(
    project_id: str,
    body: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.project_id == project_id)
        .options(
            selectinload(Project.works).selectinload(Work.role),
        )
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not _is_manager(project, current_user.user_id):
        raise HTTPException(status_code=403, detail="Only the project manager can add members")

    user_id = body.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    already = any(w.user_id == user_id for w in project.works)
    if already:
        raise HTTPException(status_code=409, detail="User is already a member of this project")

    member_role = await _get_member_role(db)
    db.add(Work(user_id=user_id, project_id=project_id, role_id=member_role.role_id))
    await db.commit()
    return {"detail": "Member added"}


# ── DELETE /projects/{project_id}/members/{user_id} ───────────────────────────

@router.delete("/projects/{project_id}/members/{user_id}", status_code=200)
async def remove_member(
    project_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.project_id == project_id)
        .options(
            selectinload(Project.works).selectinload(Work.role),
        )
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not _is_manager(project, current_user.user_id):
        raise HTTPException(status_code=403, detail="Only the project manager can remove members")

    work = next((w for w in project.works if w.user_id == user_id), None)
    if not work:
        raise HTTPException(status_code=404, detail="Member not found in this project")
    if work.role and work.role.name == "PROJECT_MANAGER":
        raise HTTPException(status_code=400, detail="Cannot remove the project manager")

    await db.delete(work)
    await db.commit()
    return {"detail": "Member removed"}


# ── GET /workflows ────────────────────────────────────────────────────────────

@router.get("/workflows")
async def get_workflows(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TaskWorkflow).options(selectinload(TaskWorkflow.steps))
    )
    workflows = result.scalars().all()
    output = []
    for wf in workflows:
        steps = _order_steps(wf.steps)
        output.append({
            "task_workflow_id": wf.task_workflow_id,
            "name": wf.name,
            "steps": [
                {
                    "step_id": s.step_id,
                    "status_name": s.status_name,
                    "is_first": s.is_first,
                    "is_last": s.is_last,
                }
                for s in steps
            ],
        })
    return output


# ── GET /resources ────────────────────────────────────────────────────────────

@router.get("/resources")
async def get_resources(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Resource))
    resources = result.scalars().all()
    return [
        {
            "resource_id": r.resource_id,
            "name": r.name,
            "resource_type": r.resource_type,
            "total_quantity": r.total_quantity,
            "status": r.status.value if r.status else None,
        }
        for r in resources
    ]


# ── POST /projects/{project_id}/tasks ─────────────────────────────────────────

@router.post("/projects/{project_id}/tasks", status_code=201)
async def create_task(
    project_id: str,
    body: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.project_id == project_id)
        .options(selectinload(Project.works).selectinload(Work.role))
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not _is_manager(project, current_user.user_id):
        raise HTTPException(status_code=403, detail="Only the project manager can create tasks")

    workflow_id = body.get("task_workflow_id")
    if not workflow_id:
        raise HTTPException(status_code=400, detail="task_workflow_id is required")

    steps_result = await db.execute(
        select(TaskWorkflowStep).where(TaskWorkflowStep.task_workflow_id == workflow_id)
    )
    steps = steps_result.scalars().all()
    first_step = next((s for s in steps if s.is_first), None)
    if not first_step:
        raise HTTPException(status_code=400, detail="Selected workflow has no first step")

    deadline_str = body.get("deadline")
    deadline = datetime.strptime(deadline_str, "%Y-%m-%d") if deadline_str else None

    task = Task(
        name=body["name"],
        description=body.get("description") or None,
        priority=body.get("priority") or None,
        task_workflow_id=workflow_id,
        current_step_id=first_step.step_id,
        deadline=deadline,
        assigned_user_id=body.get("assigned_user_id") or None,
        project_id=project_id,
    )
    db.add(task)
    await db.flush()

    for st in body.get("subtasks", []):
        if st.get("name", "").strip():
            db.add(Subtask(task_id=task.task_id, name=st["name"].strip()))

    for res in body.get("resources", []):
        rid = res.get("resource_id")
        if not rid:
            continue
        rf = res.get("reserved_from")
        ru = res.get("reserved_until")
        db.add(TaskResource(
            task_id=task.task_id,
            resource_id=rid,
            quantity=int(res.get("quantity") or 1),
            reserved_from=datetime.strptime(rf, "%Y-%m-%d") if rf else None,
            reserved_until=datetime.strptime(ru, "%Y-%m-%d") if ru else None,
            status=TaskResourceStatus.reserved,
        ))

    await db.commit()
    return {"task_id": task.task_id, "detail": "Task created"}
