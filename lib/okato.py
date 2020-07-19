import logging
from typing import List, Optional

from lib.api.okato import request_all_federal_okato, request_inner_okato
from lib.parsers import parse_federal_okato, parse_inner_okato
from models.region import FederalRegion, Country


def get_all_federal_okato() -> List[FederalRegion]:
    unprocessed = request_all_federal_okato()
    return parse_federal_okato(unprocessed)


def get_regions_inner_okato(region: FederalRegion) -> FederalRegion:
    unprocessed = request_inner_okato(region.okato)
    districts = parse_inner_okato(unprocessed)
    return FederalRegion(okato=region.okato,
                         name=region.name,
                         districts=districts
                         )


def all_okato_codes() -> Country:
    """Returns all federal regions and their subregions with okato codes"""
    all_codes = Country()
    try:
        fed_regions = get_all_federal_okato()
    except Exception:
        return all_codes
    for region in fed_regions:
        try:
            full_region = get_regions_inner_okato(region)
        except Exception as e:
            logging.exception(e)
            continue
        all_codes.regions.append(
            full_region
        )
    return all_codes
