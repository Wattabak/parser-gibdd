import json
import logging
from datetime import date
from pathlib import Path
from pprint import pformat
from typing import Optional

import click

from parser_gibdd.gibdd_api.converters import package_crashes_subregion, package_crashes_fed_region, \
    package_crashes_country
from parser_gibdd.interface.declarative import CrashesRussiaDeclarativeInterface
from parser_gibdd.models.region import Region, FederalRegion, Country

logger = logging.getLogger("parser_gibdd.gibdd_cli")


@click.group()
def main():
    pass


@main.command()
@click.option("-s", "save_path", required=False, type=click.Path(), )
def all_okato(save_path: Optional[Path]) -> Optional[Country]:
    """Get OKATO codes for the whole country

    If save_path is not passed, data will just be printed in stdout
    """
    all_codes = CrashesRussiaDeclarativeInterface.get_okato_codes()
    click.echo([
        f"{fed.name} муниципалитетов: {len(fed.districts)}"
        for fed in all_codes.regions
    ])
    save_path = Path(save_path)

    if not save_path:
        click.echo(pformat(all_codes.dict()))
    else:
        with save_path.open("w") as raw:
            json.dump(all_codes.dict(), raw)
    return all_codes


@main.command()
@click.option("-ds", "--dstart", "date_from",
              required=True,
              type=click.DateTime(formats=["%Y-%m"]),
              default=date(year=2015, month=1, day=1).strftime("%Y-%m"),
              help="Get crashes starting from this date")
@click.option("-de", "--dend", "date_to",
              required=True,
              type=click.DateTime(formats=["%Y-%m"]),
              default=date.today().strftime("%Y-%m"),
              help="Get crashes ending on this date")
@click.option("-R", "--federal",
              required=True,
              type=int,
              help="OKATO code of federal region")
@click.option("-s",
              "--save_path",
              required=True,
              type=click.Path(exists=True))
@click.option("-r", "--municipal",
              required=False,
              type=int,
              help="OKATO code of municipal region")
@click.option("-c", "--okato-cache-path",
              required=False,
              type=click.Path(exists=True),
              help="Path to a local copy of the OKATO codes json")
def verbose(date_from: date,
            date_to: date,
            federal: int,
            save_path: Path,
            municipal: Optional[int] = None,
            okato_cache_path: Optional[Path] = None, ) -> None:
    """Get gibdd data for given set of options"""
    okato_cache_path = Path(okato_cache_path) if okato_cache_path else None
    all_codes = CrashesRussiaDeclarativeInterface.get_okato_codes(
        local_path=okato_cache_path
    )
    interface = CrashesRussiaDeclarativeInterface(all_codes)
    region, crashes = interface.get_crashes_russia_region(
        date_start=date_from,
        date_end=date_to,
        region_code=municipal if municipal else federal,
    )
    if isinstance(region, FederalRegion):
        package_crashes_fed_region(crashes,
                                   federal_region=region.name)
    elif isinstance(region, Region) and not municipal:
        click.echo(f"Whoops, no federal region with okato code {federal} found, "
                   f"however, there is a subregion with that OKATO code, named: {region.name}"
                   f"results were saved")
    package_crashes_subregion(crashes)
    # TODO: use save_path to customize the package path and refactor the package function


@main.command()
@click.option("-ds", "--dstart", "date_from",
              required=True,
              type=click.DateTime(formats=["%Y-%m"]),
              default=date(year=2015, month=1, day=1).strftime("%Y-%m"),
              help="Get crashes starting from this date")
@click.option("-de", "--dend", "date_to",
              required=True,
              type=click.DateTime(formats=["%Y-%m"]),
              default=date.today().strftime("%Y-%m"),
              help="Get crashes ending on this date")
@click.option("-r", "--region",
              required=True,
              prompt='Enter the name of the required region',
              type=str,
              help="Name of the required region")
@click.option("-c", "--okato-cache-path",
              required=False,
              type=click.Path(exists=True),
              help="Path to a local copy of the OKATO codes json")
@click.pass_context
def name(ctx: click.Context,
         date_from: date,
         date_to: date,
         region: str,
         okato_cache_path: Path) -> None:
    """Get gibdd data by region name
    """
    okato_cache_path = Path(okato_cache_path).absolute()
    all_codes = CrashesRussiaDeclarativeInterface.get_okato_codes(
        local_path=okato_cache_path
    )
    found_regions = all_codes.find_region(region)
    if not found_regions:
        click.echo("Region you specified was not found, try again")
        return
    for ind, reg in enumerate(found_regions):
        region_type = 'Федеральный' if isinstance(reg, FederalRegion) else 'Муниципальный'
        parent_region = all_codes.get_parent_region(reg)
        click.echo(f"[{ind}] Region {reg.name}, code {reg.okato}, "
                   f"region_type {region_type}, parent_region {getattr(parent_region, 'name', None)}")
    selected_index = click.prompt(text="Select the region from the list, only write the index, Example: [0]",
                                  type=click.Choice([str(ind) for ind, reg in enumerate(found_regions)]),
                                  show_choices=True)
    selected_region = found_regions[int(selected_index)]

    if isinstance(selected_region, FederalRegion):
        federal = selected_region.okato
        municipal = None
    else:
        federal = all_codes.get_parent_region(selected_region).okato
        municipal = selected_region.okato
    ctx.invoke(verbose,
               date_from=date_from,
               date_to=date_to,
               federal=federal,
               municipal=municipal)


@main.command()
@click.option("-ds", "--dstart", "date_from",
              required=True,
              type=click.DateTime(formats=["%Y-%m"]),
              default=date(year=2015, month=1, day=1).strftime("%Y-%m"),
              help="Get crashes starting from this date")
@click.option("-de", "--dend", "date_to",
              required=True,
              type=click.DateTime(formats=["%Y-%m"]),
              default=date.today().strftime("%Y-%m"),
              help="Get crashes ending on this date")
@click.option("-c", "--okato-cache-path",
              required=False,
              type=click.Path(exists=True),
              help="Path to a local copy of the OKATO codes json")
def country(date_from: date,
            date_to: date,
            okato_cache_path: Path) -> None:
    okato_cache_path = Path(okato_cache_path)
    all_codes = CrashesRussiaDeclarativeInterface.get_okato_codes(
        local_path=okato_cache_path
    )
    interface = CrashesRussiaDeclarativeInterface(all_codes)
    country_results = interface.get_crashes_russia_country(
        date_start=date_from,
        date_end=date_to
    )
    package_crashes_country(country_results)


if __name__ == "__main__":
    main()
