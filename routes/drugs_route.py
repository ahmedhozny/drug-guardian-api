from fastapi import APIRouter, Query, HTTPException

import schemes.drug
from models import DDIModel
from schemes import DDIChecker
from services.drugs import search_for_drug, get_drug_by_ref, interaction_checker_service
from storage import db_instance

router = APIRouter()


@router.get("/")
async def search(search_key: str = Query(default=None, min_length=3)):
    if search_key is None:
        return db_instance.all("drugs")
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
async def interaction_checker(drugs: DDIChecker):
    print((await (db_instance.filter(DDIModel, drug_id_1=1, drug_id_2=2)))[0])
    res = await interaction_checker_service(drugs.drugs)
    return res
