import { useEffect, useState } from "react";
import "./ProjectDocuments.css";
import { useNavigate, useParams } from "react-router-dom";
import { authFetch } from "@/lib/api";

export default function ProjectDocuments() {
    const { projectId } = useParams();
    const navigate = useNavigate();

    const [user, setUser] = useState(null);
    const [projects, setProjects] = useState([]);
    const [selectedProject, setSelectedProject] = useState(null);
    const [documents, setDocuments] = useState([]);
    const [showMenu, setShowMenu] = useState(false);

    const [filters, setFilters] = useState({
        name: "",
        author: "",
        date: "",
        type: "",
        tag: "",
    });

    useEffect(() => {
        const loggedUser = JSON.parse(localStorage.getItem("user"));
        setUser(loggedUser);

        async function loadPageData() {
            const projectsResponse = await authFetch("/projects/my");

            if (!projectsResponse.ok) {
                alert("Failed to load projects.");
                return;
            }

            const projectsData = await projectsResponse.json();
            setProjects(projectsData);

            const currentProject = projectsData.find(
                (project) => String(project.project_id) === String(projectId)
            );

            setSelectedProject(currentProject || null);

            await loadDocuments({
                name: "",
                author: "",
                date: "",
                type: "",
                tag: "",
            });
        }

        loadPageData();
    }, [projectId]);

    async function loadDocuments(customFilters = filters) {
        const params = new URLSearchParams();

        if (customFilters.name.trim()) {
            params.append("name", customFilters.name.trim());
        }

        if (customFilters.author.trim()) {
            params.append("author", customFilters.author.trim());
        }

        if (customFilters.date.trim()) {
            params.append("date", customFilters.date.trim());
        }

        if (customFilters.type.trim()) {
            params.append("type", customFilters.type.trim());
        }

        if (customFilters.tag.trim()) {
            params.append("tag", customFilters.tag.trim());
        }

        const queryString = params.toString();

        const response = await authFetch(
            `/projects/${projectId}/documents${queryString ? `?${queryString}` : ""}`
        );

        if (!response.ok) {
            alert("Failed to load documents.");
            return;
        }

        const data = await response.json();
        setDocuments(data);
    }

    function formatDate(value) {
        if (!value) {
            return "-";
        }

        return new Date(value).toLocaleDateString("sr-RS");
    }

    function handleFilterChange(field, value) {
        setFilters((prev) => ({
            ...prev,
            [field]: value,
        }));
    }

    function handleSearch() {
        loadDocuments();
    }

    function handleClearFilters() {
        const emptyFilters = {
            name: "",
            author: "",
            date: "",
            type: "",
            tag: "",
        };

        setFilters(emptyFilters);
        loadDocuments(emptyFilters);
    }

    return (
        <div className="project-documents-page">
            <header className="project-documents-header">
                <div className="project-documents-logo">DOCUMENT MANAGEMENT</div>

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

            <div className="project-documents-layout">
                <aside className="project-documents-sidebar">
                    <div
                        className="sidebar-title"
                        onClick={() => navigate("/projects")}
                    >
                        ▼ Projects
                    </div>

                    {projects.map((project) => {
                        const isCurrentProject =
                            String(project.project_id) === String(projectId);

                        return (
                            <div key={project.project_id} className="project-group">
                                <div
                                    className="project-item"
                                    onClick={() =>
                                        navigate("/projects", {
                                            state: { selectedProjectId: project.project_id },
                                        })
                                    }
                                >
                                    <span>{isCurrentProject ? "▼" : "▶"}</span>
                                    <span>{project.name}</span>
                                </div>

                                {isCurrentProject && (
                                    <div className="project-tabs-list">
                                        <div className="project-tab-item active-tab">
                                            <span>▼</span>
                                            <span>Documents</span>
                                        </div>

                                        <div className="documents-list">
                                            {documents.length === 0 ? (
                                                <div className="document-item empty-document-item">
                                                    No documents
                                                </div>
                                            ) : (
                                                documents.map((document) => (
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

                <main className="project-documents-content">
                    <h1>
                        {selectedProject
                            ? `${selectedProject.name} - documents`
                            : "Project documents"}
                    </h1>

                    <div className="documents-filters">
                        <input
                            placeholder="Name"
                            value={filters.name}
                            onChange={(e) => handleFilterChange("name", e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === "Enter") handleSearch();
                            }}
                        />

                        <input
                            placeholder="Author"
                            value={filters.author}
                            onChange={(e) => handleFilterChange("author", e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === "Enter") handleSearch();
                            }}
                        />

                        <input
                            type="date"
                            value={filters.date}
                            onChange={(e) => handleFilterChange("date", e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === "Enter") handleSearch();
                            }}
                        />

                        <input
                            placeholder="Type"
                            value={filters.type}
                            onChange={(e) => handleFilterChange("type", e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === "Enter") handleSearch();
                            }}
                        />

                        <input
                            placeholder="Tag"
                            value={filters.tag}
                            onChange={(e) => handleFilterChange("tag", e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === "Enter") handleSearch();
                            }}
                        />

                        <button
                            type="button"
                            className="search-button"
                            onClick={handleSearch}
                        >
                            🔍
                        </button>

                        <button
                            type="button"
                            className="clear-filters-button"
                            onClick={handleClearFilters}
                        >
                            Clear
                        </button>
                    </div>

                    <table className="documents-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Type</th>
                                <th>Created at</th>
                                <th>Status</th>
                                <th>Tags</th>
                                <th></th>
                            </tr>
                        </thead>

                        <tbody>
                            {documents.length === 0 ? (
                                <tr>
                                    <td colSpan="6" className="no-documents-cell">
                                        No documents found.
                                    </td>
                                </tr>
                            ) : (
                                documents.map((document) => (
                                    <tr key={document.document_id}>
                                        <td>
                                            <button
                                                type="button"
                                                className="document-name-link"
                                                onClick={() => navigate(`/documents/${document.document_id}`)}
                                            >
                                                {document.name}
                                            </button>
                                        </td>
                                        <td>{document.document_type_name || "-"}</td>
                                        <td>{formatDate(document.created_at)}</td>
                                        <td>{document.status || "-"}</td>
                                        <td>
                                            {(document.tags || []).length > 0
                                                ? document.tags.join(", ")
                                                : "-"}
                                        </td>
                                        <td>
                                            <button
                                                className="activity-link"
                                                onClick={() =>
                                                    navigate(`/documents/${document.document_id}`)
                                                }
                                            >
                                                Activity
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>

                    <button
                        className="upload-document-button"
                        onClick={() => navigate(`/projects/${projectId}/documents/upload`)}
                    >
                        + Upload document
                    </button>
                </main>
            </div>
        </div>
    );
}