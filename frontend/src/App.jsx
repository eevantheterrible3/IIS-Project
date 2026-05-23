import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Projects from "./pages/Projects";
import DocumentDetails from "./pages/DocumentDetails";
import AppLayout from "./layouts/AppLayout";
import DocumentsList from "./pages/app/DocumentsList";
import DocumentView from "./pages/app/DocumentView";
import DocumentTypesList from "./pages/app/DocumentTypesList";
import SectionTemplatesList from "./pages/app/SectionTemplatesList";
import SystemPrompts from "./pages/app/SystemPrompts";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/projects" element={<Projects />} />
                <Route path="/documents/:documentId" element={<DocumentDetails />} />

                <Route path="/app" element={<AppLayout />}>
                    <Route index element={<Navigate to="/app/documents" replace />} />
                    <Route path="documents" element={<DocumentsList />} />
                    <Route path="documents/:id" element={<DocumentView />} />
                    <Route path="document-types" element={<DocumentTypesList />} />
                    <Route path="section-templates" element={<SectionTemplatesList />} />
                    <Route path="system-prompts" element={<SystemPrompts />} />
                    <Route path="new-document" element={<div className="p-6 text-gray-400">Generisanje dokumenta — uskoro.</div>} />
                </Route>

                <Route path="/" element={<Navigate to="/app/documents" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
