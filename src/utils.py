from datetime import datetime
from typing import Tuple


def latest_yearmonth() -> Tuple[int, int]:
    """Get the latest valid year and month"""
    now = datetime.now()

    year = now.year
    month = now.month - 1
    if not month:
        year -= 1
        month = 12
    return year, month
