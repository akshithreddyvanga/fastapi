
from dotenv import load_dotenv
from fastapi import FastAPI
from .database import engine
from . import models
from .routers import items, files


load_dotenv()


models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(items.router)
app.include_router(files.router)





