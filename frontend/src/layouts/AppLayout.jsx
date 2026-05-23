import { Outlet, useNavigate } from "react-router-dom";
import Sidebar from "@/components/Sidebar";

export default function AppLayout() {
    const navigate = useNavigate();
    const user = JSON.parse(localStorage.getItem("user") || "{}");

    function logout() {
        localStorage.clear();
        navigate("/login");
    }

    return (
        <div className="flex h-screen bg-white overflow-hidden">
            <Sidebar />

            <div className="flex-1 flex flex-col overflow-hidden">
                <header className="h-11 border-b flex items-center justify-between px-4 shrink-0">
                    <span className="text-sm font-semibold text-gray-800">DocAssist</span>
                    <button
                        onClick={logout}
                        className="w-7 h-7 rounded-full bg-gray-200 text-gray-700 text-xs font-bold hover:bg-gray-300 flex items-center justify-center"
                        title={user.name}
                    >
                        {user.name?.charAt(0).toUpperCase()}
                    </button>
                </header>

                <main className="flex-1 overflow-auto bg-white">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
