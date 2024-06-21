import uuid

from sqlalchemy import Column, String, ForeignKey, BINARY, Integer
from sqlalchemy.orm import relationship

from models import BaseModel
from models.uuid_registry import UuidRegistry


class AddressModel(BaseModel):
    __tablename__ = 'addresses'

    _id = Column(Integer, name="id", primary_key=True, autoincrement=True)
    country = Column(String(2), name="country", nullable=False)
    state = Column(String(255), name="state", nullable=False)
    street = Column(String(255), name="street", nullable=False)
    city = Column(String(255), name="city", nullable=False)
    zip = Column(String(5), name="zip", nullable=False)

    uuid = Column(BINARY(16), nullable=False, unique=True, index=True)