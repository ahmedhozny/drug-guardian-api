from sqlalchemy import Column, Integer, String, Boolean, BINARY

from models import BaseModel


class AccountVerification(BaseModel):
    __tablename__ = 'account_verification'

    _id = Column(Integer, primary_key=True)
    uuid_registry = Column(BINARY(16), nullable=False)
    token = Column(String(255), nullable=False, index=True)
    used = Column(Boolean, nullable=False, default=False)
