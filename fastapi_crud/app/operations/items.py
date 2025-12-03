
from sqlalchemy.exc import IntegrityError
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, status


def create(db: Session, item: schemas.ItemBase) :
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
    


def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


def read_items_all(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = db.query(models.Item).offset(skip).limit(limit).all()
    return items 


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


def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item by ID."""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return
