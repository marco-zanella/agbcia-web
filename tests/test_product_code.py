from agbcia_web.product_code import default_product_code


def test_default_product_code_from_four_char_game_code():
    assert default_product_code("TEST") == "CTR-N-TEST"


def test_default_product_code_falls_back_for_unusual_game_code():
    assert default_product_code("AB") == "CTR-N-AGBC"
