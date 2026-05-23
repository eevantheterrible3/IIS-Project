import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ChevronLeft, Save } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

function formatDate(dateStr) {
    if (!dateStr) return "—";
    return new Date(dateStr).toLocaleDateString("sr", { day: "2-digit", month: "2-digit", year: "numeric" });
}

export default function DocumentView() {
    const { id } = useParams();
    const navigate = useNavigate();

    const [document, setDocument] = useState(null);
    const [sections, setSections] = useState([]);
    const [versions, setVersions] = useState([]);
    const [saving, setSaving] = useState(null);

    useEffect(() => {
        fetch(`http://localhost:8000/documents/${id}`)
            .then(r => r.json()).then(setDocument);
        fetch(`http://localhost:8000/documents/${id}/sections`)
            .then(r => r.json()).then(setSections);
    }, [id]);

    async function saveSection(section) {
        setSaving(section.document_section_id);
        await fetch(`http://localhost:8000/document-sections/${section.document_section_id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content: section.content }),
        });
        setSaving(null);
    }

    function updateSectionContent(sectionId, content) {
        setSections(prev => prev.map(s =>
            s.document_section_id === sectionId ? { ...s, content } : s
        ));
    }

    if (!document) {
        return <div className="p-6 text-sm text-gray-400">Učitavanje...</div>;
    }

    return (
        <div className="p-6">
            <button
                onClick={() => navigate("/app/documents")}
                className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-800 mb-4"
            >
                <ChevronLeft size={15} /> Dokumenti
            </button>

            <div className="flex items-start justify-between mb-5">
                <div>
                    <h1 className="text-xl font-semibold text-gray-900">{document.name}</h1>
                    <div className="flex items-center gap-2 mt-1">
                        <span className="text-sm text-gray-500">{document.project_name}</span>
                        <Badge variant="outline" className="text-xs">{document.status}</Badge>
                    </div>
                </div>
            </div>

            <Tabs defaultValue="preview">
                <TabsList className="mb-4">
                    <TabsTrigger value="preview">Pregled</TabsTrigger>
                    <TabsTrigger value="versions">Istorija verzija</TabsTrigger>
                </TabsList>

                <TabsContent value="preview">
                    {sections.length === 0 ? (
                        <p className="text-sm text-gray-400">Ovaj dokument nema sekcija.</p>
                    ) : (
                        <div className="space-y-5">
                            {sections.map(section => (
                                <div key={section.document_section_id} className="border rounded-md p-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <h3 className="text-sm font-semibold text-gray-700">
                                            {section.section_name || `Sekcija ${section.order_index + 1}`}
                                        </h3>
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            className="h-7 text-xs"
                                            disabled={saving === section.document_section_id}
                                            onClick={() => saveSection(section)}
                                        >
                                            <Save size={12} className="mr-1" />
                                            {saving === section.document_section_id ? "Čuvanje..." : "Sačuvaj"}
                                        </Button>
                                    </div>
                                    <Textarea
                                        value={section.content || ""}
                                        onChange={e => updateSectionContent(section.document_section_id, e.target.value)}
                                        placeholder="Sadržaj sekcije..."
                                        rows={5}
                                        className="text-sm resize-none"
                                    />
                                </div>
                            ))}
                        </div>
                    )}
                </TabsContent>

                <TabsContent value="versions">
                    {versions.length === 0 ? (
                        <p className="text-sm text-gray-400">Nema sačuvanih verzija.</p>
                    ) : (
                        <div className="border rounded-md divide-y">
                            {versions.map(v => (
                                <div key={v.document_version_id} className="px-4 py-3 flex items-center justify-between">
                                    <div>
                                        <span className="text-sm font-medium text-gray-800">Verzija {v.version_number}</span>
                                        {v.note && <p className="text-xs text-gray-500 mt-0.5">{v.note}</p>}
                                    </div>
                                    <span className="text-xs text-gray-400">{formatDate(v.created_at)}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </TabsContent>
            </Tabs>
        </div>
    );
}
