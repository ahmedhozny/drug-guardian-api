import logging
from typing import Type, Union, List, Dict, Any, TypeVar

from fastapi import HTTPException
from sqlalchemy import Column
from sqlalchemy.exc import SQLAlchemyError

from models import BaseModel
from storage import DBStorage
from storage.cache import Cache

# Setting up logger for storage errors
logger = logging.getLogger('storage.error')
logger.setLevel(logging.INFO)

# Type variable bound to BaseModel
T = TypeVar('T', bound=BaseModel)

class StorageSession:
    """
    Class to manage the storage session, handling both database and cache interactions.
    """
    def __init__(self):
        self.db_instance = DBStorage()
        self.cache = Cache()

    def new_object(self, obj: T) -> bool:
        """
        Adds a new object to the database and invalidates the related cache.

        :param obj: The object to be added.
        :return: True if the operation was successful, False otherwise.
        """
        try:
            self.cache.remove(f"{obj.__tablename__}:{obj.id}")
            self.db_instance.new(obj)
            self.cache.invalidate_cache_for_table(type(obj))
            return True
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            raise HTTPException(status_code=500, detail=e.args[0])

    def remove_object(self, obj: T) -> bool:
        """
        Removes an object from the database and cache.

        :param obj: The object to be removed.
        :return: True if the operation was successful, False otherwise.
        """
        try:
            self.cache.remove(f"{obj.__tablename__}:{obj.id}")
            self.db_instance.remove(obj)
            return True
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            raise HTTPException(status_code=500, detail=e.args[0])

    def update_object(self, obj: T, updates: Dict[Column, Any]) -> bool:
        """
        Updates an object in the database and removes the related cache.

        :param obj: The object to be updated.
        :param updates: Dictionary of updates to apply to the object.
        :return: True if the operation was successful, False otherwise.
        """
        try:
            for col, value in updates.items():
                setattr(obj, col.key, value)
            self.cache.remove(f"{obj.__tablename__}:{obj.id}")
            self.db_instance.update(obj)
            return True
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            raise HTTPException(status_code=500, detail=e.args[0])

    async def get_object(self, model: Type[T], id: int) -> Union[T, None]:
        """
        Retrieves an object by ID, first checking the cache and then the database.

        :param model: The model class of the object.
        :param id: The ID of the object to retrieve.
        :return: The retrieved object, or None if not found.
        """
        cached_obj = await self.cache.get(model, id, 300)
        if cached_obj:
            return cached_obj

        try:
            res = await self.db_instance.get_by_id(model, id)
            if res:
                self.cache.store(res, 300)
            return res
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            raise HTTPException(status_code=500, detail=e.args[0])

    async def list(self, model: Type[T], just_count: bool = False) -> Union[List[T], int]:
        """
        Retrieves all objects of a given model.

        :param model: The model class of the objects to retrieve.
        :param just_count: If True, returns the count of objects.
        :return: List of objects or count of objects.
        """
        try:
            res = await self.db_instance.all(model)
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            raise HTTPException(status_code=500, detail=e.args[0])
        return len(res) if just_count else res

    async def filter(self, model: Type[T], filters: Dict[Column, Any] = None) -> List[T]:
        """
        Filters objects based on provided filters using 'and' operator.

        :param model: The model class of the objects to filter.
        :param filters: Dictionary of filters {column: value}.
        :return: List of filtered objects.
        """
        if filters is None:
            return await self.list(model)

        res = await self.cache.smembers("filter", model, filters)
        if res is not None:
            return res

        try:
            members = await self.db_instance.search_for(model, filters, "and")
            for member in members:
                self.cache.sadd("filter", member, filters)
            return members
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            raise HTTPException(status_code=500, detail=e.args[0])

    async def find(self, model: Type[T], filters: Dict[Column, Any] = None) -> List[T]:
        """
        Finds objects based on provided filters using 'or' operator.

        :param model: The model class of the objects to find.
        :param filters: Dictionary of filters {column: value}.
        :return: List of found objects.
        """
        if filters is None:
            return await self.list(model)

        res = await self.cache.smembers("find", model, filters)
        if res is not None:
            return res

        try:
            members = await self.db_instance.search_for(model, filters, "or")
            for member in members:
                self.cache.sadd("find", member, filters)
            return members
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            raise HTTPException(status_code=500, detail=e.args[0])

    def get_db_instance(self) -> DBStorage:
        """
        Returns the DBStorage instance.

        :return: The DBStorage instance.
        """
        return self.db_instance
