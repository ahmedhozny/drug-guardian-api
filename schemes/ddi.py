from typing import List

from pydantic import BaseModel


class DDIChecker(BaseModel):
    drugs: List[str]
