import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { authFetch } from "@/lib/api";
import {
  Check,
  ChevronLeft,
  Clock,
  Eye,
  Loader2,
  RotateCcw,
  Save,
  Send,
  Sparkles,
  Star,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

function formatDate(dateStr) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("en", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function renderDoc(sections) {
  return sections
    .map((s, i) => `## ${s.section_name || `Section ${i + 1}`}\n${s.content || ""}`)
    .join("\n\n");
}

export default function DocumentView() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [document, setDocument] = useState(null);
  const [sections, setSections] = useState([]);
  const [versions, setVersions] = useState([]);
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [saving, setSaving] = useState(false);
  const [savedMsg, setSavedMsg] = useState(false);
  const [tab, setTab] = useState("preview");
  const [reopening, setReopening] = useState(false);
  const [reverting, setReverting] = useState(false);

  // Draft chat-refine state
  const [messages, setMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [refining, setRefining] = useState(false);
  const [chatError, setChatError] = useState(null);
  const [accepting, setAccepting] = useState(false);

  // Rating dialog state
  const [showRating, setShowRating] = useState(false);
  const [ratingScore, setRatingScore] = useState(0);
  const [ratingComment, setRatingComment] = useState("");
  const [submittingRating, setSubmittingRating] = useState(false);

  useEffect(() => {
    authFetch(`/documents/${id}`)
      .then((r) => r.json())
      .then(setDocument);
    authFetch(`/documents/${id}/sections`)
      .then((r) => r.json())
      .then((data) => setSections(Array.isArray(data) ? data : []));
    fetchVersions();
  }, [id]);

  // Seed the conversation transcript once, when a draft document + its sections are loaded.
  useEffect(() => {
    if (
      document?.status === "draft" &&
      sections.length > 0 &&
      messages.length === 0
    ) {
      setMessages([
        { role: "user", text: document.user_prompt || "Generate the document." },
        { role: "assistant", text: renderDoc(sections) },
      ]);
    }
  }, [document, sections]);

  async function fetchVersions() {
    const data = await authFetch(`/documents/${id}/versions`).then((r) =>
      r.json(),
    );
    setVersions(Array.isArray(data) ? data : []);
  }

  async function handleSave() {
    setSaving(true);
    const res = await authFetch(`/documents/${id}/save`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sections: sections.map((s) => ({
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

  async function handleSend() {
    const instruction = chatInput.trim();
    if (!instruction || refining) return;
    setChatError(null);
    setRefining(true);
    const history = [...messages, { role: "user", text: instruction }];
    setMessages(history);
    setChatInput("");

    const res = await authFetch(`/documents/${id}/refine-sections`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ history }),
    });

    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      setChatError(body.detail || "Refinement failed. Please try again.");
      setRefining(false);
      return;
    }

    const updated = await res.json();
    setSections(updated);
    setMessages((prev) => [
      ...prev,
      { role: "assistant", text: renderDoc(updated) },
    ]);
    setRefining(false);
  }

  async function handleAccept() {
    setAccepting(true);
    const res = await authFetch(`/documents/${id}/accept`, { method: "POST" });
    setAccepting(false);
    if (res.ok) {
      await fetchVersions();
      setMessages([]);
      setChatInput("");
      setChatError(null);
      setDocument((d) => (d ? { ...d, status: "active" } : d));
      setShowRating(true);
    }
  }

  async function submitRating() {
    if (!ratingScore) return;
    setSubmittingRating(true);
    await authFetch(`/documents/${id}/ratings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ score: ratingScore, comment: ratingComment || null }),
    });
    setSubmittingRating(false);
    setShowRating(false);
  }

  async function handleRevert(version) {
    setReverting(true);
    const res = await authFetch(
      `/documents/${id}/revert/${version.document_version_id}`,
      { method: "POST" },
    );
    setReverting(false);
    if (res.ok) {
      const updated = await res.json();
      setSections(updated);
      setTab("preview");
    }
  }

  async function handleReopen() {
    setReopening(true);
    const res = await authFetch(`/documents/${id}/reopen`, { method: "POST" });
    setReopening(false);
    if (res.ok) {
      setMessages([]);
      setDocument((d) => (d ? { ...d, status: "draft" } : d));
    }
  }

  function updateSectionContent(sectionId, content) {
    setSections((prev) =>
      prev.map((s) =>
        s.document_section_id === sectionId ? { ...s, content } : s,
      ),
    );
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

  const isDraft = document.status === "draft";

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
            <h1 className="text-2xl font-bold text-slate-900">
              {document.name}
            </h1>
          </div>
          <p className="text-sm text-slate-400">
            {document.project_name}
            {document.author && <> · by {document.author}</>}
          </p>
        </div>
        {isDraft ? (
          <Button
            className="bg-emerald-600 hover:bg-emerald-500 gap-1.5"
            disabled={accepting}
            onClick={handleAccept}
          >
            <Check size={14} />
            {accepting ? "Accepting..." : "Accept document"}
          </Button>
        ) : (
          <Button
            variant="outline"
            className="gap-1.5"
            disabled={reopening}
            onClick={handleReopen}
          >
            <Sparkles size={14} />
            {reopening ? "Opening..." : "Edit with AI"}
          </Button>
        )}
      </div>

      {isDraft ? (
        // Draft: iterative generation — section preview + chat refine panel
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-6">
          <div className="space-y-4">
            {sections.length === 0 ? (
              <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
                <p className="text-slate-500 font-medium">No sections</p>
              </div>
            ) : (
              sections.map((section, i) => (
                <div
                  key={section.document_section_id}
                  className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden"
                >
                  <div className="px-5 py-3 border-b border-slate-100 bg-slate-50">
                    <h3 className="text-sm font-semibold text-slate-700">
                      {section.section_name || `Section ${i + 1}`}
                    </h3>
                  </div>
                  <div className="p-5 text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
                    {section.content || (
                      <span className="text-slate-300 italic">Empty</span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Chat refine panel */}
          <div className="lg:sticky lg:top-8 h-fit bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col max-h-[calc(100vh-160px)]">
            <div className="px-4 py-3 border-b border-slate-100 flex items-center gap-2">
              <Sparkles size={15} className="text-indigo-600" />
              <span className="text-sm font-semibold text-slate-700">
                Refine with AI
              </span>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-[200px]">
              {messages.map((m, i) =>
                m.role === "user" ? (
                  <div key={i} className="flex justify-end">
                    <div className="bg-indigo-600 text-white text-sm rounded-lg rounded-br-sm px-3 py-2 max-w-[85%] whitespace-pre-wrap">
                      {m.text}
                    </div>
                  </div>
                ) : (
                  <div key={i} className="flex justify-start">
                    <div className="bg-slate-100 text-slate-500 text-xs rounded-lg rounded-bl-sm px-3 py-2 flex items-center gap-1.5">
                      <Check size={12} className="text-emerald-500" />
                      Document updated
                    </div>
                  </div>
                ),
              )}
              {refining && (
                <div className="flex justify-start">
                  <div className="bg-slate-100 text-slate-500 text-xs rounded-lg px-3 py-2 flex items-center gap-1.5">
                    <Loader2 size={12} className="animate-spin" />
                    Generating...
                  </div>
                </div>
              )}
            </div>
            {chatError && (
              <p className="px-4 text-xs text-red-600">{chatError}</p>
            )}
            <div className="p-3 border-t border-slate-100">
              <Textarea
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Ask the AI to adjust the document..."
                rows={2}
                className="resize-none text-sm mb-2"
                disabled={refining}
              />
              <Button
                className="w-full bg-indigo-600 hover:bg-indigo-500 gap-1.5"
                onClick={handleSend}
                disabled={refining || !chatInput.trim()}
              >
                <Send size={13} /> Send
              </Button>
            </div>
          </div>
        </div>
      ) : (
        // Finished: editable preview + version history
        <Tabs value={tab} onValueChange={setTab}>
          <TabsList className="bg-slate-100 p-1 rounded-lg mb-6">
            <TabsTrigger
              value="preview"
              className="flex items-center gap-1.5 data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-md"
            >
              <Eye size={13} /> Preview
            </TabsTrigger>
            <TabsTrigger
              value="versions"
              className="flex items-center gap-1.5 data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-md"
            >
              <Clock size={13} /> Version History
              {versions.length > 0 && (
                <span className="ml-1 px-1.5 py-0.5 rounded-full text-xs bg-slate-200 text-slate-600">
                  {versions.length}
                </span>
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
                <p className="text-slate-400 text-sm mt-1">
                  This document has no sections yet.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {sections.map((section, i) => (
                  <div
                    key={section.document_section_id}
                    className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden"
                  >
                    <div className="px-5 py-3 border-b border-slate-100 bg-slate-50">
                      <h3 className="text-sm font-semibold text-slate-700">
                        {section.section_name || `Section ${i + 1}`}
                      </h3>
                    </div>
                    <div className="p-4">
                      <Textarea
                        value={section.content || ""}
                        onChange={(e) =>
                          updateSectionContent(
                            section.document_section_id,
                            e.target.value,
                          )
                        }
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
                <p className="text-slate-400 text-sm mt-1">
                  Save the document to create a version.
                </p>
              </div>
            ) : (
              <div className="flex gap-4 h-[600px]">
                {/* Left: version list */}
                <div className="w-56 shrink-0 bg-white rounded-xl border border-slate-200 shadow-sm overflow-y-auto">
                  {versions.map((v) => (
                    <button
                      key={v.document_version_id}
                      onClick={() => setSelectedVersion(v)}
                      className={`w-full text-left px-4 py-3 border-b border-slate-100 last:border-0 transition-colors ${
                        selectedVersion?.document_version_id ===
                        v.document_version_id
                          ? "bg-indigo-50 border-l-2 border-l-indigo-500"
                          : "hover:bg-slate-50"
                      }`}
                    >
                      <div className="text-sm font-semibold text-slate-800">
                        v{v.version_number}
                      </div>
                      <div className="text-xs text-slate-400 mt-0.5">
                        {formatDate(v.created_at)}
                      </div>
                      {v.author_name && (
                        <div className="text-xs text-slate-400">
                          {v.author_name}
                        </div>
                      )}
                    </button>
                  ))}
                </div>

                {/* Right: version content */}
                <div className="flex-1 overflow-y-auto">
                  {!selectedVersion ? (
                    <div className="bg-white rounded-xl border border-slate-200 h-full flex items-center justify-center">
                      <p className="text-slate-400 text-sm">
                        Select a version to view
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-sm font-semibold text-slate-700">
                          Version {selectedVersion.version_number}
                        </span>
                        <span className="text-xs text-slate-400">
                          {formatDate(selectedVersion.created_at)}
                        </span>
                        {selectedVersion.author_name && (
                          <span className="text-xs text-slate-400">
                            · {selectedVersion.author_name}
                          </span>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          className="ml-auto gap-1.5"
                          disabled={reverting}
                          onClick={() => handleRevert(selectedVersion)}
                        >
                          <RotateCcw size={13} />
                          {reverting ? "Restoring..." : "Restore this version"}
                        </Button>
                      </div>
                      {getVersionSections(selectedVersion).map((section, i) => (
                        <div
                          key={i}
                          className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden"
                        >
                          <div className="px-5 py-3 border-b border-slate-100 bg-slate-50">
                            <h3 className="text-sm font-semibold text-slate-700">
                              {section.section_name || `Section ${i + 1}`}
                            </h3>
                          </div>
                          <div className="p-5 text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
                            {section.content || (
                              <span className="text-slate-300 italic">Empty</span>
                            )}
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
      )}

      {/* Rating dialog (after accept) */}
      <Dialog open={showRating} onOpenChange={setShowRating}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Rate this document</DialogTitle>
            <p className="text-sm text-slate-500 pt-0.5">
              How satisfied are you with the generated result?
            </p>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map((n) => (
                <button
                  key={n}
                  onClick={() => setRatingScore(n)}
                  className="p-1"
                  type="button"
                >
                  <Star
                    size={28}
                    className={
                      n <= ratingScore
                        ? "fill-amber-400 text-amber-400"
                        : "text-slate-300"
                    }
                  />
                </button>
              ))}
            </div>
            <Textarea
              value={ratingComment}
              onChange={(e) => setRatingComment(e.target.value)}
              placeholder="Comments, suggestions, or objections (optional)..."
              rows={4}
              className="resize-none text-sm"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRating(false)}>
              Skip
            </Button>
            <Button
              className="bg-indigo-600 hover:bg-indigo-500"
              onClick={submitRating}
              disabled={!ratingScore || submittingRating}
            >
              {submittingRating ? "Submitting..." : "Submit rating"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
