import { useEffect, useState } from "react";
import { Pencil, Trash2, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";

const emptyForm = { name: "", description: "", system_prompt: "" };

export default function DocumentTypesList() {
    const [types, setTypes] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [editTarget, setEditTarget] = useState(null);
    const [form, setForm] = useState(emptyForm);
    const [deleteTarget, setDeleteTarget] = useState(null);

    useEffect(() => { fetchTypes(); }, []);

    async function fetchTypes() {
        const res = await fetch("http://localhost:8000/document-types");
        setTypes(await res.json());
    }

    function openCreate() {
        setEditTarget(null);
        setForm(emptyForm);
        setShowModal(true);
    }

    function openEdit(type) {
        setEditTarget(type);
        setForm({ name: type.name, description: type.description || "", system_prompt: type.system_prompt || "" });
        setShowModal(true);
    }

    async function handleSave() {
        if (!form.name.trim()) return;
        const url = editTarget
            ? `http://localhost:8000/document-types/${editTarget.document_type_id}`
            : "http://localhost:8000/document-types";
        const method = editTarget ? "PUT" : "POST";
        const res = await fetch(url, {
            method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(form),
        });
        if (!res.ok) { alert("Greška."); return; }
        setShowModal(false);
        fetchTypes();
    }

    async function handleDelete() {
        const res = await fetch(`http://localhost:8000/document-types/${deleteTarget.document_type_id}`, { method: "DELETE" });
        if (!res.ok) { alert("Greška pri brisanju."); return; }
        setTypes(t => t.filter(x => x.document_type_id !== deleteTarget.document_type_id));
        setDeleteTarget(null);
    }

    return (
        <div className="p-6">
            <div className="flex items-center justify-between mb-5">
                <h1 className="text-xl font-semibold text-gray-900">Tipovi dokumentata</h1>
                <Button size="sm" onClick={openCreate}>+ Novi tip</Button>
            </div>

            <div className="border rounded-md overflow-hidden">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b bg-gray-50">
                            <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Naziv</th>
                            <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Opis</th>
                            <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Sistemski prompt</th>
                            <th className="px-4 py-2.5 w-20" />
                        </tr>
                    </thead>
                    <tbody>
                        {types.length === 0 && (
                            <tr>
                                <td colSpan={4} className="px-4 py-8 text-center text-gray-400 text-sm">
                                    Nema tipova dokumenata.
                                </td>
                            </tr>
                        )}
                        {types.map(type => (
                            <tr key={type.document_type_id} className="border-b last:border-0 hover:bg-gray-50">
                                <td className="px-4 py-3 font-medium text-gray-900">{type.name}</td>
                                <td className="px-4 py-3 text-gray-500 max-w-xs truncate">{type.description || "—"}</td>
                                <td className="px-4 py-3 text-gray-400 max-w-xs truncate font-mono text-xs">
                                    {type.system_prompt || "—"}
                                </td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-1">
                                        <button className="p-1 text-gray-400 hover:text-gray-700 rounded" onClick={() => openEdit(type)}>
                                            <Pencil size={14} />
                                        </button>
                                        <button className="p-1 text-gray-400 hover:text-red-500 rounded" onClick={() => setDeleteTarget(type)}>
                                            <Trash2 size={14} />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <Dialog open={showModal} onOpenChange={setShowModal}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>{editTarget ? "Uredi tip dokumenta" : "Novi tip dokumenta"}</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 py-2">
                        <div className="space-y-1.5">
                            <Label>Naziv</Label>
                            <Input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="Naziv tipa" />
                        </div>
                        <div className="space-y-1.5">
                            <Label>Opis</Label>
                            <Textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} rows={2} placeholder="Kratak opis..." />
                        </div>
                        <div className="space-y-1.5">
                            <Label>Sistemski prompt</Label>
                            <Textarea value={form.system_prompt} onChange={e => setForm(f => ({ ...f, system_prompt: e.target.value }))} rows={4} placeholder="Opšti sistemski prompt za ovaj tip dokumenta..." className="font-mono text-xs" />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setShowModal(false)}>Otkaži</Button>
                        <Button onClick={handleSave}>Sačuvaj</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            <Dialog open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
                <DialogContent>
                    <DialogHeader><DialogTitle>Obriši tip dokumenta</DialogTitle></DialogHeader>
                    <p className="text-sm text-gray-600">
                        Da li ste sigurni da želite da obrišete tip <strong>{deleteTarget?.name}</strong>?
                        Šabloni sekcija neće biti obrisani.
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
