import pytest

import hearing


class TestLoadHTML:
    @pytest.mark.parametrize("index", [0, 1, 2])
    def test_html_has_title(self, index):
        soup = hearing.get_test_soup(index)
        tag = soup.div
        assert tag.text == "Register of Actions"


class TestParseHTML:
    @pytest.mark.parametrize(
        "index, expected",
        [(0, "XYZ Group LLC"), (1, "DOE, JOHN"), (2, "UMBRELLA CORPORATION")],
    )
    def test_get_plaintiff(self, index, expected):
        soup = hearing.get_test_soup(index)
        plaintiff = hearing.get_plaintiff(soup)
        assert plaintiff == expected

    @pytest.mark.parametrize(
        "index, expected",
        [(0, "J1-CV-20-001590"), (1, "J2-CV-20-001839"), (2, "J4-CV-20-000198")],
    )
    def test_get_case_number(self, index, expected):
        soup = hearing.get_test_soup(index)
        number = hearing.get_case_number(soup)
        assert number == expected
