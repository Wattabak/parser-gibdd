from typing import List

from pydantic import BaseModel


class PersonInfo(BaseModel):
    ALCO: str
    K_UCH: str
    POL: str
    NPDD: List[str]
    N_UCH: str
    SOP_NPDD: List[str]
    S_SM: str
    S_T: str
    V_ST: str


class DriverInfo(PersonInfo):
    INJURED_CARD_ID: str
    SAFETY_BELT: str
    S_SEAT_GROUP: str


class ParticipantInfo(PersonInfo):
    pass
