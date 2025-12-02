from pydantic import BaseModel
from typing import Optional


class ItemBase(BaseModel):
    name: str
    # Accept any string for email; uniqueness enforced by DB/application
    email: str


class ShowItem(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class FileMetadataBase(BaseModel):
    filename: str
    content_type: Optional[str]
    file_size: int


class FileMetadataCreate(FileMetadataBase):
    stored_path: str


class ShowFileMetadata(FileMetadataBase):
    id: int
    stored_path: str

    class Config:
        from_attributes = True