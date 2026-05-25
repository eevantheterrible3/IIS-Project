import { useState } from "react";
import "./ProjectFormModal.css";

export default function ProjectFormModal({ title, project, onClose, onSave }) {
    const [name, setName] = useState(project?.name || "");
    const [description, setDescription] = useState(project?.description || "");

    function handleSubmit() {
        if (!name.trim()) {
            alert("Project name is required.");
            return;
        }

        onSave({
            name,
            description,
            status: "ACTIVE",
        });
    }

    return (
        <div className="project-modal-overlay">
            <div className="project-modal">
                <h2>{title}</h2>

                <div className="project-form-group">
                    <label>Project name</label>
                    <input
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Enter project name"
                    />
                </div>

                <div className="project-form-group">
                    <label>Description</label>
                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Enter project description"
                    />
                </div>

                <div className="project-modal-actions">
                    <button className="project-cancel-button" onClick={onClose}>
                        Cancel
                    </button>

                    <button className="project-save-button" onClick={handleSubmit}>
                        Save
                    </button>
                </div>
            </div>
        </div>
    );
}