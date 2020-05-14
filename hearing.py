import os

def get_test_html_path():
    this_directory = os.path.dirname(os.path.realpath(__file__))
    test_directory = os.path.join(this_directory, "tests", "example_register.html")
    return test_directory