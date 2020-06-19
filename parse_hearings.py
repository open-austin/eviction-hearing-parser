import sys
import csv
import json
import os
from typing import List

import hearing


def parse_all():
    parsed_cases = []
    headers_written = False
    for id_to_parse in (line.rstrip() for line in sys.stdin):
        new_case = hearing.fetch_parsed_case(id_to_parse)
        if new_case is not None:
            if not headers_written:
                writer = csv.DictWriter(
                    sys.stdout,
                    sorted(
                        list(
                            (
                                set(new_case.keys())
                                | set(new_case["hearings"][0].keys())
                                | {"hearing_number"}
                            )
                            - {"hearings"}
                        )
                    ),
                    extrasaction="ignore",
                )
                writer.writeheader()
                headers_written = True
            else:
                for hearing_number, parsed_hearing in enumerate(new_case["hearings"]):
                    writer.writerow(
                        {
                            **new_case,
                            **parsed_hearing,
                            "hearing_number": hearing_number,
                        }
                    )


if __name__ == "__main__":
    parse_all()
