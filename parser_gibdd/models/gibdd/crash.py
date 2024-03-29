from datetime import time
from typing import List, Optional

from pydantic import BaseModel, Field

from parser_gibdd.models.gibdd.participant import ParticipantInfo
from parser_gibdd.models.gibdd.vehicle import VehicleInfo


class CrashInfo(BaseModel):
    longitude: float = Field(..., alias="COORD_L")
    latitude: float = Field(..., alias="COORD_W")
    objects_near_crash: List[str] = Field(..., alias="OBJ_DTP")
    motion_changes: str = Field(..., alias="change_org_motion")
    main_road: str = Field(..., alias="dor")
    road_category: str = Field(..., alias="dor_k")
    road_significance: str = Field(..., alias="dor_z")
    motion_affecting_factors: List[str] = Field(..., alias="factor")
    house: Optional[str] = None
    street_category: str = Field(..., alias="k_ul")
    km: str
    m: str
    settlement: str = Field(..., alias="n_p")
    road_deficiency: List[str] = Field(..., alias="ndu")
    light_conditions: str = Field(..., alias="osv")
    s_dtp: str
    road_conditions: str = Field(..., alias="s_pch")
    weather: List[str] = Field(..., alias="s_pog")
    onsite_crash_road_objects: List[str] = Field(..., alias="sdor")
    street: str
    vehicle_info: List[VehicleInfo] = Field(..., alias="ts_info")
    participant_info: List[ParticipantInfo] = Field(..., alias="uchInfo")


class CrashCard(BaseModel):
    id: int = Field(..., alias="KartId")

    crash_type: str = Field(..., alias="DTP_V")
    District: str
    vehicles_amount: int = Field(..., alias="K_TS")
    participants_amount: int = Field(..., alias="K_UCH")
    deceased: int = Field(..., alias="POG")
    wounded: int = Field(..., alias="RAN")
    date: str
    Time: time
    crash_info: CrashInfo = Field(..., alias="infoDtp")
    row: int = Field(..., alias="rowNum")


class CrashDataResponse(BaseModel):
    region_name: str = Field(..., alias="RegName")
    cards_amount: int = Field(..., alias="countCard")
    datename: Optional[str] = None
    end: int
    pokName: str
    posl: str
    wounded: int = Field(..., alias="ran")
    deceased: int = Field(..., alias="pog")
    start: int
    crashes: List[CrashCard] = Field(..., alias="tab")
