from app.services.player_verification import validate_format
def test_id_format():
    assert validate_format("123456789","1234")
    assert not validate_format("abc","1234")
    assert not validate_format("12345","server")
    assert not validate_format("12","1")
