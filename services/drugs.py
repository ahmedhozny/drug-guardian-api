import storage
from models import DrugsModel
from storage import Storage


async def search_for_drug(search: str):
    drugs = await Storage.find(DrugsModel, {DrugsModel.drug_name: search, DrugsModel.brand_name: search})
    return drugs


async def get_drug_by_id(id: int):
    res = await Storage.get_db_instance().get_by_id(DrugsModel, id)
    return res


async def get_drug_by_ref(ref: str):
    res = await storage.Storage.find(DrugsModel, {DrugsModel.drug_ref: ref})
    return res
