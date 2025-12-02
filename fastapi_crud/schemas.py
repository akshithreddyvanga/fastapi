from pydantic import BaseModel
class ItemBase(BaseModel):
    name: str
    email: str

class ShowItem(BaseModel):
    name: str

    class Config:
        orm_mode = True