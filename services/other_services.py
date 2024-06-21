from typing import Type

from fastapi import HTTPException

import schemas
from models import BaseModel
from models.addresses import AddressModel

from storage import Storage


def addLocation(location: schemas.Address, table: Type[BaseModel]):
    if location is None:
        return None

    if location.get("country") is None:
        raise HTTPException(status_code=400, detail="Missing country")

    if location.get("state") is None:
        raise HTTPException(status_code=400, detail="Missing state")

    if location.get("city") is None:
        raise HTTPException(status_code=400, detail="Missing city")

    if location.get("street") is None:
        raise HTTPException(status_code=400, detail="Missing street")

    if location.get("zip") is None:
        raise HTTPException(status_code=400, detail="Missing zip")

    obj = AddressModel(**location.model_dump())
    Storage.new_object(obj)
