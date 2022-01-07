from datetime import date
from typing import List

from pydantic import BaseModel, Field


class GibddDateString(str):
    string_format = 'MONTHS:%s.%s'

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """TODO: still need to implement validation"""
        if not isinstance(v, str):
            raise TypeError('string required')
        return cls(v)

    @classmethod
    def from_year_month(cls, year: int, month: int):
        return cls(
            f'MONTHS:{month}.{year}'
        )

    @classmethod
    def from_date(cls, _date: date):
        return cls(
            f'MONTHS:{_date.month}.{_date.year}'
        )


class GibddDateListString(str):
    """Very stupid structure but that is the easiest way to implement the website's structure

    """

    @classmethod
    def from_date_string(cls, datestring: GibddDateString):
        return cls(f'[\"{datestring}\"]')


class GibddMainMapData(BaseModel):
    maptype: int
    region: str = Field(description='The code of the queried region, be it a federal region or a municipality')
    date: GibddDateListString = Field(description='Month and year of the OKATO codes origin')
    pok: str


class DtpCardDataOrder(BaseModel):
    field_type: int = Field(alias='type')
    fieldName: str


class GibddDTPCardData(BaseModel):
    date: List[GibddDateString] = Field(description='All months and years for which the data needs to be retrieved')
    ParReg: str = Field(description='Code of the region, a.k.a the federal region to be retrieved')
    order: DtpCardDataOrder
    reg: str = Field(description='This is a code of the municipality (subregion) that is being queried')
    ind: str
    st: str = Field(description='First data point to get, the starting point')
    en: str = Field(description='Last data point to get, the end')

    def to_request_form(self):
        """Format that works with the website request"""
        return {"data": self.json(by_alias=True, separators=(',', ':'))}
