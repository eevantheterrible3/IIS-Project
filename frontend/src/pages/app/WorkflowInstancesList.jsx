import { useEffect, useState } from "react";
import { authFetch, API_BASE } from "@/lib/api";
import "./CrudPages.css";

const emptyForm = { document_id: "", workflow_id: "", designated_user_id: "", note: "" };

export default function WorkflowInstancesList() {
    const [instances, setInstances] = useState([]);
    const [workflows, setWorkflows] = useState([]);
    const [documents, setDocuments] = useState([]);
    const [members, setMembers] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [editTarget, setEditTarget] = useState(null);
    const [form, setForm] = useState(emptyForm);
    const [deleteTarget, setDeleteTarget] = useState(null);

    const [expandedId, setExpandedId] = useState(null);
    const [steps, setSteps] = useState([]);
    const [showStepModal, setShowStepModal] = useState(false);
    const [editStep, setEditStep] = useState(null);
    const [stepForm, setStepForm] = useState({ status: "pending", progress: "0", assigned_user_id: "", note: "" });
    const [deleteStep, setDeleteStep] = useState(null);

    const selectedProject = JSON.parse(localStorage.getItem("selectedProject") || "{}");

    useEffect(() => {
        fetchInstances();
        authFetch("/workflows").then(r => r.json()).then(setWorkflows);
        authFetch("/documents/my").then(r => r.json()).then(setDocuments);
        if (selectedProject.project_id) {
            authFetch(`/projects/${selectedProject.project_id}/members`).then(r => r.json()).then(setMembers);
        }
    }, []);

    async function fetchInstances() {
        setInstances(await authFetch("/workflow-instances").then(r => r.json()));
    }

    async function fetchSteps(instanceId) {
        setSteps(await authFetch(`/workflow-instance-steps/instance/${instanceId}`).then(r => r.json()));
    }

    function toggleExpand(instanceId) {
        if (expandedId === instanceId) { setExpandedId(null); return; }
        setExpandedId(instanceId);
        fetchSteps(instanceId);
    }

    function openCreate() { setEditTarget(null); setForm(emptyForm); setShowModal(true); }
    function openEdit(inst) {
        setEditTarget(inst);
        setForm({ document_id: inst.document_id, workflow_id: inst.workflow_id, designated_user_id: inst.designated_user_id || "", note: inst.note || "" });
        setShowModal(true);
    }

    const selectedDoc = documents.find(d => d.document_id === form.document_id);
    const matchingWorkflows = selectedDoc
        ? workflows.filter(w => !w.document_type_id || w.document_type_id === selectedDoc.document_type_id)
        : [];

    function handleDocChange(docId) {
        const doc = documents.find(d => d.document_id === docId);
        const matching = doc ? workflows.filter(w => !w.document_type_id || w.document_type_id === doc.document_type_id) : [];
        const autoWf = matching.length === 1 ? matching[0].workflow_id : "";
        setForm(f => ({ ...f, document_id: docId, workflow_id: autoWf }));
    }

    async function handleSave() {
        if (!form.workflow_id || !form.document_id) return;
        if (editTarget) {
            const res = await authFetch(`/workflow-instances/${editTarget.instance_id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ current_step_id: editTarget.current_step_id, designated_user_id: form.designated_user_id || null, note: form.note || null }) });
            if (!res.ok) { alert("Something went wrong."); return; }
        } else {
            const res = await authFetch("/workflow-instances", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ workflow_id: form.workflow_id, document_id: form.document_id, designated_user_id: form.designated_user_id || null, note: form.note || null }) });
            if (!res.ok) {
                const data = await res.json().catch(() => null);
                alert(data?.detail || "Something went wrong.");
                return;
            }
        }
        setShowModal(false);
        fetchInstances();
    }

    async function handleDelete() {
        const res = await authFetch(`/workflow-instances/${deleteTarget.instance_id}`, { method: "DELETE" });
        if (!res.ok) { alert("Failed to delete."); return; }
        setInstances(i => i.filter(x => x.instance_id !== deleteTarget.instance_id));
        if (expandedId === deleteTarget.instance_id) setExpandedId(null);
        setDeleteTarget(null);
    }

    function openEditStep(s) {
        setEditStep(s);
        setStepForm({ status: s.status || "pending", progress: String(s.progress ?? 0), assigned_user_id: s.assigned_user_id || "", note: s.note || "" });
        setShowStepModal(true);
    }

    async function handleSaveStep() {
        const res = await authFetch(`/workflow-instance-steps/${editStep.instance_step_id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status: stepForm.status, progress: parseInt(stepForm.progress) || 0, assigned_user_id: stepForm.assigned_user_id || null, note: stepForm.note || null }) });
        if (!res.ok) { alert("Something went wrong."); return; }
        setShowStepModal(false);
        fetchSteps(expandedId);
    }

    async function handleDeleteStep() {
        const res = await authFetch(`/workflow-instance-steps/${deleteStep.instance_step_id}`, { method: "DELETE" });
        if (!res.ok) { alert("Failed to delete."); return; }
        setSteps(s => s.filter(x => x.instance_step_id !== deleteStep.instance_step_id));
        setDeleteStep(null);
    }

    function statusBadge(status) {
        if (status === "completed") return "green";
        if (status === "in_progress") return "amber";
        return "";
    }

    return (
        <div className="crud-page">
            <div className="crud-page-header">
                <div>
                    <h1>Document Preparation</h1>
                    <p>Track the progress of preparing each document through its workflow</p>
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                    <button
                        className="crud-add-button"
                        style={{ background: "#4F46E5" }}
                        onClick={() => {
                            const token = localStorage.getItem("access_token");
                            window.open(`${API_BASE}/reports/workflows?token=${token}`, "_blank");
                        }}
                    >PDF Report</button>
                    <button className="crud-add-button" onClick={openCreate}>+ Start preparation</button>
                </div>
            </div>

            {instances.length === 0 && (
                <div className="crud-empty">
                    <p>No documents being prepared</p>
                    <p>Start a preparation to track a document through its workflow steps.</p>
                </div>
            )}

            <div className="crud-card-list">
                {instances.map(inst => (
                    <div key={inst.instance_id} className="crud-card">
                        <div className="crud-card-header" onClick={() => toggleExpand(inst.instance_id)}>
                            <span className="crud-card-toggle">{expandedId === inst.instance_id ? "▼" : "▶"}</span>
                            <span className="crud-card-title">{inst.document_name || inst.document_id}</span>
                            {inst.document_type_name && <span className="crud-badge blue">{inst.document_type_name}</span>}
                            {inst.current_step_name && <span className="crud-badge amber">{inst.current_step_name}</span>}
                            <span className="crud-card-meta">{inst.designated_user_name || ""}</span>
                            <span className="crud-card-meta">{inst.started_at ? new Date(inst.started_at).toLocaleDateString() : ""}</span>
                            <span className="crud-card-actions">
                                <button className="edit-action" onClick={e => { e.stopPropagation(); openEdit(inst); }}>Edit</button>
                                <button className="delete-action" onClick={e => { e.stopPropagation(); setDeleteTarget(inst); }}>Delete</button>
                            </span>
                        </div>
                        {expandedId === inst.instance_id && (
                            <div className="crud-card-body">
                                <div className="crud-card-body-header">
                                    <span>Preparation Steps</span>
                                </div>
                                {steps.length === 0 ? (
                                    <p style={{ fontSize: 13, color: "#999" }}>No steps for this preparation.</p>
                                ) : steps.map(s => (
                                    <div key={s.instance_step_id} className="crud-step-row">
                                        <div className="crud-step-row-left">
                                            <span className="crud-step-name">{s.action_name || s.action_id}</span>
                                            <span className={`crud-badge ${statusBadge(s.status)}`}>{s.status}</span>
                                            <div className="crud-progress-bar">
                                                <div className="crud-progress-track">
                                                    <div className="crud-progress-fill" style={{ width: `${s.progress}%` }} />
                                                </div>
                                                <span className="crud-progress-text">{s.progress}%</span>
                                            </div>
                                            {s.assigned_user_name && <span style={{ fontSize: 12, color: "#888" }}>{s.assigned_user_name}</span>}
                                        </div>
                                        <div className="crud-step-actions">
                                            <button className="edit-action" onClick={() => openEditStep(s)}>Edit</button>
                                            <button className="delete-action" onClick={() => setDeleteStep(s)}>Remove</button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {showModal && (
                <div className="crud-modal-overlay">
                    <div className="crud-modal">
                        <h2>{editTarget ? "Edit preparation" : "Start document preparation"}</h2>
                        {!editTarget && (
                            <>
                                <div className="crud-form-group">
                                    <label>Document</label>
                                    <select value={form.document_id} onChange={e => handleDocChange(e.target.value)}>
                                        <option value="">Select document...</option>
                                        {documents.map(d => (
                                            <option key={d.document_id} value={d.document_id}>
                                                {d.name}{d.document_type_name ? ` (${d.document_type_name})` : ""}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div className="crud-form-group">
                                    <label>Workflow</label>
                                    <select value={form.workflow_id} onChange={e => setForm(f => ({ ...f, workflow_id: e.target.value }))} disabled={!form.document_id}>
                                        <option value="">{!form.document_id ? "Select a document first..." : "Select workflow..."}</option>
                                        {matchingWorkflows.map(w => (
                                            <option key={w.workflow_id} value={w.workflow_id}>
                                                {w.name}{w.document_type_name ? ` (${w.document_type_name})` : ""}
                                            </option>
                                        ))}
                                    </select>
                                    {form.document_id && matchingWorkflows.length === 0 && (
                                        <span style={{ fontSize: 12, color: "#dc2626" }}>No workflows defined for this document type.</span>
                                    )}
                                </div>
                            </>
                        )}
                        <div className="crud-form-group">
                            <label>Designated User</label>
                            <select value={form.designated_user_id} onChange={e => setForm(f => ({ ...f, designated_user_id: e.target.value }))}>
                                <option value="">None</option>
                                {members.map(m => (
                                    <option key={m.user_id} value={m.user_id}>{m.name} ({m.role})</option>
                                ))}
                            </select>
                        </div>
                        <div className="crud-form-group">
                            <label>Note</label>
                            <textarea value={form.note} onChange={e => setForm(f => ({ ...f, note: e.target.value }))} placeholder="Optional note..." />
                        </div>
                        <div className="crud-modal-actions">
                            <button className="crud-cancel-button" onClick={() => setShowModal(false)}>Cancel</button>
                            <button className="crud-save-button" onClick={handleSave}>Save</button>
                        </div>
                    </div>
                </div>
            )}

            {deleteTarget && (
                <div className="crud-modal-overlay">
                    <div className="crud-modal">
                        <h2>Delete preparation</h2>
                        <p>Are you sure you want to delete the preparation for <strong>{deleteTarget.document_name || "this document"}</strong>? All steps will be removed.</p>
                        <div className="crud-modal-actions">
                            <button className="crud-cancel-button" onClick={() => setDeleteTarget(null)}>Cancel</button>
                            <button className="crud-delete-button" onClick={handleDelete}>Delete</button>
                        </div>
                    </div>
                </div>
            )}

            {showStepModal && (
                <div className="crud-modal-overlay">
                    <div className="crud-modal">
                        <h2>Edit step</h2>
                        <div className="crud-form-group">
                            <label>Status</label>
                            <select value={stepForm.status} onChange={e => setStepForm(f => ({ ...f, status: e.target.value }))}>
                                <option value="pending">Pending</option>
                                <option value="in_progress">In Progress</option>
                                <option value="completed">Completed</option>
                            </select>
                        </div>
                        <div className="crud-form-group">
                            <label>Progress ({stepForm.progress}%)</label>
                            <input type="range" min="0" max="100" value={stepForm.progress} onChange={e => setStepForm(f => ({ ...f, progress: e.target.value }))} />
                        </div>
                        <div className="crud-form-group">
                            <label>Assigned User</label>
                            <select value={stepForm.assigned_user_id} onChange={e => setStepForm(f => ({ ...f, assigned_user_id: e.target.value }))}>
                                <option value="">None</option>
                                {members.map(m => (
                                    <option key={m.user_id} value={m.user_id}>{m.name} ({m.role})</option>
                                ))}
                            </select>
                        </div>
                        <div className="crud-form-group">
                            <label>Note</label>
                            <textarea value={stepForm.note} onChange={e => setStepForm(f => ({ ...f, note: e.target.value }))} placeholder="Optional note..." />
                        </div>
                        <div className="crud-modal-actions">
                            <button className="crud-cancel-button" onClick={() => setShowStepModal(false)}>Cancel</button>
                            <button className="crud-save-button" onClick={handleSaveStep}>Save</button>
                        </div>
                    </div>
                </div>
            )}

            {deleteStep && (
                <div className="crud-modal-overlay">
                    <div className="crud-modal">
                        <h2>Remove step</h2>
                        <p>Remove <strong>{deleteStep.action_name || "this step"}</strong> from this preparation?</p>
                        <div className="crud-modal-actions">
                            <button className="crud-cancel-button" onClick={() => setDeleteStep(null)}>Cancel</button>
                            <button className="crud-delete-button" onClick={handleDeleteStep}>Remove</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
