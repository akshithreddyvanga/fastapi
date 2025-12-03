
from fastapi import Depends, HTTPException, status, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pathlib import Path
from ..core.config import settings
from .. import models, schemas
from ..database import get_db


UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)



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


def list_files(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    
    files = db.query(models.FileMetadata).offset(skip).limit(limit).all()
    return files




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
