from os import getenv
from typing import Any, Type, Dict, List, TypeVar, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine, and_, or_, Column
from sqlalchemy.orm import sessionmaker, scoped_session

from models.base_model import BaseModel

load_dotenv()

# Type variable bound to BaseModel
T = TypeVar('T', bound=BaseModel)

class DBStorage:
    """
    Database storage class to handle database operations using SQLAlchemy.
    """
    __engine = None
    __session = None

    def __init__(self):
        """
        Initializes the database engine and session. Drops all tables if the environment is set to test.
        """
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
        """
        Adds a new object to the database session.

        :param obj: The object to add.
        :param commit: If True, commits the transaction.
        """
        self.__session.add(obj)
        if commit:
            self.__session.commit()

    def remove(self, obj: T, commit: bool = True):
        """
        Removes an object from the database session.

        :param obj: The object to remove.
        :param commit: If True, commits the transaction.
        """
        self.__session.delete(obj)
        if commit:
            self.__session.commit()

    def update(self, obj: T, commit: bool = True):
        """
        Updates an existing object in the database session.

        :param obj: The object to update.
        :param commit: If True, commits the transaction.
        """
        self.__session.merge(obj)
        if commit:
            self.__session.commit()

    async def all(self, cls: Type[T]) -> List[T]:
        """
        Retrieves all objects of a given class from the database.

        :param cls: The class of the objects to retrieve.
        :return: A list of all objects.
        """
        all_objects = []
        query = self.__session.query(cls)
        for element in query:
            all_objects.append(element)
        return all_objects

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
        """
        Counts the number of records matching the given filters.

        :param model: SQLAlchemy model class to filter.
        :param filters: Dictionary of filters {column_name: value}.
        :param operator: 'or' or 'and' to apply for filter conditions.
        :return: Count of matching records.
        """
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

    async def get_by_attr(self, cls: Type[T], key: str, attr: Any) -> Optional[T]:
        """
        Retrieves a single object by a specific attribute.

        :param cls: The class of the object to retrieve.
        :param key: The attribute name to filter by.
        :param attr: The attribute value to filter by.
        :return: The retrieved object, or None if not found.
        """
        result = self.__session.query(cls).filter_by(**{key: attr}).first()
        return result

    async def get_by_id(self, cls: Type[T], id: int) -> Optional[T]:
        """
        Retrieves a single object by its ID.

        :param cls: The class of the object to retrieve.
        :param id: The ID of the object to retrieve.
        :return: The retrieved object, or None if not found.
        """
        result = self.__session.query(cls).filter_by(_id=id).first()
        return result

    def reload(self):
        """
        Creates all tables in the database and initializes a new session.
        """
        BaseModel.metadata.create_all(self.__engine)
        session_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(session_factory)
        self.__session = Session()

    def get_session(self):
        """
        Returns the current database session.

        :return: The current session.
        """
        return self.__session
