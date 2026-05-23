import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Pencil, Trash2, FileText, Plus } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { authFetch } from "@/lib/api";

function timeAgo(dateStr) {
    if (!dateStr) return "—";
    const diff = Math.floor((Date.now() - new Date(dateStr)) / 1000);
    if (diff < 60) return "just now";
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    const days = Math.floor(diff / 86400);
    if (days < 7) return `${days}d ago`;
    return `${Math.floor(days / 7)}w ago`;
}

const statusColors = {
    draft: "bg-amber-50 text-amber-700 border-amber-200",
    active: "bg-emerald-50 text-emerald-700 border-emerald-200",
    finished: "bg-slate-100 text-slate-600 border-slate-200",
};

export default function DocumentsList() {
    const navigate = useNavigate();

    const [documents, setDocuments] = useState([]);
    const [documentTypes, setDocumentTypes] = useState([]);
    const [projects, setProjects] = useState([]);
    const [search, setSearch] = useState("");
    const [showCreate, setShowCreate] = useState(false);
    const [createForm, setCreateForm] = useState({ name: "", document_type_id: "", project_id: "", user_prompt: "" });
    const [deleteTarget, setDeleteTarget] = useState(null);

    useEffect(() => {
        fetchDocuments();
        authFetch("/document-types").then(r => r.json()).then(setDocumentTypes);
        setProjects(JSON.parse(localStorage.getItem("projects") || "[]"));
    }, []);

    async function fetchDocuments() {
        const res = await authFetch("/documents/my");
        setDocuments(await res.json());
    }

    async function handleCreate() {
        if (!createForm.name || !createForm.document_type_id || !createForm.project_id) return;
        const res = await authFetch("/documents", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: createForm.name,
                document_type_id: parseInt(createForm.document_type_id),
                project_id: parseInt(createForm.project_id),
                user_prompt: createForm.user_prompt || null,
            }),
        });
        if (!res.ok) { alert("Failed to create document."); return; }
        setShowCreate(false);
        setCreateForm({ name: "", document_type_id: "", project_id: "", user_prompt: "" });
        fetchDocuments();
    }

    async function handleDelete() {
        const res = await authFetch(`/documents/delete/${deleteTarget.document_id}`, { method: "DELETE" });
        if (!res.ok) { alert("Failed to delete document."); return; }
        setDocuments(d => d.filter(x => x.document_id !== deleteTarget.document_id));
        setDeleteTarget(null);
    }

    const filtered = documents.filter(d =>
        d.name.toLowerCase().includes(search.toLowerCase()) ||
        (d.user_prompt || "").toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="p-8">
            <div className="flex items-start justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Documents</h1>
                    <p className="text-sm text-slate-500 mt-1">{documents.length} document{documents.length !== 1 ? "s" : ""} across all projects</p>
                </div>
                <div className="flex items-center gap-3">
                    <Input
                        placeholder="Search documents..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        className="w-56 h-9 bg-white"
                    />
                    <Button
                        onClick={() => setShowCreate(true)}
                        className="bg-indigo-600 hover:bg-indigo-500 text-white gap-1.5"
                    >
                        <Plus size={15} /> New document
                    </Button>
                </div>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-slate-100">
                            <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Name</th>
                            <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Description</th>
                            <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Type</th>
                            <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Status</th>
                            <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Modified</th>
                            <th className="px-5 py-3 w-20" />
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                        {filtered.length === 0 && (
                            <tr>
                                <td colSpan={6} className="px-5 py-16 text-center">
                                    <FileText size={32} className="mx-auto mb-3 text-slate-300" />
                                    <p className="text-slate-500 font-medium">No documents yet</p>
                                    <p className="text-slate-400 text-xs mt-1">Create your first document to get started.</p>
                                </td>
                            </tr>
                        )}
                        {filtered.map(doc => (
                            <tr
                                key={doc.document_id}
                                className="hover:bg-slate-50 cursor-pointer transition-colors group"
                                onClick={() => navigate(`/app/documents/${doc.document_id}`)}
                            >
                                <td className="px-5 py-3.5">
                                    <div className="flex items-center gap-2.5">
                                        <div className="w-7 h-7 rounded-md bg-indigo-50 flex items-center justify-center shrink-0">
                                            <FileText size={13} className="text-indigo-500" />
                                        </div>
                                        <span className="font-semibold text-slate-800">{doc.name}</span>
                                    </div>
                                </td>
                                <td className="px-5 py-3.5 text-slate-500 max-w-xs truncate">{doc.user_prompt || "—"}</td>
                                <td className="px-5 py-3.5">
                                    {doc.document_type_name
                                        ? <span className="text-slate-600 font-medium">{doc.document_type_name}</span>
                                        : <span className="text-slate-300">—</span>
                                    }
                                </td>
                                <td className="px-5 py-3.5">
                                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${statusColors[doc.status] || statusColors.draft}`}>
                                        {doc.status}
                                    </span>
                                </td>
                                <td className="px-5 py-3.5 text-slate-400 text-xs">{timeAgo(doc.updated_at || doc.created_at)}</td>
                                <td className="px-5 py-3.5">
                                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity" onClick={e => e.stopPropagation()}>
                                        <button
                                            className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-md transition-colors"
                                            onClick={() => navigate(`/app/documents/${doc.document_id}`)}
                                        >
                                            <Pencil size={13} />
                                        </button>
                                        <button
                                            className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-md transition-colors"
                                            onClick={() => setDeleteTarget(doc)}
                                        >
                                            <Trash2 size={13} />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <Dialog open={showCreate} onOpenChange={setShowCreate}>
                <DialogContent className="sm:max-w-md">
                    <DialogHeader>
                        <DialogTitle>New document</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 py-2">
                        <div className="space-y-1.5">
                            <Label>Name</Label>
                            <Input value={createForm.name} onChange={e => setCreateForm(f => ({ ...f, name: e.target.value }))} placeholder="Document name" />
                        </div>
                        <div className="space-y-1.5">
                            <Label>Document type</Label>
                            <Select value={createForm.document_type_id} onValueChange={v => setCreateForm(f => ({ ...f, document_type_id: v }))}>
                                <SelectTrigger><SelectValue placeholder="Select type..." /></SelectTrigger>
                                <SelectContent>
                                    {documentTypes.map(t => (
                                        <SelectItem key={t.document_type_id} value={String(t.document_type_id)}>{t.name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="space-y-1.5">
                            <Label>Project</Label>
                            <Select value={createForm.project_id} onValueChange={v => setCreateForm(f => ({ ...f, project_id: v }))}>
                                <SelectTrigger><SelectValue placeholder="Select project..." /></SelectTrigger>
                                <SelectContent>
                                    {projects.map(p => (
                                        <SelectItem key={p.project_id} value={String(p.project_id)}>{p.project_name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="space-y-1.5">
                            <Label>Description <span className="text-slate-400 font-normal">(optional)</span></Label>
                            <Textarea value={createForm.user_prompt} onChange={e => setCreateForm(f => ({ ...f, user_prompt: e.target.value }))} placeholder="Short description or instructions..." rows={3} />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setShowCreate(false)}>Cancel</Button>
                        <Button className="bg-indigo-600 hover:bg-indigo-500" onClick={handleCreate}>Create document</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            <Dialog open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
                <DialogContent className="sm:max-w-sm">
                    <DialogHeader><DialogTitle>Delete document</DialogTitle></DialogHeader>
                    <p className="text-sm text-slate-600">Are you sure you want to delete <strong>{deleteTarget?.name}</strong>? This cannot be undone.</p>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setDeleteTarget(null)}>Cancel</Button>
                        <Button variant="destructive" onClick={handleDelete}>Delete</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
