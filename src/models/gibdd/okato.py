from typing import List

from pydantic import BaseModel, Field


class RegionMapInfo(BaseModel):
    id: int
    name: str
    path: str


class RegionMapData(BaseModel):
    maps: List[RegionMapInfo]
    separator: str


class MapMetaData(BaseModel):
    pass


class RegionMetaData(BaseModel):
    MapChart: MapMetaData


class RegionDataResponse(BaseModel):
    metabase: List[RegionMapData]
    data: RegionMetaData
    region: str = Field(..., alias="regionname")
