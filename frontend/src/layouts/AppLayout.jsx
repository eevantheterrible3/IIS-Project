import { useEffect, useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import Sidebar from "@/components/Sidebar";

export default function AppLayout() {
    const navigate = useNavigate();
    const [showMenu, setShowMenu] = useState(false);
    const token = localStorage.getItem("access_token");
    const user = JSON.parse(localStorage.getItem("user") || "null");

    useEffect(() => {
        if (!token || !user) navigate("/login", { replace: true });
    }, []);

    function logout() {
        localStorage.clear();
        navigate("/login");
    }

    if (!token || !user) return null;

    return (
        <div className="flex h-screen bg-slate-50 overflow-hidden">
            <Sidebar />

            <div className="flex-1 flex flex-col overflow-hidden">
                <header className="h-12 bg-white border-b border-slate-200 flex items-center justify-end px-5 shrink-0">
                    <div className="relative">
                        <button
                            onClick={() => setShowMenu(v => !v)}
                            className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 text-sm font-semibold hover:bg-indigo-200 transition-colors flex items-center justify-center"
                        >
                            {user.name?.charAt(0).toUpperCase()}
                        </button>
                        {showMenu && (
                            <div className="absolute right-0 mt-1 w-48 bg-white border border-slate-200 rounded-lg shadow-lg py-1 z-50">
                                <div className="px-3 py-2 text-sm text-slate-500 border-b border-slate-100">
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
