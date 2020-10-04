import logging

from requests import Response, post

from lib.utils import latest_yearmonth

logger = logging.getLogger(__name__)


def request_all_federal_okato() -> Response:
    """Get okato codes for all federal regions

    """
    cur_year, cur_month = latest_yearmonth()

    r = post("http://stat.gibdd.ru/map/getMainMapData",
             json={
                 "maptype": 1,
                 "region": "877",  # код РФ
                 "date": f"[\"MONTHS:{cur_month}.{cur_year}\"]",
                 "pok": "1"
             })
    if not r.ok:
        raise Exception(f"Unable to get the current OKATO codes, {r.content}")
    logger.info("Successfully received current data on current OKATO codes")
    return r


def request_inner_okato(region_code: str) -> Response:
    """Get okato codes for the municipalities in the federal region

    Parameters
    ----------
    region_code : str
        OKATO of the region to query
    """
    year, month = latest_yearmonth()
    r = post("http://stat.gibdd.ru/map/getMainMapData", json={
        "maptype": 1,
        "date": f"[\"MONTHS:{month}.{year}\"]",
        "pok": "1",
        "region": region_code
    })
    if not r.ok:
        raise Exception(f"Unable to get okato codes for a region with code {region_code}")
    logger.info(f"Received the okato codes for a region with code {region_code}")
    return r
