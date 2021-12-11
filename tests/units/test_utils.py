from datetime import datetime
from unittest import mock

from parser_gibdd import utils


def test_latest_yearmonth(test_date, expected_result):
    with mock.patch('parser_gibdd.utils.datetime', return_value=datetime.date(2014, 6, 2)):
        year, month = utils.latest_yearmonth()
        assert expected_result == year, month
