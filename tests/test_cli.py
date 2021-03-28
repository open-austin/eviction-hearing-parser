from datetime import date

from scrapers import TestScraper
import parse_hearings
import get_all_filings_settings_between_dates as filings_settings

FAKE_SCRAPER = TestScraper()


class TestCLI:
    def test_make_case_list(self):
        ids_to_parse = ["J1-CV-20-001590"]
        cases = FAKE_SCRAPER.make_case_list(ids_to_parse)
        assert cases[0]["register_url"].endswith("CaseID=2286743")
        assert cases[0]["hearings"][0]["hearing_type"] == "Eviction Hearing"

    def test_parse_cases_from_cli(self):
        ids_to_parse = ["J1-CV-20-001590"]
        cases = parse_hearings.parse_all_from_parse_filings(
            case_nums=ids_to_parse,
            showbrowser=False,
            scraper=FAKE_SCRAPER,
        )
        assert cases[0]["register_url"].endswith("CaseID=2286743")
        assert cases[0]["hearings"][0]["hearing_type"] == "Eviction Hearing"

    def test_split_into_weeks(self):
        weeks = filings_settings.split_into_weeks(
            start=date(2020, 1, 1), end=date(2020, 12, 31)
        )
        assert len(weeks) == 53
        assert weeks[-1][0] == date(2020, 12, 30)

    def test_no_failure_messages_when_getting_all_filings(self):
        failures = filings_settings.get_all_filings_settings_between_dates(
            start_date=date(2015, 10, 21), end_date=date(2015, 10, 21), county="test"
        )
        assert not failures
