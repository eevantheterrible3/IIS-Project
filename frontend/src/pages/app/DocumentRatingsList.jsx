import { useEffect, useState } from "react";
import { authFetch } from "@/lib/api";
import "./CrudPages.css";

const emptyForm = { score: "3", comment: "" };

export default function DocumentRatingsList() {
    const [documents, setDocuments] = useState([]);
    const [selectedDocId, setSelectedDocId] = useState("");
    const [ratings, setRatings] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [editTarget, setEditTarget] = useState(null);
    const [form, setForm] = useState(emptyForm);
    const [deleteTarget, setDeleteTarget] = useState(null);

    useEffect(() => {
        authFetch("/documents/my").then(r => r.json()).then(setDocuments);
    }, []);

    useEffect(() => {
        if (selectedDocId) fetchRatings();
        else setRatings([]);
    }, [selectedDocId]);

    async function fetchRatings() {
        setRatings(await authFetch(`/document-ratings/document/${selectedDocId}`).then(r => r.json()));
    }

    function openCreate() { setEditTarget(null); setForm(emptyForm); setShowModal(true); }
    function openEdit(r) {
        setEditTarget(r);
        setForm({ score: String(r.score), comment: r.comment || "" });
        setShowModal(true);
    }

    async function handleSave() {
        const payload = editTarget
            ? { score: parseInt(form.score), comment: form.comment || null }
            : { document_id: selectedDocId, score: parseInt(form.score), comment: form.comment || null };
        const url = editTarget ? `/document-ratings/${editTarget.document_rating_id}` : "/document-ratings";
        const res = await authFetch(url, { method: editTarget ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
        if (!res.ok) { alert("Something went wrong."); return; }
        setShowModal(false);
        fetchRatings();
    }

    async function handleDelete() {
        const res = await authFetch(`/document-ratings/${deleteTarget.document_rating_id}`, { method: "DELETE" });
        if (!res.ok) { alert("Failed to delete."); return; }
        setRatings(r => r.filter(x => x.document_rating_id !== deleteTarget.document_rating_id));
        setDeleteTarget(null);
    }

    function renderStars(score) {
        return "★★★★★".split("").map((s, i) => (
            <span key={i} className={`crud-star ${i < score ? "filled" : ""}`}>{s}</span>
        ));
    }

    return (
        <div className="crud-page">
            <div className="crud-page-header">
                <div>
                    <h1>Document Ratings</h1>
                    <p>Select a document to view and manage ratings</p>
                </div>
                {selectedDocId && (
                    <button className="crud-add-button" onClick={openCreate}>+ Add rating</button>
                )}
            </div>

            <div className="crud-selector">
                <label>Document</label>
                <select value={selectedDocId} onChange={e => setSelectedDocId(e.target.value)}>
                    <option value="">Select a document...</option>
                    {documents.map(d => <option key={d.document_id} value={d.document_id}>{d.name}</option>)}
                </select>
            </div>

            <table className="crud-table">
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Score</th>
                        <th>Comment</th>
                        <th>Date</th>
                        <th className="actions-cell"></th>
                    </tr>
                </thead>
                <tbody>
                    {!selectedDocId && (
                        <tr><td colSpan={5} className="crud-empty">
                            <p>Select a document</p>
                            <p>Choose a document above to see its ratings.</p>
                        </td></tr>
                    )}
                    {selectedDocId && ratings.length === 0 && (
                        <tr><td colSpan={5} className="crud-empty">
                            <p>No ratings yet</p>
                            <p>Add a rating to get started.</p>
                        </td></tr>
                    )}
                    {ratings.map(r => (
                        <tr key={r.document_rating_id}>
                            <td><strong>{r.user_name || r.user_id}</strong></td>
                            <td><span className="crud-stars-display">{renderStars(r.score)}</span></td>
                            <td>{r.comment || <span className="crud-muted">—</span>}</td>
                            <td>{r.created_at ? new Date(r.created_at).toLocaleDateString() : "—"}</td>
                            <td className="actions-cell">
                                <button className="edit-action" onClick={() => openEdit(r)}>Edit</button>
                                <button className="delete-action" onClick={() => setDeleteTarget(r)}>Delete</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {showModal && (
                <div className="crud-modal-overlay">
                    <div className="crud-modal">
                        <h2>{editTarget ? "Edit rating" : "New rating"}</h2>
                        <div className="crud-form-group">
                            <label>Score</label>
                            <div className="crud-stars">
                                {[1, 2, 3, 4, 5].map(n => (
                                    <button key={n} type="button" className={`crud-star ${n <= parseInt(form.score) ? "filled" : ""}`} onClick={() => setForm(f => ({ ...f, score: String(n) }))}>★</button>
                                ))}
                            </div>
                        </div>
                        <div className="crud-form-group">
                            <label>Comment</label>
                            <textarea value={form.comment} onChange={e => setForm(f => ({ ...f, comment: e.target.value }))} placeholder="Optional comment..." />
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
                        <h2>Delete rating</h2>
                        <p>Are you sure you want to delete this rating?</p>
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
