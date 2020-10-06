import json
import logging
from datetime import date
from pathlib import Path

import click

from src.api.convert import crash_to_excel
from src.api.gibdd.crashes import subregion_crashes
from src.api.okato import all_okato_codes
from src.api.parsers import parse_crash_cards

logger = logging.getLogger("src.gibdd_cli")


@click.group()
def main():
    pass


@main.command()
def okato() -> None:
    path = Path("../cache/okato_codes_latest.json")
    if not path.exists():
        all_codes = all_okato_codes()
        click.echo([
            f"{fed.name} муниципалитетов: {len(fed.districts)}"
            for fed in all_codes.regions
        ])
        with path.open("w") as raw:
            json.dump(all_codes.dict(), raw)
    else:
        with path.open("r") as raw:
            all_codes = json.loads(raw.read())
        check_codes = all_okato_codes()
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
@click.option("-R", "--federal", required=True, type=int)
@click.option("-r", "--municipal", required=True, type=int, )
def verbose(date_from: date,
            date_to: date,
            federal: int,
            municipal: int):
    required_crashes = subregion_crashes(federal, municipal, date_from, date_to)
    parsed_crashes = [parse_crash_cards(crash) for crash in required_crashes]
    for crash in parsed_crashes:
        crash_to_excel(crash)


if __name__ == "__main__":
    main()
