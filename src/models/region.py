from typing import List, Optional

from pydantic import BaseModel


class Region(BaseModel):
    name: str
    okato: Optional[str] = None


class FederalRegion(Region):
    districts: List[Region] = []


class Country(BaseModel):
    regions: List[FederalRegion] = []
