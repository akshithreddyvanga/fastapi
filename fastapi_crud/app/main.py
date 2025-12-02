import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File  
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from . import models
from . import schemas
from .database import engine, get_db, Base
from pathlib import Path
from fastapi.responses import FileResponse
from .routers import items, files

load_dotenv()
models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(items.router)
app.include_router(files.router)





