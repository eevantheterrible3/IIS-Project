import { useEffect, useState } from "react";
import "./DocumentDetails.css";
import documentIcon from "../assets/document-icon.png";
import editIcon from "../assets/edit.png";
import deleteIcon from "../assets/delete.png";
import { useNavigate, useParams } from "react-router-dom";
import EditDocumentModal from "../pages/EditDocumentModal";
import Header from "../components/Header";
import { authFetch, API_BASE } from "@/lib/api";

export default function DocumentDetails() {
    const { documentId } = useParams();
    const [document, setDocument] = useState(null);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const navigate = useNavigate();
    const [showEditModal, setShowEditModal] = useState(false);
    const [projectDocuments, setProjectDocuments] = useState([]);

    useEffect(() => {
        authFetch(`/documents/${documentId}`)
            .then((response) => response.json())
            .then((data) => setDocument(data));
    }, [documentId]);
    useEffect(() => {
        authFetch(`/documents/${documentId}`)
            .then((response) => response.json())
            .then((data) => {
                setDocument(data);

                authFetch(`/projects/${data.project_id}/documents`)
                    .then((response) => response.json())
                    .then((documents) => setProjectDocuments(documents));
            });
    }, [documentId]);

    if (!document) {
        return <div className="document-details-page">Loading...</div>;
    }
    async function handleDelete() {
        const response = await authFetch(`/documents/delete/${documentId}`, {
            method: "DELETE",
        });

        if (!response.ok) {
            alert("Failed to delete document.");
            return;
        }

        navigate("/projects");
    }

    return (
        <div className="document-details-page">
            <Header />

            <div className="document-layout">
                <aside className="document-left-panel">
                    <div className="details-sidebar-title">▼ Projects</div>

                    <div className="details-project-open">
                        <div className="details-project-name">▼ {document.project_name}</div>

                        <div
                            className="details-documents-title"
                            onClick={() =>
                                navigate("/projects", {
                                    state: { selectedProjectId: document.project_id }
                                })
                            }
                        >
                            ▼ Documents
                        </div>
                        <div className="details-documents-list">
                            {projectDocuments.map((projectDocument) => (
                                <div
                                    key={projectDocument.document_id}
                                    className={
                                        projectDocument.document_id === documentId
                                            ? "details-document-selected"
                                            : "details-document-item"
                                    }
                                    onClick={() => navigate(`/documents/${projectDocument.document_id}`)}
                                >
                                    {projectDocument.name}
                                </div>
                            ))}
                        </div>

                        <div className="details-permissions">▶ Permissions</div>
                    </div>
                </aside>

                <main className="document-preview">
                    <div className="document-title-row">
                        <div className="document-title-left">
                            <img src={documentIcon} alt="Document icon" className="document-title-icon" />
                            <h1>{document.name}</h1>
                        </div>

                        <div className="document-actions">
                            <button
                                className="document-action-button edit-button"
                                onClick={() => setShowEditModal(true)}
                            >
                                <img src={editIcon} alt="Edit" />
                                Edit
                            </button>

                            <button
                                className="document-action-button delete-button"
                                onClick={() => setShowDeleteModal(true)}
                            >
                                <img src={deleteIcon} alt="Delete" />
                                Delete
                            </button>
                        </div>
                    </div>
                    <div className="document-tags">
                        {(document.tags || []).map((tag) => (
                            <span key={tag.name} className="document-tag">
                                {tag.name}
                            </span>
                        ))}
                    </div>
                    <div className="document-paper">
                        <iframe
                            src={`${API_BASE}/documents/${documentId}/file`}
                            className="document-frame"
                            title={document.name}
                        />
                    </div>
                </main>

                <aside className="metadata-panel">
                    <h3>Document Details</h3>

                    {document.metadata.map((item) => (
                        <div key={item.name} className="metadata-item">
                            <strong>{item.name}</strong>
                            <span>{item.value}</span>
                        </div>
                    ))}
                </aside>
            </div>
            {showDeleteModal && (
                <div className="delete-modal-overlay">
                    <div className="delete-modal">
                        <h2>Delete document</h2>
                        <p>Are you sure you want to delete this document?</p>

                        <div className="delete-modal-actions">
                            <button
                                className="cancel-delete-button"
                                onClick={() => setShowDeleteModal(false)}
                            >
                                Cancel
                            </button>

                            <button
                                className="confirm-delete-button"
                                onClick={handleDelete}
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}
            {showEditModal && (
                <EditDocumentModal
                    document={document}
                    onClose={() => setShowEditModal(false)}
                    onSave={async (updatedData) => {
                        const response = await authFetch(`/documents/${documentId}/edit`, {
                            method: "PUT",
                            headers: {
                                "Content-Type": "application/json",
                            },
                            body: JSON.stringify(updatedData),
                        });

                        if (!response.ok) {
                            alert("Failed to update document.");
                            return;
                        }

                        const updatedDocument = await response.json();

                        setDocument(updatedDocument);
                        setShowEditModal(false);
                    }}
                />
            )}
        </div>
    );
}