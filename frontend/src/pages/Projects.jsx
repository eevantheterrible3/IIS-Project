import { useEffect, useState } from "react";
import "./Projects.css";
import { useNavigate } from "react-router-dom";


export default function Projects() {
    const [projects, setProjects] = useState([]);
    const [documentsByProject, setDocumentsByProject] = useState({});
    const [openedProjectId, setOpenedProjectId] = useState(null);
    const [user, setUser] = useState(null);
    const [selectedProject, setSelectedProject] = useState(null);
    const [showMenu, setShowMenu] = useState(false);
    const navigate = useNavigate();


    useEffect(() => {
        const loggedUser = JSON.parse(localStorage.getItem("user"));
        setUser(loggedUser);

        fetch(`http://localhost:8000/projects/my?user_id=${loggedUser.user_id}`)
            .then((response) => response.json())
            .then((data) => setProjects(data));
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
    function formatRole(role) {
        return role?.toLowerCase().replaceAll("_", " ");
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
                    <div className="sidebar-title">▼ Projects</div>

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
                            <h1 className="project-title">
                                {selectedProject.name} - {formatRole(selectedProject.role)}
                            </h1>

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
                        <h1>Select a project</h1>
                    )}
                </main>
            </div>
        </div>
    );
}