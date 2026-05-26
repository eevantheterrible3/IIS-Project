import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { ChevronDown, ChevronRight, X, Plus, UserPlus } from "lucide-react";
import { authFetch } from "@/lib/api";

const PRIORITY_CLS = {
    high:   "text-red-600 bg-red-50 border border-red-200",
    medium: "text-yellow-700 bg-yellow-50 border border-yellow-200",
    low:    "text-blue-600 bg-blue-50 border border-blue-200",
};

const SUBTASK_STATUS_CLS = {
    created:     "text-gray-500 bg-gray-50 border border-gray-200",
    in_progress: "text-yellow-700 bg-yellow-50 border border-yellow-200",
    done:        "text-green-700 bg-green-50 border border-green-200",
};

export default function ProjectDetail() {
    const { project_id } = useParams();
    const navigate = useNavigate();

    const [project, setProject]       = useState(null);
    const [loading, setLoading]       = useState(true);
    const [expanded, setExpanded]     = useState({});

    // add-member modal
    const [showAddMember, setShowAddMember] = useState(false);
    const [allUsers, setAllUsers]           = useState([]);
    const [selectedUser, setSelectedUser]   = useState("");
    const [addingMember, setAddingMember]   = useState(false);

    async function fetchProject() {
        const r = await authFetch(`/project-realization/projects/${project_id}`);
        if (!r.ok) { setLoading(false); return; }
        const data = await r.json();
        setProject(data);
        setLoading(false);
    }

    useEffect(() => { fetchProject(); }, [project_id]);

    function toggleExpand(taskId) {
        setExpanded(prev => ({ ...prev, [taskId]: !prev[taskId] }));
    }

    async function openAddMember() {
        if (allUsers.length === 0) {
            const r = await authFetch("/project-realization/users");
            if (r.ok) setAllUsers(await r.json());
        }
        setSelectedUser("");
        setShowAddMember(true);
    }

    async function confirmAddMember() {
        if (!selectedUser) return;
        setAddingMember(true);
        await authFetch(`/project-realization/projects/${project_id}/members`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: selectedUser }),
        });
        setAddingMember(false);
        setShowAddMember(false);
        fetchProject();
    }

    async function removeMember(userId) {
        await authFetch(`/project-realization/projects/${project_id}/members/${userId}`, {
            method: "DELETE",
        });
        fetchProject();
    }

    if (loading) {
        return <div className="p-8 text-gray-400 text-sm">Loading...</div>;
    }
    if (!project) {
        return <div className="p-8 text-gray-400 text-sm">Project not found.</div>;
    }

    const { stats, members, tasks, is_manager } = project;

    // users not yet in project (for dropdown)
    const memberIds = new Set(members.map(m => m.user_id));
    const usersToAdd = allUsers.filter(u => !memberIds.has(u.user_id));

    return (
        <div className="p-6 space-y-5">

            {/* Breadcrumb */}
            <nav className="text-xs text-gray-400 flex items-center gap-1.5">
                <Link to="/app/project-realization/projects" className="hover:text-gray-600 transition-colors">
                    Projects
                </Link>
                <span>/</span>
                <span className="text-gray-700 font-medium">{project.name}</span>
            </nav>

            {/* Title row */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <h2 className="text-xl font-bold text-gray-900">{project.name}</h2>
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        project.status === "active"
                            ? "text-green-700 bg-green-50 border border-green-200"
                            : "text-gray-500 bg-gray-50 border border-gray-200"
                    }`}>
                        {project.status}
                    </span>
                </div>
                {is_manager && (
                    <button
                        onClick={() => navigate(`/app/project-realization/projects/${project_id}/new-task`)}
                        className="px-3 py-1.5 text-sm bg-gray-900 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    >
                        + New task
                    </button>
                )}
            </div>

            {/* Stats row */}
            <div className="grid grid-cols-4 gap-3">
                {[
                    { label: "Progress",     value: `${stats.progress}%` },
                    { label: "Total tasks",  value: stats.total },
                    { label: "Completed",    value: stats.completed },
                    { label: "Late",         value: stats.late, red: stats.late > 0 },
                ].map(s => (
                    <div key={s.label} className="bg-white rounded-xl border border-gray-200 px-4 py-3">
                        <p className="text-xs text-gray-400 mb-0.5">{s.label}</p>
                        <p className={`text-xl font-bold ${s.red ? "text-red-600" : "text-gray-900"}`}>
                            {s.value}
                        </p>
                    </div>
                ))}
            </div>

            {/* Team members */}
            <div className="bg-white rounded-xl border border-gray-200 px-5 py-4">
                <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold text-gray-800">Team members</h3>
                    {is_manager && (
                        <button
                            onClick={openAddMember}
                            className="flex items-center gap-1.5 px-2.5 py-1 text-xs border border-gray-200 rounded-md hover:bg-gray-50 transition-colors"
                        >
                            <UserPlus size={12} />
                            Add member
                        </button>
                    )}
                </div>
                <div className="flex flex-wrap gap-2">
                    {members.map(m => {
                        const isPM = m.role === "PROJECT_MANAGER";
                        return (
                            <div
                                key={m.user_id}
                                className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-full text-sm"
                            >
                                <span className="text-gray-800 font-medium">
                                    {m.name} {m.last_name}
                                </span>
                                {isPM && (
                                    <span className="text-xs text-gray-400">(PM)</span>
                                )}
                                {is_manager && !isPM && (
                                    <button
                                        onClick={() => removeMember(m.user_id)}
                                        className="text-gray-400 hover:text-red-500 transition-colors"
                                    >
                                        <X size={12} />
                                    </button>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Tasks table */}
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-gray-100 text-gray-500 text-xs uppercase tracking-wide">
                            <th className="text-left px-5 py-3 font-medium">Task</th>
                            <th className="text-left px-5 py-3 font-medium">Status</th>
                            <th className="text-left px-5 py-3 font-medium">Priority</th>
                            <th className="text-left px-5 py-3 font-medium">Assigned to</th>
                            <th className="text-left px-5 py-3 font-medium">Deadline</th>
                            <th className="px-5 py-3" />
                        </tr>
                    </thead>
                    <tbody>
                        {tasks.length === 0 && (
                            <tr>
                                <td colSpan={6} className="px-5 py-8 text-center text-gray-400">
                                    No tasks yet.
                                </td>
                            </tr>
                        )}
                        {tasks.map(task => (
                            <>
                                {/* Task row */}
                                <tr
                                    key={task.task_id}
                                    className={`border-b border-gray-50 transition-colors ${
                                        task.is_late ? "bg-red-50 hover:bg-red-100" : "hover:bg-gray-50"
                                    }`}
                                >
                                    <td className="px-5 py-3.5 font-medium text-gray-900">
                                        <div className="flex items-center gap-2">
                                            {task.subtasks.length > 0 && (
                                                <button
                                                    onClick={() => toggleExpand(task.task_id)}
                                                    className="text-gray-400 hover:text-gray-700 transition-colors"
                                                >
                                                    {expanded[task.task_id]
                                                        ? <ChevronDown size={14} />
                                                        : <ChevronRight size={14} />
                                                    }
                                                </button>
                                            )}
                                            {task.subtasks.length === 0 && (
                                                <span className="w-[14px]" />
                                            )}
                                            <span className={task.is_completed ? "line-through text-gray-400" : ""}>
                                                {task.name}
                                            </span>
                                            {task.is_late && (
                                                <span className="text-xs text-red-500 font-medium">Late</span>
                                            )}
                                        </div>
                                    </td>
                                    <td className="px-5 py-3.5 text-gray-600">
                                        {task.status ?? "—"}
                                    </td>
                                    <td className="px-5 py-3.5">
                                        {task.priority ? (
                                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${PRIORITY_CLS[task.priority] ?? ""}`}>
                                                {task.priority}
                                            </span>
                                        ) : "—"}
                                    </td>
                                    <td className="px-5 py-3.5 text-gray-500">
                                        {task.assigned_user ?? "—"}
                                    </td>
                                    <td className={`px-5 py-3.5 ${task.is_late ? "text-red-600 font-medium" : "text-gray-500"}`}>
                                        {task.deadline ?? "—"}
                                    </td>
                                    <td className="px-5 py-3.5 text-right">
                                        {task.subtasks.length > 0 && (
                                            <span className="text-xs text-gray-400">
                                                {task.subtasks.length} subtask{task.subtasks.length !== 1 ? "s" : ""}
                                            </span>
                                        )}
                                    </td>
                                </tr>

                                {/* Subtask rows */}
                                {expanded[task.task_id] && task.subtasks.map(s => (
                                    <tr key={s.subtask_id} className="bg-gray-50 border-b border-gray-100">
                                        <td className="pl-14 pr-5 py-2.5 text-gray-600">
                                            ↳ {s.name}
                                        </td>
                                        <td className="px-5 py-2.5">
                                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${SUBTASK_STATUS_CLS[s.status] ?? ""}`}>
                                                {s.status?.replace("_", " ")}
                                            </span>
                                        </td>
                                        <td className="px-5 py-2.5 text-gray-400">—</td>
                                        <td className="px-5 py-2.5 text-gray-500 text-xs">{s.assigned_user ?? "—"}</td>
                                        <td className="px-5 py-2.5 text-gray-400 text-xs">{s.deadline ?? "—"}</td>
                                        <td />
                                    </tr>
                                ))}

                                {/* Resources row */}
                                {expanded[task.task_id] && (
                                    <tr className="bg-blue-50 border-b border-blue-100">
                                        <td className="pl-14 pr-5 py-2 text-xs text-blue-700 font-medium" colSpan={6}>
                                            {task.resources.length === 0
                                                ? "No resources assigned"
                                                : (
                                                    <span className="flex items-center gap-3 flex-wrap">
                                                        <span className="text-blue-400">Resources:</span>
                                                        {task.resources.map(r => (
                                                            <span key={r.resource_id} className="px-2 py-0.5 bg-white border border-blue-200 rounded-full text-blue-700">
                                                                {r.name} × {r.quantity}
                                                                <span className="ml-1.5 text-blue-400">({r.status?.replace("_", " ")})</span>
                                                            </span>
                                                        ))}
                                                    </span>
                                                )
                                            }
                                        </td>
                                    </tr>
                                )}
                            </>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Add Member Modal */}
            {showAddMember && (
                <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-sm p-6">
                        <h3 className="text-base font-semibold text-gray-900 mb-4">Add team member</h3>
                        <select
                            value={selectedUser}
                            onChange={e => setSelectedUser(e.target.value)}
                            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 mb-4 focus:outline-none focus:ring-2 focus:ring-gray-300"
                        >
                            <option value="">Select a user…</option>
                            {usersToAdd.map(u => (
                                <option key={u.user_id} value={u.user_id}>
                                    {u.name} {u.last_name} ({u.email})
                                </option>
                            ))}
                        </select>
                        <div className="flex justify-end gap-2">
                            <button
                                onClick={() => setShowAddMember(false)}
                                className="px-4 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={confirmAddMember}
                                disabled={!selectedUser || addingMember}
                                className="px-4 py-2 text-sm bg-gray-900 text-white rounded-lg hover:bg-gray-700 disabled:opacity-40 transition-colors"
                            >
                                {addingMember ? "Adding…" : "Add"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
