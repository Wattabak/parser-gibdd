import logging
from datetime import date
from itertools import chain
from json import dumps, JSONDecodeError, loads
from typing import Tuple, List

from requests import Response, Session
from requests.adapters import HTTPAdapter

from models.region import FederalRegion, Country

logger = logging.getLogger(__name__)


class CrashesNotFoundError(Exception):
    pass


def subregion_timeframe_crashes_amount(region: int,
                                       subregion: int,
                                       year: int,
                                       months: Tuple[int, int] = (1, 12),
                                       cards: Tuple[int, int] = (0, 50),
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
    first, last = months
    data = {
        "date": [f"MONTHS:{m}.{year}" for m in range(first, last + 1)],
        "ParReg": str(region),
        'order': {
            "type": 1, "fieldName": 'dat'
        },
        "reg": str(subregion),
        'ind': '1',
        'st': str(cards[0]),
        'en': str(cards[1])
    }

    data = dumps(
        data, separators=(',', ':')
    ).encode('utf8').decode("unicode-escape")

    try:
        session = Session()
        session.mount("http://stat.gibdd.ru/", HTTPAdapter(max_retries=5))
        response = session.post("http://stat.gibdd.ru/map/getDTPCardData", json={"data": data}, )
        response.json()
    except JSONDecodeError:
        logger.info("No data found with the specified options, check your inputs or continue")
        raise CrashesNotFoundError
    except (ConnectionError, TimeoutError) as e:
        logger.exception(f"unable to reach api endpoint, error: {e}")
    else:
        return response


def subregion_timeframe_crashes_all(
        region: int,
        subregion: int,
        year: int,
        months: Tuple[int, int] = (1, 12), ) -> List[Response]:
    """ALL crash data in a given timeframe for a subregion"""
    all_crashes = []
    crashes_collected = False
    while not crashes_collected:
        try:
            left_interval, right_interval = (0, 50)
            crash = subregion_timeframe_crashes_amount(
                region=region,
                subregion=subregion,
                year=year,
                months=months,
                cards=(left_interval, right_interval)
            )
            all_crashes.append(crash)
        except CrashesNotFoundError:
            crashes_collected = True
        else:
            left_interval += 50
            right_interval += 50
    logger.info(f"Data for subregion {subregion} in region {region} collected")
    return all_crashes


def subregion_timeframe_crashes_all_noloop(
        region: int,
        subregion: int,
        year: int,
        months: Tuple[int, int] = (1, 12),
) -> List[Response]:
    """ALL crash data in a given timeframe for a subregion, except with two large requests

    There is a count of cards for a given subregion in every request,
    so we get this number with one request and then send a single other request with the specified number of cards
    """
    initial_request = subregion_timeframe_crashes_amount(
        region=region,
        subregion=subregion,
        year=year,
        months=months,
        cards=(0, 1)
    )
    required_requests = loads(initial_request.json()["data"])["countCard"]
    all_crashes = subregion_timeframe_crashes_amount(
        region=region,
        subregion=subregion,
        year=year,
        months=months,
        cards=(0, required_requests)
    )

    logger.info(f"Data for subregion {subregion} in region {region} collected")
    return [all_crashes]


def subregion_crashes(region: int, subregion: int, period_start: date, period_end: date):
    """Get all crashes between two given dates"""
    st_year, st_month = period_start.year, period_start.month
    end_year, end_month = period_end.year, period_end.month

    crashes_fisrt_year = subregion_timeframe_crashes_all_noloop(
        region, subregion, year=st_year, months=(st_month, 12 - st_month)
    )
    crashes_last_year = subregion_timeframe_crashes_all_noloop(
        region, subregion, year=end_year, months=(1, end_month)
    )
    crashes_inbetween = []
    while st_year + 1 != end_year:
        st_year += 1
        crashes_inbetween.extend(subregion_timeframe_crashes_all_noloop(
            region, subregion, year=st_year, months=(1, 12)
        ))
    return chain(crashes_fisrt_year, crashes_last_year, crashes_inbetween)


def region_crashes_all(region: FederalRegion,
                       period_start: date,
                       period_end: date):
    """Get all crashes in a given federal region"""
    crashes = []
    for subregion in region.districts:
        crashes.extend(subregion_crashes(
            region=int(region.okato),
            subregion=int(subregion.okato),
            period_start=period_start,
            period_end=period_end
        ))
    return crashes


def country_crashes_all(country: Country,
                        period_start: date,
                        period_end: date):
    """
    Get all crashes in Russia

    TODO: probably could use some optimizations, it will be at least a thousand requests
    """
    crashes = []
    for fed in country.regions:
        crashes.extend(region_crashes_all(
            region=fed,
            period_start=period_start,
            period_end=period_end
        ))
    return crashes
