import { useState } from "react";
import "./EditDocumentModal.css";


export default function EditDocumentModal({ document, onClose, onSave }) {
    const [editTags, setEditTags] = useState(document.tags || []);
    const [editMetadata, setEditMetadata] = useState(document.metadata || []);

    function updateTag(index, value) {
        const updatedTags = [...editTags];
        updatedTags[index] = { name: value };
        setEditTags(updatedTags);
    }

    function removeTag(index) {
        setEditTags(editTags.filter((_, i) => i !== index));
    }

    function addTag() {
        setEditTags([...editTags, { name: "" }]);
    }

    function updateMetadata(index, field, value) {
        const updatedMetadata = [...editMetadata];
        updatedMetadata[index] = {
            ...updatedMetadata[index],
            [field]: value,
        };
        setEditMetadata(updatedMetadata);
    }

    function removeMetadata(index) {
        setEditMetadata(editMetadata.filter((_, i) => i !== index));
    }

    function addMetadata() {
        setEditMetadata([...editMetadata, { name: "", value: "" }]);
    }

    function handleSave() {
        onSave({
            tags: editTags,
            metadata: editMetadata,
        });
    }

    return (
        <div className="edit-modal-overlay">
            <div className="edit-modal">
                <h2>Edit document details</h2>

                <div className="edit-section">
                    <h3>Tags</h3>

                    {editTags.map((tag, index) => (
                        <div key={index} className="edit-row">
                            <input
                                value={tag.name}
                                onChange={(e) => updateTag(index, e.target.value)}
                                placeholder="Tag name"
                            />

                            <button
                                className="remove-edit-button"
                                onClick={() => removeTag(index)}
                            >
                                Remove
                            </button>
                        </div>
                    ))}

                    <button className="add-edit-button" onClick={addTag}>
                        + Add tag
                    </button>
                </div>

                <div className="edit-section">
                    <h3>Metadata</h3>

                    {editMetadata.map((item, index) => (
                        <div key={index} className="edit-row metadata-edit-row">
                            <input
                                value={item.name}
                                onChange={(e) =>
                                    updateMetadata(index, "name", e.target.value)
                                }
                                placeholder="Name"
                            />

                            <input
                                value={item.value}
                                onChange={(e) =>
                                    updateMetadata(index, "value", e.target.value)
                                }
                                placeholder="Value"
                            />

                            <button
                                className="remove-edit-button"
                                onClick={() => removeMetadata(index)}
                            >
                                Remove
                            </button>
                        </div>
                    ))}

                    <button className="add-edit-button" onClick={addMetadata}>
                        + Add metadata
                    </button>
                </div>

                <div className="edit-modal-actions">
                    <button className="cancel-edit-button" onClick={onClose}>
                        Cancel
                    </button>

                    <button className="save-edit-button" onClick={handleSave}>
                        Save
                    </button>
                </div>
            </div>
        </div>
    );
}