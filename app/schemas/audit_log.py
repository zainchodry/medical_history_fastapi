from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    action: str
    resource: str
    resource_id: int | None = None
    details: str | None = None
    ip_address: str | None = None
    created_at: datetime | None = None
