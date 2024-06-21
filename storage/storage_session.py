import logging
from typing import Type, Union, List, Dict, Any, TypeVar

from fastapi import HTTPException
from sqlalchemy import Column
from sqlalchemy.exc import SQLAlchemyError

from models import BaseModel
from storage import DBStorage
from storage.cache import Cache

logger = logging.getLogger('storage.error')
logger.setLevel(logging.INFO)


T = TypeVar('T', bound=BaseModel)


class StorageSession:
    def __init__(self):
        self.db_instance = DBStorage()
        self.cache = Cache()

    # TODO: Reconsider using async for database modify functions
    def new_object(self, obj: T) -> bool:
        try:
            self.cache.remove(f"{obj.__tablename__}:{obj.id}")
            self.db_instance.new(obj)
            self.cache.invalidate_cache_for_table(type(obj))
            return True
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            raise HTTPException(status_code=500, detail=e.args[0])

    def remove_object(self, obj: T):
        try:
            self.cache.remove(f"{obj.__tablename__}:{obj.id}")
            self.db_instance.remove(obj)
            return True
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            raise HTTPException(status_code=500, detail=e.args[0])

    def update_object(self, obj: T, updates: Dict[Column, Any]) -> bool:
        try:
            for col, value in updates.items():
                setattr(obj, col.key, value)
            self.cache.remove(f"{obj.__tablename__}:{obj.id}")
            self.db_instance.update(obj)  # new() will handle both new and updated objects
            return True
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            raise HTTPException(status_code=500, detail=e.args[0])

    async def get_object(self, model: Type[T], id: int) -> Union[T, None]:
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

    async def list(self, model: Type[T], just_count: bool = False) -> List[T]:
        try:
            res = await self.db_instance.all(model)
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            raise HTTPException(status_code=500, detail=e.args[0])
        return len(res) if just_count else res

    async def filter(self, model: Type[T], filters: Dict[Column, Any] = None) -> List[T]:
        if filters is None:
            res = await self.list(model)
            return res

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
        if filters is None:
            res = await self.list(model)
            return res

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
        return self.db_instance
