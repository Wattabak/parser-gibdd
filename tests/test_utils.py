from datetime import datetime
from unittest import mock

import pytest

from parser_gibdd.library import utils


@pytest.fixture()
def test_dates():
    return [
        (datetime(2014, 6, 2), (2014, 6)),
        (datetime(2021, 1, 1), (2020, 12))
    ]


def test_latest_yearmonth(test_dates):
    for test_date, expected_result in test_dates:
        with mock.patch('parser_gibdd.utils.datetime', return_value=test_date):
            year, month = utils.latest_yearmonth()
            assert year, month == expected_result
