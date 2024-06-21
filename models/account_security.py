from datetime import timedelta

from krb5 import Principal
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func, Boolean
from sqlalchemy.orm import Relationship

from models import BaseModel, AccountDetails


class AccountSecurity(BaseModel):
	__tablename__ = 'account_security'

	_id = Column(Integer, name="id", primary_key=True, autoincrement=True)
	account_id = Column(Integer, ForeignKey(AccountDetails._id), nullable=False, unique=True)

	# Kerberos Authentication (For Negotiate)
	keytab_password = Column(String(255), nullable=True)
	keytab_password_expiry = Column(DateTime(timezone=True), nullable=False)

	# OAuth (For Bearer)
	password_hashed = Column(String(255), nullable=False)

	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
	expired = Column(Boolean, default=False)

	account = Relationship(AccountDetails, foreign_keys=[account_id])
