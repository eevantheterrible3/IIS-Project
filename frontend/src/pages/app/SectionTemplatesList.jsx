import { useEffect, useState } from "react";
import { Pencil, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";

const emptyForm = { name: "", document_type_id: "", content_structure: "", system_prompt: "", order_index: "0" };

export default function SectionTemplatesList() {
    const [templates, setTemplates] = useState([]);
    const [documentTypes, setDocumentTypes] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [editTarget, setEditTarget] = useState(null);
    const [form, setForm] = useState(emptyForm);
    const [deleteTarget, setDeleteTarget] = useState(null);

    useEffect(() => {
        fetchAll();
        fetch("http://localhost:8000/document-types").then(r => r.json()).then(setDocumentTypes);
    }, []);

    async function fetchAll() {
        const types = await fetch("http://localhost:8000/document-types").then(r => r.json());
        const all = [];
        for (const t of types) {
            const res = await fetch(`http://localhost:8000/document-types/${t.document_type_id}/section-templates`);
            const tpls = await res.json();
            tpls.forEach(tpl => all.push({ ...tpl, document_type_name: t.name }));
        }
        setTemplates(all);
    }

    function openCreate() {
        setEditTarget(null);
        setForm(emptyForm);
        setShowModal(true);
    }

    function openEdit(tpl) {
        setEditTarget(tpl);
        setForm({
            name: tpl.name,
            document_type_id: String(tpl.document_type_id || ""),
            content_structure: tpl.content_structure || "",
            system_prompt: tpl.system_prompt || "",
            order_index: String(tpl.order_index),
        });
        setShowModal(true);
    }

    async function handleSave() {
        if (!form.name.trim() || !form.document_type_id) return;
        const payload = {
            name: form.name,
            content_structure: form.content_structure || null,
            system_prompt: form.system_prompt || null,
            order_index: parseInt(form.order_index) || 0,
        };
        let res;
        if (editTarget) {
            res = await fetch(`http://localhost:8000/section-templates/${editTarget.section_template_id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
        } else {
            res = await fetch(`http://localhost:8000/document-types/${form.document_type_id}/section-templates`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
        }
        if (!res.ok) { alert("Greška."); return; }
        setShowModal(false);
        fetchAll();
    }

    async function handleDelete() {
        const res = await fetch(`http://localhost:8000/section-templates/${deleteTarget.section_template_id}`, { method: "DELETE" });
        if (!res.ok) { alert("Greška pri brisanju."); return; }
        setTemplates(t => t.filter(x => x.section_template_id !== deleteTarget.section_template_id));
        setDeleteTarget(null);
    }

    return (
        <div className="p-6">
            <div className="flex items-center justify-between mb-5">
                <h1 className="text-xl font-semibold text-gray-900">Šabloni sekcija</h1>
                <Button size="sm" onClick={openCreate}>+ Novi šablon</Button>
            </div>

            <div className="border rounded-md overflow-hidden">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b bg-gray-50">
                            <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Naziv</th>
                            <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Tip dokumenta</th>
                            <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Struktura</th>
                            <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide w-16">Redosled</th>
                            <th className="px-4 py-2.5 w-20" />
                        </tr>
                    </thead>
                    <tbody>
                        {templates.length === 0 && (
                            <tr>
                                <td colSpan={5} className="px-4 py-8 text-center text-gray-400 text-sm">
                                    Nema šablona sekcija.
                                </td>
                            </tr>
                        )}
                        {templates.map(tpl => (
                            <tr key={tpl.section_template_id} className="border-b last:border-0 hover:bg-gray-50">
                                <td className="px-4 py-3 font-medium text-gray-900">{tpl.name}</td>
                                <td className="px-4 py-3 text-gray-500">{tpl.document_type_name || "—"}</td>
                                <td className="px-4 py-3 text-gray-400 max-w-xs truncate text-xs">{tpl.content_structure || "—"}</td>
                                <td className="px-4 py-3 text-gray-500 text-center">{tpl.order_index}</td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-1">
                                        <button className="p-1 text-gray-400 hover:text-gray-700 rounded" onClick={() => openEdit(tpl)}>
                                            <Pencil size={14} />
                                        </button>
                                        <button className="p-1 text-gray-400 hover:text-red-500 rounded" onClick={() => setDeleteTarget(tpl)}>
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
                        <DialogTitle>{editTarget ? "Uredi šablon sekcije" : "Novi šablon sekcije"}</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 py-2">
                        <div className="space-y-1.5">
                            <Label>Naziv sekcije</Label>
                            <Input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="Naziv" />
                        </div>
                        {!editTarget && (
                            <div className="space-y-1.5">
                                <Label>Tip dokumenta</Label>
                                <Select value={form.document_type_id} onValueChange={v => setForm(f => ({ ...f, document_type_id: v }))}>
                                    <SelectTrigger><SelectValue placeholder="Izaberi tip..." /></SelectTrigger>
                                    <SelectContent>
                                        {documentTypes.map(t => (
                                            <SelectItem key={t.document_type_id} value={String(t.document_type_id)}>{t.name}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        )}
                        <div className="space-y-1.5">
                            <Label>Redosled</Label>
                            <Input type="number" value={form.order_index} onChange={e => setForm(f => ({ ...f, order_index: e.target.value }))} />
                        </div>
                        <div className="space-y-1.5">
                            <Label>Struktura sadržaja</Label>
                            <Textarea value={form.content_structure} onChange={e => setForm(f => ({ ...f, content_structure: e.target.value }))} rows={3} placeholder="Opis strukture sekcije..." />
                        </div>
                        <div className="space-y-1.5">
                            <Label>Sistemski prompt</Label>
                            <Textarea value={form.system_prompt} onChange={e => setForm(f => ({ ...f, system_prompt: e.target.value }))} rows={4} placeholder="Prompt za generisanje ove sekcije..." className="font-mono text-xs" />
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
                    <DialogHeader><DialogTitle>Obriši šablon sekcije</DialogTitle></DialogHeader>
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
