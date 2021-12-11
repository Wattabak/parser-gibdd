import logging
from typing import List

from parser_gibdd.models.gibdd.okato import RegionDataResponse
from models.region import Region, FederalRegion

logger = logging.getLogger(__name__)


def parse_inner_okato(response: RegionDataResponse) -> List[Region]:
    """Get a mapping of code-name for the municipalities in the particular federal region"""
    return [
        Region(okato=reg.id, name=reg.name)
        for reg in response.metabase[0].maps
    ]


def parse_federal_okato(response: RegionDataResponse) -> List[FederalRegion]:
    """Returns the mapping region code-name"""

    return [
        FederalRegion(okato=reg.id, name=reg.name)
        for reg in response.metabase[0].maps
    ]
