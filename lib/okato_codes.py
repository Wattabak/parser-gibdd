import json
import logging
from datetime import datetime
from typing import Tuple, Dict, List, Any

from requests import Response, post


def latest_yearmonth() -> Tuple[int, int]:
    """Get the latest valid year and month"""
    now = datetime.now()

    year = now.year
    month = now.month - 1
    if not month:
        year -= 1
        month = 12
    return year, month


def req_federal_okato_codes() -> Response:
    """Get okato codes for all federal regions"""
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
    logging.info("Successfully received current data on current OKATO codes")
    return r


def parse_federal_okato(federal_response: Response) -> Dict[str, str]:
    """Returns the mapping region code-name"""
    d = federal_response.json()
    regions_dict = json.loads(
        json.loads(d["metabase"])[0]["maps"]
    )
    return {reg["id"]: reg["name"]
            for reg in regions_dict}


def req_municipalities_codes(region_code: str) -> Response:
    """Get okato codes for the municipalities in the federal region"""
    year, month = latest_yearmonth()
    r = post("http://stat.gibdd.ru/map/getMainMapData", json={
        "maptype": 1,
        "date": f"[\"MONTHS:{month}.{year}\"]",
        "pok": "1",
        "region": region_code
    })
    if not r.ok:
        raise Exception(f"Unable to get okato codes for a region with code {region_code}")
    logging.info(f"Received the okato codes for a region with code {region_code}")
    return r


def parse_municipality_okato(munic_response: Response) -> Dict[str, str]:
    """Get a mapping of code-name for the municipalities in the particular federal region"""
    d = munic_response.json()
    regions_dict = json.loads(
        json.loads(d["metabase"])[0]["maps"]
    )
    return {reg["id"]: reg["name"]
            for reg in regions_dict}


def country_okato_codes() -> List[Dict[str, Any]]:
    country_codes = []
    try:
        federal = req_federal_okato_codes()
        federal_okato = parse_federal_okato(federal)
    except Exception as e:
        return None
    for code, name in federal_okato.items():
        try:
            municipal = req_municipalities_codes(code)
            municipal_okato = parse_municipality_okato(municipal)
        except Exception as e:
            logging.exception(e)
            continue
        country_codes.append({"id": code, "name": name, "districts": municipal_okato})
    return country_codes


