import { NavLink, useNavigate } from "react-router-dom";
import { FileText, Sparkles, Layers, LayoutTemplate, Zap, Plus, Cog, GitBranch, Play, Filter, GitMerge, Star } from "lucide-react";

const navItems = [
    { to: "/app/documents", icon: FileText, label: "Documents" },
    { to: "/app/new-document", icon: Sparkles, label: "New Document" },
    { to: "/app/document-types", icon: Layers, label: "Document Types" },
    { to: "/app/section-templates", icon: LayoutTemplate, label: "Section Templates" },
    { to: "/app/document-ratings", icon: Star, label: "Ratings" },
    { to: "/app/system-prompts", icon: Zap, label: "System Prompts" },
    { to: "/app/workflow-actions", icon: Cog, label: "Workflow Actions" },
    { to: "/app/workflows", icon: GitBranch, label: "Workflows" },
    { to: "/app/workflow-instances", icon: Play, label: "Instances" },
    { to: "/app/condition-types", icon: Filter, label: "Condition Types" },
    { to: "/app/conditions", icon: GitMerge, label: "Conditions" },
];

export default function Sidebar() {
    const navigate = useNavigate();

    return (
        <aside className="w-56 flex flex-col bg-slate-900 shrink-0">
            <div className="px-4 py-5 border-b border-slate-700">
                <span className="text-white font-bold text-lg tracking-tight">DocAssist</span>
            </div>

            <div className="px-3 pt-3 pb-2">
                <button
                    onClick={() => navigate("/app/new-document")}
                    className="w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
                >
                    <Plus size={15} />
                    New Document
                </button>
            </div>

            <nav className="flex-1 px-3 pb-3 space-y-0.5">
                {navItems.map(({ to, icon: Icon, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        className={({ isActive }) =>
                            `flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors ${
                                isActive
                                    ? "bg-slate-700 text-white font-medium"
                                    : "text-slate-400 hover:bg-slate-800 hover:text-slate-100"
                            }`
                        }
                    >
                        <Icon size={15} />
                        {label}
                    </NavLink>
                ))}
            </nav>

        </aside>
    );
}
