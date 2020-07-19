import json
from typing import List

import pandas as pd
from requests import Response

from models.region import Region, FederalRegion


def parse_crash_cards(response: Response) -> pd.DataFrame:
    parsed = json.loads(response.json()['data'])
    region = parsed['RegName']
    cards = parsed['tab']

    PROCESSED_CARDS = []
    for card in cards:
        processed_card = {}
        info = card.pop("infoDtp") if "infoDtp" in card.keys() else {}
        ts_info = info.pop("ts_info") if info else {}
        uchInfo = info.pop("uchInfo") if info else []
        processed_card.update(**card, **info)
        PROCESSED_CARDS.append(processed_card)

    df = pd.DataFrame.from_dict(*PROCESSED_CARDS)
    return df.rename(columns={
        "KartId": "id",
        "rowNum": "row",
        "DTP_V": "crash_type",
        "POG": "deceased",
        "RAN": "wounded",
        "K_TS": "vehicles",
        "K_UCH": "participants",
        "ndu": "road_deficiency",
        "s_pog": "weather",
        "osv": "light_conditions",
        "s_pch": "road_conditions",
        "n_p": "settlement",
        "dor": "main_road",
        "dor_k": "road_category",
        "dor_z": "road_significance",
        "k_ul": "street_category",
        "sdor": "onsite_crash_road_objects",
        "COORD_W": "latitude",
        "COORD_L": "longitude",
    })


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
