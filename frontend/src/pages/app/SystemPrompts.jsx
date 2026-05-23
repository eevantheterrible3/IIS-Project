import { useEffect, useState } from "react";
import { Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";

export default function SystemPrompts() {
    const [docTypes, setDocTypes] = useState([]);
    const [sectionTemplates, setSectionTemplates] = useState([]);
    const [editTarget, setEditTarget] = useState(null);
    const [editPrompt, setEditPrompt] = useState("");

    useEffect(() => { fetchAll(); }, []);

    async function fetchAll() {
        const types = await fetch("http://localhost:8000/document-types").then(r => r.json());
        setDocTypes(types);

        const all = [];
        for (const t of types) {
            const res = await fetch(`http://localhost:8000/document-types/${t.document_type_id}/section-templates`);
            const tpls = await res.json();
            tpls.forEach(tpl => all.push({ ...tpl, document_type_name: t.name }));
        }
        setSectionTemplates(all);
    }

    function openEdit(item, type) {
        setEditTarget({ ...item, _type: type });
        setEditPrompt(item.system_prompt || "");
    }

    async function handleSave() {
        const { _type, ...item } = editTarget;
        let res;
        if (_type === "doctype") {
            res = await fetch(`http://localhost:8000/document-types/${item.document_type_id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: item.name, description: item.description, system_prompt: editPrompt }),
            });
        } else {
            res = await fetch(`http://localhost:8000/section-templates/${item.section_template_id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: item.name, content_structure: item.content_structure, system_prompt: editPrompt, order_index: item.order_index }),
            });
        }
        if (!res.ok) { alert("Greška."); return; }
        setEditTarget(null);
        fetchAll();
    }

    return (
        <div className="p-6 space-y-8">
            <h1 className="text-xl font-semibold text-gray-900">Sistemski promptovi</h1>

            <section>
                <h2 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">
                    Opšti promptovi — Tipovi dokumenata
                </h2>
                <div className="border rounded-md overflow-hidden">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b bg-gray-50">
                                <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Tip dokumenta</th>
                                <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Sistemski prompt</th>
                                <th className="px-4 py-2.5 w-12" />
                            </tr>
                        </thead>
                        <tbody>
                            {docTypes.length === 0 && (
                                <tr><td colSpan={3} className="px-4 py-6 text-center text-gray-400 text-sm">Nema tipova dokumenata.</td></tr>
                            )}
                            {docTypes.map(t => (
                                <tr key={t.document_type_id} className="border-b last:border-0 hover:bg-gray-50">
                                    <td className="px-4 py-3 font-medium text-gray-900">{t.name}</td>
                                    <td className="px-4 py-3 text-gray-400 font-mono text-xs max-w-lg truncate">
                                        {t.system_prompt || <span className="not-italic text-gray-300">—</span>}
                                    </td>
                                    <td className="px-4 py-3">
                                        <button className="p-1 text-gray-400 hover:text-gray-700 rounded" onClick={() => openEdit(t, "doctype")}>
                                            <Pencil size={14} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </section>

            <section>
                <h2 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">
                    Promptovi šablona sekcija
                </h2>
                <div className="border rounded-md overflow-hidden">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b bg-gray-50">
                                <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Sekcija</th>
                                <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Tip dokumenta</th>
                                <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Sistemski prompt</th>
                                <th className="px-4 py-2.5 w-12" />
                            </tr>
                        </thead>
                        <tbody>
                            {sectionTemplates.length === 0 && (
                                <tr><td colSpan={4} className="px-4 py-6 text-center text-gray-400 text-sm">Nema šablona sekcija.</td></tr>
                            )}
                            {sectionTemplates.map(tpl => (
                                <tr key={tpl.section_template_id} className="border-b last:border-0 hover:bg-gray-50">
                                    <td className="px-4 py-3 font-medium text-gray-900">{tpl.name}</td>
                                    <td className="px-4 py-3 text-gray-500">{tpl.document_type_name}</td>
                                    <td className="px-4 py-3 text-gray-400 font-mono text-xs max-w-sm truncate">
                                        {tpl.system_prompt || <span className="not-italic text-gray-300">—</span>}
                                    </td>
                                    <td className="px-4 py-3">
                                        <button className="p-1 text-gray-400 hover:text-gray-700 rounded" onClick={() => openEdit(tpl, "section")}>
                                            <Pencil size={14} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </section>

            <Dialog open={!!editTarget} onOpenChange={() => setEditTarget(null)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Uredi sistemski prompt — {editTarget?.name}</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-1.5 py-2">
                        <Label>Sistemski prompt</Label>
                        <Textarea
                            value={editPrompt}
                            onChange={e => setEditPrompt(e.target.value)}
                            rows={8}
                            className="font-mono text-xs"
                            placeholder="Unesi sistemski prompt..."
                        />
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setEditTarget(null)}>Otkaži</Button>
                        <Button onClick={handleSave}>Sačuvaj</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
