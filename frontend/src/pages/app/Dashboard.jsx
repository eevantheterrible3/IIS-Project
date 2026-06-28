import { useEffect, useRef, useState } from "react";
import {
    ResponsiveContainer,
    AreaChart,
    Area,
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
} from "recharts";
import {
    Activity,
    Coins,
    DollarSign,
    Timer,
    Download,
    BarChart3,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { authFetch } from "@/lib/api";
import { exportDashboardPdf } from "@/lib/pdf";

const PIE_COLORS = ["#6366f1", "#22c55e", "#f59e0b", "#ec4899", "#06b6d4", "#8b5cf6", "#ef4444", "#14b8a6"];

const fmtInt = (n) => Number(n || 0).toLocaleString("en-US");
const fmtCost = (n) => `$${Number(n || 0).toFixed(4)}`;

function startFromRange(days) {
    if (!days) return null;
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() - days);
    return d.toISOString();
}

function StatCard({ icon: Icon, label, value, accent }) {
    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
            <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</span>
                <div className={`w-8 h-8 rounded-md flex items-center justify-center ${accent}`}>
                    <Icon size={16} />
                </div>
            </div>
            <div className="mt-3 text-2xl font-bold text-slate-900">{value}</div>
        </div>
    );
}

function ChartCard({ title, children }) {
    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
            <h2 className="text-sm font-semibold text-slate-700 mb-4">{title}</h2>
            {children}
        </div>
    );
}

