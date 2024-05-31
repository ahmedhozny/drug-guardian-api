from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from models import BaseModel, DrugsModel


class DDIModel(BaseModel):
    __tablename__ = 'drug_drug_interaction'

    _id = Column(Integer, name="id", primary_key=True, autoincrement=True)
    drug_id_1 = Column(Integer, ForeignKey(DrugsModel._id), nullable=False)
    drug_id_2 = Column(Integer, ForeignKey(DrugsModel._id), nullable=False)
    interaction = Column(Integer)

    __table_args__ = (UniqueConstraint('drug_id_1', 'drug_id_2', name='uix_drug_drug_interaction'),)

    drug_1 = relationship("DrugsModel", foreign_keys=[drug_id_1])
    drug_2 = relationship("DrugsModel", foreign_keys=[drug_id_2])
