from datetime import date

import pytest

import parse_settings


class TestFetchSettings:
    def test_fetch_settings(self):
        settings = parse_settings.make_setting_list(days_to_pull=[date(2020, 9, 1)])
        assert any(case["case_number"] == "J1-CV-19-005480" for case in settings)

    def test_parse_and_persist_settings(self):
        settings = parse_settings._parse_and_persist_settings(
            afterdate=date(2020, 9, 1), beforedate=date(2020, 9, 2), db=False, gs=False
        )
        assert any(case["case_number"] == "J1-CV-19-005480" for case in settings)
