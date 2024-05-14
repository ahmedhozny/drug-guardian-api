from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models import BaseModel, DrugsModel


class DDIModel(BaseModel):
	__tablename__ = 'drug_drug_interaction'

	drug_id_1 = Column(Integer, ForeignKey(DrugsModel.id), nullable=False, primary_key=True)
	drug_id_2 = Column(Integer, ForeignKey(DrugsModel.id), nullable=False, primary_key=True)
	interaction = Column(Integer)

	drug_1 = relationship("DrugsModel", foreign_keys=[drug_id_1])
	drug_2 = relationship("DrugsModel", foreign_keys=[drug_id_2])
