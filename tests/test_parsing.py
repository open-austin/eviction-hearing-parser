import datetime
from decimal import Decimal

import pytest

from cases import CaseEvent
from hearing import BaseParser
import load_pages

TravisParser = BaseParser()


class TestLoadHTML:
    @pytest.mark.parametrize("index", [0, 1, 2, 3])
    def test_html_has_title(self, index):
        soup = load_pages.get_test_soup(index)
        tag = soup.div
        assert tag.text == "Register of Actions"


class TestParseHTML:
    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "XYZ Group LLC"),
            (1, "MOE, JOHN"),
            (2, "UMBRELLA CORPORATION"),
            (3, "National Landlords, LLC"),
            (4, "We Sue You, Llc"),
            (5, "LESS SORE LLC"),
            (6, "Lorde, Land"),
            (7, "LAND LORDE, DBA LORDE"),
            (8, "THE HOUSING AUTHORITY OF THE CITY OF AUSTIN"),
            (9, "Proper Tea LLC"),
            (10, "Proper Tea LLC"),
            # (11, "Lorde, Land A; Lorde, Land B"),
            (12, "Proper Tea LLC"),
            (13, "Proper Tea LLC"),
        ],
    )
    def test_get_plaintiff(self, index, expected):
        soup = load_pages.get_test_soup(index)
        plaintiff = TravisParser.get_plaintiff(soup=soup)
        assert plaintiff == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "Doe, John G."),
            (1, "Person, Unnamed"),
            (1, "Roe, Jane"),
            (1, "Roe, Jean"),
            (2, "Noe, Ann"),
            (3, "Lewis, Lois"),
            (6, "Ant, Ten"),
            (7, "Ant, Ten"),
            (8, "ANT AND ALL OTHER OCCUPANTS, TEN"),
            (9, "Ter, Wren"),
            (10, "Ter, Wren"),
            (11, "Ter, Wren"),
            (12, "Ter, Wren A; Ter, Wren B; Ter, Wren C"),
            (13, "Ter, Wren A; Ter, Wren B"),
        ],
    )
    def test_get_defendants(self, index, expected):
        soup = load_pages.get_test_soup(index)
        defendants = TravisParser.get_defendants(soup)
        assert expected in defendants

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "XYZ Group LLC vs. John G Doe"),
            (1, "JOHN MOE vs. Jane Roe,Unnamed Person,Jean Roe"),
            (2, "UMBRELLA CORPORATION vs. Ann Noe"),
            (3, "National Landlords, LLC vs. Lois Lewis,Louis Lewis"),
            (6, "Land Lorde vs. Ten Ant"),
            (7, "LAND LORDE, DBA LORDE vs. TEN ANT AND ALL OTHER OCCUPANTS"),
            (
                8,
                "THE HOUSING AUTHORITY OF THE CITY OF AUSTIN vs. TEN ANT AND ALL OTHER OCCUPANTS",
            ),
            (9, "Proper Tea LLC vs. Wren Ter"),
            (10, "Proper Tea LLC vs. Wren Ter"),
            (11, "Wren A Ter,Wren B Ter vs. Wren Ter and all other occupants"),
            (12, "Proper Tea LLC vs. Wren A Ter,Wren B Ter,Wren C Ter"),
            (13, "Proper Tea LLC vs. Wren A Ter,Wren B Ter"),
        ],
    )
    def test_get_style(self, index, expected):
        soup = load_pages.get_test_soup(index)
        style = TravisParser.get_style(soup)
        assert style == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "J1-CV-20-001590"),
            (1, "J2-CV-20-001839"),
            (2, "J4-CV-20-000198"),
            (3, "J2-CV-20-001919"),
            (6, "J3-EV-20-000001"),
            (7, "J2-CV-20-000021"),
            (8, "J1-CV-20-000002"),
            (9, "J1-CV-20-001388"),
            (10, "J3-EV-19-001138"),
            (11, "J2-CV-19-002733"),
            (12, "J4-CV-19-003223"),
            (13, "J4-CV-19-000576"),
        ],
    )
    def test_get_case_number(self, index, expected):
        soup = load_pages.get_test_soup(index)
        number = TravisParser.get_case_number(soup)
        assert number == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "78724"),
            (1, "78759"),
            (2, "78741-0000"),
            (3, "78727"),
            (4, "78721"),
            (5, "78723"),
            (6, "78736"),
            (7, "78728"),
            (8, "78702"),
            (9, "78752"),
            (10, "78746"),
            (11, "78660"),
            (12, "78744"),
            (13, "78744"),
        ],
    )
    def test_get_defendant_zip(self, index, expected):
        soup = load_pages.get_test_soup(index)
        number = TravisParser.get_zip(TravisParser.get_defendant_elements(soup).pop())
        assert number == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "78703"),
            (1, "78759"),
            (2, ""),
            (3, "78705"),
            (4, "23541"),
            (5, "77056"),
            (6, "78736"),
            (7, "78752"),
            (8, "78702"),
            (9, "78752"),
            (10, "78258"),
            (11, "78750"),
            (12, "78258"),
            (13, "78752"),
        ],
    )
    def test_get_plaintiff_zip(self, index, expected):
        soup = load_pages.get_test_soup(index)
        number = TravisParser.get_zip(TravisParser.get_plaintiff_elements(soup).pop())
        assert number == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "(11:00 AM)"),
            (1, "(11:00 AM)"),
            (2, "(2:00 PM)"),
            (3, ""),
            (6, ""),
            (7, "(9:30 AM)"),
            (8, "(11:30 AM)"),
            (9, "(2:00 PM)"),
            (10, "(9:00 AM)"),
            (11, "(9:30 AM)"),
            (12, "(10:00 AM)"),
            (13, "(9:00 AM)"),
        ],
    )
    def test_get_hearing_text(self, index, expected):
        soup = load_pages.get_test_soup(index)
        hearing_tags = TravisParser.get_hearing_tags(soup)
        hearing_tag = hearing_tags[-1] if len(hearing_tags) > 0 else None
        passage = TravisParser.get_hearing_text(hearing_tag)
        assert expected in passage

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "Original Petition"),
            (1, "Original Petition"),
            (2, "Original Petition"),
            (3, "Original Petition"),
            (6, "Original Petition"),
            (7, "Original Petition"),
            (8, "Citation Issued"),
            (9, "Original Petition"),
            (10, "Original Petition"),
            (11, "Original Petition"),
            (12, "Original Petition"),
            (13, "Defendant's SCRA Received"),
        ],
    )
    def test_get_first_event(self, index, expected):
        soup = load_pages.get_test_soup(index)
        hearing_tags = TravisParser.get_hearing_and_event_tags(soup)
        hearing_tag = hearing_tags[0] if len(hearing_tags) > 0 else None
        assert expected in hearing_tag.text

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "Williams, Yvonne M."),
            (1, "Slagle, Randall"),
            (2, "Gonzalez, Raul Arturo"),
            (3, ""),
            (6, "Judge, Mike"),
            (7, "Judge, Mike"),
            (8, "Judge, Aaron"),
            (9, "Williams, Yvonne M."),
            (10, "Holmes, Sylvia"),
            (11, "Slagle, Randall"),
            (12, "Gonzalez, Raul Arturo"),
            (13, "Gonzalez, Raul Arturo"),
        ],
    )
    def test_get_hearing_officer(self, index, expected):
        soup = load_pages.get_test_soup(index)
        hearing_tags = TravisParser.get_hearing_tags(soup)
        hearing_tag = hearing_tags[-1] if len(hearing_tags) > 0 else None
        name = TravisParser.get_hearing_officer(hearing_tag)
        assert name == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "11:00 AM"),
            (1, "11:00 AM"),
            (2, "2:00 PM"),
            (3, ""),
            (6, "9:00 AM"),
            (7, "9:30 AM"),
            (8, "11:30 AM"),
            (9, "2:00 PM"),
            (10, "9:00 AM"),
            (11, "9:30 AM"),
            (12, "10:00 AM"),
            (13, "9:00 AM"),
        ],
    )
    def test_get_hearing_time(self, index, expected):
        soup = load_pages.get_test_soup(index)
        hearing_tags = TravisParser.get_hearing_tags(soup)
        hearing_tag = hearing_tags[-1] if len(hearing_tags) > 0 else None
        time = TravisParser.get_hearing_time(hearing_tag)
        assert expected == time

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "05/14/2020"),
            (1, "05/14/2020"),
            (2, "06/05/2020"),
            (3, ""),
            (6, "01/14/2020"),
            (7, "01/21/2020"),
            (8, "01/23/2020"),
            (9, "06/25/2020"),
            (10, "12/09/2019"),
            (11, "07/02/2019"),
            (12, "10/18/2019"),
            (13, "03/13/2019"),
        ],
    )
    def test_get_hearing_date(self, index, expected):
        soup = load_pages.get_test_soup(index)
        hearing_tags = TravisParser.get_hearing_tags(soup)
        hearing_tag = hearing_tags[-1] if len(hearing_tags) > 0 else None
        hearing_date = TravisParser.get_hearing_date(hearing_tag)
        assert expected == hearing_date

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, 1),
            (1, 2),
            (2, 4),
            (3, 2),
            (6, 3),
            (7, 2),
            (8, 1),
            (9, 1),
            (10, 3),
            (11, 2),
            (12, 4),
            (13, 4),
        ],
    )
    def test_get_precinct_number(self, index, expected):
        soup = load_pages.get_test_soup(index)
        precinct_number = TravisParser.get_precinct_number(soup)
        assert expected == precinct_number

    @pytest.mark.parametrize(
        "index, hearing_index, expected",
        [
            (0, 0, False),
            (1, 0, False),
            (2, 3, False),
            (2, 2, True),
            (3, 0, False),
            (6, 0, True),
            (7, 0, True),
            (8, 0, True),
            # (9, 0, False),  # Canceled hearing
            # (9, 1, False),  # Canceled hearing
            (10, 0, True),
            # (10, 1, False),  # Canceled hearing
            # (11, 1, False),  # Canceled hearing
            # (11, 2, False),  # Canceled hearing
            # (11, 3, False),  # Canceled hearing
            (12, 0, False),
            (12, 1, False),
            (12, 2, True),
            # (13, 0, False),  # Canceled hearing
            # (13, 1, False),  # Canceled hearing
        ],
    )
    def test_defendant_appeared(self, index, hearing_index, expected):
        soup = load_pages.get_test_soup(index)
        hearing_tags = TravisParser.get_hearing_tags(soup)
        hearing_tag = hearing_tags[hearing_index] if len(hearing_tags) > 0 else None
        appeared = TravisParser.did_defendant_appear(hearing_tag)
        assert expected == appeared

    @pytest.mark.parametrize(
        "index, defendant, expected",
        [
            (0, "Doe, John G", "05/01/2020"),
            (1, "Person, Unnamed", "05/06/2020"),
            (1, "Roe, Jane", "05/06/2020"),
            (1, "Roe, Jean", "05/06/2020"),
            (2, "Noe, Ann", "01/22/2020"),
            (3, "Lewis, Lois", None),
            (4, "Tenant, David", "12/08/2018"),
            (5, "SEE, LES", "11/16/2019"),
            (6, "Ant, Ten", "01/02/2020"),
            # (7, "Ant, Ten", "01/08/2020"),
            # (8, "ANT AND ALL OTHER OCCUPANTS, TEN", "01/14/2020"),
            (9, "Ter, Wren", "06/01/2020"),
            (10, "Ter, Wren", "10/24/2019"),
            (11, "Ter, Wren", "05/20/2019"),
            (12, "Ter, Wren A", "09/24/2019"),
            (12, "Ter, Wren C", "09/24/2019"),
            (12, "Ter, Wren B", "09/24/2019"),
            (13, "Ter, Wren B", "02/19/2019"),
            (13, "Ter, Wren A", "02/19/2019"),
        ],
    )
    def test_defendant_served(self, index, defendant, expected):
        soup = load_pages.get_test_soup(index)
        served = TravisParser.was_defendant_served(soup)
        assert served.get(defendant) == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, []),
            (1, ["05/05/2020"]),
            (2, ["01/22/2020"]),
            (3, []),
            (6, []),
            (7, []),
            (8, []),
            (9, []),
            (10, ["10/24/2019"]),
            (11, []),
            (12, []),
            (13, []),
        ],
    )
    def test_alternative_service(self, index, expected):
        soup = load_pages.get_test_soup(index)
        served = TravisParser.was_defendant_alternative_served(soup)
        assert expected == served

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, None),
            (1, None),
            (2, None),
            (3, None),
            (4, "03/13/2020"),
            (5, "03/13/2020"),
            (6, "01/14/2020"),
            (7, "01/21/2020"),
            (8, "01/23/2020"),
            (9, None),
            (10, "12/10/2019"),
            (11, "07/02/2019"),
            (12, "10/18/2019"),
            (13, "03/11/2019"),
        ],
    )
    def test_disposition_date(self, index, expected):
        soup = load_pages.get_test_soup(index)
        answer = TravisParser.get_disposition_date(soup)
        assert expected == answer

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, None),
            (1, None),
            (2, None),
            (3, None),
            (4, Decimal("5163.35")),
            (5, Decimal("5980.43")),
            (6, None),
            (7, Decimal("1793.16")),
            (8, Decimal("1477.90")),
            (9, None),
            (10, None),
            (11, None),
            (12, None),
            (13, None),
        ],
    )
    def test_disposition_amount(self, index, expected):
        soup = load_pages.get_test_soup(index)
        amount = TravisParser.get_disposition_amount(soup)
        assert expected == amount

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, ""),
            (1, ""),
            (2, ""),
            (3, ""),
            (4, "We Sue You, Llc"),
            (5, "LESS SORE LLC"),
            (6, "Les See"),
            (7, "LAND LORDE, DBA LORDE"),
            (8, "THE HOUSING AUTHORITY OF THE CITY OF AUSTIN"),
            (9, ""),
            (10, "Wren Ter"),
            (11, ""),
            (12, "Wren A Ter, et al"),
            (13, ""),
        ],
    )
    def test_disposition_awarded_to(self, index, expected):
        soup = load_pages.get_test_soup(index)
        disposition_tr = TravisParser.get_disposition_tr_element(soup)
        winning_party = TravisParser.get_disposition_awarded_to(disposition_tr)
        assert winning_party == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, ""),
            (1, ""),
            (2, ""),
            (3, ""),
            (4, "David Tenant"),
            (5, "LES SEE"),
            (6, "Land Lorde"),
            (7, "Ten Ant"),
            (8, "TEN ANT AND ALL OTHER OCCUPANTS"),
            (9, ""),
            (10, "Proper Tea LLC"),
            (11, ""),
            (12, "Proper Tea LLC"),
            (13, ""),
        ],
    )
    def test_disposition_awarded_against(self, index, expected):
        soup = load_pages.get_test_soup(index)
        disposition_tr = TravisParser.get_disposition_tr_element(soup)
        losing_party = TravisParser.get_disposition_awarded_against(disposition_tr)
        assert losing_party == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, None),
            (1, None),
            (2, None),
            (3, None),
            (4, "Default Judgment"),
            (5, "Default Judgment"),
            (6, "Final Judgment"),
            (7, "Final Judgment"),
            (8, "Default Judgment"),
            (9, None),
            (10, "Agreed Judgment"),
            (11, "Nonsuited/Dismissed by Plaintiff"),
            (12, "Final Judgment"),
            (13, "Nonsuited/Dismissed by Plaintiff"),
        ],
    )
    def test_disposition_type(self, index, expected):
        soup = load_pages.get_test_soup(index)
        disposition_tr = TravisParser.get_disposition_tr_element(soup)
        if disposition_tr is None:
            dt = None
        else:
            dt = TravisParser.get_disposition_type(disposition_tr)
        assert dt == expected

    @pytest.mark.parametrize(
        "test_html_file_index, expected_comments",
        [
            (0, None),
            (1, None),
            (2, None),
            (3, None),
            (4, None),
            (5, None),
            (
                6,
                "Comment: PLTF TAKE NOTHING. APPEAL DATE: 01/21/2020. BOND AMT: $500.00. EMAILED JDMT TO BOTH PARTIES.",
            ),
            (7, "Comment: EMAILED TO BOTH. KD"),
            (8, None),
            (9, None),
            (
                10,
                "Comment: PLTF TAKE NOTHING. APPEAL DATE: 12/16/2019. BOND AMT: $25.00. EMAILED JDMT TO BOTH PARTIES.",
            ),
            (11, None),
            (
                12,
                "Comment: + INT @ 5.25%. JGMT FOR DEFS, PLF TAKE NOTHING. APPEAL BOND $500.00.",
            ),
            (13, None),
        ],
    )
    def test_comments(self, test_html_file_index, expected_comments):
        soup = load_pages.get_test_soup(test_html_file_index)
        comments = TravisParser.get_comments(soup)
        assert comments == expected_comments

    @pytest.mark.parametrize(
        "test_html_file_index, expected_event_details",
        [
            (0, None),
            (1, None),
            (2, None),
            (3, None),
            (4, None),
            (5, None),
            (6, None),
            (
                7,
                CaseEvent(case_event_date=datetime.date(2020, 2, 3)),
            ),
            (
                8,
                CaseEvent(case_event_date=datetime.date(2020, 2, 3)),
            ),
            (9, None),
            (10, None),
            (11, None),
            (12, None),
            (13, None),
        ],
    )
    def test_get_writ(self, test_html_file_index, expected_event_details):
        soup = load_pages.get_test_soup(test_html_file_index)
        event_details = TravisParser.get_writ(soup)
        assert event_details == expected_event_details

    @pytest.mark.parametrize(
        "test_html_file_index, expected_event_details",
        [
            (0, None),
            (1, None),
            (2, None),
            (3, None),
            (4, None),
            (5, None),
            (6, None),
            (7, CaseEvent(case_event_date=datetime.date(2020, 1, 29))),
            (8, CaseEvent(case_event_date=datetime.date(2020, 2, 3))),
            (9, None),
            (10, None),
            (11, None),
            (12, None),
            (13, None),
        ],
    )
    def test_get_writ_of_possession_service(
        self, test_html_file_index, expected_event_details
    ):
        soup = load_pages.get_test_soup(test_html_file_index)
        event_details = TravisParser.get_writ_of_possession_service(soup)
        assert event_details == expected_event_details

    @pytest.mark.parametrize(
        "test_html_file_index, expected_event_details",
        [
            (0, None),
            (1, None),
            (2, None),
            (3, None),
            (4, None),
            (5, None),
            (6, None),
            (7, None),
            (8, CaseEvent(case_event_date=datetime.date(2020, 2, 3))),
            (9, None),
            (10, None),
            (11, None),
            (12, None),
            (13, None),
        ],
    )
    def test_get_writ_of_possession_requested(
        self, test_html_file_index, expected_event_details
    ):
        soup = load_pages.get_test_soup(test_html_file_index)
        event_details = TravisParser.get_writ_of_possession_requested(soup)
        assert event_details == expected_event_details

    @pytest.mark.parametrize(
        "test_html_file_index, expected_event_details",
        [
            (0, None),
            (1, None),
            (2, None),
            (3, None),
            (4, None),
            (5, None),
            (6, None),
            (7, None),
            (8, CaseEvent(case_event_date=datetime.date(2020, 2, 4))),
            (9, None),
            (10, None),
            (11, None),
            (12, None),
            (13, None),
        ],
    )
    def test_get_writ_of_possession_sent_to_constable(
        self, test_html_file_index, expected_event_details
    ):
        soup = load_pages.get_test_soup(test_html_file_index)
        event_details = TravisParser.get_writ_of_possession_sent_to_constable(soup)
        assert event_details == expected_event_details

    @pytest.mark.parametrize(
        "test_html_file_index, expected_event_details",
        [
            (0, None),
            (1, None),
            (2, None),
            (3, None),
            (4, None),
            (5, None),
            (6, None),
            (7, CaseEvent(case_event_date=datetime.date(2020, 2, 13))),
            (8, None),
            (9, None),
            (10, None),
            (11, None),
            (12, None),
            (13, None),
        ],
    )
    def test_get_writ_returned_to_court(
        self, test_html_file_index, expected_event_details
    ):
        soup = load_pages.get_test_soup(test_html_file_index)
        event_details = TravisParser.get_writ_returned_to_court(soup)
        assert event_details == expected_event_details

    @pytest.mark.parametrize(
        "test_html_file_index, expected_attorneys",
        [
            (0, {}),
            (1, {}),
            (2, {"RYAN ELLIS": ["Noe, Ann"]}),
            (3, {}),
            (4, {}),
            (5, {}),
            (6, {}),
            (7, {}),
            (8, {}),
            (9, {"MARISSA M LATTA": ["Ter, Wren"]}),
            (10, {"MARISSA M LATTA": ["Ter, Wren"]}),
            (11, {"MARISSA M LATTA": ["Ter, Wren"]}),
            (12, {"MARISSA M LATTA": ["Ter, Wren A", "Ter, Wren B", "Ter, Wren C"]}),
            (13, {"MARISSA M LATTA": ["Ter, Wren B"]}),
        ],
    )
    def test_get_attorneys_for_defendants(
        self, test_html_file_index, expected_attorneys
    ):
        soup = load_pages.get_test_soup(test_html_file_index)
        attorneys = TravisParser.get_attorneys_for_defendants(soup)
        assert attorneys == expected_attorneys

    @pytest.mark.parametrize(
        "test_html_file_index, expected_attorneys",
        [
            (0, {}),
            (1, {}),
            (2, {"DARRELL W. COOK": ["UMBRELLA CORPORATION"]}),
            (3, {}),
            (4, {"SCOTT RHODELL STOTTLEMYRE": ["We Sue You, Llc"]}),
            (5, {"KATHARINE ALLEN": ["LESS SORE LLC"]}),
            (6, {}),
            (7, {}),
            (8, {}),
            (9, {}),
            (10, {"TRAVIS M. MILLER": ["Proper Tea LLC"]}),
            (11, {"JAMES D. PARKER": ["Lorde, Land A", "Lorde, Land B"]}),
            (12, {"R DAVID FRITSCHE": ["Proper Tea LLC"]}),
            (13, {"JAMES N. FLOYD": ["Proper Tea LLC"]}),
        ],
    )
    def test_get_attorneys_for_plaintiffs(
        self, test_html_file_index, expected_attorneys
    ):
        soup = load_pages.get_test_soup(test_html_file_index)
        attorneys = TravisParser.get_attorneys_for_plaintiffs(soup)
        assert attorneys == expected_attorneys

    @pytest.mark.parametrize(
        "test_html_file_index, plaintiff, disposition_date",
        [
            (0, "XYZ Group LLC", ""),
            (5, "LESS SORE LLC", "03/13/2020"),
            (6, "Lorde, Land", "01/14/2020"),
        ],
    )
    def test_make_parsed_case(self, test_html_file_index, plaintiff, disposition_date):
        soup = load_pages.get_test_soup(test_html_file_index)
        parsed_case = TravisParser.make_parsed_case(soup=soup)
        assert parsed_case.plaintiff == plaintiff
        assert parsed_case.disposition_date == disposition_date
