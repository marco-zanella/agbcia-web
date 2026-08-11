from agbcia_web.gamecode_lookup import GameCodeLookup, load_default


def test_lookup_is_case_insensitive():
    lookup = GameCodeLookup({"ABCD": "Some Game"})
    assert lookup.lookup("abcd") == "Some Game"


def test_lookup_returns_none_for_unknown_code():
    lookup = GameCodeLookup({})
    assert lookup.lookup("ZZZZ") is None


def test_load_default_has_a_known_entry():
    lookup = load_default()
    assert lookup.lookup("BZ6E") is not None
