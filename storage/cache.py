import json
from typing import Callable, Union, Optional

import redis


class Cache:
    def __init__(self):
        self._redis = redis.StrictRedis(host='localhost', port=6379, db=1)

    def store(self, key: str, data: Union[str, bytes, int, float], expire_in: Optional[int] = None) -> str:
        """
        Stores the given data in the Redis database and returns a unique key.
        """
        self._redis.set(key, data, ex=expire_in)
        return key

    def get(self, key: str, fn: Callable = None, expire_in: Optional[int] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieves data associated with the given key from the Redis database.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if expire_in is not None:
            self._redis.expire(key, expire_in)
        if fn is None:
            return data
        return fn(data)

    def get_str(self, key: str) -> str:
        """
        Retrieves a string value associated with the given key
        """
        return self.get(key, lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """
        Retrieves an int value associated with the given key
        """
        return self.get(key, lambda d: int(d))

    def get_list(self, key: str) -> Union[list, None]:
        """
        Retrieves a list value associated with the given key
        """
        data = self.get(key, lambda d: d.decode("utf-8"))
        if data is None:
            return None
        return json.loads(data)

    def get_dict(self, key: str) -> Union[dict, None]:
        """
        Retrieves a dict value associated with the given key
        """
        data = self.get(key, lambda d: d.decode("utf-8"))
        if data is None:
            return None
        return json.loads(data)

    def remove(self, key: str):
        """
        Removes the given key from the Redis database.
        """
        self._redis.delete(key)
