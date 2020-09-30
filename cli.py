import json
from datetime import datetime, date
from pathlib import Path
from typing import List

import attr
import click

from lib.okato import all_okato_codes


@click.group()
def main():
    pass


@main.command()
def okato() -> None:
    path = Path("cache/okato_codes_latest.json")
    if not path.exists():
        all_codes = all_okato_codes()
        click.echo([
            f"{fed.name} муниципалитетов: {len(fed.districts)}"
            for fed in all_codes.regions
        ])
        with path.open("w") as raw:
            json.dump(attr.asdict(all_codes), raw)
    else:
        with path.open("r") as raw:
            all_codes = json.loads(raw.read())
        check_codes = all_okato_codes()
        if check_codes != all_codes:
            click.echo("override codes")
            with path.open("w") as raw:
                json.dump(attr.asdict(check_codes), raw)


@main.command()
@click.option("-y", default=datetime.now().year)
@click.option("-r", prompt="Region name")
def yearly(year: int, region: str):
    """Gets info for the whole year

    """
    pass


@main.command()
@click.option("-r", prompt="Region name")
def region(region: str):
    pass


@main.command()
@click.option("-dstart", type=click.DateTime(formats=["%Y-%m"]))
@click.option("-dend", type=click.DateTime(formats=["%Y-%m-%d"]), default=str(date.today()))
@click.option("-R")
@click.option("--r")
def verbose(date_from: date,
            date_to: date,
            regions: List[str]):
    pass


@main.command()
def update():
    pass


if __name__ == "__main__":
    main()
