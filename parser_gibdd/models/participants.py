from enum import Enum
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ParticipantType(str, Enum):
    DRIVER = 'driver'
    PASSENGER = 'passenger'


class Participant(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    participant_type: ParticipantType

    alcohol_level: str
    amount: str
    gender: str
    direct_violations: List[str]
    N_UCH: str
    supplemental_violations: List[str]
    left_crash_site: str
    injury_severity: str
    driver_experience: str

    driver_ingured_card_id: str
    driver_safety_belt: str
    driver_s_seat_group: str
