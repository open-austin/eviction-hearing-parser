import pytest

import calendars
import load_pages


class TestParseCalendar:
    def test_get_calendar(self):
        soup = load_pages.get_test_calendar()
        settings = calendars.get_setting_list(soup)
        assert settings[0]["setting_style"].startswith("ALIASED")
