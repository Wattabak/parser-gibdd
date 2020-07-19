from typing import List, Optional

import attr


@attr.s(auto_attribs=True)
class Region:
    name: str
    okato: Optional[str] = None


@attr.s(auto_attribs=True)
class FederalRegion(Region):
    districts: List[Region] = []


@attr.s(auto_attribs=True)
class Country:
    regions: List[FederalRegion] = []
