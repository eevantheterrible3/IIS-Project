import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, ArrowRight, Check, Plus, X } from "lucide-react";
import { authFetch } from "@/lib/api";

const PRIORITY_CLS = {
    high:   "text-red-600 bg-red-50 border border-red-200",
    medium: "text-yellow-700 bg-yellow-50 border border-yellow-200",
    low:    "text-blue-600 bg-blue-50 border border-blue-200",
};

const SUBTASK_STATUS_CLS = {
    todo: "text-gray-500 bg-gray-50 border border-gray-200",
    done: "text-green-700 bg-green-50 border border-green-200",
};

const SUBTASK_STATUS_LABEL = { todo: "to do", done: "done" };

export default function TaskDetail() {
    const { project_id, task_id } = useParams();

    const [task, setTask]       = useState(null);
    const [loading, setLoading] = useState(true);
    const [denied, setDenied]   = useState(false);
    const [busy, setBusy]       = useState(false);

    // add-subtask modal
    const [showAdd, setShowAdd]       = useState(false);
    const [members, setMembers]       = useState([]);
    const [newSub, setNewSub]         = useState({ name: "", deadline: "", assigned_user_id: "" });

    useEffect(() => { fetchTask(); }, [task_id]);

    async function fetchTask() {
        const res = await authFetch(`/tasks/${task_id}/detail`);
        if (res.status === 403) { setDenied(true); setLoading(false); return; }
        if (res.ok) setTask(await res.json());
        setLoading(false);
    }

    async function advance() {
        setBusy(true);
        const res = await authFetch(`/tasks/${task_id}/advance`, { method: "PUT" });
        if (res.ok) setTask(await res.json());
        else alert((await res.json().catch(() => null))?.detail || "Something went wrong.");
        setBusy(false);
    }

    async function toggleSubtask(s) {
        if (!task.can_change_status) return;
        const next = s.status === "done" ? "todo" : "done";
        const res = await authFetch(`/tasks/${task_id}/subtasks/${s.subtask_id}/status`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ current_status: next }),
        });
        if (res.ok) setTask(await res.json());
    }

    async function openAdd() {
        if (members.length === 0) {
            const r = await authFetch("/project-realization/users");
            if (r.ok) setMembers(await r.json());
        }
        setNewSub({ name: "", deadline: "", assigned_user_id: "" });
        setShowAdd(true);
    }

    async function confirmAdd() {
        if (!newSub.name.trim()) return;
        const res = await authFetch(`/tasks/${task_id}/subtasks`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                task_id,
                name: newSub.name,
                deadline: newSub.deadline || null,
                assigned_user_id: newSub.assigned_user_id || null,
            }),
        });
        if (!res.ok) { alert("Something went wrong."); return; }
        setTask(await res.json());
        setShowAdd(false);
    }

    if (loading) return <div className="p-8 text-gray-400 text-sm">Loading...</div>;
    if (denied)  return <div className="p-8 text-gray-500 text-sm">You don't have access to this task.</div>;
    if (!task)   return <div className="p-8 text-gray-400 text-sm">Task not found.</div>;

    const currentIndex = task.steps.findIndex(s => s.is_current);

    return (
        <div className="p-6 space-y-5">

            {/* Breadcrumb */}
            <nav className="text-xs text-gray-400 flex items-center gap-1.5">
                <Link to="/app/project-realization/projects" className="hover:text-gray-600 transition-colors">
                    Projects
                </Link>
                <span>/</span>
                <Link to={`/app/project-realization/projects/${project_id}`} className="hover:text-gray-600 transition-colors">
                    {task.project_name}
                </Link>
                <span>/</span>
                <span className="text-gray-700 font-medium">{task.name}</span>
            </nav>

            {/* Back link */}
            <Link
                to={`/app/project-realization/projects/${project_id}`}
                className="inline-flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-700 transition-colors"
            >
                <ArrowLeft size={14} /> {task.project_name}
            </Link>

            {/* Title row */}
            <div className="flex items-center gap-3">
                <h2 className="text-xl font-bold text-gray-900">{task.name}</h2>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    task.is_completed
                        ? "text-green-700 bg-green-50 border border-green-200"
                        : "text-yellow-700 bg-yellow-50 border border-yellow-200"
                }`}>
                    {task.status ?? "—"}
                </span>
                {task.is_late && (
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-medium text-red-600 bg-red-50 border border-red-200">
                        Late
                    </span>
                )}
            </div>

            {/* Main content (details) + sidebar (workflow) */}
            <div className="grid grid-cols-3 gap-5 items-stretch">

                {/* Details — wider main column */}
                <div className="col-span-2 bg-white rounded-xl border border-gray-200 px-6 py-5 space-y-5">
                    <div className="grid grid-cols-3 gap-y-5 gap-x-6">
                        {[
                            { label: "Project",   value: task.project_name },
                            { label: "Assignee",  value: task.assigned_user ?? "—" },
                            { label: "Priority",  value: task.priority ?? "—", priority: task.priority },
                            { label: "Deadline",  value: task.deadline ?? "—", late: task.is_late },
                            { label: "Created",   value: task.created_at ?? "—" },
                        ].map(f => (
                            <div key={f.label}>
                                <p className="text-xs text-gray-400 mb-1">{f.label}</p>
                                {f.priority ? (
                                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${PRIORITY_CLS[f.priority] ?? ""}`}>
                                        {f.value}
                                    </span>
                                ) : (
                                    <p className={`text-sm font-semibold ${f.late ? "text-red-600" : "text-gray-800"}`}>
                                        {f.value}
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>

                    <div className="pt-5 border-t border-gray-100">
                        <p className="text-xs text-gray-400 mb-1.5">Description</p>
                        <p className="text-sm text-gray-700 leading-relaxed">
                            {task.description || <span className="text-gray-400">No description.</span>}
                        </p>
                    </div>
                </div>

                {/* Workflow — narrow sidebar with vertical stepper */}
                <div className="bg-white rounded-xl border border-gray-200 px-5 py-5 flex flex-col">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-4">Workflow</p>

                    <div className="flex-1">
                        {task.steps.map((s, i) => {
                            const done = currentIndex >= 0 && i < currentIndex;
                            const isLast = i === task.steps.length - 1;
                            return (
                                <div key={s.step_id} className="flex gap-3">
                                    <div className="flex flex-col items-center">
                                        <span className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 ${
                                            s.is_current
                                                ? "bg-gray-900 text-white ring-4 ring-gray-100"
                                                : done
                                                    ? "bg-green-500 text-white"
                                                    : "border-2 border-gray-200 bg-white"
                                        }`}>
                                            {done && <Check size={11} strokeWidth={3} />}
                                        </span>
                                        {!isLast && (
                                            <span className={`w-px flex-1 my-1 ${done ? "bg-green-300" : "bg-gray-200"}`} />
                                        )}
                                    </div>
                                    <div className={isLast ? "pb-0" : "pb-5"}>
                                        <p className={`text-sm ${
                                            s.is_current ? "font-semibold text-gray-900" : done ? "text-gray-600" : "text-gray-400"
                                        }`}>
                                            {s.status_name}
                                        </p>
                                        {s.is_current && <p className="text-xs text-gray-400">current</p>}
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    <div className="pt-5 mt-1 border-t border-gray-100">
                        {task.is_completed ? (
                            <p className="text-sm text-green-700 font-medium flex items-center gap-1.5">
                                <Check size={15} strokeWidth={3} /> Completed
                            </p>
                        ) : task.can_change_status && task.next_step_name ? (
                            <button
                                onClick={advance}
                                disabled={busy}
                                className="w-full flex items-center justify-center gap-1.5 px-3.5 py-2.5 text-sm bg-gray-900 text-white rounded-lg hover:bg-gray-700 disabled:opacity-40 transition-colors"
                            >
                                Move to: {task.next_step_name} <ArrowRight size={14} />
                            </button>
                        ) : (
                            <p className="text-xs text-gray-400">You don't have permission to change the status.</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Subtasks (progress lives here — it measures subtask completion) */}
            <div>
                <div className="flex items-center justify-between mb-3">
                    <h3 className="text-base font-bold text-gray-900">Subtasks</h3>
                    {task.is_manager && (
                        <button
                            onClick={openAdd}
                            className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-gray-900 text-white rounded-lg hover:bg-gray-700 transition-colors"
                        >
                            <Plus size={14} /> Add subtask
                        </button>
                    )}
                </div>

                <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                    {/* Progress strip */}
                    <div className="px-5 py-4 border-b border-gray-100">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-medium text-gray-500">
                                {task.progress_done} of {task.progress_total} done
                            </span>
                            <span className="text-xs font-semibold text-gray-700">{task.progress_percent}%</span>
                        </div>
                        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-green-500 rounded-full transition-all"
                                style={{ width: `${task.progress_percent}%` }}
                            />
                        </div>
                    </div>

                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-gray-100 text-gray-500 text-xs uppercase tracking-wide">
                                <th className="text-left px-5 py-3 font-medium">Name</th>
                                <th className="text-left px-5 py-3 font-medium">Status</th>
                                <th className="text-left px-5 py-3 font-medium">Deadline</th>
                                <th className="text-left px-5 py-3 font-medium">Assignee</th>
                            </tr>
                        </thead>
                        <tbody>
                            {task.subtasks.length === 0 && (
                                <tr>
                                    <td colSpan={4} className="px-5 py-8 text-center text-gray-400">No subtasks yet.</td>
                                </tr>
                            )}
                            {task.subtasks.map(s => (
                                <tr key={s.subtask_id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                                    <td className="px-5 py-3.5">
                                        <div className="flex items-center gap-2.5">
                                            <input
                                                type="checkbox"
                                                checked={s.status === "done"}
                                                disabled={!task.can_change_status}
                                                onChange={() => toggleSubtask(s)}
                                                className="w-4 h-4 rounded border-gray-300 text-gray-900 focus:ring-gray-400 disabled:opacity-50 cursor-pointer disabled:cursor-default"
                                            />
                                            <span className={`font-medium ${s.status === "done" ? "line-through text-gray-400" : "text-gray-900"}`}>
                                                {s.name}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-5 py-3.5">
                                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${SUBTASK_STATUS_CLS[s.status] ?? ""}`}>
                                            {SUBTASK_STATUS_LABEL[s.status] ?? s.status}
                                        </span>
                                    </td>
                                    <td className="px-5 py-3.5 text-gray-500">{s.deadline ?? "—"}</td>
                                    <td className="px-5 py-3.5 text-gray-500">{s.assigned_user ?? "—"}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Add subtask modal */}
            {showAdd && (
                <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-sm p-6 space-y-4">
                        <div className="flex items-center justify-between">
                            <h3 className="text-base font-semibold text-gray-900">Add subtask</h3>
                            <button onClick={() => setShowAdd(false)} className="text-gray-400 hover:text-gray-600">
                                <X size={16} />
                            </button>
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">
                                Name <span className="text-red-500">*</span>
                            </label>
                            <input
                                value={newSub.name}
                                onChange={e => setNewSub(f => ({ ...f, name: e.target.value }))}
                                placeholder="Subtask name"
                                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Deadline</label>
                            <input
                                type="date"
                                value={newSub.deadline}
                                onChange={e => setNewSub(f => ({ ...f, deadline: e.target.value }))}
                                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Assignee</label>
                            <select
                                value={newSub.assigned_user_id}
                                onChange={e => setNewSub(f => ({ ...f, assigned_user_id: e.target.value }))}
                                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-gray-300"
                            >
                                <option value="">Unassigned</option>
                                {members.map(u => (
                                    <option key={u.user_id} value={u.user_id}>{u.name} {u.last_name}</option>
                                ))}
                            </select>
                        </div>
                        <div className="flex justify-end gap-2 pt-1">
                            <button
                                onClick={() => setShowAdd(false)}
                                className="px-4 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={confirmAdd}
                                className="px-4 py-2 text-sm bg-gray-900 text-white rounded-lg hover:bg-gray-700 transition-colors"
                            >
                                Add
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
