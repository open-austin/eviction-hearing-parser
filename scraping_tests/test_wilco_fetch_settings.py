from datetime import date

import parse_settings


class TestFetchSettingsWilco:
    def test_cli_with_williamson_county(self):
        settings = parse_settings._parse_and_persist_settings(
            afterdate=date(2020, 9, 1),
            beforedate=date(2020, 9, 1),
            showbrowser=True,
            db=False,
            gs=False,
            county="williamson",
        )
        assert settings[0]["case_number"] == "3FED-20-0248"
        assert settings[0]["setting_time"] == "11:30 AM"