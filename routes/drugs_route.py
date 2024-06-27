from fastapi import APIRouter, Query, HTTPException

import schemas
from models import DDIModel, DrugsModel
from services.drug_interactions import interaction_checker_service
from services.drugs import search_for_drug, get_drug_by_ref
from storage import Storage

router = APIRouter()


@router.get("/")
async def search(search_key: str = Query(default=None, min_length=3)):
    if search_key is None:
        return Storage.list(DrugsModel)
    res = await search_for_drug(search_key)
    res = [{"drug_ref": item.drug_ref, "drug_name": item.drug_name, "brand_name": item.brand_name} for item in res]
    return {"results": res}


@router.get("/{drug_ref}")
async def get_by_reference(drug_ref: str):
    res = await get_drug_by_ref(drug_ref)
    if res is None:
        raise HTTPException(status_code=404, detail="")
    return res


@router.post("/interaction")
async def interaction_checker(drugs: schemas.DDIChecker):
    res = await interaction_checker_service(drugs.drugs)
    return res
