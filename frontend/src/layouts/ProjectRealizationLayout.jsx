import { useState } from "react";
import { Outlet, NavLink, useNavigate, useLocation } from "react-router-dom";
import { Home, FolderKanban, BarChart2, Package } from "lucide-react";

const navItems = [
    { to: "/app/project-realization/home",      icon: Home,         label: "Home" },
    { to: "/app/project-realization/projects",  icon: FolderKanban, label: "Projects" },
    { to: "/app/project-realization/analytics", icon: BarChart2,    label: "Analytics" },
    { to: "/app/project-realization/resources", icon: Package,      label: "Resources" },
];

const pageTitles = {
    "/app/project-realization/projects":  "Projects",
    "/app/project-realization/home":      "Home",
    "/app/project-realization/analytics": "Analytics",
    "/app/project-realization/resources": "Resources",
};

export default function ProjectRealizationLayout() {
    const navigate = useNavigate();
    const location = useLocation();
    const [showMenu, setShowMenu] = useState(false);

    const token = localStorage.getItem("access_token");
    const user = JSON.parse(localStorage.getItem("user") || "null");

    if (!token || !user) {
        navigate("/login", { replace: true });
        return null;
    }

    function logout() {
        localStorage.clear();
        navigate("/login");
    }

    const initials = `${user.name?.charAt(0) ?? ""}${user.last_name?.charAt(0) ?? ""}`.toUpperCase();
    const pageTitle = pageTitles[location.pathname] ?? "Realizacija projekata";

    return (
        <div className="flex h-screen bg-gray-50 overflow-hidden">
            <aside className="w-52 flex flex-col bg-white border-r border-gray-200 shrink-0">
                <div className="px-5 py-5 border-b border-gray-100">
                    <span className="font-bold text-gray-900 text-sm leading-tight block">
                        Project<br />Realization
                    </span>
                </div>

                <nav className="flex-1 px-3 py-3 space-y-0.5">
                    {navItems.map(({ to, icon: Icon, label }) => (
                        <NavLink
                            key={to}
                            to={to}
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors ${
                                    isActive
                                        ? "bg-gray-100 text-gray-900 font-medium border-l-2 border-gray-900"
                                        : "text-gray-500 hover:bg-gray-50 hover:text-gray-800"
                                }`
                            }
                        >
                            <Icon size={15} />
                            {label}
                        </NavLink>
                    ))}
                </nav>

                <div className="px-4 py-4 border-t border-gray-100">
                    <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-700 text-xs font-semibold flex items-center justify-center shrink-0">
                            {initials}
                        </div>
                        <div className="min-w-0">
                            <p className="text-xs font-medium text-gray-900 truncate">{user.name} {user.last_name}</p>
                            <p className="text-xs text-gray-400 truncate">Project Manager</p>
                        </div>
                    </div>
                </div>
            </aside>

            <div className="flex-1 flex flex-col overflow-hidden">
                <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6 shrink-0">
                    <h1 className="text-base font-semibold text-gray-900">{pageTitle}</h1>
                    <div className="relative">
                        <button
                            onClick={() => setShowMenu(v => !v)}
                            className="w-8 h-8 rounded-full bg-gray-900 text-white text-xs font-semibold flex items-center justify-center hover:bg-gray-700 transition-colors"
                        >
                            {initials}
                        </button>
                        {showMenu && (
                            <div className="absolute right-0 mt-1 w-44 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-50">
                                <div className="px-3 py-2 text-xs text-gray-500 border-b border-gray-100">
                                    {user.name} {user.last_name}
                                </div>
                                <button
                                    onClick={logout}
                                    className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                                >
                                    Log out
                                </button>
                            </div>
                        )}
                    </div>
                </header>

                <main className="flex-1 overflow-auto">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
