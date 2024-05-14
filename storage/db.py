from os import getenv
from typing import Any, Type

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from models.base_model import BaseModel
from models.drug import DrugsModel
from models.ddi import DDIModel

load_dotenv()


class DBStorage:
    """ create tables in environmental"""
    __engine = None
    __session = None
    __models = {"drugs": DrugsModel, "DDIs": DDIModel}

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

    def new(self, obj: BaseModel):
        self.__session.add(obj)

    def remove(self, obj: BaseModel):
        self.__session.delete(obj)

    async def all(self, cls: str):
        dic = {}
        print(cls)
        if cls not in self.__models.keys():
            return None
        cls = self.__models.get(cls)
        query = self.__session.query(cls)
        print(query)
        for element in query:
            key = "{}.{}".format(type(element).__name__, element.id)
            dic[key] = element
        return dic

    async def filter(self, cls: Type[BaseModel], **kwargs):
        """Filters objects based on the provided class and column-value pairs.

        Args:
            cls (BaseModel): The class object to filter.
            **kwargs: Keyword arguments representing column names and their values
                    to filter by.

        Returns:
            list: A list of filtered objects, or None if an error occurs.
        """

        query = self.__session.query(cls)

        # Build the filter expression dynamically based on provided arguments
        filters = []
        for column, value in kwargs.items():
            # Ensure the column exists in the class model
            if not hasattr(cls, column):
                raise ValueError(f"Column '{column}' does not exist in class '{cls.__name__}'")
            filters.append(getattr(cls, column) == value)

        # Apply all filters to the query
        query = query.filter(*filters)

        return query.all()

    async def get_by_attr(self, cls: Type[BaseModel], key: str, attr: Any):
        return self.__session.query(cls).filter_by(**{key: attr}).first()

    async def get_by_id(self, cls: Type[BaseModel], id: int):
        return self.__session.query(cls).filter_by(id=id).first()

    def reload(self):
        BaseModel.metadata.create_all(self.__engine)
        sec = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sec)
        self.__session = Session()

    def get_session(self):
        return self.__session
