import logging
from datetime import date
from pathlib import Path
from typing import Optional, Tuple, Union, List

from parser_gibdd.gibdd_api.regions import get_country_codes
from parser_gibdd.gibdd_api import request_handlers
from parser_gibdd.models.gibdd.crash import CrashDataResponse
from parser_gibdd.models.region import Country, FederalRegion, Region


class CrashesRussiaDeclarativeInterface:
    def __init__(self,
                 okato_codes: Optional[Country], ):
        self._okato_codes = okato_codes

    @property
    def okato(self) -> Country:
        if not self._okato_codes:
            self._okato_codes = self.get_okato_codes()
        return self._okato_codes

    @staticmethod
    def get_okato_codes(local_path: Optional[Path] = None) -> Country:
        if local_path:
            with local_path.open("r") as raw:
                return Country.parse_raw(raw.read())
        return get_country_codes()

    def get_crashes_russia_region(self,
                                  date_start: date,
                                  date_end: date,
                                  region_code: int,
                                  ) -> Tuple[Union[Region, FederalRegion, None], List[CrashDataResponse]]:
        region = self.okato.get_region(str(region_code))
        if not region:
            logging.info(f"No region with code {region_code} found")
            return None, []
        elif isinstance(region, FederalRegion):
            crashes = request_handlers.region_crashes_all(region=region,
                                                          period_start=date_start,
                                                          period_end=date_end)
        else:
            parent = self.okato.get_parent_region(region)
            crashes = request_handlers.subregion_crashes(parent.okato, region, date_start, date_end)

        return region, crashes

    def get_crashes_russia_country(self,
                                   date_start: date,
                                   date_end: date, ):
        country_results = request_handlers.country_crashes_all_threading(self.okato,
                                                                         period_start=date_start,
                                                                         period_end=date_end)
        return country_results

    def get_crashes_amount(self,
                           date_start: date,
                           date_end: date,
                           region_code: int,
                           ):
        """Gets the amount of crashes happening in a region and in a date range"""
        region = self.okato.get_region(str(region_code))

        if not region:
            logging.info(f"No region with code {region_code} found")
            return None
        elif isinstance(region, FederalRegion):
            crashes = 0
            for subregion in region.districts:
                crashes += request_handlers.get_crashes_amount_subregion_date(
                    region=int(region.okato),
                    subregion=int(subregion.okato),
                    date_start=date_start,
                    date_end=date_end,
                )
            return crashes
        return request_handlers.get_crashes_amount_subregion_date(
            region=int(self.okato.get_parent_region(region).okato),
            subregion=int(region.okato),
            date_start=date_start,
            date_end=date_end,
        )
