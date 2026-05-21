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

app = FastAPI(title="IIS API")
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(documents_router)
app.include_router(task_workflow_router)
app.include_router(resource_router)
app.include_router(task_router)
app.include_router(subtask_router)

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
