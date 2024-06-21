from sqlalchemy import Column, Integer, String


class OrganizationAccount():
    __tablename__ = 'organization_account'
    _id = Column(Integer, name="id", primary_key=True, autoincrement=True)
    organization_name = Column(String(255), nullable=False)
    email = Column(String(320), nullable=False)
    location_uuid = Column(String(255), nullable=False)
    phone_number = Column(String(40), nullable=False)
    organization_type = Column(String(255), nullable=False)
