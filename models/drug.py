from sqlalchemy import Column, String, Text, Integer, Float

from models import BaseModel


class DrugsModel(BaseModel):
	__tablename__ = 'drugs'

	id = Column(Integer, primary_key=True, autoincrement=True)
	drug_ref = Column(String(7), unique=True, nullable=False, index=True) #[A-Za-z][0-9]^6
	drug_name = Column(String(255), nullable=False)
	brand_name = Column(String(255), nullable=False)  # Note: multiple -> each drug
	indications = Column(Text, nullable=False)
	active_ingredient = Column(String(255), nullable=True)
	weight = Column(Float, nullable=False)
	smiles = Column(String(1000), nullable=False)
	drug_bank_ref = Column(Integer, nullable=True)
