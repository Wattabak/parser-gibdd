import logging
from typing import List

import pandas as pd

from src.models.gibdd.crash import CrashDataResponse
from src.models.gibdd.okato import RegionDataResponse
from src.models.gibdd.region import Region, FederalRegion

logger = logging.getLogger(__name__)


def parse_crash_cards(data: CrashDataResponse) -> pd.DataFrame:
    """Structure the raw data in responses"""
    parsed = []
    for card in data.crashes:
        processed_card = {}

        processed_card.update(**card.dict(exclude={'crash_info'}),
                              **card.crash_info.dict(exclude={"vehicle_info", "participant_info"}))
        parsed.append(processed_card)
    logger.info(f"Region {data.region_name} successfully parsed")
    df = pd.DataFrame.from_dict(parsed)
    return df


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
