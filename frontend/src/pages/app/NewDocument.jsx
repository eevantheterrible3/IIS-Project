import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Sparkles, Loader2, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { authFetch } from "@/lib/api";

export default function NewDocument() {
    const navigate = useNavigate();
    const [documentTypes, setDocumentTypes] = useState([]);
    const [projects, setProjects] = useState([]);
    const [selectedType, setSelectedType] = useState(null);
    const [form, setForm] = useState({ name: "", document_type_id: "", project_id: "", user_prompt: "" });
    const [loading, setLoading] = useState(false);
    const [step, setStep] = useState("idle");
    const [error, setError] = useState(null);

    useEffect(() => {
        authFetch("/document-types").then(r => r.json()).then(setDocumentTypes);
        setProjects(JSON.parse(localStorage.getItem("projects") || "[]"));
    }, []);

    function handleTypeSelect(typeId) {
        const type = documentTypes.find(t => t.document_type_id === typeId);
        setSelectedType(type || null);
        setForm(f => ({ ...f, document_type_id: typeId }));
    }

    async function handleGenerate() {
        if (!form.name || !form.document_type_id || !form.project_id || !form.user_prompt.trim()) return;
        setError(null);
        setLoading(true);
        setStep("creating");

        try {
            const createRes = await authFetch("/documents", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: form.name,
                    document_type_id: form.document_type_id,
                    project_id: form.project_id,
                    user_prompt: form.user_prompt,
                }),
            });
            if (!createRes.ok) {
                setError("Failed to create document.");
                return;
            }
            const doc = await createRes.json();

            setStep("generating");
            const genRes = await authFetch(`/documents/${doc.document_id}/generate-sections`, {
                method: "POST",
            });

            if (!genRes.ok) {
                const body = await genRes.json().catch(() => ({}));
                setError(body.detail || "AI generation failed. The document was created but sections are empty.");
                navigate(`/app/documents/${doc.document_id}`);
                return;
            }

            navigate(`/app/documents/${doc.document_id}`);
        } catch {
            setError("Something went wrong. Please try again.");
        } finally {
            setLoading(false);
            setStep("idle");
        }
    }

    const sortedTemplates = selectedType?.section_templates
        ? [...selectedType.section_templates].sort((a, b) => a.order_index - b.order_index)
        : [];

    const isValid = form.name && form.document_type_id && form.project_id && form.user_prompt.trim();

    const statusLabel = step === "creating"
        ? "Creating document..."
        : step === "generating"
        ? "Generating content with AI..."
        : isValid
        ? `Ready to generate ${sortedTemplates.length} section${sortedTemplates.length !== 1 ? "s" : ""}`
        : "Fill in all fields to continue";

    return (
        <div className="p-8 max-w-2xl mx-auto">
            <div className="flex items-center gap-3 mb-8">
                <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center shrink-0">
                    <Sparkles size={20} className="text-white" />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Generate Document</h1>
                    <p className="text-sm text-slate-500 mt-0.5">
                        AI will generate each section based on your instructions and the document type's prompts
                    </p>
                </div>
            </div>

            <div className="space-y-5">
                {/* Setup */}
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Document setup</p>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                            <Label>Name</Label>
                            <Input
                                value={form.name}
                                onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                                placeholder="e.g. Q4 Project Brief"
                                disabled={loading}
                            />
                        </div>
                        <div className="space-y-1.5">
                            <Label>Project</Label>
                            <Select value={form.project_id} onValueChange={v => setForm(f => ({ ...f, project_id: v }))} disabled={loading}>
                                <SelectTrigger><SelectValue placeholder="Select project..." /></SelectTrigger>
                                <SelectContent>
                                    {projects.map(p => (
                                        <SelectItem key={p.project_id} value={String(p.project_id)}>{p.project_name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <div className="space-y-1.5">
                        <Label>Document type</Label>
                        <Select value={form.document_type_id} onValueChange={handleTypeSelect} disabled={loading}>
                            <SelectTrigger><SelectValue placeholder="Select document type..." /></SelectTrigger>
                            <SelectContent>
                                {documentTypes.map(t => (
                                    <SelectItem key={t.document_type_id} value={String(t.document_type_id)}>{t.name}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        {selectedType?.description && (
                            <p className="text-xs text-slate-400 mt-1">{selectedType.description}</p>
                        )}
                    </div>
                </div>

                {/* Section preview */}
                {sortedTemplates.length > 0 && (
                    <div className="bg-slate-50 rounded-xl border border-slate-200 p-5">
                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                            Sections to be generated ({sortedTemplates.length})
                        </p>
                        <div className="space-y-2">
                            {sortedTemplates.map((tmpl, i) => (
                                <div key={tmpl.section_template_id} className="flex items-start gap-3">
                                    <ChevronRight size={13} className="text-slate-300 mt-0.5 shrink-0" />
                                    <div>
                                        <span className="text-sm font-medium text-slate-700">{tmpl.name}</span>
                                        {tmpl.content_structure && (
                                            <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">{tmpl.content_structure}</p>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Instructions */}
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-3">
                    <div>
                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Your instructions</p>
                        <p className="text-xs text-slate-500 mt-1">
                            Describe what this document should cover. The AI will combine your instructions with the section templates and document type prompts.
                        </p>
                    </div>
                    <Textarea
                        value={form.user_prompt}
                        onChange={e => setForm(f => ({ ...f, user_prompt: e.target.value }))}
                        placeholder="e.g. This is for the Q4 mobile app launch. Cover the feature scope, technical requirements, a timeline with milestones, and a risk assessment. The audience is the engineering and product teams..."
                        rows={6}
                        className="resize-none"
                        disabled={loading}
                    />
                </div>

                {error && (
                    <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3">{error}</p>
                )}

                {/* Footer */}
                <div className="flex items-center justify-between pt-1">
                    <p className="text-xs text-slate-400">{statusLabel}</p>
                    <Button
                        onClick={handleGenerate}
                        disabled={!isValid || loading}
                        className="bg-indigo-600 hover:bg-indigo-500 text-white gap-2 px-6"
                    >
                        {loading ? (
                            <>
                                <Loader2 size={15} className="animate-spin" />
                                {step === "creating" ? "Creating..." : "Generating..."}
                            </>
                        ) : (
                            <>
                                <Sparkles size={15} />
                                Generate Document
                            </>
                        )}
                    </Button>
                </div>
            </div>
        </div>
    );
}
