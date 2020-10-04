import json
import logging
from typing import List

import pandas as pd
from requests import Response

from models.crash import CrashDataResponse
from models.region import Region, FederalRegion

logger = logging.getLogger(__name__)


def parse_crash_cards(data: CrashDataResponse) -> pd.DataFrame:
    """Structure the raw data in responses"""
    parsed = []
    for card in data.tab:
        processed_card = {}

        processed_card.update(**card.dict(exclude={'crash_info'}),
                              **card.crash_info.dict(exclude={"vehicle_info", "participant_info"}))
        parsed.append(processed_card)
    logger.info(f"Region {data.region_name} successfully parsed")
    df = pd.DataFrame.from_dict(parsed)
    return df


def parse_inner_okato(response: Response) -> List[Region]:
    """Get a mapping of code-name for the municipalities in the particular federal region"""
    d = response.json()
    regions_dict = json.loads(
        json.loads(d["metabase"])[0]["maps"]
    )
    return [
        Region(okato=reg['id'], name=reg['name'])
        for reg in regions_dict
    ]


def parse_federal_okato(response: Response) -> List[FederalRegion]:
    """Returns the mapping region code-name"""
    d = response.json()
    regions_dict = json.loads(
        json.loads(d["metabase"])[0]["maps"]
    )
    return [
        FederalRegion(okato=reg['id'], name=reg['name'])
        for reg in regions_dict
    ]
