import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Texas Eviction Hearing Parser",
    version="0.2.0",
    description="Scraper and parser for registers of actions for Texas eviction hearings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/open-austin/eviction-hearing-parse",
    packages=setuptools.find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*"]
    ),
    install_requires=[
        "BeautifulSoup4",
        "click",
        "selenium",
    ],
    python_requires=">=3.8",
)
