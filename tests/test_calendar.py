from datetime import date

import pytest

import calendars
import load_pages
from scrapers import TestScraper


class TestParseCalendar:
    def test_get_calendar(self):
        soup = load_pages.get_test_calendar()
        settings = calendars.get_setting_list(soup)
        assert settings[0]["setting_style"].startswith("ALIASED")

    def test_make_calendar_queries(self):
        scraper = TestScraper()
        queries = list(
            scraper.calendar_queries(
                afterdate=date(2019, 12, 1), beforedate=date(2020, 1, 10)
            )
        )
        assert queries[1].prefix == "J2-CV-2019*"
