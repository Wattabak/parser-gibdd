import zipfile
from io import BytesIO
from typing import Optional, List, Dict, Any, Tuple

from pandas import DataFrame, ExcelWriter

from src.api.parsers import logger
from src.models.gibdd.crash import CrashDataResponse
from src.models.region import RegionName, FederalRegionName


def crash_to_excel(crash: DataFrame, filename: Optional[str] = None) -> None:
    if not filename:
        filename = f'{crash["region_name"][0]}'
    crash.to_excel(f"{filename}.xlsx")


def crash_data_single_dataframe(data: CrashDataResponse) -> DataFrame:
    """Structure the raw data in responses"""
    parsed = []
    for card in data.crashes:
        processed_card: Dict[str, Any] = {}

        processed_card.update(**card.dict(exclude={'crash_info'}),
                              **card.crash_info.dict(exclude={"vehicle_info", "participant_info"}))
        parsed.append(processed_card)
    logger.info(f"Region {data.region_name} successfully parsed")
    df = DataFrame(parsed)
    df["region_name"] = [data.region_name] * len(df)
    return df


def crash_to_dataframes(data: CrashDataResponse) -> Tuple[DataFrame, DataFrame, DataFrame]:
    crashes, vehicles, participants = [], [], []
    for card in data.crashes:
        crashes.append({**card.dict(exclude={'crash_info'}),
                        **card.crash_info.dict(exclude={"vehicle_info", "participant_info"}),
                        **{"region_name": data.region_name}
                        })

        vehicles.extend([
            {**veh.dict(exclude={"driver_info"}), **{"crash_id": card.id}}
            for veh in card.crash_info.vehicle_info
        ])
        participants.extend([
            {**participant.dict(), **{"crash_id": card.id}}
            for participant in card.crash_info.participant_info
        ])
        participants.extend([
            {**driver.dict(), **{"crash_id": card.id}}
            for veh in card.crash_info.vehicle_info
            for driver in veh.drivers_info
        ])
    logger.info(f"Region {data.region_name} successfully parsed")
    return DataFrame(crashes), DataFrame(vehicles), DataFrame(participants)


def package_crashes_subregion(crashes: List[CrashDataResponse],
                              filename: Optional[str] = None,
                              to_archive=False) -> None:
    """

    """
    if not filename:
        filename = f"{crashes[0].region_name}"
    with zipfile.ZipFile(f"{filename}.zip", "w") as archive:
        for crash in crashes:
            parsed_crashes, vehicles, participants = crash_to_dataframes(crash)
            excel_memory = BytesIO()
            with ExcelWriter(excel_memory) as writer:  # type: ignore
                parsed_crashes.to_excel(writer, sheet_name="crashes")
                vehicles.to_excel(writer, sheet_name="vehicles")
                participants.to_excel(writer, sheet_name="participants")
            excel_memory.seek(0)
            archive.writestr(f"{filename}_{crash.crashes[0].date[-4:]}.xlsx", excel_memory.read())


def package_crashes_fed_region(federal_data: Dict[str, List[CrashDataResponse]], federal_region: str):
    with zipfile.ZipFile(f"{federal_region}.zip", "w") as archive:
        for municipal, crashes in federal_data.items():
            for crash in crashes:
                parsed_crashes, vehicles, participants = crash_to_dataframes(crash)
                excel_memory = BytesIO()
                with ExcelWriter(excel_memory) as writer:
                    parsed_crashes.to_excel(writer, sheet_name="crashes")
                    vehicles.to_excel(writer, sheet_name="vehicles")
                    participants.to_excel(writer, sheet_name="participants")
                excel_memory.seek(0)
                archive.writestr(f"{municipal}/_{crash.crashes[0].date[-4:]}.xlsx", excel_memory.read())


country_return_type = Dict[FederalRegionName, Dict[RegionName, List[CrashDataResponse]]]


def package_crashes_country(country_data: country_return_type):
    with zipfile.ZipFile(f"Российская Федерация.zip", "w") as archive:
        for federal_name, federal_region in country_data:
            for municipal, crashes in federal_region.items():
                for crash in crashes:
                    parsed_crashes, vehicles, participants = crash_to_dataframes(crash)
                    excel_memory = BytesIO()
                    with ExcelWriter(excel_memory) as writer:
                        parsed_crashes.to_excel(writer, sheet_name="crashes")
                        vehicles.to_excel(writer, sheet_name="vehicles")
                        participants.to_excel(writer, sheet_name="participants")
                    excel_memory.seek(0)
                    archive.writestr(f"{federal_name}/{municipal}/{crash.crashes[0].date[-4:]}.xlsx",
                                     excel_memory.read())
