from sqlalchemy import Column, String, Integer, Float, BINARY


class OrganisationsModel():
	__tablename__ = 'organisations'

	_id = Column(Integer, name="id", primary_key=True, autoincrement=True)
	name = Column(String(255), nullable=False)
	country = Column(String(255), nullable=False)
	full_address = Column(String(255), nullable=True)
	registered_at = Column(Float, nullable=False)
	active = Column(Integer, nullable=False)
	uuid_registry = Column(BINARY(16), nullable=False)
