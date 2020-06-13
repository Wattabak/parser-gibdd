from datetime import datetime
from typing import Tuple

import click


@click.group()
def main():
    pass


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
