import csv
import os

import click

import hearing


@click.command()
@click.argument(
    "folder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
)
@click.argument("outfile", type=click.File(mode="w"))
def parse_all(folder, outfile):
    parsed_hearings = []
    if not any(filename.endswith(".html") for filename in os.listdir(folder)):
        raise ValueError(f"No HTML files found to parse in {folder}")
    for filename in os.listdir(folder):
        if filename.endswith(".html"):
            filepath = os.path.join(folder, filename)
            soup = hearing.load_soup_from_filepath(filepath)
            new_hearing = hearing.make_parsed_hearing(soup)
            parsed_hearings.append(new_hearing)
    fieldnames = parsed_hearings[0].keys()
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for parsed_hearing in parsed_hearings:
        writer.writerow(parsed_hearing)


if __name__ == "__main__":
    parse_all()
