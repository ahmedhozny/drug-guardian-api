from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    _id = Column(Integer, name="id", primary_key=True, autoincrement=True)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if hasattr(self, '_id') and self._id is not None:
            raise AttributeError("id attribute is immutable and cannot be changed once set.")
        self._id = value

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if k != '_sa_instance_state'}
