from decimal import Decimal

import pytest

import hearing
import load_pages

Wilco = hearing.WilliamsonParser()


class TestLoadHTML:
    @pytest.mark.parametrize("index", [0])
    def test_html_has_title(self, index):
        soup = load_pages.get_test_williamson(index)
        tag = soup.div
        assert "Register of Actions" in tag.text


class TestParseHTML:
    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "Name, Realistic Fake"),
            (1, "Fox, Michael A"),
            (2, "Fake Name, Unlikely"),
        ],
    )
    def test_get_plaintiff(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        plaintiff = Wilco.get_plaintiff(soup)
        assert plaintiff == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "Smith, Alice; Jones, Beverly"),
            (1, "McDuff, Donald"),
            (2, "Barron, Carlos; O'Oregon, Kristin"),
        ],
    )
    def test_get_defendants(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        defendants = Wilco.get_defendants(soup)
        assert expected in defendants

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "Realistic Fake Name vs. Alice Smith,Beverly Jones"),
            (1, "Michael A Fox vs. Donald McDuff"),
            (2, "Unlikely Fake Name vs. Alice Jones,Eve O'Oregon"),
        ],
    )
    def test_get_style(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        style = Wilco.get_style(soup)
        assert style == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "1JC-21-0008"),
            (1, "1JC-21-0116"),
            (0, "1JC-21-0008"),
        ],
    )
    def test_get_case_number(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        number = Wilco.get_case_number(soup)
        assert number == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, ""),
            (1, ""),
            (2, ""),
        ],
    )
    def test_get_defendant_zip(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        number = Wilco.get_zip(Wilco.get_defendant_elements(soup).pop())
        assert number == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, ""),
            (1, ""),
            (2, ""),
        ],
    )
    def test_get_plaintiff_zip(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        number = Wilco.get_zip(Wilco.get_plaintiff_elements(soup).pop())
        assert number == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "(10:30 AM)"),
            (1, "(10:45 AM)"),
            (2, "(10:30 AM)"),
        ],
    )
    def test_get_hearing_text(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        hearing_tags = Wilco.get_hearing_tags(soup)
        hearing_tag = hearing_tags[-1] if len(hearing_tags) > 0 else None
        passage = Wilco.get_hearing_text(hearing_tag)
        assert expected in passage

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "Non Military Affidavit"),
            (1, "Non Military Affidavit"),
            (2, "Non Military Affidavit"),
        ],
    )
    def test_get_first_event(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        hearing_tags = Wilco.get_hearing_and_event_tags(soup)
        hearing_tag = hearing_tags[0] if len(hearing_tags) > 0 else None
        assert expected in hearing_tag.text

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "Musselman, KT"),
            (1, "Musselman, KT"),
            (2, "Musselman, KT"),
        ],
    )
    def test_get_hearing_officer(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        hearing_tags = Wilco.get_hearing_tags(soup)
        hearing_tag = hearing_tags[-1] if len(hearing_tags) > 0 else None
        name = Wilco.get_hearing_officer(hearing_tag)
        assert name == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "10:30 AM"),
            (1, "10:45 AM"),
            (2, "10:30 AM"),
        ],
    )
    def test_get_hearing_time(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        hearing_tags = Wilco.get_hearing_tags(soup)
        hearing_tag = hearing_tags[-1] if len(hearing_tags) > 0 else None
        time = Wilco.get_hearing_time(hearing_tag)
        assert expected == time

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "01/21/2021"),
            (1, "02/03/2021"),
            (2, "01/21/2021"),
        ],
    )
    def test_get_hearing_date(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        hearing_tags = Wilco.get_hearing_tags(soup)
        hearing_tag = hearing_tags[-1] if len(hearing_tags) > 0 else None
        hearing_date = Wilco.get_hearing_date(hearing_tag)
        assert expected == hearing_date

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, 1),
            (1, 1),
            (2, 1),
        ],
    )
    def test_get_precinct_number(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        precinct_number = Wilco.get_precinct_number(soup)
        assert expected == precinct_number

    @pytest.mark.parametrize(
        "index, hearing_index, expected",
        [
            (0, 0, False),
            (1, 0, False),
            (2, 0, False),
        ],
    )
    def test_defendant_appeared(self, index, hearing_index, expected):
        soup = load_pages.get_test_williamson(index)
        hearing_tags = Wilco.get_hearing_tags(soup)
        hearing_tag = hearing_tags[hearing_index] if len(hearing_tags) > 0 else None
        appeared = Wilco.did_defendant_appear(hearing_tag)
        assert expected == appeared

    @pytest.mark.parametrize(
        "index, defendant, expected",
        [
            (0, "Smith, Alice", "01/11/2021"),
            (0, "Jones, Beverly", "01/11/2021"),
            (1, "McDuff, Donald", "01/25/2021"),
            (2, "Barron, Carlos", "01/11/2021"),
            (2, "O'Oregon, Kristin", "01/11/2021"),
        ],
    )
    def test_defendant_served(self, index, defendant, expected):
        soup = load_pages.get_test_williamson(index)
        served = Wilco.was_defendant_served(soup)
        assert served.get(defendant) == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, []),
            (1, []),
            (2, []),
        ],
    )
    def test_alternative_service(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        served = Wilco.was_defendant_alternative_served(soup)
        assert expected == served

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "01/21/2021"),
            (1, "02/02/2021"),
            (2, "01/21/2021"),
        ],
    )
    def test_disposition_date(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        answer = Wilco.get_disposition_date(soup)
        assert expected == answer

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, Decimal("1451.61")),
            (2, Decimal("1451.61")),
        ],
    )
    def test_disposition_amount(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        amount = Wilco.get_disposition_amount(soup)
        assert expected == amount

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "Realistic Fake Name"),
            (2, "Unlikely Fake Name"),
        ],
    )
    def test_disposition_awarded_to(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        disposition_tr = Wilco.get_disposition_tr_element(soup)
        winning_party = Wilco.get_disposition_awarded_to(disposition_tr)
        assert winning_party == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "Alice Smith, et al"),
            (2, "Alice Jones, et al"),
        ],
    )
    def test_disposition_awarded_against(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        disposition_tr = Wilco.get_disposition_tr_element(soup)
        losing_party = Wilco.get_disposition_awarded_against(disposition_tr)
        assert losing_party == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, "Judgment"),
            (2, "Judgment"),
        ],
    )
    def test_disposition_type(self, index, expected):
        soup = load_pages.get_test_williamson(index)
        disposition_tr = Wilco.get_disposition_tr_element(soup)
        if disposition_tr is None:
            dt = None
        else:
            dt = Wilco.get_disposition_type(disposition_tr)
        assert dt == expected

    @pytest.mark.parametrize(
        "test_html_file_index, expected_comments",
        [
            (0, None),
            (2, None),
        ],
    )
    def test_comments(self, test_html_file_index, expected_comments):
        soup = load_pages.get_test_williamson(test_html_file_index)
        comments = Wilco.get_comments(soup)
        assert comments == expected_comments

    @pytest.mark.parametrize(
        "test_html_file_index, expected_event_details",
        [
            (0, {}),
        ],
    )
    def test_get_writ(self, test_html_file_index, expected_event_details):
        soup = load_pages.get_test_williamson(test_html_file_index)
        event_details = Wilco.get_writ(soup)
        assert event_details == expected_event_details

    @pytest.mark.parametrize(
        "test_html_file_index, expected_event_details",
        [
            (0, {}),
            (2, {}),
        ],
    )
    def test_get_writ_of_possession_service(
        self, test_html_file_index, expected_event_details
    ):
        soup = load_pages.get_test_williamson(test_html_file_index)
        event_details = Wilco.get_writ_of_possession_service(soup)
        assert event_details == expected_event_details

    @pytest.mark.parametrize(
        "test_html_file_index, expected_event_details",
        [
            (0, {}),
            (2, {}),
        ],
    )
    def test_get_writ_of_possession_requested(
        self, test_html_file_index, expected_event_details
    ):
        soup = load_pages.get_test_williamson(test_html_file_index)
        event_details = Wilco.get_writ_of_possession_requested(soup)
        assert event_details == expected_event_details

    @pytest.mark.parametrize(
        "test_html_file_index, expected_event_details",
        [
            (0, {}),
            (2, {}),
        ],
    )
    def test_get_writ_of_possession_sent_to_constable(
        self, test_html_file_index, expected_event_details
    ):
        soup = load_pages.get_test_williamson(test_html_file_index)
        event_details = Wilco.get_writ_of_possession_sent_to_constable(soup)
        assert event_details == expected_event_details

    @pytest.mark.parametrize(
        "test_html_file_index, expected_event_details",
        [
            (0, {}),
            (2, {}),
        ],
    )
    def test_get_writ_returned_to_court(
        self, test_html_file_index, expected_event_details
    ):
        soup = load_pages.get_test_williamson(test_html_file_index)
        event_details = Wilco.get_writ_returned_to_court(soup)
        assert event_details == expected_event_details

    @pytest.mark.parametrize(
        "test_html_file_index, expected_attorneys",
        [
            (0, {}),
            (2, {}),
        ],
    )
    def test_get_attorneys_for_defendants(
        self, test_html_file_index, expected_attorneys
    ):
        soup = load_pages.get_test_williamson(test_html_file_index)
        attorneys = Wilco.get_attorneys_for_defendants(soup)
        assert attorneys == expected_attorneys

    @pytest.mark.parametrize(
        "test_html_file_index, expected_attorneys",
        [
            (0, {}),
            (2, {}),
        ],
    )
    def test_get_attorneys_for_plaintiffs(
        self, test_html_file_index, expected_attorneys
    ):
        soup = load_pages.get_test_williamson(test_html_file_index)
        attorneys = Wilco.get_attorneys_for_plaintiffs(soup)
        assert attorneys == expected_attorneys

    @pytest.mark.parametrize(
        "test_html_file_index, plaintiff, disposition_date",
        [
            (0, "Name, Realistic Fake", "01/21/2021"),
            (1, "Fox, Michael A", "02/02/2021"),
            (2, "Fake Name, Unlikely", "01/21/2021"),
        ],
    )
    def test_make_parsed_case(self, test_html_file_index, plaintiff, disposition_date):
        soup = load_pages.get_test_williamson(test_html_file_index)
        parsed_case = Wilco.make_parsed_case(soup=soup)
        assert parsed_case["plaintiff"] == plaintiff
        assert parsed_case["disposition_date"] == disposition_date
