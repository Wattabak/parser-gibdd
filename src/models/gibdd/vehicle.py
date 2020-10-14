from typing import List

from pydantic import BaseModel, Field

from src.models.gibdd.participant import DriverInfo


class VehicleInfo(BaseModel):
    color: str
    property_form: str = Field(..., alias="f_sob")
    issued_year: str = Field(..., alias="g_v")
    damage_points: str = Field(..., alias="m_pov")
    car_model: str = Field(..., alias="m_ts")
    car_brand: str = Field(..., alias="marka_ts")
    vehicle_amount: str = Field(..., alias="n_ts")
    o_pf: str = Field(..., alias="o_pf")
    r_rul: str = Field(..., alias="r_rul")
    technical_defects: str = Field(..., alias="t_n")
    vehicle_type: str = Field(..., alias="t_ts")
    left_crash_site: str = Field(..., alias="ts_s")
    drivers_info: List[DriverInfo] = Field(..., alias="ts_uch")
