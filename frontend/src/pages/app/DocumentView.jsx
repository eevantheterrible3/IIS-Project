import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ChevronLeft, Save, Clock, Eye } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { authFetch } from "@/lib/api";

function formatDate(dateStr) {
    if (!dateStr) return "—";
    return new Date(dateStr).toLocaleDateString("en", { day: "numeric", month: "short", year: "numeric" });
}

const statusColors = {
    draft: "bg-amber-100 text-amber-700",
    active: "bg-emerald-100 text-emerald-700",
    finished: "bg-slate-100 text-slate-600",
};

export default function DocumentView() {
    const { id } = useParams();
    const navigate = useNavigate();

    const [document, setDocument] = useState(null);
    const [sections, setSections] = useState([]);
    const [versions] = useState([]);
    const [saving, setSaving] = useState(null);

    useEffect(() => {
        authFetch(`http://localhost:8000/documents/${id}`).then(r => r.json()).then(setDocument);
        authFetch(`http://localhost:8000/documents/${id}/sections`).then(r => r.json()).then(setSections);
    }, [id]);

    async function saveSection(section) {
        setSaving(section.document_section_id);
        await authFetch(`http://localhost:8000/document-sections/${section.document_section_id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content: section.content }),
        });
        setSaving(null);
    }

    function updateSectionContent(sectionId, content) {
        setSections(prev => prev.map(s => s.document_section_id === sectionId ? { ...s, content } : s));
    }

    if (!document) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-slate-400 text-sm">Loading...</div>
            </div>
        );
    }

    return (
        <div className="p-8">
            <button
                onClick={() => navigate("/app/documents")}
                className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-700 mb-6 transition-colors"
            >
                <ChevronLeft size={15} /> Back to Documents
            </button>

            <div className="flex items-start justify-between mb-6">
                <div>
                    <div className="flex items-center gap-3 mb-1">
                        <h1 className="text-2xl font-bold text-slate-900">{document.name}</h1>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${statusColors[document.status] || statusColors.draft}`}>
                            {document.status}
                        </span>
                    </div>
                    <p className="text-sm text-slate-400">
                        {document.project_name}
                        {document.author && <> · by {document.author}</>}
                    </p>
                </div>
            </div>

            <Tabs defaultValue="preview">
                <TabsList className="bg-slate-100 p-1 rounded-lg mb-6">
                    <TabsTrigger value="preview" className="flex items-center gap-1.5 data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-md">
                        <Eye size={13} /> Preview
                    </TabsTrigger>
                    <TabsTrigger value="versions" className="flex items-center gap-1.5 data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-md">
                        <Clock size={13} /> Version History
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="preview">
                    {sections.length === 0 ? (
                        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
                            <p className="text-slate-500 font-medium">No sections</p>
                            <p className="text-slate-400 text-sm mt-1">This document has no sections yet.</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {sections.map((section, i) => (
                                <div key={section.document_section_id} className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                                    <div className="flex items-center justify-between px-5 py-3 border-b border-slate-100 bg-slate-50">
                                        <h3 className="text-sm font-semibold text-slate-700">
                                            {section.section_name || `Section ${i + 1}`}
                                        </h3>
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            className="h-7 text-xs gap-1"
                                            disabled={saving === section.document_section_id}
                                            onClick={() => saveSection(section)}
                                        >
                                            <Save size={11} />
                                            {saving === section.document_section_id ? "Saving..." : "Save"}
                                        </Button>
                                    </div>
                                    <div className="p-4">
                                        <Textarea
                                            value={section.content || ""}
                                            onChange={e => updateSectionContent(section.document_section_id, e.target.value)}
                                            placeholder="Write section content..."
                                            rows={6}
                                            className="text-sm resize-none border-0 p-0 shadow-none focus-visible:ring-0 bg-transparent"
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </TabsContent>

                <TabsContent value="versions">
                    {versions.length === 0 ? (
                        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
                            <Clock size={32} className="mx-auto mb-3 text-slate-300" />
                            <p className="text-slate-500 font-medium">No versions saved</p>
                            <p className="text-slate-400 text-sm mt-1">Version history will appear here.</p>
                        </div>
                    ) : (
                        <div className="bg-white rounded-xl border border-slate-200 shadow-sm divide-y divide-slate-100">
                            {versions.map(v => (
                                <div key={v.document_version_id} className="px-5 py-4 flex items-center justify-between hover:bg-slate-50">
                                    <div>
                                        <span className="text-sm font-semibold text-slate-800">Version {v.version_number}</span>
                                        {v.note && <p className="text-xs text-slate-500 mt-0.5">{v.note}</p>}
                                    </div>
                                    <span className="text-xs text-slate-400">{formatDate(v.created_at)}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </TabsContent>
            </Tabs>
        </div>
    );
}
