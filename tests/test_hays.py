import datetime
from decimal import Decimal

import pytest

from cases import CaseEvent
import hearing
import load_pages

Hays = hearing.HaysParser()
county = "hays"


class TestLoadHTML:
    @pytest.mark.parametrize("index", [0, 1])
    def test_html_has_title(self, index):
        soup = load_pages.get_test_soup(index, county)
        tag = soup.div
        assert "Register of Actions" in tag.text


class TestParseHTML:
    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "CastleRock at San Marcos"),
            (1, "1640 Blackacre LLC"),
        ],
    )
    def test_get_plaintiff(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        plaintiff = Hays.get_plaintiff(soup)
        assert plaintiff == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "Name1 Name2, Fake1 Fake2"),
            (1, "Realistic, Person"),
        ],
    )
    def test_get_defendants(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        defendants = Hays.get_defendants(soup)
        assert expected in defendants

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "CastleRock at San Marcos vs. Name1 Name2, Fake1 Fake2"),
            (1, "1640 Blackacre LLC vs. Person Realistic"),
        ],
    )
    def test_get_style(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        style = Hays.get_style(soup)
        assert style == expected

    @pytest.mark.parametrize(
        "index, expected",
        [(0, "F21-006J11"), (1, "F21-017J11")],
    )
    def test_get_case_number(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        number = Hays.get_case_number(soup)
        assert number == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "78666"),
            (1, "78666"),
        ],
    )
    def test_get_defendant_zip(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        number = Hays.get_zip(Hays.get_defendant_elements(soup).pop())
        assert number == expected

    @pytest.mark.parametrize(
        "index, expected",
        [(0, "78666"), (1, "80111")],
    )
    def test_get_plaintiff_zip(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        plaintiff_element = Hays.get_plaintiff_elements(soup).pop()
        number = Hays.get_zip(plaintiff_element)
        assert number == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "(10:00 AM)"),
            (1, "(10:00 AM)"),
        ],
    )
    def test_get_hearing_text(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        hearing_tags = Hays.get_hearing_tags(soup)
        hearing_tag = hearing_tags[-1] if len(hearing_tags) > 0 else None
        passage = Hays.get_hearing_text(hearing_tag)
        assert expected in passage

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "Eviction Petition Filed"),
            (1, "Eviction Petition Filed"),
        ],
    )
    def test_get_first_event(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        hearing_tags = Hays.get_hearing_and_event_tags(soup)
        hearing_tag = hearing_tags[0] if len(hearing_tags) > 0 else None
        assert expected in hearing_tag.text

    @pytest.mark.parametrize(
        "index, expected",
        [(0, "Prado, Jo Anne"), (1, "Prado, Jo Anne")],
    )
    def test_get_hearing_officer(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        hearing_tags = Hays.get_hearing_tags(soup)
        hearing_tag = hearing_tags[-1] if len(hearing_tags) > 0 else None
        name = Hays.get_hearing_officer(hearing_tag)
        assert name == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "10:00 AM"),
            (1, "10:00 AM"),
        ],
    )
    def test_get_hearing_time(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        hearing_tags = Hays.get_hearing_tags(soup)
        hearing_tag = hearing_tags[-1] if len(hearing_tags) > 0 else None
        time = Hays.get_hearing_time(hearing_tag)
        assert expected == time

    @pytest.mark.parametrize(
        "index, expected",
        [(0, "02/11/2021"), (1, "03/18/2021")],
    )
    def test_get_hearing_date(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        hearing_tags = Hays.get_hearing_tags(soup)
        hearing_tag = hearing_tags[-1] if len(hearing_tags) > 0 else None
        hearing_date = Hays.get_hearing_date(hearing_tag)
        assert expected == hearing_date

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, 1.1),
            (1, 1.1),
        ],
    )
    def test_get_precinct_number(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        precinct_number = Hays.get_precinct_number(soup)
        assert expected == precinct_number

    # NOT SURE ABOUT THESE PARAMS?
    @pytest.mark.parametrize(
        "index, hearing_index, expected",
        [
            (0, 0, False),
            (1, 0, False),
        ],
    )
    def test_defendant_appeared(self, index, hearing_index, expected):
        soup = load_pages.get_test_soup(index, county)
        hearing_tags = Hays.get_hearing_tags(soup)
        hearing_tag = hearing_tags[hearing_index] if len(hearing_tags) > 0 else None
        appeared = Hays.did_defendant_appear(hearing_tag)
        assert expected == appeared

    @pytest.mark.parametrize(
        "index, defendant, expected",
        [
            (0, "Name1 Name2, Fake1 Fake2", "01/13/2021"),
            (1, "Realistic, Person", "03/08/2021"),
        ],
    )
    def test_defendant_served(self, index, defendant, expected):
        soup = load_pages.get_test_soup(index, county)
        served = Hays.was_defendant_served(soup)
        assert served.get(defendant) == expected

    @pytest.mark.parametrize(
        "index, expected",
        [(0, []), (1, ["03/08/2021"])],
    )
    def test_alternative_service(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        served = Hays.was_defendant_alternative_served(soup)
        assert expected == served

    @pytest.mark.parametrize(
        "index, expected",
        [(0, "02/12/2021"), (1, "03/18/2021")],
    )
    def test_disposition_date(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        answer = Hays.get_disposition_date(soup)
        assert expected == answer

    @pytest.mark.parametrize(
        "index, expected",
        [(0, Decimal("2221.00")), (1, Decimal("61.00"))],
    )
    def test_disposition_amount(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        amount = Hays.get_disposition_amount(soup)
        assert expected == amount

    # Does Hays record awarded info?
    @pytest.mark.parametrize(
        "index, expected",
        [(0, ""), (1, "")],
    )
    def test_disposition_awarded_to(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        disposition_tr = Hays.get_disposition_tr_element(soup)
        winning_party = Hays.get_disposition_awarded_to(disposition_tr)
        assert winning_party == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, ""),
            (1, ""),
        ],
    )
    def test_disposition_awarded_against(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        disposition_tr = Hays.get_disposition_tr_element(soup)
        losing_party = Hays.get_disposition_awarded_against(disposition_tr)
        assert losing_party == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "Default Judgment"),
            (1, "Judgment for Plaintiff"),
        ],
    )
    def test_disposition_type(self, index, expected):
        soup = load_pages.get_test_soup(index, county)
        disposition_tr = Hays.get_disposition_tr_element(soup)
        if disposition_tr is None:
            dt = None
        else:
            dt = Hays.get_disposition_type(disposition_tr)
        assert dt == expected

    @pytest.mark.parametrize(
        "test_html_file_index, expected_comments",
        [
            (0, None),
            (1, None),
        ],
    )
    def test_comments(self, test_html_file_index, expected_comments):
        soup = load_pages.get_test_soup(test_html_file_index, county)
        comments = Hays.get_comments(soup)
        assert comments == expected_comments

    @pytest.mark.parametrize(
        "test_html_file_index, expected_event_details",
        [
            (0, None),
            (
                1,
                CaseEvent(
                    case_event_date=datetime.date(2021, 3, 30),
                    served_date="03/08/2021",
                    served_subject="Realistic, Person",
                ),
            ),
        ],
    )
    def test_get_writ(self, test_html_file_index, expected_event_details):
        soup = load_pages.get_test_soup(test_html_file_index, county)
        event_details = Hays.get_writ(soup)
        assert event_details == expected_event_details

    @pytest.mark.parametrize(
        "test_html_file_index, expected_event_details",
        [
            (0, CaseEvent(case_event_date=datetime.date(2021, 3, 11))),
            (1, CaseEvent(case_event_date=datetime.date(2021, 4, 1))),
        ],
    )
    def test_get_writ_of_possession_service(
        self, test_html_file_index, expected_event_details
    ):
        soup = load_pages.get_test_soup(test_html_file_index, county)
        event_details = Hays.get_writ_of_possession_service(soup)
        assert event_details == expected_event_details

    @pytest.mark.parametrize(
        "test_html_file_index, expected_event_details",
        [
            (0, CaseEvent(case_event_date=datetime.date(2021, 3, 10))),
            (1, CaseEvent(case_event_date=datetime.date(2021, 3, 30))),
        ],
    )
    def test_get_writ_of_possession_requested(
        self, test_html_file_index, expected_event_details
    ):
        soup = load_pages.get_test_soup(test_html_file_index, county)
        event_details = Hays.get_writ_of_possession_requested(soup)
        assert event_details == expected_event_details

    @pytest.mark.parametrize(
        "test_html_file_index, expected_event_details",
        [
            (0, None),
            (1, None),
        ],
    )
    def test_get_writ_of_possession_sent_to_constable(
        self, test_html_file_index, expected_event_details
    ):
        soup = load_pages.get_test_soup(test_html_file_index, county)
        event_details = Hays.get_writ_of_possession_sent_to_constable(soup)
        assert event_details == expected_event_details

    @pytest.mark.parametrize(
        "test_html_file_index, expected_event_details",
        [
            (0, None),
            (1, CaseEvent(case_event_date=datetime.date(2021, 4, 8))),
        ],
    )
    def test_get_writ_returned_to_court(
        self, test_html_file_index, expected_event_details
    ):
        soup = load_pages.get_test_soup(test_html_file_index, county)
        event_details = Hays.get_writ_returned_to_court(soup)
        assert event_details == expected_event_details

    @pytest.mark.parametrize(
        "test_html_file_index, expected_attorneys",
        [
            (0, {}),
            (1, {"Pro Se": ["Realistic, Person"]}),
        ],
    )
    def test_get_attorneys_for_defendants(
        self, test_html_file_index, expected_attorneys
    ):
        soup = load_pages.get_test_soup(test_html_file_index, county)
        attorneys = Hays.get_attorneys_for_defendants(soup)
        assert attorneys == expected_attorneys

    @pytest.mark.parametrize(
        "test_html_file_index, expected_attorneys",
        [
            (0, {}),
            (1, {"Learned Hand": ["1640 Blackacre LLC"]}),
        ],
    )
    def test_get_attorneys_for_plaintiffs(
        self, test_html_file_index, expected_attorneys
    ):
        soup = load_pages.get_test_soup(test_html_file_index, county)
        attorneys = Hays.get_attorneys_for_plaintiffs(soup)
        assert attorneys == expected_attorneys

    @pytest.mark.parametrize(
        "test_html_file_index, plaintiff, disposition_date, address,race,gender",
        [
            (
                0,
                "CastleRock at San Marcos",
                "02/12/2021",
                "1234 Fake St. San Marcos, TX 78666",
                "White",
                "Male",
            ),
            (
                1,
                "1640 Blackacre LLC",
                "03/18/2021",
                "1640 Blackacre Lane Apartment No. 333 San Marcos, TX 78666",
                "",
                "",
            ),
        ],
    )
    def test_make_parsed_case(
        self, test_html_file_index, plaintiff, disposition_date, address, race, gender
    ):
        soup = load_pages.get_test_soup(test_html_file_index, county)
        parsed_case = Hays.make_parsed_case(soup=soup)

        assert parsed_case.plaintiff == plaintiff
        assert parsed_case.disposition_date == disposition_date
        assert parsed_case.defendant_address == address
        assert parsed_case.defendant_race == race
        assert parsed_case.defendant_gender == gender

    @pytest.mark.parametrize(
        "test_html_file_index, expected_address",
        [
            (0, "1234 Fake St. San Marcos, TX 78666"),
            (1, "1640 Blackacre Lane Apartment No. 333 San Marcos, TX 78666"),
        ],
    )
    def test_get_defendant_address(self, test_html_file_index, expected_address):
        soup = load_pages.get_test_soup(test_html_file_index, county)
        address = Hays.get_defendant_address(soup)
        assert address == expected_address

    @pytest.mark.parametrize(
        "test_html_file_index, expected_race",
        [
            (0, "White"),
            (1, ""),
        ],
    )
    def test_get_defendant_race(self, test_html_file_index, expected_race):
        soup = load_pages.get_test_soup(test_html_file_index, county)
        race = Hays.get_defendant_race(soup)
        assert race == expected_race

    @pytest.mark.parametrize(
        "test_html_file_index, expected_gender",
        [
            (0, "Male"),
            (1, ""),
        ],
    )
    def test_get_defendant_gender(self, test_html_file_index, expected_gender):
        soup = load_pages.get_test_soup(test_html_file_index, county)
        gender = Hays.get_defendant_gender(soup)
        assert gender == expected_gender
