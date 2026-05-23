import { useEffect } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import Sidebar from "@/components/Sidebar";

export default function AppLayout() {
    const navigate = useNavigate();
    const user = JSON.parse(localStorage.getItem("user") || "null");

    useEffect(() => {
        if (!user) navigate("/login", { replace: true });
    }, []);

    function logout() {
        localStorage.clear();
        navigate("/login");
    }

    if (!user) return null;

    return (
        <div className="flex h-screen bg-slate-50 overflow-hidden">
            <Sidebar />

            <div className="flex-1 flex flex-col overflow-hidden">
                <header className="h-12 bg-white border-b border-slate-200 flex items-center justify-end px-5 shrink-0">
                    <button
                        onClick={logout}
                        title={`${user.name} ${user.last_name} — Log out`}
                        className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 text-sm font-semibold hover:bg-indigo-200 transition-colors flex items-center justify-center"
                    >
                        {user.name?.charAt(0).toUpperCase()}
                    </button>
                </header>

                <main className="flex-1 overflow-auto">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
