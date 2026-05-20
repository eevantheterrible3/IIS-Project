import { useEffect, useState } from "react";
import "./DocumentDetails.css";
import documentIcon from "../assets/document-icon.png";
import editIcon from "../assets/edit.png";
import deleteIcon from "../assets/delete.png";
import { useNavigate, useParams } from "react-router-dom";
export default function DocumentDetails() {
    const { documentId } = useParams();
    const [document, setDocument] = useState(null);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        fetch(`http://localhost:8000/documents/${documentId}`)
            .then((response) => response.json())
            .then((data) => setDocument(data));
    }, [documentId]);

    if (!document) {
        return <div className="document-details-page">Loading...</div>;
    }
    async function handleDelete() {
        const response = await fetch(`http://localhost:8000/documents/delete/${documentId}`, {
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
            <header className="document-header">
                <div className="document-logo">DOCUMENT MANAGEMENT</div>
            </header>

            <div className="document-layout">
                <aside className="document-left-panel">
                    <div className="details-sidebar-title">▼ Projects</div>

                    <div className="details-project-open">
                        <div className="details-project-name">▼ {document.project_name}</div>

                        <div className="details-documents-title">▼ Documents</div>

                        <div className="details-document-selected">
                            {document.name}
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
                            <button className="document-action-button edit-button">
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
                            src={`http://localhost:8000/documents/${documentId}/file`}
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
        </div>
    );
}