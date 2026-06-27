import { useEffect, useState } from "react";
import "./Projects.css";
import { useNavigate, useLocation } from "react-router-dom";
import ProjectFormModal from "./ProjectFormModal";
import { authFetch } from "@/lib/api";

export default function Projects() {
    const [projects, setProjects] = useState([]);
    const [documentsByProject, setDocumentsByProject] = useState({});
    const [openedProjectId, setOpenedProjectId] = useState(null);
    const [openedDocumentsProjectId, setOpenedDocumentsProjectId] = useState(null);
    const [user, setUser] = useState(null);
    const [selectedProject, setSelectedProject] = useState(null);
    const [showMenu, setShowMenu] = useState(false);

    const [activeView, setActiveView] = useState("details");

    const [selectedPermissionDocument, setSelectedPermissionDocument] = useState(null);
    const [documentPermissions, setDocumentPermissions] = useState([]);
    const [permissionsLoading, setPermissionsLoading] = useState(false);
    const [permissionsError, setPermissionsError] = useState(null);

    const [showAddPermissionModal, setShowAddPermissionModal] = useState(false);
    const [users, setUsers] = useState([]);
    const [selectedUserIds, setSelectedUserIds] = useState([]);
    const [selectedPermissionNames, setSelectedPermissionNames] = useState([]);
    const [addPermissionError, setAddPermissionError] = useState(null);
    const [addPermissionLoading, setAddPermissionLoading] = useState(false);

    const navigate = useNavigate();
    const location = useLocation();

    const [showDeleteProjectModal, setShowDeleteProjectModal] = useState(false);
    const [showAddProjectModal, setShowAddProjectModal] = useState(false);
    const [showEditProjectModal, setShowEditProjectModal] = useState(false);

    const availablePermissions = ["VIEW", "UPDATE", "DELETE", "CREATE"];

    useEffect(() => {
        const loggedUser = JSON.parse(localStorage.getItem("user"));
        setUser(loggedUser);

        authFetch("/projects/my")
            .then((response) => response.json())
            .then((data) => {
                setProjects(data);

                const selectedProjectId = location.state?.selectedProjectId;

                if (selectedProjectId) {
                    const project = data.find(
                        (p) => String(p.project_id) === String(selectedProjectId)
                    );

                    if (project) {
                        setSelectedProject(project);
                        setOpenedProjectId(project.project_id);
                        setActiveView("details");
                    }
                }
            });
    }, []);

    async function loadDocumentsForProject(projectId) {
        if (documentsByProject[projectId]) {
            return documentsByProject[projectId];
        }

        const response = await authFetch(`/projects/${projectId}/documents`);

        if (!response.ok) {
            alert("Failed to load documents.");
            return [];
        }

        const documents = await response.json();

        setDocumentsByProject((prev) => ({
            ...prev,
            [projectId]: documents,
        }));

        return documents;
    }

    function toggleProject(projectId) {
        const project = projects.find(
            (p) => String(p.project_id) === String(projectId)
        );

        setSelectedProject(project);
        setActiveView("details");
        setSelectedPermissionDocument(null);
        setDocumentPermissions([]);
        setPermissionsError(null);

        if (String(openedProjectId) === String(projectId)) {
            setOpenedProjectId(null);
            setOpenedDocumentsProjectId(null);
            return;
        }

        setOpenedProjectId(projectId);
        setOpenedDocumentsProjectId(null);
    }

    async function toggleDocuments(projectId) {
        if (String(openedDocumentsProjectId) === String(projectId)) {
            setOpenedDocumentsProjectId(null);
            return;
        }

        setOpenedDocumentsProjectId(projectId);
        await loadDocumentsForProject(projectId);
    }

    async function openPermissions(project) {
        setSelectedProject(project);
        setOpenedProjectId(project.project_id);
        setOpenedDocumentsProjectId(null);
        setActiveView("permissions");
        setSelectedPermissionDocument(null);
        setDocumentPermissions([]);
        setPermissionsError(null);

        await loadDocumentsForProject(project.project_id);
    }

    async function loadPermissionsForDocument(document) {
        setSelectedPermissionDocument(document);
        setDocumentPermissions([]);
        setPermissionsError(null);
        setPermissionsLoading(true);

        const response = await authFetch(`/documents/${document.document_id}/permissions`);

        if (!response.ok) {
            setPermissionsLoading(false);

            if (response.status === 403) {
                setPermissionsError("You do not have permission to view document permissions.");
                return;
            }

            setPermissionsError("Failed to load permissions.");
            return;
        }

        const data = await response.json();

        setDocumentPermissions(data);
        setPermissionsLoading(false);
    }

    async function loadUsers() {
        const response = await authFetch("/users");

        if (!response.ok) {
            alert("Failed to load users.");
            return;
        }

        const data = await response.json();
        setUsers(data);
    }

    async function handleOpenAddPermissionModal() {
        if (!selectedPermissionDocument) {
            return;
        }

        setSelectedUserIds([]);
        setSelectedPermissionNames([]);
        setAddPermissionError(null);
        setShowAddPermissionModal(true);

        if (users.length === 0) {
            await loadUsers();
        }
    }

    function toggleSelectedUser(userId) {
        setSelectedUserIds((prev) => {
            if (prev.includes(userId)) {
                return prev.filter((id) => id !== userId);
            }

            return [...prev, userId];
        });
    }

    function toggleSelectedPermission(permissionName) {
        setSelectedPermissionNames((prev) => {
            if (prev.includes(permissionName)) {
                return prev.filter((name) => name !== permissionName);
            }

            return [...prev, permissionName];
        });
    }

    async function handleAddPermissions() {
        if (!selectedPermissionDocument) {
            return;
        }

        if (selectedUserIds.length === 0) {
            setAddPermissionError("Select at least one user.");
            return;
        }

        if (selectedPermissionNames.length === 0) {
            setAddPermissionError("Select at least one permission.");
            return;
        }

        setAddPermissionLoading(true);
        setAddPermissionError(null);

        const response = await authFetch(
            `/documents/${selectedPermissionDocument.document_id}/permissions`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    user_ids: selectedUserIds,
                    permissions: selectedPermissionNames,
                }),
            }
        );

        setAddPermissionLoading(false);

        if (!response.ok) {
            setAddPermissionError("Failed to add permissions.");
            return;
        }

        setShowAddPermissionModal(false);
        setSelectedUserIds([]);
        setSelectedPermissionNames([]);

        await loadPermissionsForDocument(selectedPermissionDocument);
    }

    async function handleRemovePermission(userId, permissionName) {
        if (!selectedPermissionDocument) {
            return;
        }

        const confirmed = window.confirm(
            `Remove permission "${permissionName}" from this user?`
        );

        if (!confirmed) {
            return;
        }

        const response = await authFetch(
            `/documents/${selectedPermissionDocument.document_id}/permissions/${encodeURIComponent(userId)}/${encodeURIComponent(permissionName)}`,
            {
                method: "DELETE",
            }
        );

        if (!response.ok) {
            alert("Failed to remove permission.");
            return;
        }

        await loadPermissionsForDocument(selectedPermissionDocument);
    }

    function getRemovablePermissions(permission) {
        return (permission.permissions || []).filter(
            (item) => item.toLowerCase() !== "all"
        );
    }

    function isAdmin() {
        return projects.some((project) => project.role === "ADMIN");
    }

    function formatRole(role) {
        return role?.toLowerCase().replaceAll("_", " ");
    }

    function formatBoolean(value) {
        return value ? "Yes" : "No";
    }

    async function handleDeleteProject() {
        const response = await authFetch(`/projects/${selectedProject.project_id}`, {
            method: "DELETE",
        });

        if (!response.ok) {
            alert("Failed to delete project.");
            return;
        }

        setProjects(
            projects.filter(
                (project) => project.project_id !== selectedProject.project_id
            )
        );

        setSelectedProject(null);
        setOpenedProjectId(null);
        setOpenedDocumentsProjectId(null);
        setShowDeleteProjectModal(false);
    }

    async function handleCreateProject(projectData) {
        const response = await authFetch("/projects", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(projectData),
        });

        if (!response.ok) {
            alert("Failed to create project.");
            return;
        }

        const createdProject = await response.json();

        setProjects([...projects, createdProject]);
        setSelectedProject(createdProject);
        setOpenedProjectId(createdProject.project_id);
        setOpenedDocumentsProjectId(null);
        setActiveView("details");
        setShowAddProjectModal(false);
    }

    async function handleUpdateProject(projectData) {
        const response = await authFetch(`/projects/${selectedProject.project_id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(projectData),
        });

        if (!response.ok) {
            alert("Failed to update project.");
            return;
        }

        const updatedProject = await response.json();

        setProjects(
            projects.map((project) =>
                project.project_id === updatedProject.project_id
                    ? updatedProject
                    : project
            )
        );

        setSelectedProject(updatedProject);
        setShowEditProjectModal(false);
    }

    const selectedProjectDocuments = selectedProject
        ? documentsByProject[selectedProject.project_id] || []
        : [];

    return (
        <div className="projects-page">
            <header className="projects-header">
                <div className="projects-logo">DOCUMENT MANAGEMENT</div>

                <div className="user-menu-container">
                    <div
                        className="user-avatar"
                        onClick={() => setShowMenu(!showMenu)}
                    >
                        {user?.name?.charAt(0).toUpperCase()}
                    </div>

                    {showMenu && (
                        <div className="user-dropdown">
                            <button
                                className="logout-button"
                                onClick={() => {
                                    localStorage.clear();
                                    window.location.href = "/login";
                                }}
                            >
                                Log out
                            </button>
                        </div>
                    )}
                </div>
            </header>

            <div className="projects-layout">
                <aside className="projects-sidebar">
                    <div
                        className="sidebar-title"
                        onClick={() => {
                            setSelectedProject(null);
                            setOpenedProjectId(null);
                            setOpenedDocumentsProjectId(null);
                            setActiveView("details");
                            setSelectedPermissionDocument(null);
                            setDocumentPermissions([]);
                            setPermissionsError(null);
                        }}
                    >
                        ▼ Projects
                    </div>

                    {projects.map((project) => {
                        const isProjectOpen =
                            String(openedProjectId) === String(project.project_id);

                        const areDocumentsOpen =
                            String(openedDocumentsProjectId) === String(project.project_id);

                        const projectDocuments =
                            documentsByProject[project.project_id] || [];

                        return (
                            <div key={project.project_id} className="project-group">
                                <div
                                    className="project-item"
                                    onClick={() => toggleProject(project.project_id)}
                                >
                                    <span>{isProjectOpen ? "▼" : "▶"}</span>
                                    <span>{project.name}</span>
                                </div>

                                {isProjectOpen && (
                                    <div className="project-tabs-list">
                                        <div
                                            className="project-tab-item"
                                            onClick={() => navigate(`/projects/${project.project_id}/documents`)}
                                        >
                                            <span>▶</span>
                                            <span>Documents</span>
                                        </div>

                                        {areDocumentsOpen && (
                                            <div className="documents-list">
                                                {projectDocuments.length === 0 ? (
                                                    <div className="document-item empty-document-item">
                                                        No documents
                                                    </div>
                                                ) : (
                                                    projectDocuments.map((document) => (
                                                        <div
                                                            key={document.document_id}
                                                            className="document-item"
                                                            onClick={() =>
                                                                navigate(`/documents/${document.document_id}`)
                                                            }
                                                        >
                                                            {document.name}
                                                        </div>
                                                    ))
                                                )}
                                            </div>
                                        )}

                                        <div
                                            className="project-tab-item"
                                            onClick={() => openPermissions(project)}
                                        >
                                            <span>
                                                {activeView === "permissions" &&
                                                    selectedProject?.project_id === project.project_id
                                                    ? "▼"
                                                    : "▶"}
                                            </span>
                                            <span>Permissions</span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </aside>

                <main className="projects-content">
                    {selectedProject && activeView === "details" && (
                        <>
                            <div className="project-details-header">
                                <h1 className="project-title">
                                    {selectedProject.name} - {formatRole(selectedProject.role)}
                                </h1>

                                {isAdmin() && (
                                    <div className="project-actions">
                                        <button
                                            className="project-edit-button"
                                            onClick={() => setShowEditProjectModal(true)}
                                        >
                                            Edit
                                        </button>

                                        <button
                                            className="project-delete-button"
                                            onClick={() => setShowDeleteProjectModal(true)}
                                        >
                                            Delete
                                        </button>
                                    </div>
                                )}
                            </div>

                            <p className="project-description">
                                {selectedProject.description || "No description available."}
                            </p>

                            <p className="project-status">
                                Status:{" "}
                                <span
                                    className={`status-text ${selectedProject.status?.toLowerCase()}`}
                                >
                                    {selectedProject.status?.toLowerCase()}
                                </span>
                            </p>
                        </>
                    )}

                    {selectedProject && activeView === "permissions" && (
                        <div className="project-permissions-view">
                            <h1 className="project-title">
                                {selectedProject.name} - Permissions
                            </h1>

                            <div className="permissions-layout">
                                <div className="permissions-documents-panel">
                                    <h3>Documents</h3>

                                    {selectedProjectDocuments.length === 0 ? (
                                        <div className="permissions-empty">
                                            No documents for this project.
                                        </div>
                                    ) : (
                                        selectedProjectDocuments.map((document) => (
                                            <button
                                                key={document.document_id}
                                                className={
                                                    selectedPermissionDocument?.document_id === document.document_id
                                                        ? "permission-document-item selected"
                                                        : "permission-document-item"
                                                }
                                                onClick={() => loadPermissionsForDocument(document)}
                                            >
                                                {document.name}
                                            </button>
                                        ))
                                    )}
                                </div>

                                <div className="permissions-details-panel">
                                    {!selectedPermissionDocument ? (
                                        <div className="permissions-empty">
                                            Select a document to view permissions.
                                        </div>
                                    ) : (
                                        <>
                                            <div className="permissions-details-header">
                                                <h3>{selectedPermissionDocument.name}</h3>

                                                <button
                                                    className="add-permission-button"
                                                    onClick={handleOpenAddPermissionModal}
                                                >
                                                    + Add permissions
                                                </button>
                                            </div>

                                            {permissionsLoading ? (
                                                <div className="permissions-empty">
                                                    Loading permissions...
                                                </div>
                                            ) : permissionsError ? (
                                                <div className="permissions-error">
                                                    {permissionsError}
                                                </div>
                                            ) : documentPermissions.length === 0 ? (
                                                <div className="permissions-empty">
                                                    No permissions found for this document.
                                                </div>
                                            ) : (
                                                <table className="permissions-table">
                                                    <thead>
                                                        <tr>
                                                            <th>User</th>
                                                            <th>Role</th>
                                                            <th>Project member</th>
                                                            <th>Read</th>
                                                            <th>Create</th>
                                                            <th>Update</th>
                                                            <th>Delete</th>
                                                            <th>Assigned permissions</th>
                                                            <th>Actions</th>
                                                        </tr>
                                                    </thead>

                                                    <tbody>
                                                        {documentPermissions.map((permission) => {
                                                            const removablePermissions =
                                                                getRemovablePermissions(permission);

                                                            return (
                                                                <tr key={permission.user_id}>
                                                                    <td>
                                                                        <div className="permission-user-name">
                                                                            {permission.full_name}
                                                                        </div>
                                                                        <div className="permission-user-email">
                                                                            {permission.email}
                                                                        </div>
                                                                    </td>

                                                                    <td>{permission.role || "-"}</td>
                                                                    <td>{formatBoolean(permission.is_project_member)}</td>
                                                                    <td>{formatBoolean(permission.can_read)}</td>
                                                                    <td>{formatBoolean(permission.can_create)}</td>
                                                                    <td>{formatBoolean(permission.can_update)}</td>
                                                                    <td>{formatBoolean(permission.can_delete)}</td>

                                                                    <td>
                                                                        {removablePermissions.length === 0
                                                                            ? "-"
                                                                            : removablePermissions.join(", ")}
                                                                    </td>

                                                                    <td>
                                                                        {removablePermissions.length === 0 ? (
                                                                            <span className="permission-no-action">
                                                                                No assigned permissions
                                                                            </span>
                                                                        ) : (
                                                                            <div className="permission-remove-actions">
                                                                                {removablePermissions.map((permissionName) => (
                                                                                    <button
                                                                                        key={permissionName}
                                                                                        className="permission-remove-button"
                                                                                        onClick={() =>
                                                                                            handleRemovePermission(
                                                                                                permission.user_id,
                                                                                                permissionName
                                                                                            )
                                                                                        }
                                                                                    >
                                                                                        Remove {permissionName}
                                                                                    </button>
                                                                                ))}
                                                                            </div>
                                                                        )}
                                                                    </td>
                                                                </tr>
                                                            );
                                                        })}
                                                    </tbody>
                                                </table>
                                            )}
                                        </>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    {!selectedProject && (
                        <div className="empty-project-state">
                            <h1>Select a project</h1>

                            {isAdmin() && (
                                <button
                                    className="project-add-button"
                                    onClick={() => setShowAddProjectModal(true)}
                                >
                                    + Add project
                                </button>
                            )}
                        </div>
                    )}
                </main>
            </div>

            {showAddPermissionModal && (
                <div className="permission-modal-overlay">
                    <div className="permission-modal">
                        <h2>Add permissions</h2>

                        <div className="permission-modal-section">
                            <h3>Users</h3>

                            {users.length === 0 ? (
                                <div className="permissions-empty">
                                    No users found.
                                </div>
                            ) : (
                                <div className="permission-checkbox-list">
                                    {users.map((user) => (
                                        <label
                                            key={user.user_id}
                                            className="permission-checkbox-item"
                                        >
                                            <input
                                                type="checkbox"
                                                checked={selectedUserIds.includes(user.user_id)}
                                                onChange={() => toggleSelectedUser(user.user_id)}
                                            />

                                            <span>
                                                {user.name} {user.last_name}{" "}
                                                <small>{user.email}</small>
                                            </span>
                                        </label>
                                    ))}
                                </div>
                            )}
                        </div>

                        <div className="permission-modal-section">
                            <h3>Permissions</h3>

                            <div className="permission-checkbox-list">
                                {availablePermissions.map((permissionName) => (
                                    <label
                                        key={permissionName}
                                        className="permission-checkbox-item"
                                    >
                                        <input
                                            type="checkbox"
                                            checked={selectedPermissionNames.includes(permissionName)}
                                            onChange={() => toggleSelectedPermission(permissionName)}
                                        />

                                        <span>{permissionName}</span>
                                    </label>
                                ))}
                            </div>
                        </div>

                        {addPermissionError && (
                            <div className="permissions-error">
                                {addPermissionError}
                            </div>
                        )}

                        <div className="permission-modal-actions">
                            <button
                                className="cancel-permission-button"
                                onClick={() => setShowAddPermissionModal(false)}
                                disabled={addPermissionLoading}
                            >
                                Cancel
                            </button>

                            <button
                                className="confirm-permission-button"
                                onClick={handleAddPermissions}
                                disabled={addPermissionLoading}
                            >
                                {addPermissionLoading ? "Saving..." : "Save"}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {showDeleteProjectModal && (
                <div className="delete-modal-overlay">
                    <div className="delete-modal">
                        <h2>Delete project</h2>
                        <p>Are you sure you want to delete this project?</p>

                        <div className="delete-modal-actions">
                            <button
                                className="cancel-delete-button"
                                onClick={() => setShowDeleteProjectModal(false)}
                            >
                                Cancel
                            </button>

                            <button
                                className="confirm-delete-button"
                                onClick={handleDeleteProject}
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {showAddProjectModal && (
                <ProjectFormModal
                    title="Add project"
                    onClose={() => setShowAddProjectModal(false)}
                    onSave={handleCreateProject}
                />
            )}

            {showEditProjectModal && (
                <ProjectFormModal
                    title="Edit project"
                    project={selectedProject}
                    onClose={() => setShowEditProjectModal(false)}
                    onSave={handleUpdateProject}
                />
            )}
        </div>
    );
}