from pydantic import BaseModel


class DrugSearchResponse(BaseModel):
    drug_ref: str
    drug_name: str
