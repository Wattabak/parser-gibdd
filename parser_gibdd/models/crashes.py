from datetime import time
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Crash(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    region_id: str
    region_name: str

    crash_type: str
    District: str
    vehicles_amount: int
    participants_amount: int
    deceased: int
    wounded: int
    date: str
    Time: time
    row: int = Field(...,
                     description='This is just a relative index of rows in the table of crashes')

    longitude: float
    latitude: float
    objects_near_crash: List[str]
    motion_changes: str
    main_road: str
    road_category: str
    road_significance: str
    motion_affecting_factors: List[str]
    house: Optional[str] = None
    street_category: str
    km: str
    m: str
    settlement: str
    road_deficiency: List[str]
    light_conditions: str
    s_dtp: str
    road_conditions: str
    weather: List[str]
    onsite_crash_road_objects: List[str]
    street: str
    vehicles: List[UUID]
    participants: List[UUID]
