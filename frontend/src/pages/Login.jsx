import { useState } from "react";
import "./Login.css";

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    async function handleLogin(e) {
        e.preventDefault();

        const response = await fetch("http://localhost:8000/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
            alert("Incorrect email or password");
            return;
        }

        const data = await response.json();

        localStorage.setItem("user", JSON.stringify(data.user));
        localStorage.setItem("projects", JSON.stringify(data.projects));

        const selectedProject = data.projects.find(
            (project) => project.role_name === "PROJECT_MANAGER"
        );

        if (selectedProject) {
            localStorage.setItem("selectedProject", JSON.stringify(selectedProject));
            window.location.href = "/manager";
            return;
        }

        const adminProject = data.projects.find(
            (project) => project.role_name === "ADMIN"
        );

        if (adminProject) {
            localStorage.setItem("selectedProject", JSON.stringify(adminProject));
            window.location.href = "/admin";
            return;
        }

        const teamMemberProject = data.projects.find(
            (project) => project.role_name === "TEAM_MEMBER"
        );

        if (teamMemberProject) {
            localStorage.setItem("selectedProject", JSON.stringify(teamMemberProject));
            window.location.href = "/team-member";
            return;
        }

        alert("User does not have a valid role.");
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
                        onChange={(e) => setEmail(e.target.value)}
                    />

                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />

                    <button type="submit">Log in</button>
                </form>
            </div>
        </div>
    );
}