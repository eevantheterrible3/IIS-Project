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

        const firstProject = data.projects[0];

        if (firstProject.role_name.toLowerCase() === "admin") {
            window.location.href = "/admin";
        } else if (firstProject.role_name.toLowerCase() === "manager") {
            window.location.href = "/manager";
        } else {
            window.location.href = "/team-member";
        }
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