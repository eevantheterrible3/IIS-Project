import { useEffect, useState } from "react";
import { Pencil, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { authFetch } from "@/lib/api";

function PromptTable({ rows, columns, emptyIcon: Icon, emptyText, onEdit }) {
    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <table className="w-full text-sm">
                <thead>
                    <tr className="border-b border-slate-100">
                        {columns.map(col => (
                            <th key={col.key} className={`text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider ${col.className || ""}`}>{col.label}</th>
                        ))}
                        <th className="px-5 py-3 w-12" />
                    </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                    {rows.length === 0 && (
                        <tr>
                            <td colSpan={columns.length + 1} className="px-5 py-16 text-center">
                                <Icon size={32} className="mx-auto mb-3 text-slate-300" />
                                <p className="text-slate-400 text-sm">{emptyText}</p>
                            </td>
                        </tr>
                    )}
                    {rows.map(row => (
                        <tr key={row.id} className="hover:bg-slate-50 transition-colors group">
                            {columns.map(col => (
                                <td key={col.key} className={`px-5 py-3.5 ${col.cellClass || ""}`}>
                                    {col.render ? col.render(row) : row[col.key]}
                                </td>
                            ))}
                            <td className="px-5 py-3.5">
                                <button
                                    className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-md transition-colors opacity-0 group-hover:opacity-100"
                                    onClick={() => onEdit(row)}
                                >
                                    <Pencil size={13} />
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default function SystemPrompts() {
    const [docTypes, setDocTypes] = useState([]);
    const [sectionTemplates, setSectionTemplates] = useState([]);
    const [editTarget, setEditTarget] = useState(null);
    const [editPrompt, setEditPrompt] = useState("");

    useEffect(() => { fetchAll(); }, []);

    async function fetchAll() {
        const types = await authFetch("/document-types").then(r => r.json());
        setDocTypes(types);
        const all = [];
        for (const t of types) {
            const tpls = await authFetch(`/document-types/${t.document_type_id}/section-templates`).then(r => r.json());
            tpls.forEach(tpl => all.push({ ...tpl, document_type_name: t.name }));
        }
        setSectionTemplates(all);
    }

    function openEdit(item, type) { setEditTarget({ ...item, _type: type }); setEditPrompt(item.system_prompt || ""); }

    async function handleSave() {
        const { _type, ...item } = editTarget;
        const url = _type === "doctype"
            ? `/document-types/${item.document_type_id}`
            : `/section-templates/${item.section_template_id}`;
        const body = _type === "doctype"
            ? { name: item.name, description: item.description, system_prompt: editPrompt }
            : { name: item.name, content_structure: item.content_structure, system_prompt: editPrompt, order_index: item.order_index };
        const res = await authFetch(url, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
        if (!res.ok) { alert("Something went wrong."); return; }
        setEditTarget(null);
        fetchAll();
    }

    const docTypeColumns = [
        { key: "name", label: "Document Type", render: row => <span className="font-semibold text-slate-800">{row.name}</span> },
        { key: "system_prompt", label: "System Prompt", cellClass: "max-w-lg", render: row => <span className="font-mono text-xs text-slate-400 truncate block max-w-lg">{row.system_prompt || <span className="not-italic text-slate-300">No prompt set</span>}</span> },
    ];

    const sectionColumns = [
        { key: "name", label: "Section", render: row => <span className="font-semibold text-slate-800">{row.name}</span> },
        { key: "document_type_name", label: "Document Type", render: row => <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">{row.document_type_name}</span> },
        { key: "system_prompt", label: "System Prompt", cellClass: "max-w-sm", render: row => <span className="font-mono text-xs text-slate-400 truncate block max-w-sm">{row.system_prompt || <span className="not-italic text-slate-300">No prompt set</span>}</span> },
    ];

    return (
        <div className="p-8 space-y-10">
            <div>
                <h1 className="text-2xl font-bold text-slate-900">System Prompts</h1>
                <p className="text-sm text-slate-500 mt-1">Manage prompts that guide AI document generation.</p>
            </div>

            <section>
                <div className="flex items-center gap-2 mb-4">
                    <div className="w-6 h-6 rounded-md bg-violet-50 flex items-center justify-center">
                        <Zap size={13} className="text-violet-500" />
                    </div>
                    <h2 className="text-sm font-semibold text-slate-700">General Prompts — Document Types</h2>
                </div>
                <PromptTable
                    rows={docTypes.map(t => ({ ...t, id: t.document_type_id }))}
                    columns={docTypeColumns}
                    emptyIcon={Zap}
                    emptyText="No document types found."
                    onEdit={item => openEdit(item, "doctype")}
                />
            </section>

            <section>
                <div className="flex items-center gap-2 mb-4">
                    <div className="w-6 h-6 rounded-md bg-teal-50 flex items-center justify-center">
                        <Zap size={13} className="text-teal-500" />
                    </div>
                    <h2 className="text-sm font-semibold text-slate-700">Section Template Prompts</h2>
                </div>
                <PromptTable
                    rows={sectionTemplates.map(t => ({ ...t, id: t.section_template_id }))}
                    columns={sectionColumns}
                    emptyIcon={Zap}
                    emptyText="No section templates found."
                    onEdit={item => openEdit(item, "section")}
                />
            </section>

            <Dialog open={!!editTarget} onOpenChange={() => setEditTarget(null)}>
                <DialogContent className="sm:max-w-lg">
                    <DialogHeader>
                        <DialogTitle>Edit system prompt</DialogTitle>
                        <p className="text-sm text-slate-500 pt-0.5">{editTarget?.name}</p>
                    </DialogHeader>
                    <div className="space-y-1.5 py-2">
                        <Label>System prompt</Label>
                        <Textarea value={editPrompt} onChange={e => setEditPrompt(e.target.value)} rows={10} className="font-mono text-xs" placeholder="Enter system prompt..." />
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setEditTarget(null)}>Cancel</Button>
                        <Button className="bg-indigo-600 hover:bg-indigo-500" onClick={handleSave}>Save</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
