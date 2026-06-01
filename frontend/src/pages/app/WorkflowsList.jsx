import { useEffect, useState } from "react";
import { authFetch } from "@/lib/api";
import "./CrudPages.css";

const emptyForm = { name: "", document_type_id: "" };
const emptyStepForm = { action_id: "", next_action: "", is_start_step: false, condition_id: "" };

export default function WorkflowsList() {
    const [workflows, setWorkflows] = useState([]);
    const [documentTypes, setDocumentTypes] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [editTarget, setEditTarget] = useState(null);
    const [form, setForm] = useState(emptyForm);
    const [deleteTarget, setDeleteTarget] = useState(null);

    const [expandedId, setExpandedId] = useState(null);
    const [steps, setSteps] = useState([]);
    const [actions, setActions] = useState([]);
    const [conditions, setConditions] = useState([]);
    const [showStepModal, setShowStepModal] = useState(false);
    const [editStep, setEditStep] = useState(null);
    const [stepForm, setStepForm] = useState(emptyStepForm);
    const [deleteStep, setDeleteStep] = useState(null);

    useEffect(() => {
        fetchWorkflows();
        authFetch("/workflow-actions").then(r => r.json()).then(setActions);
        authFetch("/conditions").then(r => r.json()).then(setConditions);
        authFetch("/document-types").then(r => r.json()).then(setDocumentTypes);
    }, []);

    async function fetchWorkflows() {
        setWorkflows(await authFetch("/workflows").then(r => r.json()));
    }

    async function fetchSteps(workflowId) {
        setSteps(await authFetch(`/workflow-has-actions/workflow/${workflowId}`).then(r => r.json()));
    }

    function toggleExpand(workflowId) {
        if (expandedId === workflowId) { setExpandedId(null); return; }
        setExpandedId(workflowId);
        fetchSteps(workflowId);
    }

    function openCreate() { setEditTarget(null); setForm(emptyForm); setShowModal(true); }
    function openEdit(wf) {
        setEditTarget(wf);
        setForm({ name: wf.name, document_type_id: wf.document_type_id || "" });
        setShowModal(true);
    }

    async function handleSave() {
        if (!form.name.trim() || !form.document_type_id) return;
        const payload = { name: form.name, document_type_id: form.document_type_id };
        const url = editTarget ? `/workflows/${editTarget.workflow_id}` : "/workflows";
        const res = await authFetch(url, { method: editTarget ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
        if (!res.ok) { alert("Something went wrong."); return; }
        setShowModal(false);
        fetchWorkflows();
    }

    async function handleDelete() {
        const res = await authFetch(`/workflows/${deleteTarget.workflow_id}`, { method: "DELETE" });
        if (!res.ok) { alert("Failed to delete."); return; }
        setWorkflows(w => w.filter(x => x.workflow_id !== deleteTarget.workflow_id));
        if (expandedId === deleteTarget.workflow_id) setExpandedId(null);
        setDeleteTarget(null);
    }

    function openCreateStep() { setEditStep(null); setStepForm(emptyStepForm); setShowStepModal(true); }
    function openEditStep(s) {
        setEditStep(s);
        setStepForm({ action_id: s.action_id || "", next_action: s.next_action || "", is_start_step: s.is_start_step || false, condition_id: s.condition_id || "" });
        setShowStepModal(true);
    }

    async function handleSaveStep() {
        if (!stepForm.action_id) return;
        if (editStep) {
            const res = await authFetch(`/workflow-has-actions/${expandedId}/${editStep.action_id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ next_action: stepForm.next_action || null, is_start_step: stepForm.is_start_step, condition_id: stepForm.condition_id || null }) });
            if (!res.ok) { alert("Something went wrong."); return; }
        } else {
            const res = await authFetch("/workflow-has-actions", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ workflow_id: expandedId, action_id: stepForm.action_id, next_action: stepForm.next_action || null, is_start_step: stepForm.is_start_step, condition_id: stepForm.condition_id || null }) });
            if (!res.ok) { alert("Something went wrong."); return; }
        }
        setShowStepModal(false);
        fetchSteps(expandedId);
    }

    async function handleDeleteStep() {
        const res = await authFetch(`/workflow-has-actions/${expandedId}/${deleteStep.action_id}`, { method: "DELETE" });
        if (!res.ok) { alert("Failed to delete."); return; }
        setSteps(s => s.filter(x => x.action_id !== deleteStep.action_id));
        setDeleteStep(null);
    }

    return (
        <div className="crud-page">
            <div className="crud-page-header">
                <div>
                    <h1>Workflows</h1>
                    <p>Each workflow defines the preparation steps for a document type</p>
                </div>
                <button className="crud-add-button" onClick={openCreate}>+ New workflow</button>
            </div>

            {workflows.length === 0 && (
                <div className="crud-empty">
                    <p>No workflows yet</p>
                    <p>Create a workflow to define how a document type is prepared.</p>
                </div>
            )}

            <div className="crud-card-list">
                {workflows.map(wf => (
                    <div key={wf.workflow_id} className="crud-card">
                        <div className="crud-card-header" onClick={() => toggleExpand(wf.workflow_id)}>
                            <span className="crud-card-toggle">{expandedId === wf.workflow_id ? "▼" : "▶"}</span>
                            <span className="crud-card-title">{wf.document_type_name || "No document type"}</span>
                            <span className="crud-card-meta">{wf.name}</span>
                            <span className="crud-card-meta">{wf.creator_name || ""}</span>
                            <span className="crud-card-meta">{wf.created_at ? new Date(wf.created_at).toLocaleDateString() : ""}</span>
                            <span className="crud-card-actions">
                                <button className="edit-action" onClick={e => { e.stopPropagation(); openEdit(wf); }}>Edit</button>
                                <button className="delete-action" onClick={e => { e.stopPropagation(); setDeleteTarget(wf); }}>Delete</button>
                            </span>
                        </div>
                        {expandedId === wf.workflow_id && (
                            <div className="crud-card-body">
                                <div className="crud-card-body-header">
                                    <span>Preparation Steps</span>
                                    <button className="crud-small-add-button" onClick={openCreateStep}>+ Add step</button>
                                </div>
                                {steps.length === 0 ? (
                                    <p style={{ fontSize: 13, color: "#999" }}>No steps configured for this workflow.</p>
                                ) : steps.map(s => (
                                    <div key={s.action_id} className="crud-step-row">
                                        <div className="crud-step-row-left">
                                            <span className="crud-step-name">{s.action_name || s.action_id}</span>
                                            {s.is_start_step && <span className="crud-badge green">Start</span>}
                                            {s.next_action_name && <span style={{ fontSize: 13, color: "#888" }}>→ {s.next_action_name}</span>}
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
                        <h2>{editTarget ? "Edit workflow" : "New workflow"}</h2>
                        <div className="crud-form-group">
                            <label>Document Type</label>
                            <select value={form.document_type_id} onChange={e => setForm(f => ({ ...f, document_type_id: e.target.value }))}>
                                <option value="">Select document type...</option>
                                {documentTypes.map(dt => <option key={dt.document_type_id} value={dt.document_type_id}>{dt.name}</option>)}
                            </select>
                        </div>
                        <div className="crud-form-group">
                            <label>Workflow Name</label>
                            <input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="e.g. CV Preparation Flow" />
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
                        <h2>Delete workflow</h2>
                        <p>Are you sure you want to delete the workflow for <strong>{deleteTarget.document_type_name || deleteTarget.name}</strong>? All associated steps will be removed.</p>
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
                        <h2>{editStep ? "Edit step" : "Add step"}</h2>
                        <div className="crud-form-group">
                            <label>Action</label>
                            <select value={stepForm.action_id} onChange={e => setStepForm(f => ({ ...f, action_id: e.target.value }))} disabled={!!editStep}>
                                <option value="">Select action...</option>
                                {actions.map(a => <option key={a.action_id} value={a.action_id}>{a.name}</option>)}
                            </select>
                        </div>
                        <div className="crud-form-group">
                            <label>Next Action</label>
                            <select value={stepForm.next_action} onChange={e => setStepForm(f => ({ ...f, next_action: e.target.value }))}>
                                <option value="">None (optional)</option>
                                {actions.map(a => <option key={a.action_id} value={a.action_id}>{a.name}</option>)}
                            </select>
                        </div>
                        <div className="crud-form-group">
                            <label>Condition</label>
                            <select value={stepForm.condition_id} onChange={e => setStepForm(f => ({ ...f, condition_id: e.target.value }))}>
                                <option value="">None (optional)</option>
                                {conditions.map(c => <option key={c.condition_id} value={c.condition_id}>{c.condition_type_name || c.condition_id}</option>)}
                            </select>
                        </div>
                        <div className="crud-checkbox-row">
                            <input type="checkbox" id="is_start" checked={stepForm.is_start_step} onChange={e => setStepForm(f => ({ ...f, is_start_step: e.target.checked }))} />
                            <label htmlFor="is_start">Start step</label>
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
                        <p>Remove <strong>{deleteStep.action_name || "this step"}</strong> from the workflow?</p>
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
