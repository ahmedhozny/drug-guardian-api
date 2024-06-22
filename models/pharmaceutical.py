from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean, Text, BINARY
from sqlalchemy.orm import relationship

from models import BaseModel, AddressModel


class PharmaceuticalModel(BaseModel):
    __tablename__ = 'pharmaceutical'

    _id = Column(Integer, name="id", primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=False, unique=True)
    address_uuid = Column(BINARY(16), ForeignKey(AddressModel.uuid), nullable=False)
    registered_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    status = Column(String(64), nullable=False)  # TODO: status table
    uuid_registry = Column(BINARY(16), nullable=False)

    address_relationships = relationship(AddressModel, foreign_keys=[address_uuid])
