from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session
from .. import schemas
from ..database import get_db
from ..operations import files


router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=schemas.ShowFileMetadata, status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await files.upload_file(file, db)
    
     

@router.get("/", response_model=list[schemas.ShowFileMetadata])
def list_files(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return files.list_files(skip, limit, db)



@router.get("/{filename}", tags=["files"])
def download_file(filename: str, db: Session = Depends(get_db)):
    return files.download_file(filename, db)
    
