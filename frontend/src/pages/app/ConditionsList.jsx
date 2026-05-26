import { useEffect, useState } from "react";
import { authFetch } from "@/lib/api";
import "./CrudPages.css";

const emptyForm = { condition_type_id: "", document_type_id: "", role_id: "", description: "" };

export default function ConditionsList() {
    const [conditions, setConditions] = useState([]);
    const [conditionTypes, setConditionTypes] = useState([]);
    const [documentTypes, setDocumentTypes] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [editTarget, setEditTarget] = useState(null);
    const [form, setForm] = useState(emptyForm);
    const [deleteTarget, setDeleteTarget] = useState(null);

    useEffect(() => {
        fetchConditions();
        authFetch("/condition-types").then(r => r.json()).then(setConditionTypes);
        authFetch("/document-types").then(r => r.json()).then(setDocumentTypes);
    }, []);

    async function fetchConditions() {
        setConditions(await authFetch("/conditions").then(r => r.json()));
    }

    function openCreate() { setEditTarget(null); setForm(emptyForm); setShowModal(true); }
    function openEdit(c) {
        setEditTarget(c);
        setForm({
            condition_type_id: c.condition_type_id || "",
            document_type_id: c.document_type_id || "",
            role_id: c.role_id || "",
            description: c.description || "",
        });
        setShowModal(true);
    }

    async function handleSave() {
        const payload = {
            condition_type_id: form.condition_type_id || null,
            document_type_id: form.document_type_id || null,
            role_id: form.role_id || null,
            description: form.description || null,
        };
        const url = editTarget ? `/conditions/${editTarget.condition_id}` : "/conditions";
        const res = await authFetch(url, { method: editTarget ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
        if (!res.ok) { alert("Something went wrong."); return; }
        setShowModal(false);
        fetchConditions();
    }

    async function handleDelete() {
        const res = await authFetch(`/conditions/${deleteTarget.condition_id}`, { method: "DELETE" });
        if (!res.ok) { alert("Failed to delete."); return; }
        setConditions(c => c.filter(x => x.condition_id !== deleteTarget.condition_id));
        setDeleteTarget(null);
    }

    return (
        <div className="crud-page">
            <div className="crud-page-header">
                <div>
                    <h1>Conditions</h1>
                    <p>{conditions.length} condition{conditions.length !== 1 ? "s" : ""} defined</p>
                </div>
                <button className="crud-add-button" onClick={openCreate}>+ New condition</button>
            </div>

            <table className="crud-table">
                <thead>
                    <tr>
                        <th>Condition Type</th>
                        <th>Document Type</th>
                        <th>Role</th>
                        <th>Description</th>
                        <th className="actions-cell"></th>
                    </tr>
                </thead>
                <tbody>
                    {conditions.length === 0 && (
                        <tr><td colSpan={5} className="crud-empty">
                            <p>No conditions yet</p>
                            <p>Create a condition to get started.</p>
                        </td></tr>
                    )}
                    {conditions.map(c => (
                        <tr key={c.condition_id}>
                            <td><strong>{c.condition_type_name || <span className="crud-muted">—</span>}</strong></td>
                            <td>{c.document_type_name ? <span className="crud-badge">{c.document_type_name}</span> : <span className="crud-muted">—</span>}</td>
                            <td>{c.role_name ? <span className="crud-badge">{c.role_name}</span> : <span className="crud-muted">—</span>}</td>
                            <td>{c.description || <span className="crud-muted">—</span>}</td>
                            <td className="actions-cell">
                                <button className="edit-action" onClick={() => openEdit(c)}>Edit</button>
                                <button className="delete-action" onClick={() => setDeleteTarget(c)}>Delete</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {showModal && (
                <div className="crud-modal-overlay">
                    <div className="crud-modal">
                        <h2>{editTarget ? "Edit condition" : "New condition"}</h2>
                        <div className="crud-form-group">
                            <label>Condition Type</label>
                            <select value={form.condition_type_id} onChange={e => setForm(f => ({ ...f, condition_type_id: e.target.value }))}>
                                <option value="">Select condition type...</option>
                                {conditionTypes.map(t => <option key={t.condition_type_id} value={t.condition_type_id}>{t.name}</option>)}
                            </select>
                        </div>
                        <div className="crud-form-group">
                            <label>Document Type</label>
                            <select value={form.document_type_id} onChange={e => setForm(f => ({ ...f, document_type_id: e.target.value }))}>
                                <option value="">Select document type...</option>
                                {documentTypes.map(t => <option key={t.document_type_id} value={t.document_type_id}>{t.name}</option>)}
                            </select>
                        </div>
                        <div className="crud-form-group">
                            <label>Role ID</label>
                            <input value={form.role_id} onChange={e => setForm(f => ({ ...f, role_id: e.target.value }))} placeholder="Role ID" />
                        </div>
                        <div className="crud-form-group">
                            <label>Description</label>
                            <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} placeholder="Describe this condition..." />
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
                        <h2>Delete condition</h2>
                        <p>Are you sure you want to delete this condition?</p>
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
