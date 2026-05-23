from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from routers.auth import router as auth_router
from routers.projects import router as projects_router
from routers.documents import router as documents_router
from routers.document_types import router as document_types_router
from routers.section_templates import router as section_templates_router
from routers.document_sections import router as document_sections_router

app = FastAPI(title="IIS API")
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(documents_router)
app.include_router(document_types_router)
app.include_router(section_templates_router)
app.include_router(document_sections_router)

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
