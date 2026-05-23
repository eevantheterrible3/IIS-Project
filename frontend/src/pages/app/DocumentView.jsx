import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ChevronLeft, Save, Clock, Eye } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { authFetch } from "@/lib/api";

function formatDate(dateStr) {
    if (!dateStr) return "—";
    return new Date(dateStr).toLocaleDateString("en", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
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
    const [versions, setVersions] = useState([]);
    const [selectedVersion, setSelectedVersion] = useState(null);
    const [saving, setSaving] = useState(false);
    const [savedMsg, setSavedMsg] = useState(false);

    useEffect(() => {
        authFetch(`/documents/${id}`).then(r => r.json()).then(setDocument);
        authFetch(`/documents/${id}/sections`).then(r => r.json()).then(setSections);
        fetchVersions();
    }, [id]);

    async function fetchVersions() {
        const data = await authFetch(`/documents/${id}/versions`).then(r => r.json());
        setVersions(Array.isArray(data) ? data : []);
    }

    async function handleSave() {
        setSaving(true);
        const res = await authFetch(`/documents/${id}/save`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                sections: sections.map(s => ({
                    document_section_id: s.document_section_id,
                    content: s.content ?? null,
                })),
            }),
        });
        setSaving(false);
        if (res.ok) {
            setSavedMsg(true);
            setTimeout(() => setSavedMsg(false), 2000);
            fetchVersions();
        }
    }

    function updateSectionContent(sectionId, content) {
        setSections(prev => prev.map(s => s.document_section_id === sectionId ? { ...s, content } : s));
    }

    function getVersionSections(version) {
        try {
            return JSON.parse(version.full_content || "[]");
        } catch {
            return [];
        }
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
                        {versions.length > 0 && (
                            <span className="ml-1 px-1.5 py-0.5 rounded-full text-xs bg-slate-200 text-slate-600">{versions.length}</span>
                        )}
                    </TabsTrigger>
                </TabsList>

                {/* Preview tab */}
                <TabsContent value="preview">
                    <div className="flex justify-end mb-4">
                        <Button
                            className="bg-indigo-600 hover:bg-indigo-500 gap-1.5"
                            disabled={saving}
                            onClick={handleSave}
                        >
                            <Save size={13} />
                            {saving ? "Saving..." : savedMsg ? "Saved!" : "Save Document"}
                        </Button>
                    </div>

                    {sections.length === 0 ? (
                        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
                            <p className="text-slate-500 font-medium">No sections</p>
                            <p className="text-slate-400 text-sm mt-1">This document has no sections yet.</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {sections.map((section, i) => (
                                <div key={section.document_section_id} className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                                    <div className="px-5 py-3 border-b border-slate-100 bg-slate-50">
                                        <h3 className="text-sm font-semibold text-slate-700">
                                            {section.section_name || `Section ${i + 1}`}
                                        </h3>
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

                {/* Version History tab */}
                <TabsContent value="versions">
                    {versions.length === 0 ? (
                        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
                            <Clock size={32} className="mx-auto mb-3 text-slate-300" />
                            <p className="text-slate-500 font-medium">No versions saved</p>
                            <p className="text-slate-400 text-sm mt-1">Save the document to create a version.</p>
                        </div>
                    ) : (
                        <div className="flex gap-4 h-[600px]">
                            {/* Left: version list */}
                            <div className="w-56 shrink-0 bg-white rounded-xl border border-slate-200 shadow-sm overflow-y-auto">
                                {versions.map(v => (
                                    <button
                                        key={v.document_version_id}
                                        onClick={() => setSelectedVersion(v)}
                                        className={`w-full text-left px-4 py-3 border-b border-slate-100 last:border-0 transition-colors ${
                                            selectedVersion?.document_version_id === v.document_version_id
                                                ? "bg-indigo-50 border-l-2 border-l-indigo-500"
                                                : "hover:bg-slate-50"
                                        }`}
                                    >
                                        <div className="text-sm font-semibold text-slate-800">v{v.version_number}</div>
                                        <div className="text-xs text-slate-400 mt-0.5">{formatDate(v.created_at)}</div>
                                        {v.author_name && <div className="text-xs text-slate-400">{v.author_name}</div>}
                                    </button>
                                ))}
                            </div>

                            {/* Right: version content */}
                            <div className="flex-1 overflow-y-auto">
                                {!selectedVersion ? (
                                    <div className="bg-white rounded-xl border border-slate-200 h-full flex items-center justify-center">
                                        <p className="text-slate-400 text-sm">Select a version to view</p>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        <div className="flex items-center gap-2 mb-2">
                                            <span className="text-sm font-semibold text-slate-700">Version {selectedVersion.version_number}</span>
                                            <span className="text-xs text-slate-400">{formatDate(selectedVersion.created_at)}</span>
                                            {selectedVersion.author_name && <span className="text-xs text-slate-400">· {selectedVersion.author_name}</span>}
                                        </div>
                                        {getVersionSections(selectedVersion).map((section, i) => (
                                            <div key={i} className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                                                <div className="px-5 py-3 border-b border-slate-100 bg-slate-50">
                                                    <h3 className="text-sm font-semibold text-slate-700">
                                                        {section.section_name || `Section ${i + 1}`}
                                                    </h3>
                                                </div>
                                                <div className="p-5 text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
                                                    {section.content || <span className="text-slate-300 italic">Empty</span>}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </TabsContent>
            </Tabs>
        </div>
    );
}
