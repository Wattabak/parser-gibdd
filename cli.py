import json
from datetime import datetime
from pathlib import Path
from typing import Tuple

import click
import attr
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
        with open(path, "w") as raw:
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
def year(year: int, region: str):
    """Gets info for the whole year

    """
    pass


@main.command()
@click.option("-y")
@click.option("-m")
@click.option("-R")
@click.option("--r")
def verbose(year: int,
            months: Tuple[int, int],
            fed_region: str,
            mun_region: str):
    pass


@main.command()
def update():
    pass


if __name__ == "__main__":
    main()
