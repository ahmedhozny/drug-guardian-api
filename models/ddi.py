from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import relationship

from models import BaseModel, DrugsModel


class DDIModel(BaseModel):
    __tablename__ = 'drug_drug_interaction'

    _id = Column(Integer, name="id", primary_key=True, autoincrement=True)
    drug_ref_1 = Column(String(7), ForeignKey(DrugsModel.drug_ref), nullable=False)
    drug_ref_2 = Column(String(7), ForeignKey(DrugsModel.drug_ref), nullable=False)
    interaction = Column(Integer)

    __table_args__ = (UniqueConstraint(drug_ref_1, drug_ref_2, name='uix_drug_drug_interaction'),)

    drug_1 = relationship(DrugsModel, foreign_keys=[drug_ref_1])
    drug_2 = relationship(DrugsModel, foreign_keys=[drug_ref_2])
