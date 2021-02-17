import pytest

import hearing


class TestParseCalendar:
    def test_get_calendar(self):
        soup = hearing.get_test_calendar()
        settings = hearing.get_setting_list(soup)
        assert settings[0]["setting_style"].startswith("ALIASED")
