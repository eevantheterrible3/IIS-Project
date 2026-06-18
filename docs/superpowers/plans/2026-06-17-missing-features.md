# Missing Features Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add missing schemas, role-based sidebar, activity logging with auto-tracking, and project manager pages (assignment, comments, approval).

**Architecture:** Follow the existing 3-layer backend pattern (router → service → repository). Frontend follows existing patterns — Shadcn UI + Tailwind for list pages (like DocumentsList.jsx), CrudPages.css for card-based pages (like WorkflowInstancesList.jsx). New Comment model for version comments. Activity auto-logging added inline to existing document service methods.

**Tech Stack:** FastAPI, SQLAlchemy async, PostgreSQL, Alembic, React, Vite, Shadcn UI, Tailwind CSS

---

## File Map

### New files

| File | Purpose |
|------|---------|
| `backend/models/comment.py` | Comment model (document version comments) |
| `backend/schemas/comment_schema.py` | Comment create/response schemas |
| `backend/schemas/activity_schema.py` | Activity response/filter schemas |
| `backend/repositories/comment_repository.py` | Comment DB queries |
| `backend/repositories/activity_repository.py` | Activity DB queries with filters |
| `backend/services/activity_service.py` | Activity business logic + auto-log helper |
| `backend/routers/activities.py` | GET /activities with query filters |
| `backend/routers/comments.py` | CRUD for comments on document versions |
| `backend/alembic/versions/xxxx_add_comments_table.py` | Migration for comments table |
| `frontend/src/pages/app/ActivityLog.jsx` | Activity log page with table and filters |
| `frontend/src/pages/app/ProjectDocuments.jsx` | Manager view: project documents with assignment + approval |

### Modified files

| File | Change |
|------|--------|
| `backend/models/__init__.py` | Register Comment model |
| `backend/main.py` | Register activities and comments routers |
| `backend/routers/documents.py` | Add `PUT /documents/{id}/status` endpoint |
| `backend/services/document_service.py` | Add activity auto-logging to create/update/delete |
| `backend/models/document.py` | Add `comments` relationship |
| `frontend/src/components/Sidebar.jsx` | Role-based nav items |
| `frontend/src/App.jsx` | Add routes for ActivityLog, ProjectDocuments |
| `frontend/src/pages/app/DocumentView.jsx` | Add comments tab + approve button for managers |

---

## Task 1: Comment Model + Schema

**Files:**
- Create: `backend/models/comment.py`
- Create: `backend/schemas/comment_schema.py`
- Modify: `backend/models/__init__.py`
- Modify: `backend/models/document.py`

- [ ] **Step 1: Create Comment model**

Create `backend/models/comment.py`:

```python
import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Comment(Base):
    __tablename__ = "comments"

    comment_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    document_id = Column(String(36), ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    version_id = Column(String(36), ForeignKey("document_versions.document_version_id", ondelete="SET NULL"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    document = relationship("Document", back_populates="comments")
    version = relationship("DocumentVersion")
    user = relationship("User")
```

- [ ] **Step 2: Add comments relationship to Document model**

In `backend/models/document.py`, add after the `versions` relationship:

```python
comments = relationship("Comment", back_populates="document", cascade="all, delete-orphan")
```

- [ ] **Step 3: Register Comment in models/__init__.py**

Add to `backend/models/__init__.py`:

```python
from .comment import Comment
```

- [ ] **Step 4: Create comment schemas**

Create `backend/schemas/comment_schema.py`:

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CommentCreateRequest(BaseModel):
    document_id: str
    version_id: Optional[str] = None
    content: str


class CommentResponse(BaseModel):
    comment_id: str
    document_id: str
    version_id: str | None = None
    user_id: str
    user_name: str | None = None
    content: str
    created_at: datetime | None = None
