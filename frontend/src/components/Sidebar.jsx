import { NavLink, useNavigate } from "react-router-dom";
import { FileText, Sparkles, Layers, LayoutTemplate, Zap, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

const navItems = [
    { to: "/app/documents", icon: FileText, label: "Dokumenti" },
    { to: "/app/new-document", icon: Sparkles, label: "Novi dokument" },
    { to: "/app/document-types", icon: Layers, label: "Tipovi dokumentata" },
    { to: "/app/section-templates", icon: LayoutTemplate, label: "Šabloni sekcija" },
    { to: "/app/system-prompts", icon: Zap, label: "Sistemski promptovi" },
];

export default function Sidebar() {
    const navigate = useNavigate();
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    const orgName = "Mreža aktivista";

    return (
        <aside className="w-56 flex flex-col border-r bg-gray-50 shrink-0">
            <div className="p-3 border-b">
                <Button
                    className="w-full justify-start gap-2 bg-gray-900 hover:bg-gray-800 text-white"
                    onClick={() => navigate("/app/new-document")}
                >
                    <Plus size={16} />
                    Novi dokument
                </Button>
            </div>

            <nav className="flex-1 p-2 space-y-0.5">
                {navItems.map(({ to, icon: Icon, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        className={({ isActive }) =>
                            `flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors ${
                                isActive
                                    ? "bg-white shadow-sm text-gray-900 font-medium"
                                    : "text-gray-600 hover:bg-white hover:text-gray-900"
                            }`
                        }
                    >
                        <Icon size={15} />
                        {label}
                    </NavLink>
                ))}
            </nav>

            <div className="p-3 border-t">
                <p className="text-xs text-gray-400">
                    Organizacija: <span className="font-medium text-gray-600">{orgName}</span>
                </p>
            </div>
        </aside>
    );
}
