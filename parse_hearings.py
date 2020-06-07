import sys
import csv
import json
import os
from typing import List

import hearing


def parse_all():
    parsed_hearings = []
    for id_to_parse in (line.rstrip() for line in sys.stdin):
        new_hearing = hearing.fetch_parsed_hearing(id_to_parse)
        parsed_hearings.append(new_hearing)
    parsed_hearings = [ph for ph in parsed_hearings if ph is not None]
    writer = csv.DictWriter(sys.stdout, list(parsed_hearings[0].keys()))
    writer.writeheader()
    for parsed_hearing in parsed_hearings:
        writer.writerow(parsed_hearing)


if __name__ == "__main__":
    parse_all()
