import logging
from typing import List

from parser_gibdd.models.gibdd.okato import RegionDataResponse
from parser_gibdd.models.region import Region, FederalRegion

logger = logging.getLogger(__name__)


def parse_inner_okato(response: RegionDataResponse) -> List[Region]:
    """Get a mapping of code-name for the municipalities in the particular federal region"""
    return [
        Region(okato=reg.id, name=reg.name)
        for reg in response.metabase[0].maps
    ]


def parse_federal_okato(response: RegionDataResponse) -> List[FederalRegion]:
    """An array of top regions in the hierarchy"""

    return [
        FederalRegion(okato=reg.id, name=reg.name)
        for reg in response.metabase[0].maps
    ]
