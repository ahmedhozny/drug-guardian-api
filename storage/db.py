from os import getenv
from typing import Any, Type, Dict, List, TypeVar

from dotenv import load_dotenv
from sqlalchemy import create_engine, and_, or_, Column
from sqlalchemy.orm import sessionmaker, scoped_session

from models.base_model import BaseModel

load_dotenv()


T = TypeVar('T', bound=BaseModel)


class DBStorage:
    """ create tables in environmental"""
    __engine = None
    __session = None

    def __init__(self):
        user = getenv("DB_USER")
        passwd = getenv("DB_PASSWD")
        db = getenv("DB_NAME")
        host = getenv("DB_SERVER")
        env = getenv("DB_TEST")

        self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'
                                      .format(user, passwd, host, db),
                                      pool_pre_ping=True)
        if env == "TRUE":
            BaseModel.metadata.drop_all(self.__engine)

        self.reload()

    def new(self, obj: T, commit: bool = True):
        self.__session.add(obj)
        if commit:
            self.__session.commit()

    def remove(self, obj: T, commit: bool = True):
        self.__session.delete(obj)
        if commit:
            self.__session.commit()

    def update(self, obj: T, commit: bool = True):
        self.__session.merge(obj)
        if commit:
            self.__session.commit()

    async def all(self, cls: Type[T]) -> List[T]:
        all = []
        query = self.__session.query(cls)
        for element in query:
            all.append(element)
        return all

    async def search_for(self, model: Type[T], filters: Dict[Column, Any], operator='or') -> List[T]:
        """
        Generalized function to filter records based on model and filters provided.

        :param model: SQLAlchemy model class to filter.
        :param filters: Dictionary of filters {column_name: value}.
        :param operator: 'or' or 'and' to apply for filter conditions.
        :return: List of filtered records.
        """
        if not filters:
            return self.__session.query(model).all()

        conditions = []
        for key, value in filters.items():
            if isinstance(value, str):
                conditions.append(key.ilike(f"%{value}%"))
            else:
                conditions.append(key == value)

        if operator == 'and':
            query = self.__session.query(model).filter(and_(*conditions))
        else:
            query = self.__session.query(model).filter(or_(*conditions))

        return query.all()

    async def count(self, model: Type[T], filters: Dict[Column, Any], operator='or') -> int:
        if not filters:
            return self.__session.query(model).count()
        conditions = []
        for key, value in filters.items():
            if isinstance(value, str):
                conditions.append(key.ilike(f"%{value}%"))
            else:
                conditions.append(key == value)

        if operator == 'and':
            query = self.__session.query(model).filter(and_(*conditions))
        else:
            query = self.__session.query(model).filter(or_(*conditions))

        return query.count()

    async def get_by_attr(self, cls: Type[T], key: str, attr: Any):
        result = self.__session.query(cls).filter_by(**{key: attr}).first()
        return result

    async def get_by_id(self, cls: Type[T], id: int):
        result = self.__session.query(cls).filter_by(_id=id).first()
        return result

    def reload(self):
        BaseModel.metadata.create_all(self.__engine)
        sec = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sec)
        self.__session = Session()

    def get_session(self):
        return self.__session
