import abc
import json
from json.decoder import JSONDecodeError
from logging import getLogger
from pprint import pformat

from requests import Request, Session, Response
from requests.adapters import HTTPAdapter
from requests.exceptions import ChunkedEncodingError

from parser_gibdd.exceptions import ResourceUnreachable, ResourceRequestFailed, CrashesNotFoundError
from parser_gibdd.models.gibdd.crash import CrashDataResponse
from parser_gibdd.models.gibdd.okato import RegionDataResponse, RegionMapData
from parser_gibdd.models.gibdd.requests import GibddMainMapData, GibddDTPCardData

logger = getLogger(__name__)


class RequestHandler(abc.ABC):
    def __init__(self, response: Response):
        self.raw_response = response

    @abc.abstractmethod
    def parse(self):
        return self.raw_response.json()


class MapDataResponseHandler(RequestHandler):

    def parse(self) -> RegionDataResponse:
        data = self.raw_response.json()
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


class DtpCardDataResponseHandler(RequestHandler):

    def parse(self) -> CrashDataResponse:
        try:
            data = self.raw_response.json()
            return CrashDataResponse.parse_raw(self.raw_response.json()["data"])
        except (JSONDecodeError, ValueError):
            raise CrashesNotFoundError()


class GibddAPI:
    def __init__(self, host: str):
        self.host = host
        self.session = self.__create_session()

    def __create_session(self) -> Session:
        """Apply a custom adapter to handle retries"""
        s = Session()
        s.mount(self.host, HTTPAdapter(max_retries=5))
        return s

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        logger.exception(traceback)
        self.session.close()

    def request_main_map_data(self, request_data: GibddMainMapData) -> Request:
        """Request that is used to get region's OKATO codes from gibdd"""
        return Request(
            method='POST',
            url=f'{self.host}/map/getMainMapData',
            json=request_data.dict(),
        )

    def request_dtp_card_data(self, request_data: GibddDTPCardData) -> Request:
        """Get crash data from a region and timeframe"""
        return Request(
            method='POST',
            url=f'{self.host}/map/getDTPCardData',
            json=request_data.to_request_form(),
        )

    def send_request(self, request: Request) -> Response:
        try:
            request = self.session.prepare_request(request)
            response = self.session.send(request)
        except (ConnectionError, TimeoutError, ChunkedEncodingError) as e:
            raise ResourceUnreachable(f"Unable to reach the requested resource, exception:\n {e}")
        if not response.ok:
            raise ResourceRequestFailed(
                f"Request failed with status code {response.status_code}:\n"
                f"Response: {pformat(response.content)}"
            )
        logger.info('Request successful')

        return response
