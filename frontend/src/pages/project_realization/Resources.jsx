import { Fragment, useEffect, useState } from "react";
import { authFetch } from "@/lib/api";

const TYPES = ["Equipment", "Software", "Vehicle", "Space"];
const EMPTY_FORM = { name: "", resource_type: "", description: "", total_quantity: 1, status: "active" };

const STATUS_CLS = {
    active:     "text-green-700 bg-green-50 border border-green-200",
    not_active: "text-gray-500 bg-gray-100 border border-gray-200",
};

export default function PRResources() {
    const [resources, setResources]       = useState([]);
    const [typeFilter, setTypeFilter]     = useState("All types");
    const [statusFilter, setStatusFilter] = useState("All statuses");
    const [newForm, setNewForm]           = useState(EMPTY_FORM);
    const [newError, setNewError]         = useState("");
    const [editId, setEditId]             = useState(null);
    const [editForm, setEditForm]         = useState(null);
    const [editError, setEditError]       = useState("");
    const [deleteTarget, setDeleteTarget] = useState(null);
    const [deleteError, setDeleteError]   = useState("");

    const selectedProject = JSON.parse(localStorage.getItem("selectedProject") || "null");
    const isAdmin = selectedProject?.role_name === "ADMIN";

    useEffect(() => { fetchResources(); }, []);

    async function fetchResources() {
        const res = await authFetch("/project-realization/resources");
        if (res.ok) setResources(await res.json());
    }

    const allTypes = ["All types", ...new Set(resources.map(r => r.resource_type).filter(Boolean))];
    const filtered = resources.filter(r => {
        const typeOk   = typeFilter   === "All types"    || r.resource_type === typeFilter;
        const statusOk = statusFilter === "All statuses" || r.status        === statusFilter;
        return typeOk && statusOk;
    });

    function validate(form) {
        const missing = [];
        if (!form.name.trim())   missing.push("name");
        if (!form.resource_type) missing.push("resource type");
        if (!form.total_quantity || Number(form.total_quantity) < 1) missing.push("quantity");
        if (missing.length === 0) return "";
        return `Please fill in the required field${missing.length > 1 ? "s" : ""}: ${missing.join(", ")}.`;
    }

    async function handleCreate() {
        const err = validate(newForm);
        if (err) { setNewError(err); return; }
        setNewError("");
        const res = await authFetch("/project-realization/resources", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: newForm.name,
                resource_type: newForm.resource_type,
                description: newForm.description || null,
                total_quantity: Number(newForm.total_quantity),
                status: newForm.status,
            }),
        });
        if (!res.ok) { alert("Something went wrong."); return; }
        setNewForm(EMPTY_FORM);
        fetchResources();
    }

    function openEdit(r) {
        setEditId(r.resource_id);
        setEditForm({ name: r.name, resource_type: r.resource_type, description: r.description || "", total_quantity: r.total_quantity, status: r.status });
        setEditError("");
    }
    function cancelEdit() {
        setEditId(null);
        setEditForm(null);
        setEditError("");
    }

    async function handleSaveEdit() {
        const err = validate(editForm);
        if (err) { setEditError(err); return; }
        setEditError("");
        const res = await authFetch(`/project-realization/resources/${editId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: editForm.name,
                resource_type: editForm.resource_type,
                description: editForm.description || null,
                total_quantity: Number(editForm.total_quantity),
                status: editForm.status,
            }),
        });
        if (!res.ok) { alert("Something went wrong."); return; }
        cancelEdit();
        fetchResources();
    }

    async function handleDelete() {
        const res = await authFetch(`/project-realization/resources/${deleteTarget.resource_id}`, { method: "DELETE" });
        if (!res.ok) {
            const body = await res.json().catch(() => null);
            setDeleteError(body?.detail || "Failed to delete.");
            return;
        }
        setResources(r => r.filter(x => x.resource_id !== deleteTarget.resource_id));
        if (editId === deleteTarget.resource_id) cancelEdit();
        setDeleteTarget(null);
        setDeleteError("");
    }

    const colCount = isAdmin ? 5 : 4;

    const table = (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <table className="w-full text-sm">
                <thead>
                    <tr className="border-b border-gray-100 text-gray-500 text-xs uppercase tracking-wide">
                        <th className="text-left px-5 py-3 font-medium">Name</th>
                        <th className="text-left px-5 py-3 font-medium">Type</th>
                        <th className="text-left px-5 py-3 font-medium">Status</th>
                        <th className="text-left px-5 py-3 font-medium">Quantity</th>
                        {isAdmin && <th className="px-5 py-3" />}
                    </tr>
                </thead>
                <tbody>
                    {filtered.length === 0 && (
                        <tr>
                            <td colSpan={colCount} className="px-5 py-8 text-center text-gray-400">
                                No resources found.
                            </td>
                        </tr>
                    )}
                    {filtered.map(r => {
                        const isEditing = editId === r.resource_id;
                        return (
                            <Fragment key={r.resource_id}>
                                <tr className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                                    <td className="px-5 py-3.5 font-medium text-gray-900">{r.name}</td>
                                    <td className="px-5 py-3.5 text-gray-500">{r.resource_type}</td>
                                    <td className="px-5 py-3.5">
                                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${STATUS_CLS[r.status] ?? ""}`}>
                                            {r.status === "not_active" ? "inactive" : r.status}
                                        </span>
                                    </td>
                                    <td className="px-5 py-3.5 text-gray-500">{r.total_quantity}</td>
                                    {isAdmin && (
                                        <td className="px-5 py-3.5">
                                            <div className="flex gap-2 justify-end">
                                                <button
                                                    onClick={() => isEditing ? cancelEdit() : openEdit(r)}
                                                    className="px-3 py-1 text-xs border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                                                >
                                                    {isEditing ? "Close" : "Edit"}
                                                </button>
                                                <button
                                                    onClick={() => setDeleteTarget(r)}
                                                    className="px-3 py-1 text-xs border border-red-200 text-red-500 rounded-lg hover:bg-red-50 transition-colors"
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </td>
                                    )}
                                </tr>

                                {isEditing && (
                                    <tr className="border-b border-gray-100 bg-gray-50/50">
                                        <td colSpan={colCount} className="px-5 py-4">
                                            <div className="grid grid-cols-2 gap-4">
                                                <div>
                                                    <label className="block text-xs font-medium text-gray-600 mb-1">
                                                        Name <span className="text-red-500">*</span>
                                                    </label>
                                                    <input
                                                        value={editForm.name}
                                                        onChange={e => setEditForm(f => ({ ...f, name: e.target.value }))}
                                                        className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-xs font-medium text-gray-600 mb-1">
                                                        Resource type <span className="text-red-500">*</span>
                                                    </label>
                                                    <select
                                                        value={editForm.resource_type}
                                                        onChange={e => setEditForm(f => ({ ...f, resource_type: e.target.value }))}
                                                        className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300 bg-white"
                                                    >
                                                        <option value="">Select type...</option>
                                                        {TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                                                    </select>
                                                </div>
                                                <div>
                                                    <label className="block text-xs font-medium text-gray-600 mb-1">
                                                        Quantity <span className="text-red-500">*</span>
                                                    </label>
                                                    <input
                                                        type="number"
                                                        min={1}
                                                        value={editForm.total_quantity}
                                                        onChange={e => setEditForm(f => ({ ...f, total_quantity: parseInt(e.target.value) || 1 }))}
                                                        className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-xs font-medium text-gray-600 mb-1">Status</label>
                                                    <select
                                                        value={editForm.status}
                                                        onChange={e => setEditForm(f => ({ ...f, status: e.target.value }))}
                                                        className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300 bg-white"
                                                    >
                                                        <option value="active">Active</option>
                                                        <option value="not_active">Inactive</option>
                                                    </select>
                                                </div>
                                                <div className="col-span-2">
                                                    <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
                                                    <textarea
                                                        value={editForm.description}
                                                        onChange={e => setEditForm(f => ({ ...f, description: e.target.value }))}
                                                        rows={2}
                                                        className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300 resize-none"
                                                    />
                                                </div>
                                            </div>

                                            {editError && <p className="text-xs text-red-500 mt-3">{editError}</p>}

                                            <div className="flex gap-2 justify-end mt-3">
                                                <button
                                                    onClick={cancelEdit}
                                                    className="px-4 py-1.5 text-xs border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                                                >
                                                    Cancel
                                                </button>
                                                <button
                                                    onClick={handleSaveEdit}
                                                    className="px-4 py-1.5 text-xs bg-gray-900 text-white rounded-lg hover:bg-gray-700 transition-colors"
                                                >
                                                    Save
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </Fragment>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );

    return (
        <div className="p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-5">Resources</h2>

            {/* Filters */}
            <div className="flex gap-2 mb-5">
                {allTypes.map(t => (
                    <button
                        key={t}
                        onClick={() => setTypeFilter(t)}
                        className={`px-3 py-1.5 rounded-md text-sm border transition-colors ${
                            typeFilter === t
                                ? "bg-gray-900 text-white border-gray-900"
                                : "bg-white text-gray-600 border-gray-200 hover:border-gray-400"
                        }`}
                    >
                        {t}
                    </button>
                ))}
                <div className="w-px bg-gray-200 mx-1" />
                {["All statuses", "active", "not_active"].map(s => (
                    <button
                        key={s}
                        onClick={() => setStatusFilter(s)}
                        className={`px-3 py-1.5 rounded-md text-sm border transition-colors ${
                            statusFilter === s
                                ? "bg-gray-900 text-white border-gray-900"
                                : "bg-white text-gray-600 border-gray-200 hover:border-gray-400"
                        }`}
                    >
                        {s === "not_active" ? "inactive" : s}
                    </button>
                ))}
            </div>

            {isAdmin ? (
                <div className="grid grid-cols-[1fr_440px] gap-5 items-start">
                    {table}

                    {/* Right panel: always-visible new resource form */}
                    <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
                        <h3 className="text-sm font-semibold text-gray-700">New resource</h3>

                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">
                                Name <span className="text-red-500">*</span>
                            </label>
                            <input
                                value={newForm.name}
                                onChange={e => setNewForm(f => ({ ...f, name: e.target.value }))}
                                placeholder="Resource name"
                                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">
                                Resource type <span className="text-red-500">*</span>
                            </label>
                            <select
                                value={newForm.resource_type}
                                onChange={e => setNewForm(f => ({ ...f, resource_type: e.target.value }))}
                                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300 bg-white"
                            >
                                <option value="">Select type...</option>
                                {TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                            </select>
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
                            <textarea
                                value={newForm.description}
                                onChange={e => setNewForm(f => ({ ...f, description: e.target.value }))}
                                placeholder="Brief description..."
                                rows={3}
                                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300 resize-none"
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">
                                Quantity <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="number"
                                min={1}
                                value={newForm.total_quantity}
                                onChange={e => setNewForm(f => ({ ...f, total_quantity: parseInt(e.target.value) || 1 }))}
                                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Status</label>
                            <select
                                value={newForm.status}
                                onChange={e => setNewForm(f => ({ ...f, status: e.target.value }))}
                                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300 bg-white"
                            >
                                <option value="active">Active</option>
                                <option value="not_active">Inactive</option>
                            </select>
                        </div>

                        {newError && <p className="text-xs text-red-500">{newError}</p>}

                        <button
                            onClick={handleCreate}
                            className="w-full px-4 py-2 text-sm bg-gray-900 text-white rounded-lg hover:bg-gray-700 transition-colors"
                        >
                            Add resource
                        </button>
                    </div>
                </div>
            ) : (
                table
            )}

            {/* Delete confirm modal */}
            {deleteTarget && (
                <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl p-6 w-80 shadow-xl">
                        <h3 className="text-base font-semibold text-gray-900 mb-2">Delete resource</h3>
                        <p className="text-sm text-gray-500 mb-5">
                            Delete <strong>{deleteTarget.name}</strong>?
                        </p>
                        {deleteError && <p className="text-sm text-red-500 mb-4">{deleteError}</p>}
                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={() => { setDeleteTarget(null); setDeleteError(""); }}
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
