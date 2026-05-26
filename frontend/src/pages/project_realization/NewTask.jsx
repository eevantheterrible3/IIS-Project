import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { Plus } from "lucide-react";
import { authFetch } from "@/lib/api";

export default function NewTask() {
    const { project_id } = useParams();
    const navigate = useNavigate();

    const [project, setProject]         = useState(null);
    const [workflows, setWorkflows]     = useState([]);
    const [resources, setResources]     = useState([]);

    const [name, setName]               = useState("");
    const [description, setDescription] = useState("");
    const [workflowId, setWorkflowId]   = useState("");
    const [priority, setPriority]       = useState("medium");
    const [assigneeId, setAssigneeId]   = useState("");
    const [deadline, setDeadline]       = useState("");
    const [taskResources, setTaskResources] = useState([]);
    const [saving, setSaving]           = useState(false);
    const [error, setError]             = useState("");

    useEffect(() => {
        async function load() {
            const [pRes, wRes, rRes] = await Promise.all([
                authFetch(`/project-realization/projects/${project_id}`),
                authFetch("/project-realization/workflows"),
                authFetch("/project-realization/resources"),
            ]);
            const [p, w, r] = await Promise.all([pRes.json(), wRes.json(), rRes.json()]);
            setProject(p);
            setWorkflows(w);
            setResources(r);
            if (w.length > 0) setWorkflowId(w[0].task_workflow_id);
        }
        load();
    }, [project_id]);

    const selectedWorkflow = workflows.find(w => w.task_workflow_id === workflowId);

    function addResource() {
        setTaskResources(prev => [...prev, { id: Date.now(), resource_id: "", quantity: 1, reserved_from: "", reserved_until: "" }]);
    }
    function removeResource(id) {
        setTaskResources(prev => prev.filter(r => r.id !== id));
    }
    function updateResource(id, field, value) {
        setTaskResources(prev => prev.map(r => r.id === id ? { ...r, [field]: value } : r));
    }

    async function handleSave() {
        if (!name.trim())  { setError("Task name is required."); return; }
        if (!workflowId)   { setError("Please select a workflow."); return; }
        if (!priority)     { setError("Priority is required."); return; }
        if (!deadline)     { setError("Deadline is required."); return; }

        setSaving(true);
        setError("");

        const body = {
            name: name.trim(),
            description: description.trim() || null,
            task_workflow_id: workflowId,
            priority,
            assigned_user_id: assigneeId || null,
            deadline,
            subtasks: [],
            resources: taskResources
                .filter(r => r.resource_id)
                .map(r => ({
                    resource_id: r.resource_id,
                    quantity: parseInt(r.quantity) || 1,
                    reserved_from: r.reserved_from || null,
                    reserved_until: r.reserved_until || null,
                })),
        };

        const res = await authFetch(`/project-realization/projects/${project_id}/tasks`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });

        if (res.ok) {
            navigate(`/app/project-realization/projects/${project_id}`);
        } else {
            const data = await res.json();
            setError(data.detail || "Failed to create task.");
            setSaving(false);
        }
    }

    if (!project) return <div className="p-8 text-gray-400 text-sm">Loading...</div>;

    return (
        <div className="p-6">
            {/* Breadcrumb */}
            <nav className="text-xs text-gray-400 flex items-center gap-1.5 mb-5">
                <Link to="/app/project-realization/projects" className="hover:text-gray-600 transition-colors">Projects</Link>
                <span>/</span>
                <Link to={`/app/project-realization/projects/${project_id}`} className="hover:text-gray-600 transition-colors">{project.name}</Link>
                <span>/</span>
                <span className="text-gray-700 font-medium">New task</span>
            </nav>

            <h2 className="text-xl font-bold text-gray-900 mb-6">Create task</h2>

            <div className="grid grid-cols-2 gap-5 items-start">

                {/* ── Left panel ── */}
                <div className="space-y-4">

                    {/* Basic info */}
                    <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
                        <h3 className="text-sm font-semibold text-gray-700">Basic information</h3>

                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">
                                Task name <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="text"
                                value={name}
                                onChange={e => setName(e.target.value)}
                                placeholder="Enter task name..."
                                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
                            <textarea
                                value={description}
                                onChange={e => setDescription(e.target.value)}
                                placeholder="Short task description..."
                                rows={3}
                                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300 resize-none"
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                            <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">Project</label>
                                <div className="border border-gray-100 rounded-lg px-3 py-2 text-sm text-gray-400 bg-gray-50">
                                    {project.name}
                                </div>
                            </div>
                            <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">
                                    Task type <span className="text-red-500">*</span>
                                </label>
                                <select
                                    value={workflowId}
                                    onChange={e => setWorkflowId(e.target.value)}
                                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                                >
                                    {workflows.map(w => (
                                        <option key={w.task_workflow_id} value={w.task_workflow_id}>{w.name}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                            <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">
                                    Priority <span className="text-red-500">*</span>
                                </label>
                                <select
                                    value={priority}
                                    onChange={e => setPriority(e.target.value)}
                                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                                >
                                    <option value="high">High</option>
                                    <option value="medium">Medium</option>
                                    <option value="low">Low</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">Assignee</label>
                                <select
                                    value={assigneeId}
                                    onChange={e => setAssigneeId(e.target.value)}
                                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                                >
                                    <option value="">— unassigned —</option>
                                    {project.members.map(m => (
                                        <option key={m.user_id} value={m.user_id}>
                                            {m.name} {m.last_name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">
                                Deadline <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="date"
                                value={deadline}
                                onChange={e => setDeadline(e.target.value)}
                                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                            />
                        </div>
                    </div>

                </div>

                {/* ── Right panel ── */}
                <div className="space-y-4">

                    {/* Workflow visualization */}
                    <div className="bg-white rounded-xl border border-gray-200 p-5">
                        <h3 className="text-sm font-semibold text-gray-700 mb-3">Workflow — task flow</h3>
                        {selectedWorkflow ? (
                            <>
                                <div className="flex items-center flex-wrap gap-1.5 mb-3">
                                    {selectedWorkflow.steps.map((step, i) => (
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
                                            {i < selectedWorkflow.steps.length - 1 && (
                                                <span className="text-gray-300 text-xs">→</span>
                                            )}
                                        </div>
                                    ))}
                                </div>
                                <p className="text-xs text-gray-400">
                                    Task is created with status "{selectedWorkflow.steps[0]?.status_name}"
                                </p>
                            </>
                        ) : (
                            <p className="text-xs text-gray-400">Select a task type to see the workflow.</p>
                        )}
                    </div>

                    {/* Resources */}
                    <div className="bg-white rounded-xl border border-gray-200 p-5">
                        <h3 className="text-sm font-semibold text-gray-700 mb-3">Resources</h3>
                        <div className="space-y-3">
                            {taskResources.map(r => {
                                const res = resources.find(x => x.resource_id === r.resource_id);
                                return (
                                    <div key={r.id} className="border border-gray-100 rounded-lg p-3 space-y-2">
                                        <div className="grid grid-cols-[1fr_80px] gap-2">
                                            <div>
                                                <label className="block text-xs text-gray-500 mb-1">Assign resource</label>
                                                <select
                                                    value={r.resource_id}
                                                    onChange={e => updateResource(r.id, "resource_id", e.target.value)}
                                                    className="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                                                >
                                                    <option value="">Select...</option>
                                                    {resources.map(res => (
                                                        <option key={res.resource_id} value={res.resource_id}>{res.name}</option>
                                                    ))}
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-xs text-gray-500 mb-1">Quantity</label>
                                                <input
                                                    type="number"
                                                    min={1}
                                                    value={r.quantity}
                                                    onChange={e => updateResource(r.id, "quantity", e.target.value)}
                                                    className="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                                                />
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-2 gap-2">
                                            <div>
                                                <label className="block text-xs text-gray-500 mb-1">From</label>
                                                <input
                                                    type="date"
                                                    value={r.reserved_from}
                                                    onChange={e => updateResource(r.id, "reserved_from", e.target.value)}
                                                    className="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-xs text-gray-500 mb-1">To</label>
                                                <input
                                                    type="date"
                                                    value={r.reserved_until}
                                                    onChange={e => updateResource(r.id, "reserved_until", e.target.value)}
                                                    className="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
                                                />
                                            </div>
                                        </div>
                                        {res && (
                                            <p className="text-xs text-gray-400">
                                                {res.name} · {res.resource_type} · total qty: {res.total_quantity}
                                            </p>
                                        )}
                                        <button
                                            onClick={() => removeResource(r.id)}
                                            className="text-xs text-red-400 hover:text-red-600 transition-colors"
                                        >
                                            Remove
                                        </button>
                                    </div>
                                );
                            })}
                        </div>
                        <button
                            onClick={addResource}
                            className="mt-3 text-sm text-gray-500 hover:text-gray-800 transition-colors flex items-center gap-1.5"
                        >
                            <Plus size={13} /> Assign resource
                        </button>
                    </div>
                </div>
            </div>

            {error && (
                <p className="mt-4 text-sm text-red-600">{error}</p>
            )}

            {/* Action buttons */}
            <div className="flex justify-end gap-3 mt-6">
                <button
                    onClick={() => navigate(`/app/project-realization/projects/${project_id}`)}
                    className="px-5 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                    Cancel
                </button>
                <button
                    onClick={handleSave}
                    disabled={saving}
                    className="px-5 py-2 text-sm bg-gray-900 text-white rounded-lg hover:bg-gray-700 disabled:opacity-40 transition-colors"
                >
                    {saving ? "Saving..." : "Save task"}
                </button>
            </div>
        </div>
    );
}
