import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File  
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import models, schemas
from .database import engine, get_db, Base
from pathlib import Path
from fastapi.responses import FileResponse


models.Base.metadata.create_all(bind=engine)
app = FastAPI()

load_dotenv()

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.post("/items/", response_model=schemas.ShowItem, status_code=status.HTTP_201_CREATED,tags=["CRUD"])
def create_item(item: schemas.ItemBase, db: Session = Depends(get_db)):
    existing = db.query(models.Item).filter(models.Item.email == item.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists. Email must be unique."
        )

    db_item = models.Item(name=item.name, email=item.email)
    db.add(db_item)
    try:
        db.commit()
        db.refresh(db_item)
        return db_item
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists. Email must be unique."
        )

@app.get("/items/{item_id}", response_model=schemas.ShowItem,tags=["CRUD"])
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.get("/items/", response_model=list[schemas.ShowItem],tags=["CRUD"])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = db.query(models.Item).offset(skip).limit(limit).all()
    return items 

@app.put("/items/{item_id}", response_model=schemas.ShowItem,tags=["CRUD"])
def update_item(item_id: int, item: schemas.ItemBase, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    other = db.query(models.Item).filter(models.Item.email == item.email).first()
    if other and other.id != item_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists. Email must be unique."
        )

    try:
        db_item.name = item.name
        db_item.email = item.email
        db.commit()
        db.refresh(db_item)
        return db_item
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists. Email must be unique."
        )

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT,tags=["CRUD"])
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item by ID."""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return


@app.post("/files/upload", response_model=schemas.ShowFileMetadata, status_code=status.HTTP_201_CREATED, tags=["files"])
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_location = UPLOAD_DIR / file.filename
    try:
        content = await file.read()
        with open(file_location, "wb") as buffer:
            buffer.write(content)

        file_size = len(content)

        db_file = models.FileMetadata(
            filename=file.filename,
            stored_path=file_location.as_posix(),
            content_type=file.content_type or "application/octet-stream",
            file_size=file_size,
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        return db_file
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Filename already exists. Choose a different filename."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error uploading file: {str(e)}"
        )

@app.get("/files", response_model=list[schemas.ShowFileMetadata], tags=["files"])
def list_files(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    
    files = db.query(models.FileMetadata).offset(skip).limit(limit).all()
    return files

@app.get("/files/{filename}", tags=["files"])
def download_file(filename: str, db: Session = Depends(get_db)):

    db_file = db.query(models.FileMetadata).filter(models.FileMetadata.filename == filename).first()
    if db_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"File with filename '{filename}' not found"}
        )

    file_path = Path(db_file.stored_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "File not found on disk"}
        )

    return FileResponse(
        path=file_path,
        filename=db_file.filename,
        media_type=db_file.content_type,
    )
