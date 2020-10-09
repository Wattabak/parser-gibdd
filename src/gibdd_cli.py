import json
import logging
from datetime import date
from pathlib import Path

import click

from src.api.convert import crash_to_excel
from src.api.gibdd.crashes import subregion_crashes
from src.api.parsers import parse_crash_cards
from src.api.regions import get_country_codes
from src.models.region import FederalRegion, Country

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
              help="Get crashes starting from this date")
@click.option("-de", "--dend", "date_to",
              required=True,
              type=click.DateTime(formats=["%Y-%m"]), default=str(date.today()),
              help="Get crashes ending on this date")
@click.option("-R", "--federal",
              required=True,
              type=int,
              help="OKATO code of federal region")
@click.option("-r", "--municipal",
              required=True,
              type=int,
              help="OKATO code of municipal region")
def verbose(date_from: date,
            date_to: date,
            federal: int,
            municipal: int) -> None:
    required_crashes = subregion_crashes(federal, municipal, date_from, date_to)
    parsed_crashes = [parse_crash_cards(crash) for crash in required_crashes]
    for crash in parsed_crashes:
        crash_to_excel(crash)


@main.command()
@click.option("-ds", "--dstart", "date_from",
              required=True,
              type=click.DateTime(formats=["%Y-%m"]),
              help="Get crashes starting from this date")
@click.option("-de", "--dend", "date_to",
              required=True,
              type=click.DateTime(formats=["%Y-%m"]), default=str(date.today()),
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
        raise NotImplementedError("currently unable to parse whole federal regions, enter municipality")
    ctx.invoke(verbose,
               date_from=date_from,
               date_to=date_to,
               federal=all_codes.get_parent_region(selected_region).okato,
               municipal=selected_region.okato)


if __name__ == "__main__":
    main()
