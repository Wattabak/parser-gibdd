import zipfile
from io import BytesIO
from pathlib import Path
from typing import Optional, List, Dict, Tuple

from pandas import DataFrame, ExcelWriter
from tablib import Dataset, Databook

from parser_gibdd.gibdd_api.parsers import logger
from parser_gibdd.models.crashes import Crash
from parser_gibdd.models.gibdd.crash import CrashDataResponse
from parser_gibdd.models.participants import Participant, ParticipantType
from parser_gibdd.models.region import RegionName, FederalRegionName
from parser_gibdd.models.vehicles import Vehicle


def crash_to_excel(crash: DataFrame, filename: Optional[str] = None) -> None:
    if not filename:
        filename = f'{crash["region_name"][0]}'
    crash.to_excel(f"{filename}.xlsx")


def normalize_crash_data(
        responses: List[CrashDataResponse],
) -> Tuple[List[Crash], List[Participant], List[Vehicle]]:
    crashes, vehicles, participants = [] * 3
    for response in responses:
        for crash in response.crashes:
            normalized_crash = Crash(
                region_name=response.region_name,
                **crash.dict(by_alias=False, exclude={'crash_info'}),
                **crash.crash_info.dict(by_alias=False,
                                        exclude={'vehicle_info', 'participant_info'})
            )
            for vehicle in crash.crash_info.vehicle_info:

                normalized_vehicle = Vehicle(
                    **vehicle.dict(by_alias=False, exclude={'drivers_info'})
                )
                for driver in vehicle.drivers_info:
                    driver = Participant(
                        participant_type=ParticipantType.DRIVER,
                        **driver.dict(by_alias=False)
                    )
                    participants.append(driver)
                    normalized_vehicle.drivers.append(driver.id)
                normalized_crash.vehicles.append(normalized_vehicle.id)
                vehicles.append(normalized_vehicle)
            for participant in crash.crash_info.participant_info:
                normalized_participant = Participant(
                    participant_type=ParticipantType.PASSENGER,
                    **participant.dict(by_alias=False)
                )
                normalized_crash.participants.append(normalized_participant.id)
                participants.append(normalized_participant)
    return crashes, participants, vehicles


def export_to_excel(crashes: List[Crash],
                    participants: List[Participant],
                    vehicles: [List[Vehicle]],
                    save_path: Optional[Path]):
    databook = Databook(
        sets=[
            Dataset(title='crashes').load(*crashes),
            Dataset(title='vehicles').load(*vehicles),
            Dataset(title='participants').load(*participants),

        ]
    )
    writer = databook.export('xlsx')
    if save_path and save_path.exists():
        writer.save()


def crash_data_single_dataframe(data: CrashDataResponse) -> DataFrame:
    """Structure the raw data in responses"""
    parsed = []
    for card in data.crashes:
        processed_card = {
            **card.dict(exclude={'crash_info'}),
            **card.crash_info.dict(exclude={"vehicle_info", "participant_info"})
        }
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
                              ) -> None:
    """
    TODO: Oh how do I wish to rewrite all of these packaging functions so that they make more sense
    TODO: abysmal code, but currently I dont want to fix this, however, one day it shall be made better
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


def package_crashes_fed_region(federal_data: Dict[str, List[CrashDataResponse]],
                               federal_region: str,
                               ) -> None:
    """

    TODO: Oh how do I wish to rewrite all of these packaging functions so that they make more sense
    TODO: abysmal code, but currently I dont want to fix this, however, one day it shall be made better
    """
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


def package_crashes_country(country_data: country_return_type, ) -> None:
    """

    TODO: Oh how do I wish to rewrite all of these packaging functions so that they make more sense
    TODO: abysmal code, but currently I dont want to fix this, however, one day it shall be made better
    """
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
