from scrapers import FakeScraper
import parse_hearings

FAKE_SCRAPER = FakeScraper()


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
            json=False,
            db=False,
            scraper=FAKE_SCRAPER,
        )
        assert cases[0]["register_url"].endswith("CaseID=2286743")
        assert cases[0]["hearings"][0]["hearing_type"] == "Eviction Hearing"
