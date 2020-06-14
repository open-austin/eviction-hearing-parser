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
        ],
    )
    def test_get_case_number(self, index, expected):
        soup = hearing.get_test_soup(index)
        number = hearing.get_case_number(soup)
        assert number == expected

    @pytest.mark.parametrize(
        "index, expected",
        [(0, "78724"), (1, "78759"), (2, "78741-0000"), (3, "78727")],
    )
    def test_get_zip(self, index, expected):
        soup = hearing.get_test_soup(index)
        number = hearing.get_zip(hearing.get_defendant_elements(soup).pop())
        assert number == expected

    @pytest.mark.parametrize(
        "index, expected",
        [(0, "(11:00 AM)"), (1, "(11:00 AM)"), (2, "(2:00 PM)"), (3, "")],
    )
    def test_get_hearing_text(self, index, expected):
        soup = hearing.get_test_soup(index)
        passage = hearing.get_hearing_text(soup)
        assert expected in passage

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "Williams, Yvonne M."),
            (1, "Slagle, Randall"),
            (2, "Gonzalez, Raul Arturo"),
            (3, ""),
        ],
    )
    def test_get_hearing_officer(self, index, expected):
        soup = hearing.get_test_soup(index)
        name = hearing.get_hearing_officer(soup)
        assert name == expected

    @pytest.mark.parametrize(
        "index, expected", [(0, "11:00 AM"), (1, "11:00 AM"), (2, "2:00 PM"), (3, "")],
    )
    def test_get_hearing_time(self, index, expected):
        soup = hearing.get_test_soup(index)
        time = hearing.get_hearing_time(soup)
        assert expected == time

    @pytest.mark.parametrize(
        "index, expected",
        [(0, "05/14/2020"), (1, "05/14/2020"), (2, "06/05/2020"), (3, "")],
    )
    def test_get_hearing_date(self, index, expected):
        soup = hearing.get_test_soup(index)
        hearing_date = hearing.get_hearing_date(soup)
        assert expected == hearing_date

    @pytest.mark.parametrize(
        "index, expected", [(0, 1), (1, 2), (2, 4), (3, 2)],
    )
    def test_get_precinct_number(self, index, expected):
        soup = hearing.get_test_soup(index)
        precinct_number = hearing.get_precinct_number(soup)
        assert expected == precinct_number

    @pytest.mark.parametrize(
        "index, expected", [(0, False), (1, False), (2, True), (3, False)],
    )
    def test_defendant_appeared(self, index, expected):
        soup = hearing.get_test_soup(index)
        appeared = hearing.did_defendant_appear(soup)
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
        ],
    )
    def test_defendant_served(self, index, defendant, expected):
        soup = hearing.get_test_soup(index)
        served = hearing.was_defendant_served(soup)
        assert served.get(defendant) == expected

    @pytest.mark.parametrize(
        "index, expected", [(0, []), (1, ["05/05/2020"]), (2, ["01/22/2020"]), (3, [])],
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
        ],
    )
    def test_judgment_date(self, index, expected):
        soup = hearing.get_test_soup(index)
        answer = hearing.get_judgment_date(soup)
        assert expected == answer

    @pytest.mark.parametrize(
        "index, expected",
        [(0, None), (1, None), (2, None), (3, None), (4, 5163.35), (5, 5980.43)],
    )
    def test_judgment_amount(self, index, expected):
        soup = hearing.get_test_soup(index)
        amount = hearing.get_judgment_amount(soup)
        assert expected == amount
