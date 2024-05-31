import asyncio
from typing import List

from storage import db_instance as db
from models import DDIModel


async def interaction_checker_service(drugs: List[str]):
    interactions = await asyncio.gather(
        *[
            db.filter(DDIModel, drug_id_1=drugs[i], drug_id_2=drugs[j])
            for i in range(len(drugs))
            for j in range(i + 1, len(drugs))
        ])

    return interactions
