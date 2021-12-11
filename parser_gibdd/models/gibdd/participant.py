from typing import List

from pydantic import BaseModel, Field


class PersonInfo(BaseModel):
    alcohol_level: str = Field(..., alias="ALCO")
    amount: str = Field(..., alias="K_UCH")
    gender: str = Field(..., alias="POL")
    direct_violations: List[str] = Field(..., alias="NPDD")
    N_UCH: str = Field(..., alias="N_UCH")
    supplemental_violations: List[str] = Field(..., alias="SOP_NPDD")
    left_crash_site: str = Field(..., alias="S_SM")
    injury_severity: str = Field(..., alias="S_T")
    driver_experience: str = Field(..., alias="V_ST")


class DriverInfo(PersonInfo):
    INJURED_CARD_ID: str
    SAFETY_BELT: str
    S_SEAT_GROUP: str


class ParticipantInfo(PersonInfo):
    pass
