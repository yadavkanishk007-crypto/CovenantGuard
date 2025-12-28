from pydantic import BaseModel
from typing import Literal


class UserCreate(BaseModel):
    username: str
    password: str
    role: Literal["admin", "operator", "viewer"]


class UserLogin(BaseModel):
    username: str
    password: str

