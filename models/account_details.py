from sqlalchemy import Column, Integer, ForeignKey, String, BINARY
from sqlalchemy.orm import relationship

from models import BaseModel, AccountTypes


class AccountDetails(BaseModel):
    __tablename__ = 'account_details'

    _id = Column(Integer, name="id", primary_key=True, autoincrement=True)
    account_type_id = Column(Integer, ForeignKey(AccountTypes._id), nullable=False)
    organization_uuid = Column(BINARY(16), nullable=False)
    principal = Column(String(255), nullable=False, unique=True)
    account_status = Column(String(50), nullable=False)

    account_type = relationship(AccountTypes, foreign_keys=[account_type_id])
