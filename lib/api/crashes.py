import json
from typing import Tuple

from requests import Response, post


def subregion_timeframe_crashes_amount(region: int,
                                       subregion: int,
                                       year: int,
                                       months: Tuple[int, int] = (1, 12),
                                       cards: Tuple[int, int] = (1, 20),
                                       ) -> Response:
    """Returns the required amount of crash data

    Parameters
    ----------
    region : int
        OKATO code of the region to parse
    subregion : int
        OKATO code of the subregion to parse
    year : int
        _
    months: Tuple[int, int]
        range of months to request data from
    cards : Tuple[int, int]
        range of cards to retrieve
    Returns
    -------
    Response
        object of the response
    """
    data = {
        "date": [f"MONTHS:{m}.{year}" for m in range(*months)],
        "ParReg": region,
        'order': {
            "type": 1, "fieldName": 'dat'
        },
        "reg": subregion,
        'ind': '1',
        'st': cards[0],
        'en': cards[1]
    }

    data = json.dumps(
        data, separators=(',', ':')
    ).encode('utf8').decode("unicode-escape")

    response = post("http://stat.gibdd.ru/map/getDTPCardData",
                    json={"data": data}
                    )
    if response.ok:
        return response


def subregion_timeframe_crashes_all(
        region: int,
        subregion: int,
        year: int,
        months: Tuple[int, int] = (1, 12), ):
    """ALL crash data in a given timeframe for a subregion"""
    try:
        subregion_timeframe_crashes_amount()
    except Exception as e:
        pass


def subregion_crashes_all():
    pass


def region_crashes_all():
    pass


def country_crashes_all():
    pass