```

- [ ] **Step 5: Create Alembic migration**

Run: `cd /home/uros/Documents/IIS/IIS-Project && docker compose exec backend alembic revision --autogenerate -m "add_comments_table"`

Then verify the generated migration creates the `comments` table with the correct columns and foreign keys.

- [ ] **Step 6: Apply migration**

Run: `docker compose exec backend alembic upgrade head`

---

## Task 2: Activity Log Schemas

**Files:**
- Create: `backend/schemas/activity_schema.py`

- [ ] **Step 1: Create activity schemas**

Create `backend/schemas/activity_schema.py`:

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ActivityResponse(BaseModel):
    activity_id: str
    document_id: str
    document_name: str | None = None
    user_id: str
    user_name: str | None = None
    type: str
    date: datetime | None = None
```

---

## Task 3: Activity Log Backend (Repository + Service + Router)

**Files:**
- Create: `backend/repositories/activity_repository.py`
- Create: `backend/services/activity_service.py`
- Create: `backend/routers/activities.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Create activity repository**

Create `backend/repositories/activity_repository.py`:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.activity import Activity


class ActivityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, user_id: str = None, activity_type: str = None, document_id: str = None):
        query = select(Activity).options(
            selectinload(Activity.user),
            selectinload(Activity.document),
        ).order_by(Activity.date.desc())

        if user_id:
            query = query.where(Activity.user_id == user_id)
        if activity_type:
            query = query.where(Activity.type == activity_type)
        if document_id:
            query = query.where(Activity.document_id == document_id)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, activity: Activity):
        self.db.add(activity)
        await self.db.commit()
        return activity
```

- [ ] **Step 2: Create activity service**

Create `backend/services/activity_service.py`:

```python
from models.activity import Activity, ActivityType
from schemas.activity_schema import ActivityResponse


class ActivityService:
    def __init__(self, activity_repository):
        self.activity_repository = activity_repository

    async def get_activities(self, user_id=None, activity_type=None, document_id=None):
        activities = await self.activity_repository.get_all(user_id, activity_type, document_id)
        return [
            ActivityResponse(
                activity_id=a.activity_id,
                document_id=a.document_id,
                document_name=a.document.name if a.document else None,
                user_id=a.user_id,
                user_name=f"{a.user.name} {a.user.last_name}" if a.user else None,
                type=a.type.value,
                date=a.date,
            )
            for a in activities
        ]

    async def log_activity(self, document_id: str, user_id: str, activity_type: ActivityType):
        activity = Activity(
            document_id=document_id,
            user_id=user_id,
            type=activity_type,
        )
        return await self.activity_repository.create(activity)
```

- [ ] **Step 3: Create activities router**

