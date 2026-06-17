import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { authFetch } from "@/lib/api";

export default function Home() {
    const navigate = useNavigate();
    const [data, setData]       = useState(null);
    const [loading, setLoading] = useState(true);

    const user = JSON.parse(localStorage.getItem("user") || "null");

    useEffect(() => {
        authFetch("/project-realization/home")
            .then(r => r.json())
            .then(d => { setData(d); setLoading(false); })
            .catch(() => setLoading(false));
    }, []);

    if (loading) return <div className="p-8 text-gray-400 text-sm">Loading...</div>;
    if (!data)   return <div className="p-8 text-gray-400 text-sm">Could not load data.</div>;

    const totalTasks     = data.projects.reduce((s, p) => s + p.task_total, 0);
    const totalCompleted = data.projects.reduce((s, p) => s + p.task_completed, 0);
    const pct = v => totalTasks > 0 ? Math.round(v / totalTasks * 100) : 0;

    const distribution = [
        { label: "Completed", value: totalCompleted,  color: "bg-green-500",  dot: "bg-green-500" },
        { label: "Active",    value: data.stats_active, color: "bg-amber-400", dot: "bg-amber-400" },
        { label: "Late",      value: data.stats_late,   color: "bg-red-400",   dot: "bg-red-400"   },
    ];

    const stats = [
        { label: "Projects",        value: data.stats_projects },
        { label: "Active tasks",    value: data.stats_active },
        { label: "Completed tasks", value: totalCompleted },
        { label: "Late tasks",      value: data.stats_late, red: data.stats_late > 0 },
    ];

    return (
        <div className="p-6 space-y-5">

            {/* Greeting */}
            <h2 className="text-xl font-bold text-gray-900">
                Welcome back, {user?.name ?? ""}
            </h2>

            {/* Top row: stats left + distribution right */}
            <div className="grid grid-cols-2 gap-5">

                {/* Stats — 2x2 grid */}
                <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
                    <div className="grid grid-cols-2 divide-x divide-y divide-gray-100">
                        {stats.map(s => (
                            <div key={s.label} className="px-6 py-5">
                                <p className={`text-3xl font-bold ${s.red ? "text-red-500" : "text-gray-900"}`}>
                                    {s.value}
                                </p>
                                <p className="text-xs text-gray-400 mt-1">{s.label}</p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Task distribution */}
                <div className="bg-white border border-gray-200 rounded-xl px-6 py-5">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-4">
                        Task distribution
                    </p>
                    <div className="space-y-3.5">
                        {distribution.map(d => (
                            <div key={d.label} className="flex items-center gap-3">
                                <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${d.dot}`} />
                                <span className="text-sm text-gray-600 w-24 shrink-0">{d.label}</span>
                                <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full rounded-full ${d.color}`}
                                        style={{ width: `${pct(d.value)}%` }}
                                    />
                                </div>
                                <span className="text-sm text-gray-500 w-8 text-right shrink-0">
                                    {pct(d.value)}%
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Projects grid */}
            <h3 className="text-sm font-semibold text-gray-700">Projects</h3>
            <div className="grid grid-cols-2 gap-4">
                {data.projects.map(p => {
                    const isFinished = p.status === "finished";
                    const hasLate    = p.task_late > 0;

                    return (
                        <div
                            key={p.project_id}
                            onClick={() => navigate(`/app/project-realization/projects/${p.project_id}`)}
                            className="bg-white border border-gray-200 rounded-xl px-5 py-4 cursor-pointer hover:shadow-sm hover:border-gray-300 transition-all"
                        >
                            <div className="flex items-start justify-between gap-3 mb-3">
                                <p className="font-semibold text-gray-900 text-sm leading-snug">
                                    {p.name}
                                </p>
                                <span className={`w-2 h-2 rounded-full shrink-0 mt-1 ${
                                    isFinished ? "bg-gray-300" :
                                    hasLate    ? "bg-red-400"  : "bg-green-500"
                                }`} />
                            </div>

                            <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden mb-1.5">
                                <div
                                    className={`h-full rounded-full ${hasLate ? "bg-red-400" : "bg-green-500"}`}
                                    style={{ width: `${p.progress}%` }}
                                />
                            </div>

                            <div className="flex items-center justify-between text-xs text-gray-400">
                                <div className="flex items-center gap-2">
                                    {p.manager_name && <span>{p.manager_name}</span>}
                                    {p.manager_name && <span>·</span>}
                                    <span>{p.member_count} members</span>
                                    {hasLate && (
                                        <span className="text-red-500 font-medium">· {p.task_late} late</span>
                                    )}
                                </div>
                                <span>{p.task_completed}/{p.task_total} tasks · {p.progress}%</span>
                            </div>
                        </div>
                    );
                })}

                {data.projects.length === 0 && (
                    <div className="col-span-2 py-12 text-center text-gray-400 text-sm">
                        No projects available.
                    </div>
                )}
            </div>
        </div>
    );
}
