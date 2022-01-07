import concurrent.futures
import logging
from datetime import date
from functools import partial
from typing import Tuple, List, Dict, Union

from parser_gibdd.api.gibdd_api import GibddAPI, DtpCardDataResponseHandler
from parser_gibdd.exceptions import CrashesNotFoundError
from parser_gibdd.models.gibdd.crash import CrashDataResponse
from parser_gibdd.models.gibdd.requests import GibddDTPCardData, GibddDateString, DtpCardDataOrder
from parser_gibdd.models.region import FederalRegion, Country
from parser_gibdd.models.region import RegionName, FederalRegionName

logger = logging.getLogger(__name__)


def subregion_timeframe_crashes_amount(region: Union[str, int],
                                       subregion: Union[str, int],
                                       year: int,
                                       months: Tuple[int, int] = (1, 12),
                                       cards: Tuple[int, int] = (0, 50)) -> CrashDataResponse:
    """Returns the required amount of crash data

    Parameters
    ----------
    region : int
        OKATO code of the region to parse
    subregion : int
        OKATO code of the subregion to parse
    year : int
        year to query the request to
    months: Tuple[int, int]
        range of months to request data from
    cards : Tuple[int, int]
        range of cards to retrieve
    """
    first, last = months
    request_data = GibddDTPCardData(
        date=[GibddDateString.from_year_month(year, m) for m in range(first, last + 1)],
        ParReg=str(region),
        order=DtpCardDataOrder(type=1, fieldName='dat'),
        reg=str(subregion),
        ind='1',
        st=str(cards[0]),
        en=str(cards[1])
    )
    with GibddAPI("http://stat.gibdd.ru/") as api:
        request = api.request_dtp_card_data(request_data)
        response = api.send_request(request)
        parsed_response = DtpCardDataResponseHandler(response).parse()
    return parsed_response


def subregion_timeframe_crashes_all(
        region: Union[str, int],
        subregion: Union[str, int],
        year: int,
        months: Tuple[int, int] = (1, 12), ) -> List[CrashDataResponse]:
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
        region: Union[str, int],
        subregion: Union[str, int],
        year: int,
        months: Tuple[int, int] = (1, 12),
) -> List[CrashDataResponse]:
    """ALL crash data in a given timeframe for a subregion, except with two large requests

    There is a count of cards for a given subregion in every request,
    so we get this number with one request and then send a single other request with the specified number of cards
    """
    crashes = []
    try:
        initial_request = subregion_timeframe_crashes_amount(
            region=region,
            subregion=subregion,
            year=year,
            months=months,
            cards=(0, 1)
        )
        all_crashes = subregion_timeframe_crashes_amount(
            region=region,
            subregion=subregion,
            year=year,
            months=months,
            cards=(0, initial_request.cards_amount)
        )
        crashes.append(all_crashes)
    except CrashesNotFoundError:
        pass
    logger.info(f"Data for subregion {subregion} in region {region} collected")
    return crashes


def subregion_crashes(region: Union[str, int],
                      subregion: Union[str, int],
                      period_start: date,
                      period_end: date) -> List[CrashDataResponse]:
    """Get all crashes between two given dates"""
    st_year, st_month = period_start.year, period_start.month
    end_year, end_month = period_end.year, period_end.month

    logger.info(f"retrieving crashes for:\nregion: {region},\nsubregion: {subregion}")
    if st_year == end_year:
        return subregion_timeframe_crashes_all_noloop(
            region, subregion, year=st_year, months=(st_month, end_month)
        )

    crashes_first_year = subregion_timeframe_crashes_all_noloop(
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
    return [*crashes_first_year,
            *crashes_last_year,
            *crashes_inbetween]


def region_crashes_all(region: FederalRegion,
                       period_start: date,
                       period_end: date) -> Dict[RegionName, List[CrashDataResponse]]:
    """Get all crashes in a given federal region"""
    crashes: Dict[RegionName, List[CrashDataResponse]] = {}
    if not region.okato:
        raise Exception(
            f"No okato code for federal region: {region.name}, update the cache for federal regions"
        )
    for subregion in region.districts:
        if not subregion.okato:
            raise Exception(
                f"No okato code for municipal region: {subregion.name}, update the cache for federal regions"
            )
        crashes[subregion.name] = subregion_crashes(
            region=region.okato,
            subregion=subregion.okato,
            period_start=period_start,
            period_end=period_end
        )
    return crashes


def region_crashes_all_threading(region: FederalRegion,
                                 period_start: date,
                                 period_end: date) -> Dict[RegionName, List[CrashDataResponse]]:
    if not region.okato:
        raise Exception(
            f"No okato code for federal region: {region.name}, update the cache for federal regions"
        )
    concrete_subregion_crashes = partial(subregion_crashes, region=region.okato, period_start=period_start,
                                         period_end=period_end)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        result = executor.map(
            lambda x: (x.name, concrete_subregion_crashes(subregion=x.okato)), region.districts
        )
    return {name: crash_data for name, crash_data in result}


def country_crashes_all(country: Country,
                        period_start: date,
                        period_end: date) -> List[Dict[RegionName, List[CrashDataResponse]]]:
    """
    Get all crashes in Russia

    TODO: probably could use some optimizations, it will be at least a thousand requests
    """
    crashes: List[Dict[RegionName, List[CrashDataResponse]]] = []
    for fed in country.regions:
        crashes.append(region_crashes_all(
            region=fed,
            period_start=period_start,
            period_end=period_end
        ))
    return crashes


country_return_type = Dict[FederalRegionName, Dict[RegionName, List[CrashDataResponse]]]


def country_crashes_all_threading(country: Country,
                                  period_start: date,
                                  period_end: date
                                  ) -> country_return_type:
    return {
        fed.name: region_crashes_all_threading(
            region=fed,
            period_start=period_start,
            period_end=period_end
        )
        for fed in country.regions
    }
    # with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
    #     result = executor.map(
    #         lambda x: (x.name, region_crashes_all_threading(region=x,
    #                                                         period_start=period_start,
    #                                                         period_end=period_end)), country.regions
    #     )
    # return {name: data for name, data in result}
