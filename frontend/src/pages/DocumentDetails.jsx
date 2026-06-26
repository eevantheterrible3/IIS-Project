import { useEffect, useState } from "react";
import "./DocumentDetails.css";
import documentIcon from "../assets/document-icon.png";
import editIcon from "../assets/edit.png";
import deleteIcon from "../assets/delete.png";
import { useNavigate, useParams } from "react-router-dom";
import EditDocumentModal from "../pages/EditDocumentModal";
import Header from "../components/Header";
import { authFetch } from "@/lib/api";

export default function DocumentDetails() {
    const { documentId } = useParams();

    const [document, setDocument] = useState(null);
    const [projectDocuments, setProjectDocuments] = useState([]);
    const [pdfUrl, setPdfUrl] = useState(null);
    const [pdfError, setPdfError] = useState(null);

    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);

    const [showActivityModal, setShowActivityModal] = useState(false);
    const [activities, setActivities] = useState([]);
    const [activitiesLoading, setActivitiesLoading] = useState(false);
    const [activitiesError, setActivitiesError] = useState(null);

    const navigate = useNavigate();

    useEffect(() => {
        async function loadDocument() {
            const response = await authFetch(`/documents/${documentId}`);

            if (!response.ok) {
                alert("Failed to load document.");
                return;
            }

            const data = await response.json();
            setDocument(data);

            const projectDocumentsResponse = await authFetch(`/projects/${data.project_id}/documents`);

            if (!projectDocumentsResponse.ok) {
                return;
            }

            const documents = await projectDocumentsResponse.json();
            setProjectDocuments(documents);
        }

        loadDocument();
    }, [documentId]);

    useEffect(() => {
        let objectUrl = null;

        async function loadPdf() {
            setPdfUrl(null);
            setPdfError(null);

            const response = await authFetch(`/documents/${documentId}/file`);

            if (!response.ok) {
                console.error("Failed to load PDF:", response.status);
                setPdfError("PDF could not be loaded.");
                return;
            }

            const blob = await response.blob();
            objectUrl = URL.createObjectURL(blob);
            setPdfUrl(objectUrl);
        }

        loadPdf();

        return () => {
            if (objectUrl) {
                URL.revokeObjectURL(objectUrl);
            }
        };
    }, [documentId]);

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

    async function handleOpenActivities() {
        setShowActivityModal(true);
        setActivitiesLoading(true);
        setActivitiesError(null);

        const response = await authFetch(`/documents/${documentId}/activities`);

        if (!response.ok) {
            setActivitiesError("Failed to load activities.");
            setActivitiesLoading(false);
            return;
        }

        const data = await response.json();
        setActivities(data);
        setActivitiesLoading(false);
    }

    function formatActivityType(type) {
        const normalizedType = String(type).toLowerCase();

        if (normalizedType.includes("view")) {
            return "viewed the document";
        }

        if (normalizedType.includes("update")) {
            return "updated the document";
        }

        if (normalizedType.includes("create")) {
            return "created the document";
        }

        if (normalizedType.includes("delete")) {
            return "deleted the document";
        }

        return normalizedType;
    }

    function formatActivityDate(date) {
        if (!date) {
            return "";
        }

        return new Date(date).toLocaleString("en-GB", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    }

    function getActivityUserName(activity) {
        if (!activity.user) {
            return "Unknown user";
        }

        const name = activity.user.name || "";
        const lastName = activity.user.last_name || "";

        const fullName = `${name} ${lastName}`.trim();

        return fullName || activity.user.email || "Unknown user";
    }

    if (!document) {
        return <div className="document-details-page">Loading...</div>;
    }
    async function handleOpenActivityReport() {
        const response = await authFetch(`/documents/${documentId}/activities/report`);

        if (!response.ok) {
            alert("Failed to generate activity report.");
            return;
        }

        const blob = await response.blob();
        const fileUrl = URL.createObjectURL(blob);

        window.open(fileUrl, "_blank");
    }
    function getActivityInitials(activity) {
        const userName = getActivityUserName(activity);

        return userName
            .split(" ")
            .filter(Boolean)
            .map((part) => part.charAt(0).toUpperCase())
            .slice(0, 2)
            .join("");
    }

    function getActivityConfig(type) {
        const normalizedType = String(type || "").toLowerCase();

        if (normalizedType.includes("view")) {
            return {
                label: "Viewed",
                description: "viewed this document",
                className: "activity-badge-view",
                icon: "👁",
            };
        }

        if (normalizedType.includes("update")) {
            return {
                label: "Updated",
                description: "updated this document",
                className: "activity-badge-update",
                icon: "✎",
            };
        }

        if (normalizedType.includes("create")) {
            return {
                label: "Created",
                description: "created this document",
                className: "activity-badge-create",
                icon: "+",
            };
        }

        if (normalizedType.includes("delete")) {
            return {
                label: "Deleted",
                description: "deleted this document",
                className: "activity-badge-delete",
                icon: "×",
            };
        }

        return {
            label: "Activity",
            description: formatActivityType(type),
            className: "activity-badge-default",
            icon: "•",
        };
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
                                    state: { selectedProjectId: document.project_id },
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
                                        String(projectDocument.document_id) === String(documentId)
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
                                className="document-action-button activity-button"
                                onClick={handleOpenActivities}
                            >
                                Activity
                            </button>
                            <button
                                className="document-action-button activity-report-button"
                                onClick={handleOpenActivityReport}
                            >
                                Activity PDF
                            </button>

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
                        {pdfUrl ? (
                            <iframe
                                src={pdfUrl}
                                className="document-frame"
                                title={document.name}
                            />
                        ) : pdfError ? (
                            <div className="pdf-error">{pdfError}</div>
                        ) : (
                            <div>Loading PDF...</div>
                        )}
                    </div>
                </main>

                <aside className="metadata-panel">
                    <h3>Document Details</h3>

                    {(document.metadata || []).map((item) => (
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

            {showActivityModal && (
                <div className="activity-modal-overlay">
                    <div className="activity-modal">
                        <div className="activity-modal-header">
                            <div>
                                <h2>Document Activity</h2>
                                <p className="activity-modal-subtitle">
                                    Activity history for <strong>{document.name}</strong>
                                </p>
                            </div>

                            <button
                                className="activity-modal-close"
                                onClick={() => setShowActivityModal(false)}
                            >
                                ×
                            </button>
                        </div>

                        <div className="activity-modal-content">
                            {activitiesLoading ? (
                                <div className="activity-modal-message">
                                    Loading activities...
                                </div>
                            ) : activitiesError ? (
                                <div className="activity-modal-error">
                                    {activitiesError}
                                </div>
                            ) : activities.length === 0 ? (
                                <div className="activity-modal-message">
                                    No activities recorded for this document.
                                </div>
                            ) : (
                                <>
                                    <div className="activity-modal-summary">
                                        Total activities: <strong>{activities.length}</strong>
                                    </div>

                                    <table className="activity-table">
                                        <thead>
                                            <tr>
                                                <th>User</th>
                                                <th>Activity</th>
                                                <th>Date</th>
                                            </tr>
                                        </thead>

                                        <tbody>
                                            {activities.map((activity) => (
                                                <tr key={activity.activity_id}>
                                                    <td>
                                                        <div className="activity-user-cell">
                                                            <div className="activity-user-avatar">
                                                                {getActivityUserName(activity)
                                                                    .charAt(0)
                                                                    .toUpperCase()}
                                                            </div>

                                                            <span>
                                                                {getActivityUserName(activity)}
                                                            </span>
                                                        </div>
                                                    </td>

                                                    <td>
                                                        <span className="activity-type-text">
                                                            {formatActivityType(activity.type)}
                                                        </span>
                                                    </td>

                                                    <td className="activity-date-cell">
                                                        {formatActivityDate(activity.date)}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </>
                            )}
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