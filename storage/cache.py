import base64
import json
from datetime import datetime
from typing import Union, Optional, TypeVar, Type, Dict, Any, List
import redis
from sqlalchemy import Column

from models import BaseModel

T = TypeVar('T', bound=BaseModel)


def _to_attribute_string(attributes: Dict[Column, Any]) -> str:
    attributes_list = [f"{key.name}={value}" for key, value in attributes.items()]
    return "\t".join(attributes_list)


def _from_attribute_string(attribute_string: str) -> Dict[Column, Any]:
    attributes = {}
    pairs = attribute_string.split("\t")
    for pair in pairs:
        key, value = pair.split("=")
        column = Column(name=key)
        attributes[column] = value
    return attributes


def is_base64(s: str) -> bool:
    try:
        return base64.b64encode(base64.b64decode(s)) == s.encode('utf-8')
    except Exception:
        return False

def is_isoformat(s: str) -> bool:
    try:
        datetime.fromisoformat(s)
        return True
    except ValueError:
        return False


class Cache:
    def __init__(self):
        self._redis = redis.StrictRedis(host='localhost', port=6379, db=1)

    def store(self, obj: T, expire_in: Optional[int] = None):
        """
        Stores the given object in the Redis database and sets an optional expiration time.

        :param obj: The object to store, which should be an instance of a model inheriting from BaseModel.
        :param expire_in: Optional expiration time in seconds. If not provided, the key will not expire.
        """
        cache_key = f"{obj.__tablename__}:{obj.id}"
        dict_obj = obj.to_dict()
        self._redis.set(cache_key, json.dumps(dict_obj), ex=expire_in)

    async def get(self, model: Type[T], id: int, expire_in: Optional[int] = None) -> T | None:
        """
        Retrieves an object by its ID from the Redis database and reconstructs it into the model instance.

        :param model: The model class to reconstruct the object.
        :param id: The ID of the object to retrieve.
        :param expire_in: Optional expiration time in seconds. If provided, resets the expiration time.
        :return: The reconstructed model instance if found, otherwise None.
        """
        cache_key = f"{model.__tablename__}:{id}"
        data = self._redis.get(cache_key)
        if data is None:
            return None

        from_data = json.loads(data)
        for key, val in from_data.items():
            if isinstance(val, str) and is_base64(val):
                from_data[key] = base64.b64decode(val.encode('utf-8'))
            elif isinstance(val, str) and is_isoformat(val):
                from_data[key] = datetime.fromisoformat(val)
        if expire_in is not None:
            self._redis.expire(cache_key, expire_in)
        return model(**from_data)

    def _decode(self, data: Union[bytes, str, int, float]) -> Union[str, int, float]:
        """
        Helper method to decode Redis data.

        :param data: The data to decode.
        :return: The decoded data.
        """
        if isinstance(data, bytes):
            return data.decode("utf-8")
        return data

    def remove(self, key: str):
        """
        Removes the given key from the Redis database.

        :param key: The key to remove.
        """
        self._redis.delete(key)

    def client(self) -> redis.StrictRedis:
        """
        Returns a Redis client instance.

        :return: The Redis client instance.
        """
        return self._redis

    def sadd(self, method: str, obj: T, filters: Dict[Column, Any]) -> int:
        """
        Adds an object's ID to a set in Redis based on the method and filter criteria, and stores the object.

        :param method: The method name (e.g., 'filter') to include in the cache key.
        :param obj: The object whose ID will be added to the set.
        :param filters: A dictionary of filter criteria.
        :return: The number of elements that were added to the set.
        """
        attributes = _to_attribute_string(filters)

        cache_key = f"{method}:{obj.__tablename__}:{attributes}"
        self.store(obj)
        return self._redis.sadd(cache_key, obj.id)

    async def smembers(self, method: str, model: Type[T], filters: Dict[Column, Any]) -> Optional[List[T]]:
        """
        Retrieves all members of the set stored at the given key, constructs model instances, and returns them.

        :param method: The method name (e.g., 'filter') to include in the cache key.
        :param model: The model class to reconstruct the objects.
        :param filters: A dictionary of filter criteria.
        :return: A list of model instances if the set is found, otherwise None.
        """
        attributes = _to_attribute_string(filters)

        cache_key = f"{method}:{model.__tablename__}:{attributes}"
        members = self._redis.smembers(cache_key)
        if not members:
            return None

        res = []
        for member in members:
            obj = await self.get(model, member.decode("utf-8"))
            if obj:
                res.append(obj)
        return res

    def invalidate_cache_for_table(self, model: Type[T]) -> None:
        """
        Invalidates all cache entries related to a specific table.
        """
        cursor = 0
        keys = []
        while True:
            cursor, batch = self._redis.scan(cursor, f"*:{model.__tablename__}:*")
            keys.extend(batch)
            if cursor == 0:
                break
        for key in keys:
            self._redis.delete(key.decode('utf-8'))
