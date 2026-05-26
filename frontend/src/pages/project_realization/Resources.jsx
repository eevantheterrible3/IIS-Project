import { useEffect, useState } from "react";
import { authFetch } from "@/lib/api";

const STATUS_CLS = {
    active:     "text-green-700 bg-green-50 border border-green-200",
    not_active: "text-gray-500 bg-gray-100 border border-gray-200",
};

export default function PRResources() {
    const [resources, setResources] = useState([]);
    const [loading, setLoading]     = useState(true);
    const [typeFilter, setTypeFilter]     = useState("All types");
    const [statusFilter, setStatusFilter] = useState("All statuses");

    useEffect(() => {
        authFetch("/project-realization/resources")
            .then(r => r.json())
            .then(data => { setResources(data); setLoading(false); })
            .catch(() => setLoading(false));
    }, []);

    const allTypes    = ["All types",    ...new Set(resources.map(r => r.resource_type).filter(Boolean))];
    const allStatuses = ["All statuses", "active", "not_active"];

    const filtered = resources.filter(r => {
        const typeOk   = typeFilter   === "All types"    || r.resource_type === typeFilter;
        const statusOk = statusFilter === "All statuses" || r.status        === statusFilter;
        return typeOk && statusOk;
    });

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
                {allStatuses.map(s => (
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

            {/* Table */}
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-gray-100 text-gray-500 text-xs uppercase tracking-wide">
                            <th className="text-left px-5 py-3 font-medium">Name</th>
                            <th className="text-left px-5 py-3 font-medium">Type</th>
                            <th className="text-left px-5 py-3 font-medium">Status</th>
                            <th className="text-left px-5 py-3 font-medium">Quantity</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading && (
                            <tr>
                                <td colSpan={4} className="px-5 py-8 text-center text-gray-400">Loading...</td>
                            </tr>
                        )}
                        {!loading && filtered.length === 0 && (
                            <tr>
                                <td colSpan={4} className="px-5 py-8 text-center text-gray-400">No resources found.</td>
                            </tr>
                        )}
                        {filtered.map(r => (
                            <tr key={r.resource_id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                                <td className="px-5 py-3.5 font-medium text-gray-900">{r.name}</td>
                                <td className="px-5 py-3.5 text-gray-500">{r.resource_type}</td>
                                <td className="px-5 py-3.5">
                                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${STATUS_CLS[r.status] ?? ""}`}>
                                        {r.status === "not_active" ? "inactive" : r.status}
                                    </span>
                                </td>
                                <td className="px-5 py-3.5 text-gray-500">{r.total_quantity}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
