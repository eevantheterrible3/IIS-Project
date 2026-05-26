# Auto-version document on workflow step completion

## Summary

When a workflow instance step is completed, automatically create a new `DocumentVersion` snapshot of the document linked to that workflow instance. This connects the workflow execution lifecycle to the document versioning system.

## Trigger

The versioning fires inside `WorkflowInstanceStepService.update()` when `status` transitions to `"completed"`.

## Version metadata

- **author_id**: The authenticated user who triggered the step completion (passed from the router).
- **version_number**: Latest version number + 1 (existing `DocumentVersionRepository.get_latest_number` logic).
- **full_content**: JSON snapshot of all `DocumentSection`s for the document (same format as the existing `/save` endpoint).
- **note**: `Auto-saved after completing step "{action_name}" in workflow "{workflow_name}"`.

## Changes

### 1. `WorkflowInstanceStepService`

**Constructor** accepts three additional repositories:
- `WorkflowInstanceRepository` — to load the parent instance (for `document_id` and `workflow.name`)
- `DocumentSectionRepository` — to snapshot the document sections
- `DocumentVersionRepository` — to query latest version number and create the new version

**`update()` method** gains an `author_id: str | None = None` parameter. After persisting a status change to `"completed"`:
1. Load the parent `WorkflowInstance` (with workflow relationship) using `instance_id` from the step.
2. Load all `DocumentSection`s for the instance's `document_id`.
3. Build a JSON snapshot in the existing format: `[{section_name, content, order_index}, ...]`.
4. Query latest version number and create a `DocumentVersion`.

### 2. `workflow_instance_steps.py` router

The `update_step` endpoint constructs the service with the additional repositories and passes `current_user.user_id` as `author_id` to `service.update()`.

## Not in scope

- No new models, migrations, or endpoints.
- No changes to the existing manual `/documents/{id}/save` versioning flow.
- No frontend changes.
