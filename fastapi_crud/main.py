from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File  
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db, Base
from pathlib import Path
import shutil
from fastapi.responses import FileResponse


models.Base.metadata.create_all(bind=engine)
app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.post("/items/", response_model=schemas.ShowItem, status_code=status.HTTP_201_CREATED)
def create_item(item: schemas.ItemBase, db: Session = Depends(get_db)):
    db_item = models.Item(name=item.name, email=item.email)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/{item_id}", response_model=schemas.ShowItem)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.get("/items/", response_model=list[schemas.ShowItem])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = db.query(models.Item).offset(skip).limit(limit).all()
    if items is None:
        raise HTTPException(status_code=404, detail="Items not found")
    return items 

@app.put("/items/{item_id}", response_model=schemas.ShowItem)
def update_item(item_id: int, item: schemas.ItemBase, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.name = item.name
    db_item.email = item.email
    db.commit()
    db.refresh(db_item)
    return db_item
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):   
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return
'''
@app.post("/uploadfile/",tags=["uploadfile"])
async def create_upload_file(file: UploadFile = File(...)):
    print(file.file)
    print(file._in_memory)
    content = await file.read()
    print(content)
    return {"filename": file.filename, "content_type": file.content_type, "content_size": len(content)}
'''

@app.post("/uploadfile/", tags=["uploadfile"])
async def create_upload_file(file: UploadFile = File(...)):
    file_location = UPLOAD_DIR / file.filename
    with file_location.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"info": f"file '{file.filename}' saved at '{file_location.as_posix()}'"}

@app.get("/downloadfile/{filename}", tags=["uploadfile"])
async def download_file(filename: str):
    file_location = UPLOAD_DIR / filename
    if not file_location.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_location, filename=filename, media_type='application/octet-stream')
