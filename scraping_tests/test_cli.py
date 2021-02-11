import pytest

import parse_hearings


class TestCLI:

    def test_make_case_list(self):
        ids_to_parse = ["J1-CV-20-001590"]
        cases = parse_hearings.make_case_list(ids_to_parse)
        assert cases[0]["register_url"].endswith("CaseID=2286743")
        assert cases[0]["hearings"][0]["appeared"] is True
