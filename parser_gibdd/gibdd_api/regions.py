import logging
from typing import List
from warnings import warn

from parser_gibdd.gibdd_api.request_handlers import request_all_federal_okato, request_inner_okato
from parser_gibdd.gibdd_api.parsers import parse_federal_okato, parse_inner_okato
from parser_gibdd.library.exceptions import RegionNotFoundError
from parser_gibdd.models.region import FederalRegion, Country

logger = logging.getLogger(__name__)


def get_federal_regions() -> List[FederalRegion]:
    """Returns only high level federal regions, no inner data"""
    unprocessed = request_all_federal_okato()
    return parse_federal_okato(unprocessed)


def get_municipalities_by_federal(region: FederalRegion) -> FederalRegion:
    """Получаем все окато регионов входящих в запрашиваемый федеральный округ"""
    unprocessed = request_inner_okato(region.okato)
    districts = parse_inner_okato(unprocessed)
    return FederalRegion(okato=region.okato,
                         name=region.name,
                         districts=districts
                         )


def get_country_codes() -> Country:
    """Returns all federal regions and their subregions with okato codes"""
    all_codes = Country()
    try:
        fed_regions = get_federal_regions()
    except Exception as e:
        logger.exception(e)
        raise RegionNotFoundError(e)
    for region in fed_regions:
        try:
            full_region = get_municipalities_by_federal(region)
        except Exception as e:
            logger.warning(e)
            warn(f'The data for region {region.name} could not be found, '
                 f'that may result in an incomplete dataset')
            continue
        all_codes.regions.append(
            full_region
        )
    return all_codes
