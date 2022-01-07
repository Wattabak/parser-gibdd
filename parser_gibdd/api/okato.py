import logging

from parser_gibdd.api.gibdd_api import GibddAPI, MapDataResponseHandler
from parser_gibdd.models.gibdd.okato import RegionDataResponse
from parser_gibdd.models.gibdd.requests import GibddMainMapData, GibddDateString, GibddDateListString
from parser_gibdd.utils import latest_yearmonth

logger = logging.getLogger(__name__)


def request_all_federal_okato() -> RegionDataResponse:
    """Get okato codes for all federal regions

    Only one request, efficient
    """
    request_data = GibddMainMapData(
        maptype=1,
        region='877',
        date=GibddDateListString.from_date_string(GibddDateString.from_year_month(*latest_yearmonth())),
        pok='1'
    )
    with GibddAPI("http://stat.gibdd.ru/") as api:
        request = api.request_main_map_data(request_data)
        response = api.send_request(request)
        parsed_response = MapDataResponseHandler(response).parse()
    return parsed_response


def request_inner_okato(region_code: str) -> RegionDataResponse:
    """Get okato codes for the municipalities in the federal region

    Parameters
    ----------
    region_code : str
        OKATO of the region to query
    """
    request_data = GibddMainMapData(
        maptype=1,
        region=region_code,
        date=GibddDateListString.from_date_string(GibddDateString.from_year_month(*latest_yearmonth())),
        pok='1'
    )
    with GibddAPI("http://stat.gibdd.ru/") as api:
        request = api.request_main_map_data(request_data)
        response = api.send_request(request)
        parsed_response = MapDataResponseHandler(response).parse()
    return parsed_response
