import { useEffect, useState } from "react";
import { authFetch } from "@/lib/api";
import "./CrudPages.css";

const typeColors = {
    create: "green",
    update: "amber",
    delete: "",
    view: "blue",
};

export default function ActivityLog() {
    const [activities, setActivities] = useState([]);
    const [filterType, setFilterType] = useState("");

    useEffect(() => { fetchActivities(); }, []);

    async function fetchActivities() {
        const params = new URLSearchParams();
        if (filterType) params.set("type", filterType);
        const url = `/activities${params.toString() ? "?" + params : ""}`;
        setActivities(await authFetch(url).then(r => r.json()));
    }

    function handleFilter() { fetchActivities(); }

    return (
        <div className="crud-page">
            <div className="crud-page-header">
                <div>
                    <h1>Activity Log</h1>
                    <p>Track all document operations across the system</p>
                </div>
            </div>

            <div style={{ display: "flex", gap: 12, marginBottom: 20, alignItems: "end" }}>
                <div className="crud-form-group" style={{ marginBottom: 0, minWidth: 160 }}>
                    <label>Action type</label>
                    <select value={filterType} onChange={e => setFilterType(e.target.value)}>
                        <option value="">All</option>
                        <option value="create">Create</option>
                        <option value="update">Update</option>
                        <option value="delete">Delete</option>
                        <option value="view">View</option>
                    </select>
                </div>
                <button className="crud-add-button" onClick={handleFilter} style={{ height: 37 }}>Filter</button>
            </div>

            <table className="crud-table">
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Action</th>
                        <th>Document</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {activities.length === 0 && (
                        <tr><td colSpan={4} style={{ textAlign: "center", padding: 40, color: "#999" }}>No activities found</td></tr>
                    )}
                    {activities.map(a => (
                        <tr key={a.activity_id}>
                            <td>{a.user_name || a.user_id}</td>
                            <td><span className={`crud-badge ${typeColors[a.type] || ""}`}>{a.type}</span></td>
                            <td>{a.document_name || a.document_id}</td>
                            <td>{a.date ? new Date(a.date).toLocaleString() : "—"}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
