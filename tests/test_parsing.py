from decimal import Decimal

import pytest

import hearing


class TestLoadHTML:
    @pytest.mark.parametrize("index", [0, 1, 2, 3])
    def test_html_has_title(self, index):
        soup = hearing.get_test_soup(index)
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
        ],
    )
    def test_get_plaintiff(self, index, expected):
        soup = hearing.get_test_soup(index)
        plaintiff = hearing.get_plaintiff(soup)
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
        ],
    )
    def test_get_defendants(self, index, expected):
        soup = hearing.get_test_soup(index)
        defendants = hearing.get_defendants(soup)
        assert expected in defendants

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "XYZ Group LLC vs. John G Doe"),
            (1, "JOHN MOE vs. Jane Roe,Unnamed Person,Jean Roe"),
            (2, "UMBRELLA CORPORATION vs. Ann Noe"),
            (3, "National Landlords, LLC vs. Lois Lewis,Louis Lewis"),
            (6, "Land Lorde vs. Ten Ant"),
        ],
    )
    def test_get_style(self, index, expected):
        soup = hearing.get_test_soup(index)
        style = hearing.get_style(soup)
        assert style == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "J1-CV-20-001590"),
            (1, "J2-CV-20-001839"),
            (2, "J4-CV-20-000198"),
            (3, "J2-CV-20-001919"),
            (6, "J3-EV-20-000001"),
        ],
    )
    def test_get_case_number(self, index, expected):
        soup = hearing.get_test_soup(index)
        number = hearing.get_case_number(soup)
        assert number == expected

    @pytest.mark.parametrize(
        "index, expected",
        [(0, "78724"), (1, "78759"), (2, "78741-0000"), (3, "78727"), (6, "78736")],
    )
    def test_get_zip(self, index, expected):
        soup = hearing.get_test_soup(index)
        number = hearing.get_zip(hearing.get_defendant_elements(soup).pop())
        assert number == expected

    @pytest.mark.parametrize(
        "index, expected",
        [(0, "(11:00 AM)"), (1, "(11:00 AM)"), (2, "(2:00 PM)"), (3, ""), (6, "")],
    )
    def test_get_hearing_text(self, index, expected):
        soup = hearing.get_test_soup(index)
        hearing_tags = hearing.get_hearing_tags(soup)
        hearing_tag = hearing_tags[-1] if len(hearing_tags) > 0 else None
        passage = hearing.get_hearing_text(hearing_tag)
        assert expected in passage

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "Williams, Yvonne M."),
            (1, "Slagle, Randall"),
            (2, "Gonzalez, Raul Arturo"),
            (3, ""),
            (6, "Judge, Mike"),
        ],
    )
    def test_get_hearing_officer(self, index, expected):
        soup = hearing.get_test_soup(index)
        hearing_tags = hearing.get_hearing_tags(soup)
        hearing_tag = hearing_tags[-1] if len(hearing_tags) > 0 else None
        name = hearing.get_hearing_officer(hearing_tag)
        assert name == expected

    @pytest.mark.parametrize(
        "index, expected",
        [(0, "11:00 AM"), (1, "11:00 AM"), (2, "2:00 PM"), (3, ""), (6, "9:00 AM")],
    )
    def test_get_hearing_time(self, index, expected):
        soup = hearing.get_test_soup(index)
        hearing_tags = hearing.get_hearing_tags(soup)
        hearing_tag = hearing_tags[-1] if len(hearing_tags) > 0 else None
        time = hearing.get_hearing_time(hearing_tag)
        assert expected == time

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "05/14/2020"),
            (1, "05/14/2020"),
            (2, "06/05/2020"),
            (3, ""),
            (6, "01/14/2020"),
        ],
    )
    def test_get_hearing_date(self, index, expected):
        soup = hearing.get_test_soup(index)
        hearing_tags = hearing.get_hearing_tags(soup)
        hearing_tag = hearing_tags[-1] if len(hearing_tags) > 0 else None
        hearing_date = hearing.get_hearing_date(hearing_tag)
        assert expected == hearing_date

    @pytest.mark.parametrize(
        "index, expected", [(0, 1), (1, 2), (2, 4), (3, 2), (6, 3)],
    )
    def test_get_precinct_number(self, index, expected):
        soup = hearing.get_test_soup(index)
        precinct_number = hearing.get_precinct_number(soup)
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
        ],
    )
    def test_defendant_appeared(self, index, hearing_index, expected):
        soup = hearing.get_test_soup(index)
        hearing_tags = hearing.get_hearing_tags(soup)
        hearing_tag = hearing_tags[hearing_index] if len(hearing_tags) > 0 else None
        appeared = hearing.did_defendant_appear(hearing_tag)
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
            (6, "Ant, Ten", "01/02/2020"),
        ],
    )
    def test_defendant_served(self, index, defendant, expected):
        soup = hearing.get_test_soup(index)
        served = hearing.was_defendant_served(soup)
        assert served.get(defendant) == expected

    @pytest.mark.parametrize(
        "index, expected",
        [(0, []), (1, ["05/05/2020"]), (2, ["01/22/2020"]), (3, []), (6, [])],
    )
    def test_alternative_service(self, index, expected):
        soup = hearing.get_test_soup(index)
        served = hearing.was_defendant_alternative_served(soup)
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
        ],
    )
    def test_judgment_date(self, index, expected):
        soup = hearing.get_test_soup(index)
        answer = hearing.get_judgment_date(soup)
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
        ],
    )
    def test_judgment_amount(self, index, expected):
        soup = hearing.get_test_soup(index)
        amount = hearing.get_disposition_amount(soup)
        assert expected == amount

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "N/A"),
            (1, "N/A"),
            (2, "N/A"),
            (3, "N/A"),
            (4, "We Sue You, Llc"),
            (5, "LESS SORE LLC"),
            (6, "Les See"),
        ],
    )
    def test_disposition_awarded_to(self, index, expected):
        soup = hearing.get_test_soup(index)
        disposition_tr = hearing.get_disposition_tr_element(soup)
        winning_party = hearing.get_disposition_awarded_to(disposition_tr)
        assert winning_party == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "N/A"),
            (1, "N/A"),
            (2, "N/A"),
            (3, "N/A"),
            (4, "David Tenant"),
            (5, "LES SEE"),
            (6, "Land Lorde"),
        ],
    )
    def test_disposition_awarded_against(self, index, expected):
        soup = hearing.get_test_soup(index)
        disposition_tr = hearing.get_disposition_tr_element(soup)
        losing_party = hearing.get_disposition_awarded_against(disposition_tr)
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
        ],
    )
    def test_disposition_type(self, index, expected):
        soup = hearing.get_test_soup(index)
        disposition_tr = hearing.get_disposition_tr_element(soup)
        if disposition_tr is None:
            dt = None
        else:
            dt = hearing.get_disposition_type(disposition_tr)
        assert dt == expected

    @pytest.mark.parametrize(
        "test_html_file_index, expected_comments",
        [
            (0, []),
            (1, []),
            (2, []),
            (3, []),
            (4, []),
            (5, []),
            (
                6,
                [
                    "Comment: PLTF TAKE NOTHING. APPEAL DATE: 01/21/2020. BOND AMT: $500.00. EMAILED JDMT TO BOTH PARTIES."
                ],
            ),
        ],
    )
    def test_comments(self, test_html_file_index, expected_comments):
        soup = hearing.get_test_soup(test_html_file_index)
        comments = hearing.get_comments(soup)
        assert comments == expected_comments
