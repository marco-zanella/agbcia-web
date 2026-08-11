from agbcia_web.title_id_hash import default_title_id


def test_default_title_id_matches_native_vc_pattern():
    title_id = default_title_id("TEST", "01")
    assert title_id[0:4] == bytes.fromhex("00040000")
    assert title_id[4] == 0x00
    assert title_id[5] & 0xF0 == 0xF0
    assert title_id[7] == 0x00


def test_default_title_id_is_deterministic():
    assert default_title_id("TEST", "01") == default_title_id("TEST", "01")


def test_default_title_id_varies_with_input():
    assert default_title_id("TEST", "01") != default_title_id("OTHR", "01")
