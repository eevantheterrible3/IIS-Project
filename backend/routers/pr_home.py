from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository
from repositories.task_resource_repository import TaskResourceRepository
from schemas.project_schema import HomeMyTask, HomeProjectItem, HomeResponse, ReportProjectItem, ReportWorkflowStep, ReportMember, ReportResponse
from services.pdf_report_service import generate_report_pdf

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

    stats_total = sum(p.task_total for p in home_projects)
    stats_completed = sum(p.task_completed for p in home_projects)

    return HomeResponse(
        stats_projects=len(projects),
        stats_total_tasks=stats_total,
        stats_active=stats_active,
        stats_completed=stats_completed,
        stats_late=stats_late,
        projects=home_projects,
        my_tasks=my_tasks,
    )


@router.get("/report", response_model=ReportResponse)
async def get_report(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uid = current_user.user_id
    is_admin = await ProjectRepository(db).is_user_admin(uid)
    projects = await ProjectRepository(db).get_all_with_members()
    if not is_admin:
        projects = [p for p in projects if any(w.user_id == uid for w in p.works)]

    project_ids = [p.project_id for p in projects]
    tasks = await TaskRepository(db).get_report(project_ids)

    now = datetime.now()
    tasks_by_project: dict[str, list] = {}
    for t in tasks:
        tasks_by_project.setdefault(t.project_id, []).append(t)

    report_projects: list[ReportProjectItem] = []
    stats_active = 0
    stats_late = 0

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
        report_projects.append(ReportProjectItem(
            name=p.name,
            task_total=total,
            task_completed=completed,
            task_late=late,
            progress=progress,
            deadline=p.end_date.strftime("%d.%m.%Y") if p.end_date else None,
            manager_name=f"{manager.name} {manager.last_name}" if manager else None,
        ))

    stats_total = sum(p.task_total for p in report_projects)
    stats_completed = sum(p.task_completed for p in report_projects)

    step_counts: dict[str, int] = {}
    for t in tasks:
        if t.current_step:
            name = t.current_step.status_name
            step_counts[name] = step_counts.get(name, 0) + 1

    workflow_steps = [
        ReportWorkflowStep(step_name=k, task_count=v)
        for k, v in sorted(step_counts.items(), key=lambda x: -x[1])
    ]

    member_stats: dict[str, dict] = {}
    for t in tasks:
        if t.assigned_user:
            name = f"{t.assigned_user.name} {t.assigned_user.last_name}"
            if name not in member_stats:
                member_stats[name] = {"active": 0, "completed": 0}
            if t.current_step and t.current_step.is_last:
                member_stats[name]["completed"] += 1
            else:
                member_stats[name]["active"] += 1

    members = [
        ReportMember(name=k, active_tasks=v["active"], completed_tasks=v["completed"])
        for k, v in sorted(member_stats.items(), key=lambda x: -(x[1]["active"] + x[1]["completed"]))
    ]

    return ReportResponse(
        generated_at=now.strftime("%d.%m.%Y %H:%M"),
        stats_projects=len(projects),
        stats_total_tasks=stats_total,
        stats_completed=stats_completed,
        stats_active=stats_active,
        stats_late=stats_late,
        projects=report_projects,
        workflow_steps=workflow_steps,
        members=members,
    )


@router.get("/report/download")
async def download_report(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uid = current_user.user_id
    is_admin = await ProjectRepository(db).is_user_admin(uid)
    projects = await ProjectRepository(db).get_all_with_members()
    if not is_admin:
        projects = [p for p in projects if any(w.user_id == uid for w in p.works)]

    is_pm = any(
        any(w.user_id == uid and w.role and w.role.name == "PROJECT_MANAGER" for w in p.works)
        for p in projects
    )
    if not is_admin and not is_pm:
        raise HTTPException(status_code=403, detail="Only admins and project managers can generate reports.")

    project_ids = [p.project_id for p in projects]
    tasks = await TaskRepository(db).get_report(project_ids)
    task_resources = await TaskResourceRepository(db).get_all_with_resource()

    now = datetime.now()
    tasks_by_project: dict[str, list] = {}
    for t in tasks:
        tasks_by_project.setdefault(t.project_id, []).append(t)

    proj_rows = []
    stats_active = stats_late = 0
    for p in projects:
        ptasks = tasks_by_project.get(p.project_id, [])
        total = len(ptasks)
        completed = sum(1 for t in ptasks if t.current_step and t.current_step.is_last)
        late = sum(1 for t in ptasks if t.deadline and t.deadline < now and not (t.current_step and t.current_step.is_last))
        progress = round(completed / total * 100) if total else 0
        stats_active += total - completed
        stats_late += late
        manager = next((w.user for w in p.works if w.role and w.role.name == "PROJECT_MANAGER"), None)
        proj_rows.append({
            "name": p.name,
            "manager": f"{manager.name} {manager.last_name}" if manager else "—",
            "deadline": p.end_date.strftime("%d.%m.%Y") if p.end_date else "—",
            "total": total, "completed": completed, "late": late, "progress": progress,
        })

    stats_total = sum(r["total"] for r in proj_rows)
    stats_completed = sum(r["completed"] for r in proj_rows)

    resource_map: dict[str, dict] = {}
    for tr in task_resources:
        if tr.resource and tr.task_id in {t.task_id for t in tasks}:
            rid = tr.resource_id
            if rid not in resource_map:
                resource_map[rid] = {"name": tr.resource.name, "type": tr.resource.resource_type or "—", "quantity": tr.resource.total_quantity, "count": 0, "quantity_used": 0}
            resource_map[rid]["count"] += 1
            resource_map[rid]["quantity_used"] += tr.quantity or 1
    res_rows = sorted(resource_map.values(), key=lambda x: -x["count"])

    priority_counts: dict[str, int] = {}
    step_counts: dict[str, int] = {"Not started": 0, "In progress": 0, "Completed": 0}
    for t in tasks:
        key = t.priority.value if t.priority else "none"
        priority_counts[key] = priority_counts.get(key, 0) + 1
        if t.current_step:
            if t.current_step.is_last:
                step_counts["Completed"] += 1
            elif t.current_step.is_first:
                step_counts["Not started"] += 1
            else:
                step_counts["In progress"] += 1

    project_name_map = {p.project_id: p.name for p in projects}
    unassigned_rows = sorted(
        [{"project": project_name_map.get(t.project_id, "—"), "task": t.name}
         for t in tasks if not t.assigned_user_id],
        key=lambda x: x["project"],
    )

    pdf_bytes = generate_report_pdf(
        generated_at=now.strftime("%d.%m.%Y %H:%M"),
        generated_by=f"{current_user.name} {current_user.last_name}",
        stats_total=stats_total,
        stats_completed=stats_completed,
        stats_active=stats_active,
        stats_late=stats_late,
        proj_rows=proj_rows,
        res_rows=res_rows,
        priority_counts=priority_counts,
        unassigned_rows=unassigned_rows,
        step_counts=step_counts,
    )
    filename = f"Report_{now.strftime('%d.%m.%Y')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
