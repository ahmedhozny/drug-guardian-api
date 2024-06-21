import base64
import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, inspect, BINARY, DateTime
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
        dict_obj = {k: v for k, v in self.__dict__.items() if k != '_sa_instance_state'}
        for key, val in dict_obj.items():
            if isinstance(val, bytes):
                dict_obj[key] = base64.b64encode(val).decode('utf-8')
            elif isinstance(val, datetime):
                dict_obj[key] = val.isoformat()
        return dict_obj
