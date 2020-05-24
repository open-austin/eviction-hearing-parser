import pytest

import hearing


class TestSearchPage:
    @pytest.mark.parametrize(
        "index, expected",
        [(0, "Final Status"), (1, "Final Status"), (2, "Trial/Hearing Set"),],
    )
    def test_get_case_status(self, index, expected):
        soup = hearing.get_test_search_page(index)
        status = hearing.get_status(soup)
        assert expected in status
