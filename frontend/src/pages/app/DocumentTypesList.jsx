import { useEffect, useState } from "react";
import { Pencil, Trash2, Layers, Plus } from "lucide-react";
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
        setTypes(await fetch("http://localhost:8000/document-types").then(r => r.json()));
    }

    function openCreate() { setEditTarget(null); setForm(emptyForm); setShowModal(true); }
    function openEdit(type) {
        setEditTarget(type);
        setForm({ name: type.name, description: type.description || "", system_prompt: type.system_prompt || "" });
        setShowModal(true);
    }

    async function handleSave() {
        if (!form.name.trim()) return;
        const url = editTarget ? `http://localhost:8000/document-types/${editTarget.document_type_id}` : "http://localhost:8000/document-types";
        const res = await fetch(url, { method: editTarget ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
        if (!res.ok) { alert("Something went wrong."); return; }
        setShowModal(false);
        fetchTypes();
    }

    async function handleDelete() {
        const res = await fetch(`http://localhost:8000/document-types/${deleteTarget.document_type_id}`, { method: "DELETE" });
        if (!res.ok) { alert("Failed to delete."); return; }
        setTypes(t => t.filter(x => x.document_type_id !== deleteTarget.document_type_id));
        setDeleteTarget(null);
    }

    return (
        <div className="p-8">
            <div className="flex items-start justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Document Types</h1>
                    <p className="text-sm text-slate-500 mt-1">{types.length} type{types.length !== 1 ? "s" : ""} defined</p>
                </div>
                <Button onClick={openCreate} className="bg-indigo-600 hover:bg-indigo-500 text-white gap-1.5">
                    <Plus size={15} /> New type
                </Button>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-slate-100">
                            <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Name</th>
                            <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Description</th>
                            <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">System Prompt</th>
                            <th className="px-5 py-3 w-20" />
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                        {types.length === 0 && (
                            <tr>
                                <td colSpan={4} className="px-5 py-16 text-center">
                                    <Layers size={32} className="mx-auto mb-3 text-slate-300" />
                                    <p className="text-slate-500 font-medium">No document types yet</p>
                                    <p className="text-slate-400 text-xs mt-1">Create a document type to get started.</p>
                                </td>
                            </tr>
                        )}
                        {types.map(type => (
                            <tr key={type.document_type_id} className="hover:bg-slate-50 transition-colors group">
                                <td className="px-5 py-3.5">
                                    <div className="flex items-center gap-2.5">
                                        <div className="w-7 h-7 rounded-md bg-violet-50 flex items-center justify-center shrink-0">
                                            <Layers size={13} className="text-violet-500" />
                                        </div>
                                        <span className="font-semibold text-slate-800">{type.name}</span>
                                    </div>
                                </td>
                                <td className="px-5 py-3.5 text-slate-500 max-w-xs truncate">{type.description || <span className="text-slate-300">—</span>}</td>
                                <td className="px-5 py-3.5 text-slate-400 max-w-xs truncate font-mono text-xs">{type.system_prompt || <span className="not-italic text-slate-300">—</span>}</td>
                                <td className="px-5 py-3.5">
                                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-md transition-colors" onClick={() => openEdit(type)}><Pencil size={13} /></button>
                                        <button className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-md transition-colors" onClick={() => setDeleteTarget(type)}><Trash2 size={13} /></button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <Dialog open={showModal} onOpenChange={setShowModal}>
                <DialogContent className="sm:max-w-md">
                    <DialogHeader><DialogTitle>{editTarget ? "Edit document type" : "New document type"}</DialogTitle></DialogHeader>
                    <div className="space-y-4 py-2">
                        <div className="space-y-1.5">
                            <Label>Name</Label>
                            <Input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="Type name" />
                        </div>
                        <div className="space-y-1.5">
                            <Label>Description</Label>
                            <Textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} rows={2} placeholder="Short description..." />
                        </div>
                        <div className="space-y-1.5">
                            <Label>System prompt</Label>
                            <Textarea value={form.system_prompt} onChange={e => setForm(f => ({ ...f, system_prompt: e.target.value }))} rows={4} placeholder="General system prompt for this document type..." className="font-mono text-xs" />
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
                    <DialogHeader><DialogTitle>Delete document type</DialogTitle></DialogHeader>
                    <p className="text-sm text-slate-600">Are you sure you want to delete <strong>{deleteTarget?.name}</strong>? Section templates will not be deleted.</p>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setDeleteTarget(null)}>Cancel</Button>
                        <Button variant="destructive" onClick={handleDelete}>Delete</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
