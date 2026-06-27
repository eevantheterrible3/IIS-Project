from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from routers.auth import router as auth_router
from routers.projects import router as projects_router
from routers.documents import router as documents_router
from routers.task_workflow import router as task_workflow_router
from routers.resource import router as resource_router
from routers.task import router as task_router
from routers.subtask import router as subtask_router
from routers.document_types import router as document_types_router
from routers.section_templates import router as section_templates_router
from routers.document_sections import router as document_sections_router
from routers.pr_home import router as pr_home_router
from routers.pr_projects import router as pr_projects_router
from routers.pr_workflows import router as pr_workflows_router
from routers.pr_resources import router as pr_resources_router
from routers.pr_users import router as pr_users_router
from routers.document_ratings import router as document_ratings_router
from routers.workflows import router as workflows_router
from routers.workflow_actions import router as workflow_actions_router
from routers.workflow_has_actions import router as workflow_has_actions_router
from routers.workflow_instances import router as workflow_instances_router
from routers.condition_types import router as condition_types_router
from routers.conditions import router as conditions_router
from routers.workflow_instance_steps import router as workflow_instance_steps_router
from routers.users import router as users_router

app = FastAPI(title="IIS API")
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(documents_router)
app.include_router(task_workflow_router)
app.include_router(resource_router)
app.include_router(task_router)
app.include_router(subtask_router)
app.include_router(document_types_router)
app.include_router(section_templates_router)
app.include_router(document_sections_router)
app.include_router(pr_home_router)
app.include_router(pr_projects_router)
app.include_router(pr_workflows_router)
app.include_router(pr_resources_router)
app.include_router(pr_users_router)
app.include_router(document_ratings_router)
app.include_router(workflows_router)
app.include_router(workflow_actions_router)
app.include_router(workflow_has_actions_router)
app.include_router(workflow_instances_router)
app.include_router(condition_types_router)
app.include_router(conditions_router)
app.include_router(workflow_instance_steps_router)
app.include_router(users_router, prefix="/users", tags=["users"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}
