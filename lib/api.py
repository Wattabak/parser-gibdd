import json
from typing import Tuple

from requests import Response, post


def request_crash_info(region: int,
                       subregion: int,
                       year: int,
                       months: Tuple[int, int] = (1, 12),
                       ) -> Response:
    """Returns the data from gibdd website 

    region: int
        OKATO code of the region to parse

    subregion: int
        OKATO code of the subregion to parse
    """
    data = {
        "date": [f"MONTHS:{m}.{year}" for m in range(months)],
        "ParReg": region,
        'order': {
            "type": 1, "fieldName": 'dat'
        },
        "reg": subregion,
        'ind': '1',
        'st': '1',
        'en': '20'
    }

    data = json.dumps(
        data, separators=(',', ':')
    ).encode('utf8').decode("unicode-escape")

    response = post("http://stat.gibdd.ru/map/getDTPCardData",
                    json={"data": data})
    if response.ok:
        return response


