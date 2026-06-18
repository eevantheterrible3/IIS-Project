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
        setDocuments(await authFetch(`/projects/${projectId}/documents`).then(r => r.json()));
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
                                    <span className={`crud-badge ${doc.status === "approved" ? "green" : doc.status === "review" ? "amber" : ""}`}>
                                        {doc.status}
                                    </span>
                                </td>
                                <td>{assignee ? assignee.name : "—"}</td>
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
