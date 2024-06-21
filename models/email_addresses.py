import uuid
from typing import Type, TypeVar

from sqlalchemy import Column, BINARY, Integer, String
from models import BaseModel

T = TypeVar('T', bound=BaseModel)


class EmailAddresses(BaseModel):
    __tablename__ = 'email_addresses'

    _id = Column(Integer, name="id", primary_key=True, autoincrement=True)
    organization_uuid = Column(BINARY(16), nullable=False, unique=True)
    email = Column(String(320), nullable=False, unique=True)
