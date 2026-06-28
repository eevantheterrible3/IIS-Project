import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import AppLayout from "./layouts/AppLayout";
import Dashboard from "./pages/app/Dashboard";
import DocumentsList from "./pages/app/DocumentsList";
import DocumentView from "./pages/app/DocumentView";
import DocumentTypesList from "./pages/app/DocumentTypesList";
import SectionTemplatesList from "./pages/app/SectionTemplatesList";
import SystemPrompts from "./pages/app/SystemPrompts";
import NewDocument from "./pages/app/NewDocument";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<Login />} />

                <Route path="/app" element={<AppLayout />}>
                    <Route index element={<Navigate to="/app/dashboard" replace />} />
                    <Route path="dashboard" element={<Dashboard />} />
                    <Route path="documents" element={<DocumentsList />} />
                    <Route path="documents/:id" element={<DocumentView />} />
                    <Route path="document-types" element={<DocumentTypesList />} />
                    <Route path="section-templates" element={<SectionTemplatesList />} />
                    <Route path="system-prompts" element={<SystemPrompts />} />
                    <Route path="new-document" element={<NewDocument />} />
                </Route>

                <Route path="/" element={<Navigate to="/app/dashboard" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
