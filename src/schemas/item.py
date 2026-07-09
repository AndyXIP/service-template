from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float = Field(gt=0)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)


class ItemRead(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
