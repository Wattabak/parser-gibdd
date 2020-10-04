import uuid

import pandas as pd


def crash_to_excel(crash: pd.DataFrame, ) -> None:
    crash.to_excel(f"{uuid.uuid4()}.xlsx")
