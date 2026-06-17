from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.subtask import Subtask
from models.task import Task
from models.task_resource import TaskResource
from models.task_status_history import TaskStatusHistory
from models.task_workflow import TaskWorkflow


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_project(self, project_id: str):
        result = await self.db.execute(
            select(Task).where(Task.project_id == project_id)
        )
        return result.scalars().all()

    async def get_by_id(self, task_id: str):
        result = await self.db.execute(
            select(Task).where(Task.task_id == task_id)
        )
        return result.scalar_one_or_none()

    async def create(self, task: Task):
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def update(self, task: Task):
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete(self, task: Task):
        await self.db.delete(task)
        await self.db.commit()

    # ── Project Realization methods ───────────────────────────────────────────

    async def get_by_project_with_relations(self, project_id: str):
        result = await self.db.execute(
            select(Task)
            .where(Task.project_id == project_id)
            .options(
                selectinload(Task.current_step),
                selectinload(Task.assigned_user),
                selectinload(Task.subtasks).selectinload(Subtask.assigned_user),
                selectinload(Task.resources).selectinload(TaskResource.resource),
            )
        )
        return result.scalars().all()

    async def get_detail_with_relations(self, task_id: str):
        result = await self.db.execute(
            select(Task)
            .where(Task.task_id == task_id)
            .options(
                selectinload(Task.current_step),
                selectinload(Task.assigned_user),
                selectinload(Task.project),
                selectinload(Task.subtasks).selectinload(Subtask.assigned_user),
                selectinload(Task.workflow).selectinload(TaskWorkflow.steps),
            )
        )
        return result.scalar_one_or_none()

    async def add_status_history(self, task_id: str, old_step_id: str | None, new_step_id: str, user_id: str):
        history = TaskStatusHistory(
            task_id=task_id,
            old_step_id=old_step_id,
            new_step_id=new_step_id,
            changed_by_user_id=user_id,
        )
        self.db.add(history)
        await self.db.commit()
        return history

    async def create_with_resources(self, task: Task, subtasks: list, resources: list):
        self.db.add(task)
        for s in subtasks:
            self.db.add(s)
        for r in resources:
            self.db.add(r)
        await self.db.commit()
        await self.db.refresh(task)
        return task
