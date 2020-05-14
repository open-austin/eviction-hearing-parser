import hearing


class TestLoadHTML:
    def test_html_has_title(self, soup):
        tag = soup.div
        assert tag.text == "Register of Actions"


class TestParseHTML:
    def test_get_plaintiff(self, soup):
        plaintiff = hearing.get_plaintiff(soup)
        assert plaintiff == "Doe, John G."
