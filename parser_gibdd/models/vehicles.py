from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Vehicle(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    color: str
    property_form: str
    issued_year: str
    damage_points: str
    car_model: str
    car_brand: str
    vehicle_amount: str
    o_pf: str
    r_rul: str
    technical_defects: str
    vehicle_type: str
    left_crash_site: str
    drivers: List[UUID]
