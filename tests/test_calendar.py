from datetime import date

import pytest

import calendars
import load_pages
from scrapers import FakeScraper


class TestParseCalendar:
    def test_get_calendar(self):
        soup = load_pages.get_test_calendar()
        settings = calendars.get_setting_list(soup)
        assert settings[0]["setting_style"].startswith("ALIASED")

    def test_fetch_settings(self):
        scraper = FakeScraper()
        settings = scraper.make_setting_list(days_to_pull=[date(2015, 10, 21)])
        assert any(case["case_number"] == "J1-CV-20-002326" for case in settings)

    def test_make_calendar_queries(self):
        scraper = FakeScraper()
        queries = list(
            scraper.calendar_queries(
                afterdate=date(2019, 12, 1), beforedate=date(2020, 1, 10)
            )
        )
        assert queries[1].prefix == "J2-CV-2019*"
