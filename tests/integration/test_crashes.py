import unittest
from datetime import date

from lib.api.crashes import (
    subregion_timeframe_crashes_amount,
    subregion_timeframe_crashes_all_noloop,
    subregion_crashes
)
from lib.parsers import parse_crash_cards
from models.crash import CrashDataResponse


class TestCrashes(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_subregion_crashes(self) -> None:
        data = subregion_crashes(90, 90401, date(year=2019, month=1, day=1), date(year=2019, month=2, day=1))
        self.assertIsInstance(next(data), CrashDataResponse)

        parsed = [parse_crash_cards(crash) for crash in data]
        print(parsed)

    def test_subregion_timeframe_crashes_amount(self) -> None:
        data = subregion_timeframe_crashes_amount(region=90, subregion=90401, year=2019, months=(1, 2),
                                                  cards=(1, 20))

        self.assertIsInstance(data, CrashDataResponse)

    def test_subregion_timeframe_crashes_all_noloop(self) -> None:
        data = subregion_timeframe_crashes_all_noloop(region=90, subregion=90401, year=2019, months=(1, 2))
        self.assertIsInstance(data[0], CrashDataResponse)


if __name__ == "__main__":
    unittest.main()
