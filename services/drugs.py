import storage
from models import DrugsModel
from storage import Storage, db_instance as db
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
    res = await storage.Storage.find(DrugsModel, {DrugsModel.drug_ref: ref})
    return res
