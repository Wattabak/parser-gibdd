import pytest
from requests import Request

from parser_gibdd.api.gibdd_api import GibddAPI
from parser_gibdd.models.gibdd.requests import GibddMainMapData, GibddDateListString, GibddDateString, GibddDTPCardData, \
    DtpCardDataOrder


@pytest.fixture()
def gibdd_api():
    return GibddAPI(host='http://stat.gibdd.ru')


def test_gibdd_api():
    pass


def test_request_main_map_data(gibdd_api: GibddAPI):
    request_data = GibddMainMapData(
        maptype=1,
        region='877',
        date=GibddDateListString.from_date_string(GibddDateString.from_year_month(2021, 1)),
        pok='1'
    )
    request = gibdd_api.request_main_map_data(request_data=request_data)
    assert isinstance(request, Request)
    assert request_data.dict() == request.json
    assert gibdd_api.host + '/map/getMainMapData' == request.url


def test_request_dtp_card_data(gibdd_api: GibddAPI):
    request_data = GibddDTPCardData(
        date=[GibddDateString.from_year_month(2021, m) for m in range(1, 6 + 1)],
        ParReg=1,
        order=DtpCardDataOrder(type=1, fieldName='dat'),
        reg=str(1),
        ind='1',
        st=str(0),
        en=str(50)
    )
    request = gibdd_api.request_dtp_card_data(request_data=request_data)
    assert isinstance(request, Request)
    assert request_data.to_request_form() == request.json
    assert gibdd_api.host + '/map/getDTPCardData' == request.url
