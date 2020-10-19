import json
import logging
from datetime import date
from pathlib import Path
from typing import Optional

import click

from src.api.convert import package_crashes_subregion, package_crashes_fed_region, package_crashes_country
from src.api.gibdd.crashes import subregion_crashes, region_crashes_all, region_crashes_all_threading, \
    country_crashes_all_threading
from src.api.regions import get_country_codes
from src.models.gibdd.region import FederalRegion, Country, Region

logger = logging.getLogger("src.gibdd_cli")


@click.group()
def main():
    pass


@main.command()
@click.option("-f", "--file", "filename", required=False, default="./cache/okato_codes_latest.json")
@click.option("-u", "--update", required=False, default=False, type=bool)
def okato(filename: str, update: bool) -> None:
    """Update OKATO codes cache or ensure that it exists

    """
    path = Path(filename)
    if not path.exists():
        all_codes = get_country_codes()
        click.echo([
            f"{fed.name} муниципалитетов: {len(fed.districts)}"
            for fed in all_codes.regions
        ])
        with path.open("w") as raw:
            json.dump(all_codes.dict(), raw)
    else:
        with path.open("r") as raw:
            all_codes = json.loads(raw.read())
        check_codes = get_country_codes()
        if check_codes != all_codes:
            click.echo("override codes")
            with path.open("w") as raw:
                json.dump(check_codes.dict(), raw)


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
@click.option("-r", "--municipal",
              required=False,
              type=int,
              help="OKATO code of municipal region")
@click.option("-o", "--okato", "okato_path",
              required=False,
              default="./cache/okato_codes_latest.json",
              help="Name of the required region")
def verbose(date_from: date,
            date_to: date,
            federal: int,
            municipal: Optional[int] = None,
            okato_path: Optional[str] = None) -> None:
    """Get gibdd data for a given """
    if not municipal:
        path = Path(okato_path)
        with path.open("r") as raw:
            all_codes = Country.parse_raw(raw.read())
        federal_region = all_codes.get_region(str(federal), federal=True)
        if not federal_region or isinstance(federal_region, Region):
            click.echo(f"Whoops, no federal region with okato code {federal} found")
            return
        region_crashes = region_crashes_all(region=federal_region, period_start=date_from, period_end=date_to)
        package_crashes_fed_region(region_crashes, federal_region=federal_region.name)
    required_crashes = subregion_crashes(federal, municipal, date_from, date_to)
    package_crashes_subregion(required_crashes)


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
              prompt='Enter the required region',
              type=str,
              help="Name of the required region")
@click.option("-o", "--okato", "okato_path",
              required=False,
              default="./cache/okato_codes_latest.json",
              help="Name of the required region")
@click.pass_context
def name(ctx: click.Context, date_from: date, date_to: date, region: str, okato_path: str) -> None:
    """Get gibdd data by region name"""
    path = Path(okato_path)
    with path.open("r") as raw:
        all_codes = Country.parse_raw(raw.read())
    found_regions = all_codes.find_region(region)
    if not found_regions:
        click.echo("region you specified was not found, try again")
        return
    for ind, reg in enumerate(found_regions):
        click.echo(f"[{ind}] Region {reg.name}, code {reg.okato}")
    selected_index = click.prompt(text="Select region, only write the index, Example: [0]",
                                  type=click.Choice([str(ind) for ind, reg in enumerate(found_regions)]),
                                  show_choices=True)
    selected_region = found_regions[int(selected_index)]
    if isinstance(selected_region, FederalRegion):
        region_crashes = region_crashes_all_threading(region=selected_region, period_start=date_from,
                                                      period_end=date_to)
        package_crashes_fed_region(region_crashes, federal_region=selected_region.name)
        return
    ctx.invoke(verbose,
               date_from=date_from,
               date_to=date_to,
               federal=all_codes.get_parent_region(selected_region).okato,
               municipal=selected_region.okato)


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
@click.option("-o", "--okato", "okato_path",
              required=False,
              default="./cache/okato_codes_latest.json",
              help="Name of the required region")
def country(date_from: date, date_to: date, okato_path: str) -> None:
    path = Path(okato_path)
    with path.open("r") as raw:
        all_codes = Country.parse_raw(raw.read())
    country_results = country_crashes_all_threading(all_codes, period_start=date_from, period_end=date_to)
    package_crashes_country(country_results)


if __name__ == "__main__":
    main()
