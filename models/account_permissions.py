from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func, Boolean
from sqlalchemy.orm import Relationship

from models import BaseModel, AccountDataModel


class AccountPermissionModel(BaseModel):
	__tablename__ = 'account_permissions'

	_id = Column(Integer, name="id", primary_key=True, autoincrement=True)
	account_id = Column(Integer, ForeignKey(AccountDataModel._id), nullable=False)
	password_hashed = Column(String(255), nullable=False)
	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
	expired = Column(Boolean, default=False)
	account = Relationship('AccountDataModel', foreign_keys=[account_id])
