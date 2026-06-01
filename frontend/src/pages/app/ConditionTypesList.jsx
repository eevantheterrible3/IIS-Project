import { useEffect, useState } from "react";
import { authFetch } from "@/lib/api";
import "./CrudPages.css";

const emptyForm = { name: "" };

export default function ConditionTypesList() {
    const [types, setTypes] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [editTarget, setEditTarget] = useState(null);
    const [form, setForm] = useState(emptyForm);
    const [deleteTarget, setDeleteTarget] = useState(null);

    useEffect(() => { fetchTypes(); }, []);

    async function fetchTypes() {
        setTypes(await authFetch("/condition-types").then(r => r.json()));
    }

    function openCreate() { setEditTarget(null); setForm(emptyForm); setShowModal(true); }
    function openEdit(type) {
        setEditTarget(type);
        setForm({ name: type.name });
        setShowModal(true);
    }

    async function handleSave() {
        if (!form.name.trim()) return;
        const url = editTarget ? `/condition-types/${editTarget.condition_type_id}` : "/condition-types";
        const res = await authFetch(url, { method: editTarget ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
        if (!res.ok) { alert("Something went wrong."); return; }
        setShowModal(false);
        fetchTypes();
    }

    async function handleDelete() {
        const res = await authFetch(`/condition-types/${deleteTarget.condition_type_id}`, { method: "DELETE" });
        if (!res.ok) { alert("Failed to delete."); return; }
        setTypes(t => t.filter(x => x.condition_type_id !== deleteTarget.condition_type_id));
        setDeleteTarget(null);
    }

    return (
        <div className="crud-page">
            <div className="crud-page-header">
                <div>
                    <h1>Condition Types</h1>
                    <p>{types.length} type{types.length !== 1 ? "s" : ""} defined</p>
                </div>
                <button className="crud-add-button" onClick={openCreate}>+ New type</button>
            </div>

            <table className="crud-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th className="actions-cell"></th>
                    </tr>
                </thead>
                <tbody>
                    {types.length === 0 && (
                        <tr><td colSpan={2} className="crud-empty">
                            <p>No condition types yet</p>
                            <p>Create a condition type to get started.</p>
                        </td></tr>
                    )}
                    {types.map(type => (
                        <tr key={type.condition_type_id}>
                            <td><strong>{type.name}</strong></td>
                            <td className="actions-cell">
                                <button className="edit-action" onClick={() => openEdit(type)}>Edit</button>
                                <button className="delete-action" onClick={() => setDeleteTarget(type)}>Delete</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {showModal && (
                <div className="crud-modal-overlay">
                    <div className="crud-modal">
                        <h2>{editTarget ? "Edit condition type" : "New condition type"}</h2>
                        <div className="crud-form-group">
                            <label>Name</label>
                            <input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="Condition type name" />
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
                        <h2>Delete condition type</h2>
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