export default function Dashboard() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [exporting, setExporting] = useState(false);
    const [documentTypes, setDocumentTypes] = useState([]);
    const [range, setRange] = useState("30");
    const [typeFilter, setTypeFilter] = useState("all");
    const contentRef = useRef(null);

    useEffect(() => {
        authFetch("/document-types").then(r => r.json()).then(setDocumentTypes).catch(() => {});
    }, []);

    useEffect(() => {
        fetchDashboard();
    }, [range, typeFilter]);

    async function fetchDashboard() {
        setLoading(true);
        const params = new URLSearchParams();
        const start = startFromRange(range === "all" ? null : Number(range));
        if (start) params.set("start", start);
        if (typeFilter !== "all") params.set("document_type_id", typeFilter);
        try {
            const res = await authFetch(`/analytics/dashboard?${params.toString()}`);
            if (!res.ok) { setData(null); return; }
            setData(await res.json());
        } catch {
            setData(null);
        } finally {
            setLoading(false);
        }
    }

    async function handleExport() {
        if (!data || !contentRef.current) return;
        setExporting(true);
        try {
            await exportDashboardPdf(contentRef.current, data);
        } catch (e) {
            alert("Greška pri generisanju PDF-a.");
        } finally {
            setExporting(false);
        }
    }

    const s = data?.summary;
    const hasData = s && s.total_generations > 0;

    return (
        <div className="p-8">
            <div className="flex items-start justify-between mb-8 gap-4 flex-wrap">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
                    <p className="text-sm text-slate-500 mt-1">Potrošnja i korišćenje LLM-a za generisanje dokumenata</p>
                </div>
                <div className="flex items-center gap-3 flex-wrap">
                    <Select value={range} onValueChange={setRange}>
                        <SelectTrigger className="w-40 h-9 bg-white"><SelectValue /></SelectTrigger>
                        <SelectContent>
                            <SelectItem value="7">Poslednjih 7 dana</SelectItem>
                            <SelectItem value="30">Poslednjih 30 dana</SelectItem>
                            <SelectItem value="90">Poslednjih 90 dana</SelectItem>
                            <SelectItem value="all">Sve vreme</SelectItem>
                        </SelectContent>
                    </Select>
                    <Select value={typeFilter} onValueChange={setTypeFilter}>
                        <SelectTrigger className="w-48 h-9 bg-white"><SelectValue placeholder="Svi tipovi" /></SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">Svi tipovi</SelectItem>
                            {documentTypes.map(t => (
                                <SelectItem key={t.document_type_id} value={String(t.document_type_id)}>{t.name}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                    <Button
                        onClick={handleExport}
                        disabled={!hasData || exporting}
                        className="bg-indigo-600 hover:bg-indigo-500 text-white gap-1.5"
                    >
                        <Download size={15} /> {exporting ? "Generišem..." : "Export PDF"}
                    </Button>
                </div>
            </div>

            {loading ? (
                <div className="text-center py-24 text-slate-400">Učitavanje...</div>
            ) : !hasData ? (
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm py-20 text-center">
                    <BarChart3 size={36} className="mx-auto mb-3 text-slate-300" />
                    <p className="text-slate-600 font-medium">Još nema podataka o potrošnji</p>
                    <p className="text-slate-400 text-sm mt-1">Pokreni generisanje ili doradu dokumenta da bi se ovde pojavila analitika.</p>
                </div>
            ) : (
                <div ref={contentRef} className="space-y-6">
                    {/* Summary cards */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                        <StatCard icon={Activity} label="Generisanja" value={fmtInt(s.total_generations)} accent="bg-indigo-50 text-indigo-600" />
                        <StatCard icon={Coins} label="Ukupno tokena" value={fmtInt(s.total_tokens)} accent="bg-emerald-50 text-emerald-600" />
                        <StatCard icon={DollarSign} label="Procenjeni trošak" value={fmtCost(s.estimated_cost)} accent="bg-amber-50 text-amber-600" />
                        <StatCard icon={Timer} label="Prosečna latencija" value={`${fmtInt(Math.round(s.avg_latency_ms))} ms`} accent="bg-sky-50 text-sky-600" />
                    </div>

                    {/* Charts */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-2">
                            <ChartCard title="Potrošnja tokena kroz vreme">
                                <div className="h-72">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <AreaChart data={data.time_series} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                                            <defs>
                                                <linearGradient id="tokGrad" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.35} />
                                                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                                </linearGradient>
                                            </defs>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                                            <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#94a3b8" }} />
                                            <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} />
                                            <Tooltip formatter={(v) => fmtInt(v)} />
                                            <Area type="monotone" dataKey="total_tokens" name="Tokeni" stroke="#6366f1" fill="url(#tokGrad)" strokeWidth={2} />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                </div>
                            </ChartCard>
                        </div>
                        <ChartCard title="Tokeni po tipu dokumenta">
                            <div className="h-72">
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={data.by_document_type}
                                            dataKey="total_tokens"
                                            nameKey="label"
                                            cx="50%" cy="50%"
                                            outerRadius={90}
                                        >
                                            {data.by_document_type.map((_, i) => (
                                                <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip formatter={(v) => fmtInt(v)} />
                                        <Legend wrapperStyle={{ fontSize: 11 }} />
                                    </PieChart>
                                </ResponsiveContainer>
                            </div>
                        </ChartCard>
                    </div>

                    <ChartCard title="Tokeni po modelu">
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={data.by_model} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
                                    <XAxis type="number" tick={{ fontSize: 11, fill: "#94a3b8" }} />
                                    <YAxis type="category" dataKey="label" width={140} tick={{ fontSize: 11, fill: "#64748b" }} />
                                    <Tooltip formatter={(v) => fmtInt(v)} />
                                    <Bar dataKey="total_tokens" name="Tokeni" fill="#6366f1" radius={[0, 4, 4, 0]} barSize={22} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </ChartCard>

                    {/* Recent generations table */}
                    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <div className="px-5 py-3.5 border-b border-slate-100">
                            <h2 className="text-sm font-semibold text-slate-700">Poslednja generisanja</h2>
                        </div>
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-slate-100">
                                    <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Datum</th>
                                    <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Tip</th>
                                    <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Model</th>
                                    <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Dokument</th>
                                    <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Korisnik</th>
                                    <th className="text-right px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Tokeni</th>
                                    <th className="text-right px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Trošak</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-50">
                                {data.recent.map((r) => (
                                    <tr key={r.llm_usage_log_id} className="hover:bg-slate-50 transition-colors">
                                        <td className="px-5 py-3 text-slate-600">{r.created_at ? new Date(r.created_at).toLocaleString() : "—"}</td>
                                        <td className="px-5 py-3">
                                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${r.generation_type === "refine" ? "bg-violet-50 text-violet-700 border-violet-200" : "bg-emerald-50 text-emerald-700 border-emerald-200"}`}>
                                                {r.generation_type}
                                            </span>
                                        </td>
                                        <td className="px-5 py-3 text-slate-600">{r.model || "—"}</td>
                                        <td className="px-5 py-3 text-slate-800 font-medium max-w-xs truncate">{r.document_name || "—"}</td>
                                        <td className="px-5 py-3 text-slate-600">{r.user_name || "—"}</td>
                                        <td className="px-5 py-3 text-right text-slate-700 tabular-nums">{fmtInt(r.total_tokens)}</td>
                                        <td className="px-5 py-3 text-right text-slate-700 tabular-nums">{r.estimated_cost != null ? fmtCost(r.estimated_cost) : "—"}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
