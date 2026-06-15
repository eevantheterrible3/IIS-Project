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
import ProjectRealizationLayout from "./layouts/ProjectRealizationLayout";
import PRProjects from "./pages/project_realization/Projects";
import PRProjectDetail from "./pages/project_realization/ProjectDetail";
import PRNewTask from "./pages/project_realization/NewTask";
import PRResources from "./pages/project_realization/Resources";
import WorkflowActionsList from "./pages/app/WorkflowActionsList";
import WorkflowsList from "./pages/app/WorkflowsList";
import WorkflowInstancesList from "./pages/app/WorkflowInstancesList";
import ConditionTypesList from "./pages/app/ConditionTypesList";
import ConditionsList from "./pages/app/ConditionsList";
import DocumentRatingsList from "./pages/app/DocumentRatingsList";
import ProjectDocuments from "./pages/ProjectDocuments";
import UploadDocument from "./pages/UploadDocument";
function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/projects" element={<Projects />} />
                <Route path="/documents/:documentId" element={<DocumentDetails />} />
                <Route path="/projects/:projectId/documents/upload" element={<UploadDocument />} />
                <Route path="/projects/:projectId/documents" element={<ProjectDocuments />} />
                <Route path="/app" element={<AppLayout />}>
                    <Route index element={<Navigate to="/app/documents" replace />} />
                    <Route path="documents" element={<DocumentsList />} />
                    <Route path="documents/:id" element={<DocumentView />} />
                    <Route path="document-types" element={<DocumentTypesList />} />
                    <Route path="section-templates" element={<SectionTemplatesList />} />
                    <Route path="document-ratings" element={<DocumentRatingsList />} />
                    <Route path="system-prompts" element={<SystemPrompts />} />
                    <Route path="workflow-actions" element={<WorkflowActionsList />} />
                    <Route path="workflows" element={<WorkflowsList />} />
                    <Route path="workflow-instances" element={<WorkflowInstancesList />} />
                    <Route path="condition-types" element={<ConditionTypesList />} />
                    <Route path="conditions" element={<ConditionsList />} />
                    <Route path="new-document" element={<div className="p-6 text-gray-400">Document generation — coming soon.</div>} />
                </Route>

                <Route path="/app/project-realization" element={<ProjectRealizationLayout />}>
                    <Route index element={<Navigate to="/app/project-realization/projects" replace />} />
                    <Route path="projects" element={<PRProjects />} />
                    <Route path="projects/:project_id" element={<PRProjectDetail />} />
                    <Route path="projects/:project_id/new-task" element={<PRNewTask />} />
                    <Route path="resources" element={<PRResources />} />
                </Route>

                <Route path="/" element={<Navigate to="/app/documents" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
