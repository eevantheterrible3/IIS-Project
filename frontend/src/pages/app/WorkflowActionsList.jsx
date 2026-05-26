import { useEffect, useState } from "react";
import { authFetch } from "@/lib/api";
import "./CrudPages.css";

const emptyForm = { name: "", type: "", description: "" };

export default function WorkflowActionsList() {
    const [actions, setActions] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [editTarget, setEditTarget] = useState(null);
    const [form, setForm] = useState(emptyForm);
    const [deleteTarget, setDeleteTarget] = useState(null);

    useEffect(() => { fetchActions(); }, []);

    async function fetchActions() {
        setActions(await authFetch("/workflow-actions").then(r => r.json()));
    }

    function openCreate() { setEditTarget(null); setForm(emptyForm); setShowModal(true); }
    function openEdit(action) {
        setEditTarget(action);
        setForm({ name: action.name, type: action.type || "", description: action.description || "" });
        setShowModal(true);
    }

    async function handleSave() {
        if (!form.name.trim()) return;
        const url = editTarget ? `/workflow-actions/${editTarget.action_id}` : "/workflow-actions";
        const res = await authFetch(url, { method: editTarget ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
        if (!res.ok) { alert("Something went wrong."); return; }
        setShowModal(false);
        fetchActions();
    }

    async function handleDelete() {
        const res = await authFetch(`/workflow-actions/${deleteTarget.action_id}`, { method: "DELETE" });
        if (!res.ok) { alert("Failed to delete."); return; }
        setActions(a => a.filter(x => x.action_id !== deleteTarget.action_id));
        setDeleteTarget(null);
    }

    return (
        <div className="crud-page">
            <div className="crud-page-header">
                <div>
                    <h1>Workflow Actions</h1>
                    <p>{actions.length} action{actions.length !== 1 ? "s" : ""} defined</p>
                </div>
                <button className="crud-add-button" onClick={openCreate}>+ New action</button>
            </div>

            <table className="crud-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Description</th>
                        <th className="actions-cell"></th>
                    </tr>
                </thead>
                <tbody>
                    {actions.length === 0 && (
                        <tr><td colSpan={4} className="crud-empty">
                            <p>No workflow actions yet</p>
                            <p>Create an action to get started.</p>
                        </td></tr>
                    )}
                    {actions.map(action => (
                        <tr key={action.action_id}>
                            <td><strong>{action.name}</strong></td>
                            <td>{action.type ? <span className="crud-badge">{action.type}</span> : <span className="crud-muted">—</span>}</td>
                            <td>{action.description || <span className="crud-muted">—</span>}</td>
                            <td className="actions-cell">
                                <button className="edit-action" onClick={() => openEdit(action)}>Edit</button>
                                <button className="delete-action" onClick={() => setDeleteTarget(action)}>Delete</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {showModal && (
                <div className="crud-modal-overlay">
                    <div className="crud-modal">
                        <h2>{editTarget ? "Edit action" : "New action"}</h2>
                        <div className="crud-form-group">
                            <label>Name</label>
                            <input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="Action name" />
                        </div>
                        <div className="crud-form-group">
                            <label>Type</label>
                            <input value={form.type} onChange={e => setForm(f => ({ ...f, type: e.target.value }))} placeholder="e.g. review, approve, edit..." />
                        </div>
                        <div className="crud-form-group">
                            <label>Description</label>
                            <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} placeholder="What this action does..." />
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
                        <h2>Delete action</h2>
                        <p>Are you sure you want to delete <strong>{deleteTarget.name}</strong>?</p>
                        <div className="crud-modal-actions">
                            <button className="crud-cancel-button" onClick={() => setDeleteTarget(null)}>Cancel</button>
                            <button className="crud-delete-button" onClick={handleDelete}>Delete</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
