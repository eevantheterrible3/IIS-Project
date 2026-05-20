import { useEffect, useState } from "react";
import "./Projects.css";
import { useNavigate, useLocation } from "react-router-dom";
import ProjectFormModal from "./ProjectFormModal";

export default function Projects() {
    const [projects, setProjects] = useState([]);
    const [documentsByProject, setDocumentsByProject] = useState({});
    const [openedProjectId, setOpenedProjectId] = useState(null);
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

        fetch(`http://localhost:8000/projects/my?user_id=${loggedUser.user_id}`)
            .then((response) => response.json())
            .then((data) => {
                setProjects(data);

                const selectedProjectId = location.state?.selectedProjectId;

                if (selectedProjectId) {
                    const project = data.find((p) => p.project_id === selectedProjectId);

                    if (project) {
                        setSelectedProject(project);
                        setOpenedProjectId(selectedProjectId);
                    }
                }
            });
    }, []);

    async function toggleProject(projectId) {
        const project = projects.find((p) => p.project_id === projectId);
        setSelectedProject(project);
        if (openedProjectId === projectId) {
            setOpenedProjectId(null);
            return;
        }

        setOpenedProjectId(projectId);

        if (!documentsByProject[projectId]) {
            const response = await fetch(
                `http://localhost:8000/projects/${projectId}/documents`
            );

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
        const user = JSON.parse(localStorage.getItem("user"));
        const response = await fetch(
            `http://localhost:8000/projects/${selectedProject.project_id}?user_id=${user.user_id}`,
            {
                method: "DELETE",
            }
        );

        if (!response.ok) {
            alert("Failed to delete project.");
            return;
        }

        setProjects(projects.filter(
            (project) => project.project_id !== selectedProject.project_id
        ));

        setSelectedProject(null);
        setOpenedProjectId(null);
        setShowDeleteProjectModal(false);
    }
    async function handleCreateProject(projectData) {
        const user = JSON.parse(localStorage.getItem("user"));

        const response = await fetch(`http://localhost:8000/projects?user_id=${user.user_id}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
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
        setShowAddProjectModal(false);
    }
    async function handleUpdateProject(projectData) {
        const user = JSON.parse(localStorage.getItem("user"));
        const response = await fetch(
            `http://localhost:8000/projects/${selectedProject.project_id}?user_id=${user.user_id}`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(projectData),
            }
        );

        if (!response.ok) {
            alert("Failed to update project.");
            return;
        }

        const updatedProject = await response.json();

        setProjects(projects.map((project) =>
            project.project_id === updatedProject.project_id
                ? updatedProject
                : project
        ));

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
                                    localStorage.removeItem("user");
                                    localStorage.removeItem("projects");
                                    localStorage.removeItem("selectedProject");

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
                        }}
                    >
                        ▼ Projects
                    </div>

                    {projects.map((project) => (
                        <div key={project.project_id} className="project-group">
                            <div
                                className="project-item"
                                onClick={() => toggleProject(project.project_id)}
                            >
                                <span>
                                    {openedProjectId === project.project_id ? "▼" : "▶"}
                                </span>
                                <span>{project.name}</span>
                            </div>

                            {openedProjectId === project.project_id && (
                                <div className="documents-list">
                                    {(documentsByProject[project.project_id] || []).map((document) => (
                                        <div
                                            key={document.document_id}
                                            className="document-item"
                                            onClick={() => navigate(`/documents/${document.document_id}`)}
                                        >
                                            {document.name}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
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
                                <span className={`status-text ${selectedProject.status?.toLowerCase()}`}>
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