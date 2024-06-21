from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func, Boolean, event
from sqlalchemy.orm import Relationship

from models import BaseModel


class AccountTypes(BaseModel):
    __tablename__ = 'account_types'

    _id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(255), nullable=True)


default_rows = [
    {'name': 'Admin', 'description': 'Administrator with full access to manage the system'},
    {'name': 'Hospital', 'description': 'Hospital account with access to patient and medical records management'},
    {'name': 'Pharmaceutical', 'description': 'Pharmaceutical company account with access to drug inventory and distribution data'},
    {'name': 'Researcher', 'description': 'Researcher account with access to data analysis and research tools'}
]

event.listen(
    AccountTypes.__table__,
    'after_create',
    lambda target, connection, **kwargs: connection.execute(target.insert(), default_rows)
)
