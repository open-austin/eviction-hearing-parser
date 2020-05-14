from bs4 import BeautifulSoup


class TestLoadHTML:
    def test_html_has_title(self, soup):
        tag = soup.div
        assert tag.text == "Register of Actions"