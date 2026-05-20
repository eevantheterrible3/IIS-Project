import { useState } from "react";

export default function Header() {
    const [showMenu, setShowMenu] = useState(false);
    const user = JSON.parse(localStorage.getItem("user"));

    function logout() {
        localStorage.removeItem("user");
        localStorage.removeItem("projects");
        localStorage.removeItem("selectedProject");

        window.location.href = "/login";
    }

    return (
        <header className="projects-header">
            <div className="projects-logo">DOCUMENT MANAGEMENT</div>

            <div className="user-menu-container">
                <div
                    className="user-avatar"
                    onClick={() => setShowMenu(!showMenu)}
                >
                    {user?.name?.charAt(0).toUpperCase()}
                </div>

                {showMenu && (
                    <div className="user-dropdown">
                        <button className="logout-button" onClick={logout}>
                            Log out
                        </button>
                    </div>
                )}
            </div>
        </header>
    );
}