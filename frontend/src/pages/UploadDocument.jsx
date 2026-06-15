import { useEffect, useState } from "react";
import "./ProjectDocuments.css";
import "./UploadDocument.css";
import { useNavigate, useParams } from "react-router-dom";
import { authFetch } from "@/lib/api";

export default function UploadDocument() {
    const { projectId } = useParams();
    const navigate = useNavigate();

    const [user, setUser] = useState(null);
    const [projects, setProjects] = useState([]);
    const [selectedProject, setSelectedProject] = useState(null);
    const [documents, setDocuments] = useState([]);
    const [showMenu, setShowMenu] = useState(false);

    const [name, setName] = useState("");
    const [file, setFile] = useState(null);
    const [metadata, setMetadata] = useState([
        { name: "Author", value: "", isDefault: true, inputType: "text" },
        { name: "Category", value: "", isDefault: true, inputType: "text" },
        { name: "Creation Date", value: "", isDefault: true, inputType: "date" },
    ]);
    const [isUploading, setIsUploading] = useState(false);

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

            const documentsResponse = await authFetch(`/projects/${projectId}/documents`);

            if (!documentsResponse.ok) {
                alert("Failed to load documents.");
                return;
            }

            const documentsData = await documentsResponse.json();
            setDocuments(documentsData);
        }

        loadPageData();
    }, [projectId]);

    function handleMetadataChange(index, field, value) {
        setMetadata((prev) =>
            prev.map((item, i) =>
                i === index ? { ...item, [field]: value } : item
            )
        );
    }

    function addMetadataRow() {
        setMetadata((prev) => [
            ...prev,
            { name: "", value: "", isDefault: false, inputType: "text" },
        ]);
    }

    function removeMetadataRow(index) {
        setMetadata((prev) => prev.filter((_, i) => i !== index));
    }

    async function handleUpload(event) {
        event.preventDefault();

        if (!name.trim()) {
            alert("Document name is required.");
            return;
        }

        if (!file) {
            alert("Please select a file.");
            return;
        }

        const cleanedMetadata = metadata
            .filter(
                (item) =>
                    item.name.trim() !== "" &&
                    String(item.value).trim() !== ""
            )
            .map((item) => ({
                name: item.name.trim(),
                value: String(item.value).trim(),
            }));

        const formData = new FormData();
        formData.append("project_id", projectId);
        formData.append("name", name.trim());
        formData.append("file", file);
        formData.append("metadata_json", JSON.stringify(cleanedMetadata));

        setIsUploading(true);

        const response = await authFetch("/documents/upload", {
            method: "POST",
            body: formData,
        });

        setIsUploading(false);

        if (!response.ok) {
            alert("Failed to upload document.");
            return;
        }

        navigate(`/projects/${projectId}/documents`);
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
                                        <div
                                            className="project-tab-item active-tab"
                                            onClick={() =>
                                                navigate(`/projects/${project.project_id}/documents`)
                                            }
                                        >
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
                    <div className="upload-title-row">
                        <div className="upload-icon">▣</div>

                        <div>
                            <h1>Upload New Document</h1>
                            <p>
                                {selectedProject
                                    ? `Project: ${selectedProject.name}`
                                    : "Add a new document"}
                            </p>
                        </div>
                    </div>

                    <form className="upload-card" onSubmit={handleUpload}>
                        <h2>Upload New Document</h2>

                        <div className="upload-form-group">
                            <label>Document Name</label>
                            <input
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="Enter document name..."
                            />
                        </div>

                        <div className="upload-form-group">
                            <label>Document Content</label>

                            <label className="file-upload-area">
                                <input
                                    type="file"
                                    accept="application/pdf"
                                    onChange={(e) => setFile(e.target.files[0])}
                                />

                                <div className="file-upload-icon">☁</div>

                                <div className="file-upload-text">
                                    {file ? file.name : "Click to select PDF document"}
                                </div>

                                <div className="file-upload-subtext">
                                    PDF files only
                                </div>
                            </label>
                        </div>

                        <div className="metadata-section">
                            <div className="metadata-title-row">
                                <h3>Metadata</h3>

                                <button
                                    type="button"
                                    className="add-metadata-button"
                                    onClick={addMetadataRow}
                                >
                                    + Add metadata
                                </button>
                            </div>

                            {metadata.map((item, index) => (
                                <div key={index} className="metadata-row">
                                    {item.isDefault ? (
                                        <input
                                            value={item.name}
                                            readOnly
                                            className="metadata-name-input readonly-metadata-name"
                                        />
                                    ) : (
                                        <input
                                            placeholder="Name"
                                            value={item.name}
                                            className="metadata-name-input"
                                            onChange={(e) =>
                                                handleMetadataChange(index, "name", e.target.value)
                                            }
                                        />
                                    )}

                                    <input
                                        type={item.inputType || "text"}
                                        placeholder="Value"
                                        value={item.value}
                                        className="metadata-value-input"
                                        onChange={(e) =>
                                            handleMetadataChange(index, "value", e.target.value)
                                        }
                                    />

                                    <button
                                        type="button"
                                        className="remove-metadata-button"
                                        onClick={() => removeMetadataRow(index)}
                                        disabled={item.isDefault}
                                    >
                                        ×
                                    </button>
                                </div>
                            ))}
                        </div>

                        <div className="upload-actions">
                            <button
                                type="button"
                                className="cancel-upload-button"
                                onClick={() => navigate(`/projects/${projectId}/documents`)}
                            >
                                Cancel
                            </button>

                            <button
                                type="submit"
                                className="submit-upload-button"
                                disabled={isUploading}
                            >
                                {isUploading ? "Uploading..." : "Upload"}
                            </button>
                        </div>
                    </form>
                </main>
            </div>
        </div>
    );
}