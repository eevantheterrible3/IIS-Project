import { NavLink, useNavigate } from "react-router-dom";
import {
    FileText, Layers, LayoutTemplate, Zap, Plus,
    Cog, GitBranch, Play, Filter, GitMerge, ClipboardList, Activity,
} from "lucide-react";

const allNavItems = [
    { to: "/app/documents", icon: FileText, label: "Documents", roles: ["ADMIN", "PROJECT_MANAGER", "TEAM_MEMBER"] },
    { to: "/app/project-documents", icon: ClipboardList, label: "Project Docs", roles: ["PROJECT_MANAGER"] },
    { to: "/app/document-types", icon: Layers, label: "Document Types", roles: ["ADMIN"] },
    { to: "/app/section-templates", icon: LayoutTemplate, label: "Section Templates", roles: ["ADMIN"] },
    { to: "/app/system-prompts", icon: Zap, label: "System Prompts", roles: ["ADMIN"] },
    { to: "/app/workflow-actions", icon: Cog, label: "Workflow Actions", roles: ["ADMIN"] },
    { to: "/app/workflows", icon: GitBranch, label: "Workflows", roles: ["ADMIN"] },
    { to: "/app/workflow-instances", icon: Play, label: "Instances", roles: ["ADMIN", "PROJECT_MANAGER", "TEAM_MEMBER"] },
    { to: "/app/condition-types", icon: Filter, label: "Condition Types", roles: ["ADMIN"] },
    { to: "/app/conditions", icon: GitMerge, label: "Conditions", roles: ["ADMIN"] },
    { to: "/app/activity-log", icon: Activity, label: "Activity Log", roles: ["ADMIN", "PROJECT_MANAGER"] },
];

export default function Sidebar() {
    const navigate = useNavigate();
    const selectedProject = JSON.parse(localStorage.getItem("selectedProject") || "{}");
    const role = selectedProject.role_name || "TEAM_MEMBER";
    const navItems = allNavItems.filter(item => item.roles.includes(role));

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
