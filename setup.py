
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eviction-hearing-parser",
    version="0.1.0",
    description="parses registers of actions for Travis County eviction hearings",
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
    python_requires=">=3.7",
)
