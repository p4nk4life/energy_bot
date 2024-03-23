from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from sqlmodel import Field, SQLModel



class AdminElement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    element_id: int = Field(unique=True)
    name: str
    comment: Optional[str] = None


class UserElementLink(SQLModel, table=True):
    user_id: int = Field(primary_key=True, foreign_key="user.id")
    element_id: int = Field(primary_key=True, foreign_key="element.id")
    user: "User" = Relationship(back_populates="element_links")
    element: "Element" = Relationship(back_populates="user_links")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: str = Field(unique=True)  # Сделать telegram_id уникальным
    username: str
    number: Optional[str]
    element_links: List["UserElementLink"] = Relationship(back_populates="user")


class Element(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    element_id: int
    name: str
    comment: Optional[str] = None
    user_links: List["UserElementLink"] = Relationship(back_populates="element")
    # users: List["User"] = Relationship(back_populates="element", link_model=UserElementLink)
