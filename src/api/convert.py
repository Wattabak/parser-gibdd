import uuid
from typing import Optional

import pandas as pd

from src.api.parsers import logger
from src.models.gibdd.crash import CrashDataResponse


def crash_to_excel(crash: pd.DataFrame, filename: Optional[str] = None) -> None:
    if not filename:
        filename = f'{crash["region_name"][0]}'
    crash.to_excel(f"{filename}.xlsx")


def crash_data_single_dataframe(data: CrashDataResponse) -> pd.DataFrame:
    """Structure the raw data in responses"""
    parsed = []
    for card in data.crashes:
        processed_card = {}

        processed_card.update(**card.dict(exclude={'crash_info'}),
                              **card.crash_info.dict(exclude={"vehicle_info", "participant_info"}))
        parsed.append(processed_card)
    logger.info(f"Region {data.region_name} successfully parsed")
    df = pd.DataFrame.from_dict(parsed)
    df["region_name"] = [data.region_name] * len(df)
    return df
