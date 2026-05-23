import { useState } from "react";
import "./Login.css";

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    async function handleLogin(e) {
        e.preventDefault();

        const response = await fetch("http://localhost:8000/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
            alert("Incorrect email or password");
            return;
        }

        const data = await response.json();

        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        localStorage.setItem("user", JSON.stringify(data.user));
        localStorage.setItem("projects", JSON.stringify(data.projects));

        const priority = ["PROJECT_MANAGER", "ADMIN", "TEAM_MEMBER"];
        const selected = priority.reduce(
            (found, role) => found || data.projects.find(p => p.role_name === role),
            null
        );

        if (!selected) {
            alert("User does not have a valid role.");
            return;
        }

        localStorage.setItem("selectedProject", JSON.stringify(selected));
        window.location.href = "/projects";
    }

    return (
        <div className="login-page">
            <div className="login-card">
                <h1 className="login-logo">Document Management</h1>

                <form onSubmit={handleLogin} className="login-form">
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                    />
                    <button type="submit">Log in</button>
                </form>
            </div>
        </div>
    );
}
