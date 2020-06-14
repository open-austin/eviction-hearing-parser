import csv
import json
import os
from typing import List

import click

import hearing


def get_ids_to_parse(filename: str) -> List[str]:
    ids = []
    with open(filename, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            ids.append(row[0])
    return ids


@click.command()
@click.argument(
    "infile",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.argument("outfile", type=click.File(mode="w"), default="result.json")
def parse_all(infile, outfile):
    parsed_hearings = []
    ids_to_parse = get_ids_to_parse(infile)
    for id_to_parse in ids_to_parse:
        new_hearing = hearing.fetch_parsed_case(id_to_parse)
        parsed_hearings.append(new_hearing)
    json.dump(parsed_hearings, outfile)


if __name__ == "__main__":
    parse_all()
