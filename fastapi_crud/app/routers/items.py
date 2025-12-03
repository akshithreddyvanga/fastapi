from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session 
from sqlalchemy.exc import IntegrityError
from .. import models, schemas
from ..database import get_db
from ..operations import items
router = APIRouter(prefix="/items", tags=["CRUD"])

@router.post("/", response_model=schemas.ShowItem, status_code=status.HTTP_201_CREATED)
def create_item(item: schemas.ItemBase, db: Session = Depends(get_db)):
    return items.create(db, item)

@router.get("/{item_id}", response_model=schemas.ShowItem)
def read_item(item_id: int, db: Session = Depends(get_db)):
    return items.read_item(item_id, db)

@router.get("/", response_model=list[schemas.ShowItem])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return items.read_items_all(skip, limit, db)

@router.put("/{item_id}", response_model=schemas.ShowItem)
def update_item(item_id: int, item: schemas.ItemBase, db: Session = Depends(get_db)):
    return items.update_item(item_id, item, db)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    return items.delete_item(item_id, db)
