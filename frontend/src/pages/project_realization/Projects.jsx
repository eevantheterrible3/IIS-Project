import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { authFetch } from "@/lib/api";

const STATUS_LABEL = {
    active:   { text: "active",   cls: "text-green-700 bg-green-50 border border-green-200" },
    finished: { text: "finished", cls: "text-gray-500 bg-gray-50 border border-gray-200" },
};

const ALL_STATUSES = ["All statuses", "active", "finished"];

export default function PRProjects() {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [statusFilter, setStatusFilter] = useState("All statuses");

    useEffect(() => {
        authFetch("/project-realization/projects")
            .then(r => r.json())
            .then(data => { setProjects(data); setLoading(false); })
            .catch(() => setLoading(false));
    }, []);

    const filtered = statusFilter === "All statuses"
        ? projects
        : projects.filter(p => (STATUS_LABEL[p.status]?.text ?? p.status) === statusFilter);

    return (
        <div className="p-6">
            <div className="flex items-center justify-between mb-5">
                <h2 className="text-xl font-bold text-gray-900">Projects</h2>
                <button className="px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-700 transition-colors">
                    + New project
                </button>
            </div>

            {/* Filters */}
            <div className="flex gap-2 mb-5">
                {ALL_STATUSES.map(s => (
                    <button
                        key={s}
                        onClick={() => setStatusFilter(s)}
                        className={`px-3 py-1.5 rounded-md text-sm border transition-colors ${
                            statusFilter === s
                                ? "bg-gray-900 text-white border-gray-900"
                                : "bg-white text-gray-600 border-gray-200 hover:border-gray-400"
                        }`}
                    >
                        {s}
                    </button>
                ))}
            </div>

            {/* Table */}
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-gray-100 text-gray-500 text-xs uppercase tracking-wide">
                            <th className="text-left px-5 py-3 font-medium">Project name</th>
                            <th className="text-left px-5 py-3 font-medium">Manager</th>
                            <th className="text-left px-5 py-3 font-medium">Period</th>
                            <th className="text-left px-5 py-3 font-medium">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading && (
                            <tr>
                                <td colSpan={4} className="px-5 py-8 text-center text-gray-400">
                                    Loading...
                                </td>
                            </tr>
                        )}
                        {!loading && filtered.length === 0 && (
                            <tr>
                                <td colSpan={4} className="px-5 py-8 text-center text-gray-400">
                                    No projects found.
                                </td>
                            </tr>
                        )}
                        {filtered.map(project => {
                            const status = STATUS_LABEL[project.status] ?? { text: project.status, cls: "text-gray-500 bg-gray-50 border border-gray-200" };
                            const period = project.start_date && project.end_date
                                ? `${project.start_date} – ${project.end_date}`
                                : "—";
                            return (
                                <tr key={project.project_id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                                    <td className="px-5 py-3.5 font-medium">
                                        <Link
                                            to={`/app/project-realization/projects/${project.project_id}`}
                                            className="text-gray-900 hover:text-gray-600 hover:underline transition-colors"
                                        >
                                            {project.name}
                                        </Link>
                                    </td>
                                    <td className="px-5 py-3.5 text-gray-600">{project.manager_name ?? "—"}</td>
                                    <td className="px-5 py-3.5 text-gray-500">{period}</td>
                                    <td className="px-5 py-3.5">
                                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${status.cls}`}>
                                            {status.text}
                                        </span>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
