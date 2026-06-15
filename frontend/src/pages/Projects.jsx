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

    const navigate = useNavigate();
    const location = useLocation();

    const [showDeleteProjectModal, setShowDeleteProjectModal] = useState(false);
    const [showAddProjectModal, setShowAddProjectModal] = useState(false);
    const [showEditProjectModal, setShowEditProjectModal] = useState(false);

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
                    }
                }
            });
    }, []);

    function toggleProject(projectId) {
        const project = projects.find(
            (p) => String(p.project_id) === String(projectId)
        );

        setSelectedProject(project);

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

        if (!documentsByProject[projectId]) {
            const response = await authFetch(`/projects/${projectId}/documents`);

            if (!response.ok) {
                alert("Failed to load documents.");
                return;
            }

            const documents = await response.json();

            setDocumentsByProject((prev) => ({
                ...prev,
                [projectId]: documents,
            }));
        }
    }

    function isAdmin() {
        return projects.some((project) => project.role === "ADMIN");
    }

    function formatRole(role) {
        return role?.toLowerCase().replaceAll("_", " ");
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
                                            onClick={() =>
                                                navigate(`/projects/${project.project_id}/permissions`)
                                            }
                                        >
                                            <span>▶</span>
                                            <span>Permissions</span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </aside>

                <main className="projects-content">
                    {selectedProject ? (
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
                    ) : (
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