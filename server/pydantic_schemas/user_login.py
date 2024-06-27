from pydantic import BaseModel
from sqlalchemy import Column


class UserLogin(BaseModel):
    email: str
    password: str