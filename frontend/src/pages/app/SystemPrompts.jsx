import { useEffect, useState } from "react";
import { MessageSquare, Pencil, Star, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { authFetch } from "@/lib/api";

export default function SystemPrompts() {
    const [docTypes, setDocTypes] = useState([]);
    const [sectionTemplates, setSectionTemplates] = useState([]);
    const [feedback, setFeedback] = useState([]);
    const [editTarget, setEditTarget] = useState(null);
    const [editPrompt, setEditPrompt] = useState("");

    useEffect(() => { fetchAll(); }, []);

    async function fetchAll() {
        const types = await authFetch("/document-types").then(r => r.json());
        setDocTypes(types);
        const all = [];
        const feedbackGroups = [];
        for (const t of types) {
            const tpls = await authFetch(`/document-types/${t.document_type_id}/section-templates`).then(r => r.json());
            tpls.forEach(tpl => all.push({ ...tpl, document_type_name: t.name }));
            const ratings = await authFetch(`/document-types/${t.document_type_id}/ratings`).then(r => r.json());
            if (Array.isArray(ratings) && ratings.length > 0) {
                feedbackGroups.push({ document_type_name: t.name, ratings });
            }
        }
        setSectionTemplates(all);
        setFeedback(feedbackGroups);
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
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-slate-100">
                                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Document Type</th>
                                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">System Prompt</th>
                                <th className="px-5 py-3 w-12" />
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                            {docTypes.length === 0 && (
                                <tr>
                                    <td colSpan={3} className="px-5 py-16 text-center">
                                        <Zap size={32} className="mx-auto mb-3 text-slate-300" />
                                        <p className="text-slate-400 text-sm">No document types found.</p>
                                    </td>
                                </tr>
                            )}
                            {docTypes.map(t => (
                                <tr key={t.document_type_id} className="hover:bg-slate-50 transition-colors group">
                                    <td className="px-5 py-3.5">
                                        <span className="font-semibold text-slate-800">{t.name}</span>
                                    </td>
                                    <td className="px-5 py-3.5 max-w-lg">
                                        <span className="font-mono text-xs text-slate-400 truncate block max-w-lg">
                                            {t.system_prompt || <span className="not-italic text-slate-300">No prompt set</span>}
                                        </span>
                                    </td>
                                    <td className="px-5 py-3.5">
                                        <button
                                            className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-md transition-colors opacity-0 group-hover:opacity-100"
                                            onClick={() => openEdit(t, "doctype")}
                                        >
                                            <Pencil size={13} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </section>

            <section>
                <div className="flex items-center gap-2 mb-4">
                    <div className="w-6 h-6 rounded-md bg-teal-50 flex items-center justify-center">
                        <Zap size={13} className="text-teal-500" />
                    </div>
                    <h2 className="text-sm font-semibold text-slate-700">Section Template Prompts</h2>
                </div>
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-slate-100">
                                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Section</th>
                                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Document Type</th>
                                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">System Prompt</th>
                                <th className="px-5 py-3 w-12" />
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                            {sectionTemplates.length === 0 && (
                                <tr>
                                    <td colSpan={4} className="px-5 py-16 text-center">
                                        <Zap size={32} className="mx-auto mb-3 text-slate-300" />
                                        <p className="text-slate-400 text-sm">No section templates found.</p>
                                    </td>
                                </tr>
                            )}
                            {sectionTemplates.map(tpl => (
                                <tr key={tpl.section_template_id} className="hover:bg-slate-50 transition-colors group">
                                    <td className="px-5 py-3.5">
                                        <span className="font-semibold text-slate-800">{tpl.name}</span>
                                    </td>
                                    <td className="px-5 py-3.5">
                                        <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">{tpl.document_type_name}</span>
                                    </td>
                                    <td className="px-5 py-3.5 max-w-sm">
                                        <span className="font-mono text-xs text-slate-400 truncate block max-w-sm">
                                            {tpl.system_prompt || <span className="not-italic text-slate-300">No prompt set</span>}
                                        </span>
                                    </td>
                                    <td className="px-5 py-3.5">
                                        <button
                                            className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-md transition-colors opacity-0 group-hover:opacity-100"
                                            onClick={() => openEdit(tpl, "section")}
                                        >
                                            <Pencil size={13} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </section>

            <section>
                <div className="flex items-center gap-2 mb-4">
                    <div className="w-6 h-6 rounded-md bg-amber-50 flex items-center justify-center">
                        <MessageSquare size={13} className="text-amber-500" />
                    </div>
                    <h2 className="text-sm font-semibold text-slate-700">User Feedback</h2>
                    <span className="text-xs text-slate-400">Use these ratings and comments to refine the prompts above.</span>
                </div>
                {feedback.length === 0 ? (
                    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
                        <MessageSquare size={28} className="mx-auto mb-3 text-slate-300" />
                        <p className="text-slate-400 text-sm">No feedback collected yet.</p>
                    </div>
                ) : (
                    <div className="space-y-5">
                        {feedback.map((group) => (
                            <div key={group.document_type_name} className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                                <div className="px-5 py-3 border-b border-slate-100 bg-slate-50">
                                    <span className="text-sm font-semibold text-slate-700">{group.document_type_name}</span>
                                    <span className="ml-2 text-xs text-slate-400">{group.ratings.length} rating{group.ratings.length !== 1 ? "s" : ""}</span>
                                </div>
                                <div className="divide-y divide-slate-50">
                                    {group.ratings.map((r) => (
                                        <div key={r.document_rating_id} className="px-5 py-3.5">
                                            <div className="flex items-center gap-2 mb-1">
                                                <div className="flex items-center gap-0.5">
                                                    {[1, 2, 3, 4, 5].map((n) => (
                                                        <Star key={n} size={13} className={n <= r.score ? "fill-amber-400 text-amber-400" : "text-slate-200"} />
                                                    ))}
                                                </div>
                                                {r.document_name && <span className="text-xs text-slate-400">· {r.document_name}</span>}
                                                {r.user_name && <span className="text-xs text-slate-400">· {r.user_name}</span>}
                                            </div>
                                            {r.comment && <p className="text-sm text-slate-600 leading-relaxed">{r.comment}</p>}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
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
