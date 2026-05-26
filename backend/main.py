from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from routers.auth import router as auth_router
from routers.projects import router as projects_router
from routers.documents import router as documents_router
from routers.document_types import router as document_types_router
from routers.section_templates import router as section_templates_router
from routers.document_sections import router as document_sections_router
from routers.document_ratings import router as document_ratings_router
from routers.workflows import router as workflows_router
from routers.workflow_actions import router as workflow_actions_router
from routers.workflow_has_actions import router as workflow_has_actions_router
from routers.workflow_instances import router as workflow_instances_router
from routers.condition_types import router as condition_types_router
from routers.conditions import router as conditions_router

app = FastAPI(title="IIS API")
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(documents_router)
app.include_router(document_types_router)
app.include_router(section_templates_router)
app.include_router(document_sections_router)
app.include_router(document_ratings_router)
app.include_router(workflows_router)
app.include_router(workflow_actions_router)
app.include_router(workflow_has_actions_router)
app.include_router(workflow_instances_router)
app.include_router(condition_types_router)
app.include_router(conditions_router)

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
