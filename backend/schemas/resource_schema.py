from pydantic import BaseModel

from models.resource import ResourceStatus


class CreateResourceRequest(BaseModel):
    name: str
    resource_type: str
    description: str | None = None
    total_quantity: int = 1


class UpdateResourceRequest(BaseModel):
    name: str | None = None
    resource_type: str | None = None
    description: str | None = None
    status: ResourceStatus | None = None
    total_quantity: int | None = None


class ResourceResponse(BaseModel):
    resource_id: str
    name: str
    resource_type: str
    description: str | None
    status: ResourceStatus
    total_quantity: int

    model_config = {"from_attributes": True}
