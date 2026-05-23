import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Pencil, Trash2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

function timeAgo(dateStr) {
    if (!dateStr) return "—";
    const diff = Math.floor((Date.now() - new Date(dateStr)) / 1000);
    if (diff < 60) return "upravo sad";
    if (diff < 3600) return `pre ${Math.floor(diff / 60)} min`;
    if (diff < 86400) return `pre ${Math.floor(diff / 3600)}h`;
    const days = Math.floor(diff / 86400);
    if (days < 7) return `pre ${days} ${days === 1 ? "dan" : "dana"}`;
    const weeks = Math.floor(days / 7);
    return `pre ${weeks} ${weeks === 1 ? "nedelju" : "nedelje"}`;
}

export default function DocumentsList() {
    const navigate = useNavigate();
    const user = JSON.parse(localStorage.getItem("user") || "{}");

    const [documents, setDocuments] = useState([]);
    const [documentTypes, setDocumentTypes] = useState([]);
    const [projects, setProjects] = useState([]);
    const [search, setSearch] = useState("");

    const [showCreate, setShowCreate] = useState(false);
    const [createForm, setCreateForm] = useState({ name: "", document_type_id: "", project_id: "", user_prompt: "" });

    const [deleteTarget, setDeleteTarget] = useState(null);

    useEffect(() => {
        fetchDocuments();
        fetch("http://localhost:8000/document-types")
            .then(r => r.json()).then(setDocumentTypes);
        const storedProjects = JSON.parse(localStorage.getItem("projects") || "[]");
        setProjects(storedProjects);
    }, []);

    async function fetchDocuments() {
        const res = await fetch(`http://localhost:8000/documents/my?user_id=${user.user_id}`);
        const data = await res.json();
        setDocuments(data);
    }

    async function handleCreate() {
        if (!createForm.name || !createForm.document_type_id || !createForm.project_id) return;
        const res = await fetch(`http://localhost:8000/documents?user_id=${user.user_id}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: createForm.name,
                document_type_id: parseInt(createForm.document_type_id),
                project_id: parseInt(createForm.project_id),
                user_prompt: createForm.user_prompt || null,
            }),
        });
        if (!res.ok) { alert("Greška pri kreiranju dokumenta."); return; }
        setShowCreate(false);
        setCreateForm({ name: "", document_type_id: "", project_id: "", user_prompt: "" });
        fetchDocuments();
    }

    async function handleDelete() {
        const res = await fetch(`http://localhost:8000/documents/delete/${deleteTarget.document_id}`, { method: "DELETE" });
        if (!res.ok) { alert("Greška pri brisanju."); return; }
        setDocuments(docs => docs.filter(d => d.document_id !== deleteTarget.document_id));
        setDeleteTarget(null);
    }

    const filtered = documents.filter(d =>
        d.name.toLowerCase().includes(search.toLowerCase()) ||
        (d.user_prompt || "").toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="p-6">
            <div className="flex items-center justify-between mb-5">
                <h1 className="text-xl font-semibold text-gray-900">Lista Dokumentata</h1>
                <div className="flex items-center gap-2">
                    <Input
                        placeholder="Pretraga..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        className="w-48 h-8 text-sm"
                    />
                    <Button variant="outline" size="sm" onClick={() => setShowCreate(true)}>
                        + Novi dokument
                    </Button>
                </div>
            </div>

            <div className="border rounded-md overflow-hidden">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b bg-gray-50">
                            <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Naziv</th>
                            <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Opis</th>
                            <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Tip dokumenta</th>
                            <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Izmenjen</th>
                            <th className="px-4 py-2.5 w-16" />
                        </tr>
                    </thead>
                    <tbody>
                        {filtered.length === 0 && (
                            <tr>
                                <td colSpan={5} className="px-4 py-8 text-center text-gray-400 text-sm">
                                    Nema dokumenata.
                                </td>
                            </tr>
                        )}
                        {filtered.map(doc => (
                            <tr
                                key={doc.document_id}
                                className="border-b last:border-0 hover:bg-gray-50 cursor-pointer"
                                onClick={() => navigate(`/app/documents/${doc.document_id}`)}
                            >
                                <td className="px-4 py-3 font-medium text-gray-900">{doc.name}</td>
                                <td className="px-4 py-3 text-gray-500 max-w-xs truncate">{doc.user_prompt || "—"}</td>
                                <td className="px-4 py-3 text-gray-600">{doc.document_type_name || "—"}</td>
                                <td className="px-4 py-3 text-gray-400">{timeAgo(doc.updated_at || doc.created_at)}</td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-1" onClick={e => e.stopPropagation()}>
                                        <button
                                            className="p-1 text-gray-400 hover:text-gray-700 rounded"
                                            onClick={() => navigate(`/app/documents/${doc.document_id}`)}
                                            title="Pregled"
                                        >
                                            <Pencil size={14} />
                                        </button>
                                        <button
                                            className="p-1 text-gray-400 hover:text-red-500 rounded"
                                            onClick={() => setDeleteTarget(doc)}
                                            title="Obriši"
                                        >
                                            <Trash2 size={14} />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Create modal */}
            <Dialog open={showCreate} onOpenChange={setShowCreate}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Novi dokument</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 py-2">
                        <div className="space-y-1.5">
                            <Label>Naziv</Label>
                            <Input
                                value={createForm.name}
                                onChange={e => setCreateForm(f => ({ ...f, name: e.target.value }))}
                                placeholder="Naziv dokumenta"
                            />
                        </div>
                        <div className="space-y-1.5">
                            <Label>Tip dokumenta</Label>
                            <Select
                                value={createForm.document_type_id}
                                onValueChange={v => setCreateForm(f => ({ ...f, document_type_id: v }))}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Izaberi tip..." />
                                </SelectTrigger>
                                <SelectContent>
                                    {documentTypes.map(t => (
                                        <SelectItem key={t.document_type_id} value={String(t.document_type_id)}>
                                            {t.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="space-y-1.5">
                            <Label>Projekat</Label>
                            <Select
                                value={createForm.project_id}
                                onValueChange={v => setCreateForm(f => ({ ...f, project_id: v }))}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Izaberi projekat..." />
                                </SelectTrigger>
                                <SelectContent>
                                    {projects.map(p => (
                                        <SelectItem key={p.project_id} value={String(p.project_id)}>
                                            {p.project_name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="space-y-1.5">
                            <Label>Opis (opcionalno)</Label>
                            <Textarea
                                value={createForm.user_prompt}
                                onChange={e => setCreateForm(f => ({ ...f, user_prompt: e.target.value }))}
                                placeholder="Kratki opis ili uputstvo..."
                                rows={3}
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setShowCreate(false)}>Otkaži</Button>
                        <Button onClick={handleCreate}>Kreiraj</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Delete confirm */}
            <Dialog open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Obriši dokument</DialogTitle>
                    </DialogHeader>
                    <p className="text-sm text-gray-600">
                        Da li ste sigurni da želite da obrišete <strong>{deleteTarget?.name}</strong>?
                    </p>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setDeleteTarget(null)}>Otkaži</Button>
                        <Button variant="destructive" onClick={handleDelete}>Obriši</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
