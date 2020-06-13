import sys
import csv
import json
import os
from typing import List

import hearing


def parse_all():
    parsed_cases = []
    for id_to_parse in (line.rstrip() for line in sys.stdin):
        new_hearing = hearing.fetch_parsed_case(id_to_parse)
        if new_hearing is not None:
            parsed_cases.append(new_hearing)
    writer = csv.DictWriter(
        sys.stdout,
        sorted(
            list(
                (
                    set(parsed_cases[0].keys())
                    | set(parsed_cases[0]["hearings"][0].keys())
                    | {"hearing_number"}
                )
                - {"hearings"}
            )
        ),
        extrasaction="ignore",
    )
    writer.writeheader()
    for parsed_case in parsed_cases:
        for hearing_number, parsed_hearing in enumerate(parsed_case["hearings"]):
            writer.writerow(
                {**parsed_case, **parsed_hearing, "hearing_number": hearing_number}
            )


if __name__ == "__main__":
    parse_all()
