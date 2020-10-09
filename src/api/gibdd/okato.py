import logging
from pprint import pformat
from typing import List

from requests import Request, Response, Session
from requests.adapters import HTTPAdapter
from requests.exceptions import ChunkedEncodingError

from src.exceptions import ResourceUnreachable
from src.utils import latest_yearmonth
from src.models.okato import RegionDataResponse, RegionMapData

import json
logger = logging.getLogger(__name__)


def request_resource(requests: List[Request]) -> List[Response]:
    with Session() as session:
        session.mount("http://stat.gibdd.ru/", HTTPAdapter(max_retries=5))
        responses = []
        for request in requests:
            try:

                response = session.send(request)
            except (ConnectionError, TimeoutError, ChunkedEncodingError) as e:
                logger.exception(f"Unable to reach the requested resource, exception:\n {e}")
                raise ResourceUnreachable()
            if not response.ok:
                raise ResourceUnreachable(
                    "Unable to get the current OKATO codes:\n"
                    f"Status: {response.status_code}"
                    f"Response: {pformat(response.content)}"
                )
            responses.append(response)
    return responses


def request_all_federal_okato() -> RegionDataResponse:
    """Get okato codes for all federal regions

    Only one request, efficient
    """
    cur_year, cur_month = latest_yearmonth()
    try:
        with Session() as session:
            session.mount("http://stat.gibdd.ru/", HTTPAdapter(max_retries=5))
            response = session.post("http://stat.gibdd.ru/map/getMainMapData",
                                    json={
                                        "maptype": 1,
                                        "region": "877",  # код РФ
                                        "date": f"[\"MONTHS:{cur_month}.{cur_year}\"]",
                                        "pok": "1"
                                    })
    except (ConnectionError, TimeoutError, ChunkedEncodingError) as e:
        logger.exception(f"Unable to reach the requested resource, exception:\n {e}")
        raise ResourceUnreachable()
    if not response.ok:
        raise ResourceUnreachable(
            "Unable to get the current OKATO codes:\n"
            f"Status: {response.status_code}"
            f"Response: {pformat(response.content)}"
        )
    logger.info("Successfully received data on current OKATO codes")
    data = response.json()
    return RegionDataResponse(
        metabase=[
            RegionMapData(
                maps=json.loads(each["maps"]),
                separator=each["separator"]
            )
            for each in json.loads(data["metabase"])
        ],
        data=json.loads(data["data"]),
        regionname=data["regionname"]
    )


def request_inner_okato(region_code: str) -> RegionDataResponse:
    """Get okato codes for the municipalities in the federal region

    Parameters
    ----------
    region_code : str
        OKATO of the region to query
    """
    year, month = latest_yearmonth()
    try:
        with Session() as session:
            session.mount("http://stat.gibdd.ru/", HTTPAdapter(max_retries=5))
            response = session.post("http://stat.gibdd.ru/map/getMainMapData",
                                    json={
                                        "maptype": 1,
                                        "date": f"[\"MONTHS:{month}.{year}\"]",
                                        "pok": "1",
                                        "region": region_code
                                    })
    except (ConnectionError, TimeoutError, ChunkedEncodingError) as e:
        logger.exception(f"Unable to reach the requested resource, exception:\n region: {region_code}\n {e}")
        raise ResourceUnreachable()
    if not response.ok:
        raise ResourceUnreachable(
            f"Unable to get the OKATO codes for a region with code: {region_code}:\n"
            f"Status: {response.status_code}"
            f"Response: {pformat(response.content)}"
        )
    logger.info(f"Successfully received OKATO codes of region: {region_code}")
    data = response.json()
    return RegionDataResponse(
        metabase=[
            RegionMapData(
                maps=json.loads(each["maps"]),
                separator=each["separator"]
            )
            for each in json.loads(data["metabase"])
        ],
        data=json.loads(data["data"]),
        regionname=data["regionname"]
    )
