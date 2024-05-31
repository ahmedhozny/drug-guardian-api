import json
import logging
from typing import Type, Union, List, Dict, Any

from sqlalchemy import Column
from sqlalchemy.exc import SQLAlchemyError

from models import BaseModel

from storage.cache import Cache
from storage import DBStorage

logger = logging.getLogger('storage.error')
logger.setLevel(logging.INFO)


class StorageSession:
    def __init__(self):
        self.db_instance = DBStorage()
        self.cache = Cache()

    # TODO: Reconsider using async for database modify functions
    def new_object(self, obj: BaseModel) -> bool:
        try:
            self.cache.remove(f"{obj.__tablename__}:{obj.id}")
            self.db_instance.new(obj)
            return True
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            return False

    def remove_object(self, obj: BaseModel):
        try:
            self.cache.remove(f"{obj.__tablename__}:{obj.id}")
            self.db_instance.remove(obj)
            return True
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            return False

    def update_object(self, obj: BaseModel, updates: Dict[str, Any]) -> bool:
        try:
            for key, value in updates.items():
                setattr(obj, key, value)
            self.cache.remove(f"{obj.__tablename__}:{obj.id}")
            self.db_instance.new(obj)  # new() will handle both new and updated objects
            return True
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            return False

    async def get_object(self, model: Type[BaseModel], id: int) -> Union[BaseModel, None]:
        cache_key = f"{model.__tablename__}:{id}"
        cached_obj = self.cache.get_dict(cache_key)
        if cached_obj:
            return model(**cached_obj)

        try:
            res = await self.db_instance.get_by_id(model, id)
            if res:
                self.cache.store(cache_key, res.to_dict())
            return res
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            return None

    async def list(self, model: Type[BaseModel]) -> Union[List[BaseModel], None]:
        cache_key = f"{model.__tablename__}:all"
        cached_list = self.cache.get(cache_key)

        if cached_list:
            cached_list = json.loads(cached_list)
            return [model(**item) for item in cached_list]

        try:
            res = await self.db_instance.all(model)
            if res:
                self.cache.store(cache_key, json.dumps([item.to_dict() for item in res.values()]), 300)
            return res
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            return None

    async def filter(self, model: Type[BaseModel], filters: Dict[Column, Any], just_count: bool = False) -> Union[List[BaseModel], int, None]:
        custom_filter = dict()
        for key, value in filters.items():
            custom_filter[str(key.name)] = value

        cache_key = f"{model.__tablename__}:find:{json.dumps(custom_filter)}"
        if just_count:
            cache_key += ":count"
            cached_count = self.cache.get(cache_key)
            if cached_count is not None:
                return cached_count
        else:
            cached_list = self.cache.get(cache_key)
            if cached_list:
                cached_list = json.loads(cached_list)
                return [model(**item) for item in cached_list]

        try:
            if just_count:
                res = await self.db_instance.count(model, filters, "and")
                if res is not None:
                    self.cache.store(cache_key, res, 300)
            else:
                res = await self.db_instance.search_for(model, filters, "and")
                if res:
                    serialized_res = [item.to_dict() for item in res]
                    self.cache.store(cache_key, json.dumps(serialized_res), 300)
            return res
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            return None

    async def find(self, model: Type[BaseModel], filters: Dict[Column, Any], just_count: bool = False) -> Union[List[BaseModel], int, None]:
        custom_filter = dict()
        for key, value in filters.items():
            custom_filter[str(key.name)] = value

        cache_key = f"{model.__tablename__}:find:{json.dumps(custom_filter)}"
        if just_count:
            cache_key += ":count"
            cached_count = self.cache.get(cache_key)
            if cached_count is not None:
                return cached_count
        else:
            cached_list = self.cache.get(cache_key)
            if cached_list:
                cached_list = json.loads(cached_list)
                return [model(**item) for item in cached_list]

        try:
            if just_count:
                res = await self.db_instance.count(model, filters, "or")
                if res is not None:
                    self.cache.store(cache_key, res, 300)
            else:
                res = await self.db_instance.search_for(model, filters, "or")
                if res:
                    serialized_res = [item.to_dict() for item in res]
                    self.cache.store(cache_key, json.dumps(serialized_res), 300)
            return res
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            return None

    async def join(self, primary_model: Type[BaseModel], related_model: Type[BaseModel],
                   join_condition: Any, filters: Dict[str, Any] = None) -> Union[List[BaseModel], None]:
        cache_key = f"{primary_model.__tablename__}_join_{related_model.__tablename__}:{json.dumps(filters)}"
        cached_list = self.cache.get(cache_key)
        if cached_list:
            cached_list = json.loads(cached_list)
            return [primary_model(**item) for item in cached_list]

        try:
            result = await self.db_instance.join(primary_model, related_model, join_condition, filters)
            if result:
                self.cache.store(cache_key, json.dumps([item.to_dict() for item in result]), 300)
            return result
        except SQLAlchemyError as e:
            logger.error(e.args[0])
            return None
