import uuid
from typing import Optional

import pandas as pd


def crash_to_excel(crash: pd.DataFrame, filename: Optional[str] = None) -> None:
    if not filename:
        filename = str(uuid.uuid4())
    crash.to_excel(f"{filename}.xlsx")
