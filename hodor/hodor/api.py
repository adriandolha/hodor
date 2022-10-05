from __future__ import annotations
from pydantic import BaseModel, constr, EmailStr
from typing import List, Optional

from hodor.models import LoginType


class Permission(BaseModel):
    name: constr(max_length=100)
    id: constr(max_length=100)

    class Config:
        orm_mode = True


class Role(BaseModel):
    id: Optional[int]
    name: constr(max_length=100)
    default: Optional[bool] = False
    permissions: Optional[List[Permission]]

    class Config:
        orm_mode = True


class User(BaseModel):
    id: Optional[int]
    username: constr(max_length=100)
    email: EmailStr
    login_type: Optional[str] = LoginType.BASIC
    role: Role

    class Config:
        orm_mode = True


class CreateUser(BaseModel):
    id: Optional[int]
    username: constr(max_length=100)
    password: constr(min_length=10, max_length=100)
    email: EmailStr
    login_type: Optional[str] = LoginType.BASIC
    role: Role

    class Config:
        orm_mode = True
