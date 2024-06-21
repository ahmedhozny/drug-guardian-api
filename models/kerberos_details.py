from sqlalchemy import Column, Integer, String, Boolean, BINARY, DateTime

from models import BaseModel


class KerberosDetails(BaseModel):
    __tablename__ = 'kerberos_details'

    _id = Column(Integer, primary_key=True)
    organization_uuid = Column(BINARY(16), nullable=False)
    principal = Column(String(100), nullable=False)

    active = Column(Boolean, nullable=False, default=False)
