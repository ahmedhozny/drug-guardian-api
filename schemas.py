from typing import List

from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber


class LoginBase(BaseModel):
    account_id: int
    email: EmailStr
    password: str


class TokenBase(BaseModel):
    access_token: str
    token_type: str


class Token(TokenBase):
    account_id: int


class Address(BaseModel):
    country: str = Field(..., description="Country", example="EG", min_length=2)
    state: str = Field(..., description="State", example="Alexandria", min_length=3)
    street: str = Field(..., description="Street", example="123 Main St", min_length=3)
    city: str = Field(..., description="City", example="Alexandria", min_length=3)
    zip: str = Field(..., description="Zip Code", example="14321", min_length=5, max_length=5)

    class Config:
        orm_mode = True


class DDIChecker(BaseModel):
    drugs: List[str]


class SideEffectsPrediction(BaseModel):
    drug1_id: int
    drug2_id: int
    side_effect_id: str


class HealthcareSignupRequest(BaseModel):
    organization_name: str = Field(..., example="Heartbeats", min_length=1)
    email: EmailStr
    phone: PhoneNumber = Field(..., example="+201201234567")
    address: Address


class HealthcareSignupRequestUUID(HealthcareSignupRequest):
    uuid: str


class HealthcareSignupHandle(BaseModel):
    email: EmailStr
    confirm: bool


class AccountRegister(BaseModel):
    token: str
    email: EmailStr
    password: str
    principal: str


class OptimizationInput(BaseModel):
    optimization_type: str = Field(default="default_type")
