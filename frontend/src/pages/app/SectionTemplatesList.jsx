import { useEffect, useState } from "react";
import { Pencil, Trash2, LayoutTemplate, Plus } from "lucide-react";
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
            const tpls = await fetch(`http://localhost:8000/document-types/${t.document_type_id}/section-templates`).then(r => r.json());
            tpls.forEach(tpl => all.push({ ...tpl, document_type_name: t.name }));
        }
        setTemplates(all);
    }

    function openCreate() { setEditTarget(null); setForm(emptyForm); setShowModal(true); }
    function openEdit(tpl) {
        setEditTarget(tpl);
        setForm({ name: tpl.name, document_type_id: String(tpl.document_type_id || ""), content_structure: tpl.content_structure || "", system_prompt: tpl.system_prompt || "", order_index: String(tpl.order_index) });
        setShowModal(true);
    }

    async function handleSave() {
        if (!form.name.trim() || !form.document_type_id) return;
        const payload = { name: form.name, content_structure: form.content_structure || null, system_prompt: form.system_prompt || null, order_index: parseInt(form.order_index) || 0 };
        const url = editTarget ? `http://localhost:8000/section-templates/${editTarget.section_template_id}` : `http://localhost:8000/document-types/${form.document_type_id}/section-templates`;
        const res = await fetch(url, { method: editTarget ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
        if (!res.ok) { alert("Something went wrong."); return; }
        setShowModal(false);
        fetchAll();
    }

    async function handleDelete() {
        const res = await fetch(`http://localhost:8000/section-templates/${deleteTarget.section_template_id}`, { method: "DELETE" });
        if (!res.ok) { alert("Failed to delete."); return; }
        setTemplates(t => t.filter(x => x.section_template_id !== deleteTarget.section_template_id));
        setDeleteTarget(null);
    }

    return (
        <div className="p-8">
            <div className="flex items-start justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Section Templates</h1>
                    <p className="text-sm text-slate-500 mt-1">{templates.length} template{templates.length !== 1 ? "s" : ""} across all document types</p>
                </div>
                <Button onClick={openCreate} className="bg-indigo-600 hover:bg-indigo-500 text-white gap-1.5">
                    <Plus size={15} /> New template
                </Button>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-slate-100">
                            <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Name</th>
                            <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Document Type</th>
                            <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Content Structure</th>
                            <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider w-16 text-center">Order</th>
                            <th className="px-5 py-3 w-20" />
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                        {templates.length === 0 && (
                            <tr>
                                <td colSpan={5} className="px-5 py-16 text-center">
                                    <LayoutTemplate size={32} className="mx-auto mb-3 text-slate-300" />
                                    <p className="text-slate-500 font-medium">No section templates yet</p>
                                    <p className="text-slate-400 text-xs mt-1">Add templates to define your document structure.</p>
                                </td>
                            </tr>
                        )}
                        {templates.map(tpl => (
                            <tr key={tpl.section_template_id} className="hover:bg-slate-50 transition-colors group">
                                <td className="px-5 py-3.5">
                                    <div className="flex items-center gap-2.5">
                                        <div className="w-7 h-7 rounded-md bg-teal-50 flex items-center justify-center shrink-0">
                                            <LayoutTemplate size={13} className="text-teal-500" />
                                        </div>
                                        <span className="font-semibold text-slate-800">{tpl.name}</span>
                                    </div>
                                </td>
                                <td className="px-5 py-3.5">
                                    <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">{tpl.document_type_name || "—"}</span>
                                </td>
                                <td className="px-5 py-3.5 text-slate-400 max-w-xs truncate text-xs">{tpl.content_structure || <span className="text-slate-300">—</span>}</td>
                                <td className="px-5 py-3.5 text-slate-500 text-center font-mono text-xs">{tpl.order_index}</td>
                                <td className="px-5 py-3.5">
                                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-md transition-colors" onClick={() => openEdit(tpl)}><Pencil size={13} /></button>
                                        <button className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-md transition-colors" onClick={() => setDeleteTarget(tpl)}><Trash2 size={13} /></button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <Dialog open={showModal} onOpenChange={setShowModal}>
                <DialogContent className="sm:max-w-md">
                    <DialogHeader><DialogTitle>{editTarget ? "Edit section template" : "New section template"}</DialogTitle></DialogHeader>
                    <div className="space-y-4 py-2">
                        <div className="space-y-1.5">
                            <Label>Section name</Label>
                            <Input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="e.g. Introduction" />
                        </div>
                        {!editTarget && (
                            <div className="space-y-1.5">
                                <Label>Document type</Label>
                                <Select value={form.document_type_id} onValueChange={v => setForm(f => ({ ...f, document_type_id: v }))}>
                                    <SelectTrigger><SelectValue placeholder="Select type..." /></SelectTrigger>
                                    <SelectContent>
                                        {documentTypes.map(t => <SelectItem key={t.document_type_id} value={String(t.document_type_id)}>{t.name}</SelectItem>)}
                                    </SelectContent>
                                </Select>
                            </div>
                        )}
                        <div className="space-y-1.5">
                            <Label>Order</Label>
                            <Input type="number" value={form.order_index} onChange={e => setForm(f => ({ ...f, order_index: e.target.value }))} className="w-24" />
                        </div>
                        <div className="space-y-1.5">
                            <Label>Content structure</Label>
                            <Textarea value={form.content_structure} onChange={e => setForm(f => ({ ...f, content_structure: e.target.value }))} rows={3} placeholder="Describe the expected structure of this section..." />
                        </div>
                        <div className="space-y-1.5">
                            <Label>System prompt</Label>
                            <Textarea value={form.system_prompt} onChange={e => setForm(f => ({ ...f, system_prompt: e.target.value }))} rows={4} placeholder="Prompt used to generate this section..." className="font-mono text-xs" />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setShowModal(false)}>Cancel</Button>
                        <Button className="bg-indigo-600 hover:bg-indigo-500" onClick={handleSave}>Save</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            <Dialog open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
                <DialogContent className="sm:max-w-sm">
                    <DialogHeader><DialogTitle>Delete section template</DialogTitle></DialogHeader>
                    <p className="text-sm text-slate-600">Are you sure you want to delete <strong>{deleteTarget?.name}</strong>?</p>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setDeleteTarget(null)}>Cancel</Button>
                        <Button variant="destructive" onClick={handleDelete}>Delete</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
