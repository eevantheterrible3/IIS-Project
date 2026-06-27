from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository
from schemas.project_schema import HomeMyTask, HomeProjectItem, HomeResponse

router = APIRouter(prefix="/project-realization", tags=["PR Home"])


@router.get("/home", response_model=HomeResponse)
async def get_home(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uid = current_user.user_id
    is_admin = await ProjectRepository(db).is_user_admin(uid)
    projects = await ProjectRepository(db).get_all_with_members()
    if not is_admin:
        projects = [p for p in projects if any(w.user_id == uid for w in p.works)]

    project_ids = [p.project_id for p in projects]
    tasks = await TaskRepository(db).get_for_projects(project_ids)

    now = datetime.now()
    tasks_by_project: dict[str, list] = {}
    for t in tasks:
        tasks_by_project.setdefault(t.project_id, []).append(t)

    stats_active = 0
    stats_late = 0
    home_projects: list[HomeProjectItem] = []

    for p in projects:
        ptasks = tasks_by_project.get(p.project_id, [])
        total = len(ptasks)
        completed = sum(1 for t in ptasks if t.current_step and t.current_step.is_last)
        late = sum(
            1 for t in ptasks
            if t.deadline and t.deadline < now
            and not (t.current_step and t.current_step.is_last)
        )
        progress = round(completed / total * 100) if total else 0
        stats_active += total - completed
        stats_late += late

        manager = next(
            (w.user for w in p.works if w.role and w.role.name == "PROJECT_MANAGER"),
            None,
        )
        home_projects.append(HomeProjectItem(
            project_id=p.project_id,
            name=p.name,
            status=p.status.value if p.status else None,
            member_count=len(p.works),
            manager_name=f"{manager.name} {manager.last_name[0]}." if manager else None,
            deadline=p.end_date.strftime("%d.%m.%Y") if p.end_date else None,
            task_total=total,
            task_completed=completed,
            task_late=late,
            progress=progress,
        ))

    my_tasks: list[HomeMyTask] = []
    for t in tasks:
        if t.assigned_user_id == uid:
            is_late = bool(
                t.deadline and t.deadline < now
                and not (t.current_step and t.current_step.is_last)
            )
            is_completed = bool(t.current_step and t.current_step.is_last)
            project = next((p for p in projects if p.project_id == t.project_id), None)
            my_tasks.append(HomeMyTask(
                task_id=t.task_id,
                name=t.name,
                project_name=project.name if project else "",
                project_id=t.project_id,
                status=t.current_step.status_name if t.current_step else None,
                priority=t.priority.value if t.priority else None,
                deadline=t.deadline.strftime("%d.%m.%Y") if t.deadline else None,
                is_late=is_late,
                is_completed=is_completed,
            ))

    my_tasks.sort(key=lambda t: (t.is_completed, not t.is_late, t.deadline or "9999"))

    return HomeResponse(
        stats_projects=len(projects),
        stats_active=stats_active,
        stats_late=stats_late,
        projects=home_projects,
        my_tasks=my_tasks,
    )
