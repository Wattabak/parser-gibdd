from datetime import datetime
from typing import Tuple

__all__ = [
    'latest_yearmonth'
]


def latest_yearmonth() -> Tuple[int, int]:
    """Gets the latest year and month values. Latest means the month is already over

    If the current date is november 15 2021 then return (2021, 10), because the last complete month is october
    """
    now = datetime.now()

    year = now.year
    month = now.month - 1
    # if the current month is january get the december of last year
    if not month:
        year -= 1
        month = 12
    return year, month
