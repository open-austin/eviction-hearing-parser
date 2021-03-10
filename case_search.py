def get_register_url(status_soup) -> str:
    link_tag = status_soup.find(style="color: blue")
    relative_link = link_tag.get("href")
    return "https://odysseypa.traviscountytx.gov/JPPublicAccess/" + relative_link


def get_status_and_type(status_soup) -> str:
    tds = status_soup.find_all("td")
    divs = tds[-1].find_all("div")
    status, casetype = divs[1].text, divs[0].text
    return status, casetype
