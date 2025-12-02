from sqlalchemy import Column, Integer, String
from .database import Base


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True, unique=True)


class FileMetadata(Base):
    __tablename__ = "file_metadata"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, unique=True)
    stored_path = Column(String)
    content_type = Column(String)
    file_size = Column(Integer)