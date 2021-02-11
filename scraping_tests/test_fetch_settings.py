import pytest

import fetch_page
import hearing
import parse_settings


class TestFetchSettings:

    def test_fetch_settings(self):
        settings = parse_settings.make_setting_list(days_to_pull=["9-1-2020"])
        assert settings[0] == "??"
