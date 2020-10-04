from typing import List, Any

from pydantic import BaseModel, Field


class VehicleInfo(BaseModel):
    color: str
    property_form: str = Field(..., alias="f_sob")
    g_v: str
    m_pov: str
    m_ts: str
    marka_ts: str
    n_ts: str
    o_pf: str
    r_rul: str
    t_n: str
    t_ts: str
    ts_s: str
    ts_uch: List[Any]
