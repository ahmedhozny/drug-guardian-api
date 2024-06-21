from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import Relationship

from models import BaseModel, AccountDetails


class AccountBearer(BaseModel):
    __tablename__ = 'account_bearer'

    _id = Column(Integer, name="id", primary_key=True, autoincrement=True)

    account_id = Column(Integer, ForeignKey(AccountDetails._id), nullable=False)
    access_token = Column(String(511), nullable=False)

    account = Relationship(AccountDetails, foreign_keys=[account_id])