Create `backend/routers/activities.py`:

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.activity_repository import ActivityRepository
from schemas.activity_schema import ActivityResponse
from services.activity_service import ActivityService

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("", response_model=List[ActivityResponse])
async def get_activities(
    user_id: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    document_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ActivityService(ActivityRepository(db))
    return await service.get_activities(user_id, type, document_id)
```

- [ ] **Step 4: Register activities router in main.py**

In `backend/main.py`, add:

```python
from routers.activities import router as activities_router
```

And:

```python
app.include_router(activities_router)
```

---

## Task 4: Auto-Logging in Document Operations

**Files:**
- Modify: `backend/routers/documents.py`

The simplest approach: add activity logging directly in the router endpoints that already have access to `current_user` and `db`. This avoids refactoring the service layer.

- [ ] **Step 1: Add activity logging to document create endpoint**

In `backend/routers/documents.py`, add imports at the top:

```python
from models.activity import Activity, ActivityType
```

In the `create_document` endpoint, after `doc = await service.create_document(...)`, add:

```python
db.add(Activity(document_id=doc.document_id, user_id=current_user.user_id, type=ActivityType.CREATE))
await db.commit()
```

- [ ] **Step 2: Add activity logging to document delete endpoint**

In `delete_document`, before `return await service.delete_document(document_id)`, add:

```python
db.add(Activity(document_id=document_id, user_id=current_user.user_id, type=ActivityType.DELETE))
await db.flush()
```

- [ ] **Step 3: Add activity logging to document save endpoint**

In `save_document`, after the version is created, add:

```python
db.add(Activity(document_id=document_id, user_id=current_user.user_id, type=ActivityType.UPDATE))
await db.commit()
```

Note: save_document already commits at the end via `version_repo.create()`, so place the Activity add before that create call and remove the separate commit. Or simpler: add it right after the `created = await version_repo.create(version)` line and do a separate commit.

- [ ] **Step 4: Add activity logging to document view endpoint**

In `get_document_details`, after the service call, add:

```python
db.add(Activity(document_id=document_id, user_id=current_user.user_id, type=ActivityType.VIEW))
await db.commit()
```

---

## Task 5: Comments Backend (Repository + Router)

**Files:**
- Create: `backend/repositories/comment_repository.py`
- Create: `backend/routers/comments.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Create comment repository**

Create `backend/repositories/comment_repository.py`:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.comment import Comment


class CommentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_document(self, document_id: str):
        result = await self.db.execute(
            select(Comment)
            .where(Comment.document_id == document_id)
            .options(selectinload(Comment.user))
            .order_by(Comment.created_at.desc())
        )
        return result.scalars().all()

    async def create(self, comment: Comment):
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def delete(self, comment: Comment):
        await self.db.delete(comment)
        await self.db.commit()
```

- [ ] **Step 2: Create comments router**

Create `backend/routers/comments.py`:

```python
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.comment import Comment
from models.user import User
from repositories.comment_repository import CommentRepository
from schemas.comment_schema import CommentCreateRequest, CommentResponse

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.get("/document/{document_id}", response_model=List[CommentResponse])
async def get_document_comments(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CommentRepository(db)
    comments = await repo.get_by_document(document_id)
    return [
        CommentResponse(
            comment_id=c.comment_id,
            document_id=c.document_id,
            version_id=c.version_id,
            user_id=c.user_id,
            user_name=f"{c.user.name} {c.user.last_name}" if c.user else None,
            content=c.content,
            created_at=c.created_at,
        )
        for c in comments
    ]


@router.post("", response_model=CommentResponse)
async def create_comment(
    request: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CommentRepository(db)
    comment = Comment(
        document_id=request.document_id,
        version_id=request.version_id,
        user_id=current_user.user_id,
        content=request.content,
    )
    created = await repo.create(comment)
    return CommentResponse(
        comment_id=created.comment_id,
        document_id=created.document_id,
        version_id=created.version_id,
        user_id=created.user_id,
        user_name=f"{current_user.name} {current_user.last_name}",
        content=created.content,
        created_at=created.created_at,
    )


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CommentRepository(db)
    from sqlalchemy import select
    result = await db.execute(select(Comment).where(Comment.comment_id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Comment not found")
    await repo.delete(comment)
    return {"message": "Comment deleted"}
```

- [ ] **Step 3: Register comments router in main.py**

In `backend/main.py`, add:

```python
from routers.comments import router as comments_router
```

And:

```python
app.include_router(comments_router)
```

---

## Task 6: Document Status Endpoint (for approval)

**Files:**
- Modify: `backend/routers/documents.py`

- [ ] **Step 1: Add PUT /documents/{document_id}/status endpoint**

In `backend/routers/documents.py`, add this new Pydantic model at the top (after imports):

```python
from pydantic import BaseModel as PydanticBase

class StatusUpdateRequest(PydanticBase):
    status: str
```

Add the endpoint:

```python
@router.put("/{document_id}/status")
async def update_document_status(
    document_id: str,
    request: StatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = DocumentRepository(db)
    document = await repo.get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    document.status = request.status
    await db.commit()
    return {"message": "Status updated", "status": request.status}
```

---

## Task 7: Project Members Endpoint (for assignment dropdown)

**Files:**
- Modify: `backend/routers/projects.py`

The manager needs a list of team members in the project for the assignment dropdown.

- [ ] **Step 1: Add GET /projects/{project_id}/members endpoint**

In `backend/routers/projects.py`, add:

```python
@router.get("/{project_id}/members")
async def get_project_members(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Work)
        .where(Work.project_id == project_id)
        .options(selectinload(Work.user), selectinload(Work.role))
    )
    works = result.scalars().all()
    return [
        {
            "user_id": w.user.user_id,
            "name": f"{w.user.name} {w.user.last_name}",
            "role": w.role.name,
        }
        for w in works
    ]
```

Add this import at top of the file if not present:

```python
from sqlalchemy import select
from models.work import Work
```

---

## Task 8: Document Reassignment Endpoint

**Files:**
- Modify: `backend/routers/documents.py`

- [ ] **Step 1: Add PUT /documents/{document_id}/assign endpoint**

```python
class AssignRequest(PydanticBase):
    user_id: str

@router.put("/{document_id}/assign")
async def assign_document(
    document_id: str,
    request: AssignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = DocumentRepository(db)
    document = await repo.get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    document.user_id = request.user_id
    await db.commit()
    return {"message": "Document assigned"}
```

---

## Task 9: Role-Based Sidebar

**Files:**
- Modify: `frontend/src/components/Sidebar.jsx`

- [ ] **Step 1: Rewrite Sidebar with role-based filtering**

The `selectedProject` in localStorage contains `role_name`. Read it and show different nav items per role.

Replace the entire content of `frontend/src/components/Sidebar.jsx`:

```jsx
import { NavLink, useNavigate } from "react-router-dom";
import {
    FileText, Sparkles, Layers, LayoutTemplate, Zap, Plus,
    Cog, GitBranch, Play, Filter, GitMerge, ClipboardList, Activity,
} from "lucide-react";

const allNavItems = [
    { to: "/app/documents", icon: FileText, label: "Documents", roles: ["ADMIN", "PROJECT_MANAGER", "TEAM_MEMBER"] },
    { to: "/app/project-documents", icon: ClipboardList, label: "Project Docs", roles: ["PROJECT_MANAGER"] },
    { to: "/app/document-types", icon: Layers, label: "Document Types", roles: ["ADMIN"] },
    { to: "/app/section-templates", icon: LayoutTemplate, label: "Section Templates", roles: ["ADMIN"] },
    { to: "/app/system-prompts", icon: Zap, label: "System Prompts", roles: ["ADMIN"] },
    { to: "/app/workflow-actions", icon: Cog, label: "Workflow Actions", roles: ["ADMIN"] },
    { to: "/app/workflows", icon: GitBranch, label: "Workflows", roles: ["ADMIN"] },
    { to: "/app/workflow-instances", icon: Play, label: "Instances", roles: ["ADMIN", "PROJECT_MANAGER", "TEAM_MEMBER"] },
    { to: "/app/condition-types", icon: Filter, label: "Condition Types", roles: ["ADMIN"] },
    { to: "/app/conditions", icon: GitMerge, label: "Conditions", roles: ["ADMIN"] },
    { to: "/app/activity-log", icon: Activity, label: "Activity Log", roles: ["ADMIN", "PROJECT_MANAGER"] },
];

export default function Sidebar() {
    const navigate = useNavigate();
    const selectedProject = JSON.parse(localStorage.getItem("selectedProject") || "{}");
    const role = selectedProject.role_name || "TEAM_MEMBER";
    const navItems = allNavItems.filter(item => item.roles.includes(role));

    return (
        <aside className="w-56 flex flex-col bg-slate-900 shrink-0">
            <div className="px-4 py-5 border-b border-slate-700">
                <span className="text-white font-bold text-lg tracking-tight">DocAssist</span>
            </div>

            <div className="px-3 pt-3 pb-2">
                <button
                    onClick={() => navigate("/app/new-document")}
                    className="w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
                >
                    <Plus size={15} />
                    New Document
                </button>
            </div>

            <nav className="flex-1 px-3 pb-3 space-y-0.5">
                {navItems.map(({ to, icon: Icon, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        className={({ isActive }) =>
                            `flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors ${
                                isActive
                                    ? "bg-slate-700 text-white font-medium"
                                    : "text-slate-400 hover:bg-slate-800 hover:text-slate-100"
                            }`
                        }
                    >
                        <Icon size={15} />
                        {label}
                    </NavLink>
                ))}
            </nav>
        </aside>
    );
}
```

---

## Task 10: Activity Log Frontend Page

**Files:**
- Create: `frontend/src/pages/app/ActivityLog.jsx`

- [ ] **Step 1: Create ActivityLog page**

Create `frontend/src/pages/app/ActivityLog.jsx` following the CrudPages.css pattern (same as WorkflowInstancesList):

```jsx
import { useEffect, useState } from "react";
import { authFetch } from "@/lib/api";
import "./CrudPages.css";

const typeColors = {
    create: "green",
    update: "amber",
    delete: "",
    view: "blue",
};

export default function ActivityLog() {
    const [activities, setActivities] = useState([]);
    const [filterType, setFilterType] = useState("");
    const [filterUser, setFilterUser] = useState("");

    useEffect(() => { fetchActivities(); }, []);

    async function fetchActivities() {
        const params = new URLSearchParams();
        if (filterType) params.set("type", filterType);
        if (filterUser) params.set("user_id", filterUser);
        const url = `/activities${params.toString() ? "?" + params : ""}`;
        setActivities(await authFetch(url).then(r => r.json()));
    }

    function handleFilter() { fetchActivities(); }

    return (
        <div className="crud-page">
            <div className="crud-page-header">
                <div>
                    <h1>Activity Log</h1>
                    <p>Track all document operations across the system</p>
                </div>
            </div>

            <div style={{ display: "flex", gap: 12, marginBottom: 20, alignItems: "end" }}>
                <div className="crud-form-group" style={{ marginBottom: 0, minWidth: 160 }}>
                    <label>Action type</label>
                    <select value={filterType} onChange={e => setFilterType(e.target.value)}>
                        <option value="">All</option>
                        <option value="create">Create</option>
                        <option value="update">Update</option>
                        <option value="delete">Delete</option>
                        <option value="view">View</option>
                    </select>
                </div>
                <button className="crud-add-button" onClick={handleFilter} style={{ height: 37 }}>Filter</button>
            </div>

            <table className="crud-table">
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Action</th>
                        <th>Document</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {activities.length === 0 && (
                        <tr><td colSpan={4} style={{ textAlign: "center", padding: 40, color: "#999" }}>No activities found</td></tr>
                    )}
                    {activities.map(a => (
                        <tr key={a.activity_id}>
                            <td>{a.user_name || a.user_id}</td>
                            <td><span className={`crud-badge ${typeColors[a.type] || ""}`}>{a.type}</span></td>
                            <td>{a.document_name || a.document_id}</td>
                            <td>{a.date ? new Date(a.date).toLocaleString() : "—"}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
```

---

## Task 11: Project Documents Page (Manager)

**Files:**
- Create: `frontend/src/pages/app/ProjectDocuments.jsx`

This page lets the project manager see all documents in the selected project, reassign ownership, and change status.

- [ ] **Step 1: Create ProjectDocuments page**

Create `frontend/src/pages/app/ProjectDocuments.jsx`:

```jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { authFetch } from "@/lib/api";
import "./CrudPages.css";

const statusOptions = ["draft", "in_progress", "review", "approved", "published"];

export default function ProjectDocuments() {
    const navigate = useNavigate();
    const selectedProject = JSON.parse(localStorage.getItem("selectedProject") || "{}");
    const projectId = selectedProject.project_id;

    const [documents, setDocuments] = useState([]);
    const [members, setMembers] = useState([]);
    const [assignModal, setAssignModal] = useState(null);
    const [statusModal, setStatusModal] = useState(null);
    const [selectedUserId, setSelectedUserId] = useState("");
    const [selectedStatus, setSelectedStatus] = useState("");

    useEffect(() => {
        if (!projectId) return;
        fetchDocuments();
        authFetch(`/projects/${projectId}/members`).then(r => r.json()).then(setMembers);
    }, [projectId]);

    async function fetchDocuments() {
        const docs = await authFetch(`/projects/${projectId}/documents`).then(r => r.json());
        setDocuments(docs);
    }

    function openAssign(doc) {
        setAssignModal(doc);
        setSelectedUserId(doc.user_id || "");
    }

    function openStatus(doc) {
        setStatusModal(doc);
        setSelectedStatus(doc.status || "draft");
    }

    async function handleAssign() {
        if (!selectedUserId) return;
        const res = await authFetch(`/documents/${assignModal.document_id}/assign`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: selectedUserId }),
        });
        if (!res.ok) { alert("Failed to assign."); return; }
        setAssignModal(null);
        fetchDocuments();
    }

    async function handleStatusChange() {
        const res = await authFetch(`/documents/${statusModal.document_id}/status`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: selectedStatus }),
        });
        if (!res.ok) { alert("Failed to update status."); return; }
        setStatusModal(null);
        fetchDocuments();
    }

    if (!projectId) {
        return <div className="crud-page"><p>No project selected. Please log in again.</p></div>;
    }

    return (
        <div className="crud-page">
            <div className="crud-page-header">
                <div>
                    <h1>Project Documents</h1>
                    <p>{selectedProject.project_name} — Manage assignments and approvals</p>
                </div>
            </div>

            <table className="crud-table">
                <thead>
                    <tr>
                        <th>Document</th>
                        <th>Status</th>
                        <th>Assigned To</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {documents.length === 0 && (
                        <tr><td colSpan={4} style={{ textAlign: "center", padding: 40, color: "#999" }}>No documents in this project</td></tr>
                    )}
                    {documents.map(doc => {
                        const assignee = members.find(m => m.user_id === doc.user_id);
                        return (
                            <tr key={doc.document_id}>
                                <td>
                                    <span
                                        style={{ cursor: "pointer", color: "#2563eb", fontWeight: 600 }}
                                        onClick={() => navigate(`/app/documents/${doc.document_id}`)}
                                    >
                                        {doc.name}
                                    </span>
                                </td>
                                <td>
                                    <span
                                        className={`crud-badge ${doc.status === "approved" ? "green" : doc.status === "review" ? "amber" : ""}`}
                                        style={{ cursor: "pointer" }}
                                        onClick={() => openStatus(doc)}
                                    >
                                        {doc.status}
                                    </span>
                                </td>
                                <td>{assignee ? assignee.name : doc.user_id}</td>
                                <td className="actions-cell">
                                    <button className="edit-action" onClick={() => openAssign(doc)}>Assign</button>
                                    <button className="edit-action" onClick={() => openStatus(doc)}>Status</button>
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>

            {assignModal && (
                <div className="crud-modal-overlay">
                    <div className="crud-modal">
                        <h2>Assign "{assignModal.name}"</h2>
                        <div className="crud-form-group">
                            <label>Assign to</label>
                            <select value={selectedUserId} onChange={e => setSelectedUserId(e.target.value)}>
                                <option value="">Select member...</option>
                                {members.map(m => (
                                    <option key={m.user_id} value={m.user_id}>{m.name} ({m.role})</option>
                                ))}
                            </select>
                        </div>
                        <div className="crud-modal-actions">
                            <button className="crud-cancel-button" onClick={() => setAssignModal(null)}>Cancel</button>
                            <button className="crud-save-button" onClick={handleAssign}>Assign</button>
                        </div>
                    </div>
                </div>
            )}

            {statusModal && (
                <div className="crud-modal-overlay">
                    <div className="crud-modal">
                        <h2>Change status of "{statusModal.name}"</h2>
                        <div className="crud-form-group">
                            <label>Status</label>
                            <select value={selectedStatus} onChange={e => setSelectedStatus(e.target.value)}>
                                {statusOptions.map(s => (
                                    <option key={s} value={s}>{s}</option>
                                ))}
                            </select>
                        </div>
                        <div className="crud-modal-actions">
                            <button className="crud-cancel-button" onClick={() => setStatusModal(null)}>Cancel</button>
                            <button className="crud-save-button" onClick={handleStatusChange}>Update</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
```

---

## Task 12: Add Comments Tab to DocumentView

**Files:**
- Modify: `frontend/src/pages/app/DocumentView.jsx`

- [ ] **Step 1: Add a "Comments" tab alongside "Preview" and "Version History"**

In `frontend/src/pages/app/DocumentView.jsx`, add a third tab. The changes:

1. Add state for comments:

```jsx
const [comments, setComments] = useState([]);
const [newComment, setNewComment] = useState("");
```

2. Add fetch function:

```jsx
async function fetchComments() {
    const res = await authFetch(`/comments/document/${id}`);
    setComments(await res.json());
}
```

3. Call `fetchComments()` inside the existing `useEffect` alongside the other fetches.

4. Add submit handler:

```jsx
async function handleAddComment() {
    if (!newComment.trim()) return;
    const res = await authFetch("/comments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            document_id: id,
            version_id: selectedVersion?.document_version_id || null,
            content: newComment,
        }),
    });
    if (res.ok) {
        setNewComment("");
        fetchComments();
    }
}
```

5. Add the TabsTrigger:

```jsx
<TabsTrigger value="comments">Comments</TabsTrigger>
```

6. Add the TabsContent:

```jsx
<TabsContent value="comments">
    <div className="space-y-4">
        <div className="flex gap-2">
            <Textarea
                value={newComment}
                onChange={e => setNewComment(e.target.value)}
                placeholder="Add a comment..."
                rows={2}
                className="flex-1"
            />
            <Button onClick={handleAddComment} className="bg-indigo-600 hover:bg-indigo-500 text-white self-end">
                Post
            </Button>
        </div>
        {comments.length === 0 && (
            <p className="text-sm text-slate-400 text-center py-8">No comments yet</p>
        )}
        {comments.map(c => (
            <div key={c.comment_id} className="bg-white border border-slate-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-semibold text-slate-700">{c.user_name}</span>
                    <span className="text-xs text-slate-400">{c.created_at ? new Date(c.created_at).toLocaleString() : ""}</span>
                </div>
                {c.version_id && (
                    <span className="text-xs text-indigo-500">on version</span>
                )}
                <p className="text-sm text-slate-600 mt-1">{c.content}</p>
            </div>
        ))}
    </div>
</TabsContent>
```

---

## Task 13: Register New Routes in App.jsx

**Files:**
- Modify: `frontend/src/App.jsx`

- [ ] **Step 1: Add imports and routes**

Add imports at top:

```jsx
import ActivityLog from "./pages/app/ActivityLog";
import ProjectDocuments from "./pages/app/ProjectDocuments";
```

Add routes inside the `/app` Route, after the existing routes:

```jsx
<Route path="activity-log" element={<ActivityLog />} />
<Route path="project-documents" element={<ProjectDocuments />} />
```

---

## Task 14: Fix Project Documents Endpoint Response

**Files:**
- Modify: `backend/routers/projects.py`

The existing `GET /projects/{project_id}/documents` returns only `document_id` and `name` (via `DocumentListResponse`). The ProjectDocuments page needs `status` and `user_id` too.

- [ ] **Step 1: Update the response to include status and user_id**

In `backend/routers/projects.py`, change the `get_project_documents` endpoint to return richer data:

```python
@router.get("/{project_id}/documents")
async def get_project_documents(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = DocumentRepository(db)
    documents = await repo.get_documents_by_project_id(project_id)
    return [
        {
            "document_id": doc.document_id,
            "name": doc.name,
            "status": doc.status,
            "user_id": doc.user_id,
        }
        for doc in documents
    ]
```

Remove the `response_model=List[DocumentListResponse]` from the decorator so it returns the dict directly.

---

## Execution Order

Tasks are designed to be executed in order. Backend tasks (1-8) first, then frontend tasks (9-13), then the fixup task (14).

Dependencies:
- Tasks 1-2 create models/schemas needed by later tasks
- Task 3 depends on Task 2 (activity schema)
- Task 4 depends on Task 3 (uses Activity model import)
- Task 5 depends on Task 1 (uses Comment model)
- Tasks 6-8 are independent backend additions
- Tasks 9-13 are frontend, depend on all backend tasks being done
- Task 14 is a backend fixup needed by Task 11

Recommended: deploy and test after Task 8 (backend complete), then again after Task 13 (frontend complete).
