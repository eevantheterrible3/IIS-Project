import { useEffect, useState } from "react";
import { X, Plus } from "lucide-react";
import { authFetch } from "@/lib/api";

const EMPTY_FORM = { name: "", statuses: [{ status_name: "" }, { status_name: "" }] };

export default function Workflows() {
    const [workflows, setWorkflows] = useState([]);
    const [newForm, setNewForm] = useState(EMPTY_FORM);
    const [editId, setEditId] = useState(null);
    const [editForm, setEditForm] = useState(null);
    const [deleteTarget, setDeleteTarget] = useState(null);

    useEffect(() => { fetchWorkflows(); }, []);

    async function fetchWorkflows() {
        const res = await authFetch("/project-realization/workflows");
        if (res.ok) setWorkflows(await res.json());
    }

    // ── new form helpers ──────────────────────────────────────────────────────
    function addNewStatus() {
        setNewForm(f => ({ ...f, statuses: [...f.statuses, { status_name: "" }] }));
    }
    function removeNewStatus(i) {
        setNewForm(f => ({ ...f, statuses: f.statuses.filter((_, idx) => idx !== i) }));
    }
    function updateNewStatus(i, value) {
        setNewForm(f => ({ ...f, statuses: f.statuses.map((s, idx) => idx === i ? { status_name: value } : s) }));
    }

    async function handleCreate() {
        if (!newForm.name.trim() || newForm.statuses.some(s => !s.status_name.trim())) return;
        const res = await authFetch("/project-realization/workflows", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: newForm.name, steps: newForm.statuses }),
        });
        if (!res.ok) { alert("Something went wrong."); return; }
        setNewForm(EMPTY_FORM);
        fetchWorkflows();
    }

    // ── inline edit helpers ───────────────────────────────────────────────────
    function openEdit(wf) {
        setEditId(wf.task_workflow_id);
        setEditForm({ name: wf.name, statuses: wf.steps.map(s => ({ status_name: s.status_name })) });
    }
    function cancelEdit() { setEditId(null); setEditForm(null); }

    function updateEditStatus(i, value) {
        setEditForm(f => ({ ...f, statuses: f.statuses.map((s, idx) => idx === i ? { status_name: value } : s) }));
    }

    async function handleSaveEdit(workflowId) {
        if (!editForm.name.trim() || editForm.statuses.some(s => !s.status_name.trim())) return;
        const res = await authFetch(`/project-realization/workflows/${workflowId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: editForm.name, steps: editForm.statuses }),
        });
        if (!res.ok) { alert("Something went wrong."); return; }
        cancelEdit();
        fetchWorkflows();
    }

    async function handleDelete() {
        const res = await authFetch(`/project-realization/workflows/${deleteTarget.task_workflow_id}`, {
            method: "DELETE",
        });
        if (!res.ok) { alert("Failed to delete."); return; }
        setWorkflows(w => w.filter(x => x.task_workflow_id !== deleteTarget.task_workflow_id));
        if (editId === deleteTarget.task_workflow_id) cancelEdit();
        setDeleteTarget(null);
    }

    return (
        <div className="p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Workflows</h2>

            <div className="grid grid-cols-2 gap-5 items-start">

                {/* ── Left: workflow list with inline editing ── */}
                <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-3">
                    <h3 className="text-sm font-semibold text-gray-700">Existing workflows</h3>

                    {workflows.length === 0 && (
                        <p className="text-sm text-gray-400">No workflows yet.</p>
                    )}

                    {workflows.map(wf => {
                        const isEditing = editId === wf.task_workflow_id;
                        return (
                            <div key={wf.task_workflow_id} className="border border-gray-100 rounded-lg p-4 space-y-3">

                                {isEditing ? (
                                    /* ── edit mode ── */
                                    <>
                                        <input
                                            value={editForm.name}
                                            onChange={e => setEditForm(f => ({ ...f, name: e.target.value }))}
                                            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-gray-300"
                                        />

                                        <div className="space-y-2">
                                            {editForm.statuses.map((s, i) => (
                                                <div key={i} className="flex items-center gap-2">
                                                    <span className="w-5 h-5 rounded-full bg-gray-100 border border-gray-200 flex items-center justify-center text-xs text-gray-500 shrink-0">
                                                        {i + 1}
                                                    </span>
                                                    <input
                                                        value={s.status_name}
                                                        onChange={e => updateEditStatus(i, e.target.value)}
                                                        placeholder="Status name..."
                                                        className="flex-1 border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                                                    />
                                                    {i === 0 && <span className="text-xs text-gray-400 shrink-0">initial</span>}
                                                    {i === editForm.statuses.length - 1 && (
                                                        <span className="text-xs text-gray-400 shrink-0">final</span>
                                                    )}
                                                </div>
                                            ))}
                                        </div>

                                        <p className="text-xs text-gray-400">
                                            Statuses can only be renamed — steps cannot be added or removed once the workflow is in use.
                                        </p>

                                        <div className="flex gap-2 pt-1">
                                            <button
                                                onClick={cancelEdit}
                                                className="flex-1 px-3 py-1.5 text-xs border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                                            >
                                                Cancel
                                            </button>
                                            <button
                                                onClick={() => handleSaveEdit(wf.task_workflow_id)}
                                                className="flex-1 px-3 py-1.5 text-xs bg-gray-900 text-white rounded-lg hover:bg-gray-700 transition-colors"
                                            >
                                                Save
                                            </button>
                                        </div>
                                    </>
                                ) : (
                                    /* ── view mode ── */
                                    <>
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm font-semibold text-gray-900">{wf.name}</span>
                                            <div className="flex gap-2">
                                                <button
                                                    onClick={() => openEdit(wf)}
                                                    className="px-3 py-1 text-xs border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                                                >
                                                    Edit
                                                </button>
                                                <button
                                                    onClick={() => setDeleteTarget(wf)}
                                                    className="px-3 py-1 text-xs border border-red-200 text-red-500 rounded-lg hover:bg-red-50 transition-colors"
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </div>

                                        <div className="flex items-center flex-wrap gap-1.5">
                                            {wf.steps.map((step, i) => (
                                                <div key={step.step_id} className="flex items-center gap-1.5">
                                                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${
                                                        step.is_first
                                                            ? "bg-yellow-50 border-yellow-300 text-yellow-800"
                                                            : step.is_last
                                                                ? "bg-green-50 border-green-200 text-green-700"
                                                                : "bg-gray-50 border-gray-200 text-gray-500"
                                                    }`}>
                                                        {step.status_name}
                                                    </span>
                                                    {i < wf.steps.length - 1 && (
                                                        <span className="text-gray-300 text-xs">→</span>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* ── Right: always-visible new workflow form ── */}
                <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
                    <h3 className="text-sm font-semibold text-gray-700">New workflow</h3>

                    <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">
                            Workflow name <span className="text-red-500">*</span>
                        </label>
                        <input
                            value={newForm.name}
                            onChange={e => setNewForm(f => ({ ...f, name: e.target.value }))}
                            placeholder="e.g. Field Work"
                            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-gray-600 mb-2">Statuses</label>
                        <div className="space-y-2">
                            {newForm.statuses.map((s, i) => (
                                <div key={i} className="flex items-center gap-2">
                                    <span className="w-5 h-5 rounded-full bg-gray-100 border border-gray-200 flex items-center justify-center text-xs text-gray-500 shrink-0">
                                        {i + 1}
                                    </span>
                                    <input
                                        value={s.status_name}
                                        onChange={e => updateNewStatus(i, e.target.value)}
                                        placeholder="Status name..."
                                        className="flex-1 border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                                    />
                                    {i === 0 && <span className="text-xs text-gray-400 shrink-0">initial</span>}
                                    {i === newForm.statuses.length - 1 && (
                                        <span className="text-xs text-gray-400 shrink-0">final</span>
                                    )}
                                    {i !== 0 && i !== newForm.statuses.length - 1 && (
                                        <button onClick={() => removeNewStatus(i)} className="text-gray-300 hover:text-gray-500 transition-colors shrink-0">
                                            <X size={14} />
                                        </button>
                                    )}
                                </div>
                            ))}
                        </div>

                        <button
                            onClick={addNewStatus}
                            className="mt-2 w-full text-sm text-gray-500 hover:text-gray-800 transition-colors flex items-center justify-center gap-1.5 border border-dashed border-gray-200 rounded-lg py-2"
                        >
                            <Plus size={13} /> Add status
                        </button>
                    </div>

                    <button
                        onClick={handleCreate}
                        className="w-full px-4 py-2 text-sm bg-gray-900 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    >
                        Add workflow
                    </button>
                </div>
            </div>

            {/* Delete confirm modal */}
            {deleteTarget && (
                <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl p-6 w-80 shadow-xl">
                        <h3 className="text-base font-semibold text-gray-900 mb-2">Delete workflow</h3>
                        <p className="text-sm text-gray-500 mb-5">
                            Delete <strong>{deleteTarget.name}</strong>? All statuses will be removed.
                        </p>
                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={() => setDeleteTarget(null)}
                                className="px-4 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleDelete}
                                className="px-4 py-2 text-sm bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
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
