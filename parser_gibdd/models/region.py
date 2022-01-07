import logging
from typing import Optional, List, Union

from fuzzywuzzy import fuzz
from pydantic import BaseModel

from parser_gibdd.exceptions import RegionNotFoundError

logger = logging.getLogger(__name__)


class RegionName(str):
    pass


class FederalRegionName(str):
    pass


class Region(BaseModel):
    name: str
    okato: Optional[str] = None


class FederalRegion(Region):
    districts: List[Region] = []


class Country(Region):
    regions: List[FederalRegion] = []
    name = "Российская Федерация"
    okato = "877"

    def get_region(self, okato: str, federal: bool = False) -> Union[Region, FederalRegion]:
        for region in self.regions:
            if region.okato == okato:
                return region
            if federal:
                return None
            for subregion in region.districts:
                if subregion.okato == okato:
                    return subregion
        return None

    def find_region(self, region_name: str) -> List[Region]:
        found_regions: List[Region] = []
        for region in self.regions:
            if fuzz.partial_ratio(region.name, region_name) > 90:
                found_regions.append(region)

            for inner in region.districts:
                if fuzz.partial_ratio(inner.name, region_name) > 90:
                    found_regions.append(inner)
        return found_regions

    def get_parent_region(self, region: Region) -> FederalRegion:
        for federal in self.regions:

            if federal.okato == region.okato:
                return federal
            if region.okato in [inner.okato for inner in federal.districts]:
                return federal
        raise RegionNotFoundError(f"Region {region.name} not found in {self.name}")
