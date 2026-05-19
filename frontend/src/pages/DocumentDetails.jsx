import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import "./DocumentDetails.css";


export default function DocumentDetails() {
    const { documentId } = useParams();
    const [document, setDocument] = useState(null);

    useEffect(() => {
        fetch(`http://localhost:8000/documents/${documentId}`)
            .then((response) => response.json())
            .then((data) => setDocument(data));
    }, [documentId]);

    if (!document) {
        return <div className="document-details-page">Loading...</div>;
    }

    return (
        <div className="document-details-page">
            <header className="document-header">
                <div className="document-logo">DOCUMENT MANAGEMENT</div>
            </header>

            <div className="document-layout">
                <aside className="document-left-panel">
                    <div className="details-sidebar-title">▼ Projects</div>

                    <div className="details-project-open">
                        <div className="details-project-name">▼ {document.project_name}</div>

                        <div className="details-documents-title">▼ Documents</div>

                        <div className="details-document-selected">
                            {document.name}
                        </div>

                        <div className="details-permissions">▶ Permissions</div>
                    </div>
                </aside>

                <main className="document-preview">
                    <h1>{document.name}</h1>
                    <div className="document-paper">
                        <iframe
                            src={`http://localhost:8000/documents/${documentId}/file`}
                            className="document-frame"
                            title={document.name}
                        />
                    </div>
                </main>

                <aside className="metadata-panel">
                    <h3>Document Details</h3>

                    {document.metadata.map((item) => (
                        <div key={item.name} className="metadata-item">
                            <strong>{item.name}</strong>
                            <span>{item.value}</span>
                        </div>
                    ))}
                </aside>
            </div>
        </div>
    );
}