import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ChevronLeft, Upload, Download, Clock, MessageSquare, FileText } from "lucide-react";
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
    const fileInputRef = useRef(null);

    const [document, setDocument] = useState(null);
    const [versions, setVersions] = useState([]);
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState("");
    const [uploading, setUploading] = useState(false);

    useEffect(() => {
        authFetch(`/documents/${id}`).then(r => r.json()).then(setDocument);
        fetchVersions();
        fetchComments();
    }, [id]);

    async function fetchVersions() {
        const data = await authFetch(`/documents/${id}/versions`).then(r => r.json());
        setVersions(Array.isArray(data) ? data : []);
    }

    async function fetchComments() {
        const data = await authFetch(`/comments/document/${id}`).then(r => r.json());
        setComments(Array.isArray(data) ? data : []);
    }

    async function handleAddComment() {
        if (!newComment.trim()) return;
        const res = await authFetch("/comments", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                document_id: id,
                content: newComment,
            }),
        });
        if (res.ok) {
            setNewComment("");
            fetchComments();
        }
    }

    async function handleUpload(e) {
        const file = e.target.files?.[0];
        if (!file) return;

        const ext = file.name.split(".").pop().toLowerCase();
        if (!["docx", "xlsx"].includes(ext)) {
            alert("Only .docx and .xlsx files are allowed.");
            return;
        }

        setUploading(true);
        const formData = new FormData();
        formData.append("file", file);

        const token = localStorage.getItem("access_token");
        const res = await fetch(`http://localhost:8000/documents/${id}/upload`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
            body: formData,
        });
        setUploading(false);
        fileInputRef.current.value = "";

        if (res.ok) {
            fetchVersions();
        } else {
            const err = await res.json().catch(() => ({}));
            alert(err.detail || "Upload failed");
        }
    }

    async function handleDownload(version) {
        const token = localStorage.getItem("access_token");
        const res = await fetch(
            `http://localhost:8000/documents/${id}/versions/${version.document_version_id}/download`,
            { headers: { Authorization: `Bearer ${token}` } }
        );
        if (!res.ok) return alert("Download failed");

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = window.document.createElement("a");
        a.href = url;
        a.download = version.file_name || `v${version.version_number}`;
        a.click();
        URL.revokeObjectURL(url);
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

            <Tabs defaultValue="upload">
                <TabsList className="bg-slate-100 p-1 rounded-lg mb-6">
                    <TabsTrigger value="upload" className="flex items-center gap-1.5 data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-md">
                        <Upload size={13} /> Upload
                    </TabsTrigger>
                    <TabsTrigger value="versions" className="flex items-center gap-1.5 data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-md">
                        <Clock size={13} /> Versions
                        {versions.length > 0 && (
                            <span className="ml-1 px-1.5 py-0.5 rounded-full text-xs bg-slate-200 text-slate-600">{versions.length}</span>
                        )}
                    </TabsTrigger>
                    <TabsTrigger value="comments" className="flex items-center gap-1.5 data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-md">
                        <MessageSquare size={13} /> Comments
                        {comments.length > 0 && (
                            <span className="ml-1 px-1.5 py-0.5 rounded-full text-xs bg-slate-200 text-slate-600">{comments.length}</span>
                        )}
                    </TabsTrigger>
                </TabsList>

                {/* Upload tab */}
                <TabsContent value="upload">
                    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-12 text-center">
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".docx,.xlsx"
                            className="hidden"
                            onChange={handleUpload}
                        />
                        <FileText size={40} className="mx-auto mb-4 text-slate-300" />
                        <p className="text-slate-700 font-medium mb-1">Upload a new version</p>
                        <p className="text-slate-400 text-sm mb-6">Supported formats: .docx, .xlsx</p>
                        <Button
                            className="bg-indigo-600 hover:bg-indigo-500 gap-1.5"
                            disabled={uploading}
                            onClick={() => fileInputRef.current?.click()}
                        >
                            <Upload size={13} />
                            {uploading ? "Uploading..." : "Choose File"}
                        </Button>
                    </div>
                </TabsContent>

                {/* Versions tab */}
                <TabsContent value="versions">
                    {versions.length === 0 ? (
                        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
                            <Clock size={32} className="mx-auto mb-3 text-slate-300" />
                            <p className="text-slate-500 font-medium">No versions yet</p>
                            <p className="text-slate-400 text-sm mt-1">Upload a file to create the first version.</p>
                        </div>
                    ) : (
                        <div className="bg-white rounded-xl border border-slate-200 shadow-sm divide-y divide-slate-100">
                            {versions.map(v => (
                                <div key={v.document_version_id} className="flex items-center justify-between px-5 py-4">
                                    <div className="flex items-center gap-4">
                                        <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center">
                                            <FileText size={18} className="text-indigo-500" />
                                        </div>
                                        <div>
                                            <div className="text-sm font-semibold text-slate-800">
                                                v{v.version_number}
                                                {v.file_name && <span className="ml-2 font-normal text-slate-500">{v.file_name}</span>}
                                            </div>
                                            <div className="text-xs text-slate-400 mt-0.5">
                                                {formatDate(v.created_at)}
                                                {v.author_name && <> · {v.author_name}</>}
                                                {v.step_name && <> · {v.step_name}</>}
                                            </div>
                                        </div>
                                    </div>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="gap-1.5"
                                        onClick={() => handleDownload(v)}
                                    >
                                        <Download size={13} /> Download
                                    </Button>
                                </div>
                            ))}
                        </div>
                    )}
                </TabsContent>

                {/* Comments tab */}
                <TabsContent value="comments">
                    <div className="space-y-4">
                        <div className="flex gap-2">
                            <Textarea
                                value={newComment}
                                onChange={e => setNewComment(e.target.value)}
                                placeholder="Add a comment..."
                                rows={2}
                                className="flex-1"
                            />
                            <Button onClick={handleAddComment} className="bg-indigo-600 hover:bg-indigo-500 text-white self-end">
                                Post
                            </Button>
                        </div>
                        {comments.length === 0 && (
                            <p className="text-sm text-slate-400 text-center py-8">No comments yet</p>
                        )}
                        {comments.map(c => (
                            <div key={c.comment_id} className="bg-white border border-slate-200 rounded-lg p-4">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="text-sm font-semibold text-slate-700">{c.user_name}</span>
                                    <span className="text-xs text-slate-400">{c.created_at ? new Date(c.created_at).toLocaleString() : ""}</span>
                                </div>
                                <p className="text-sm text-slate-600 mt-1">{c.content}</p>
                            </div>
                        ))}
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}
