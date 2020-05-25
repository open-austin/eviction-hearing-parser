import parse_hearings


class TestCLI:
    def test_get_ids_to_parse(self):
        ids = parse_hearings.get_ids_to_parse(filename="test_input.csv")
        assert ids == ["J1-CV-20-001590", "J2-CV-20-001839", "J4-CV-20-000198"]
