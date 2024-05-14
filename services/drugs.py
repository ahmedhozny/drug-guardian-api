import asyncio
from typing import List

from models import DrugsModel, DDIModel
from storage import db_instance as db
from sqlalchemy import or_


async def search_for_drug(search: str):
    drugs = db.get_session().query(DrugsModel).filter(
        or_(
            DrugsModel.drug_name.ilike(f"%{search}%"),
            DrugsModel.brand_name.ilike(f"%{search}%")
        )
    ).all()
    return drugs


async def get_drug_by_id(id: int):
    res = await db.get_by_id(DrugsModel, id)
    return res


async def get_drug_by_ref(ref: str):
    res = await db.get_by_attr(DrugsModel, "drug_ref", ref)
    return res


async def interaction_checker_service(drugs: List[str]):
    interactions = await asyncio.gather(*[
        db.filter(DDIModel, drug_id_1=drugs[i], drug_id_2=drugs[j])
        for i in range(len(drugs))
        for j in range(i + 1, len(drugs))
    ])

    return interactions
