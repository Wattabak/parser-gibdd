import json
from typing import Dict, Any

import pandas as pd


def parse_crash_cards(response: Dict[str, Any]) -> pd.DataFrame:
    parsed = json.loads(response.json()['data'])
    region = parsed['RegName']
    cards = parsed['tab']

    PROCESSED_CARDS = []
    for card in cards:
        processed_card = {}
        info = card.pop("infoDtp") if "infoDtp" in card.keys() else {}
        ts_info = info.pop("ts_info") if info else {}
        uchInfo = info.pop("uchInfo") if info else []
        processed_card.update(**card, **info, )
        PROCESSED_CARDS.append(processed_card)

    df = pd.DataFrame.from_dict(PROCESSED_CARDS)
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