from storage.db import DBStorage
from storage.storage_session import StorageSession

Storage: StorageSession = StorageSession()

async def get_storage():
    yield Storage
