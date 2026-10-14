import time, json, hmac, hashlib
import pytest
from app.security.telegram import validate_init_data
def sign(data, token):
    secret=hmac.new(b"WebAppData",token.encode(),hashlib.sha256).digest()
    check="\n".join(f"{k}={v}" for k,v in sorted(data.items()))
    data["hash"]=hmac.new(secret,check.encode(),hashlib.sha256).hexdigest()
    from urllib.parse import urlencode
    return urlencode(data)
def test_valid_init_data():
    token="test-bot-token"
    query=sign({"auth_date":str(int(time.time())),"user":json.dumps({"id":123,"first_name":"Tester"},separators=(",",":"))},token)
    assert validate_init_data(query,token)["id"]==123
def test_invalid_signature_rejected():
    with pytest.raises(ValueError):
        validate_init_data("auth_date=1&user=%7B%7D&hash=wrong","test-bot-token")
def test_expired_init_data_rejected():
    token="test-bot-token"
    query=sign({"auth_date":"1","user":json.dumps({"id":123})},token)
    with pytest.raises(ValueError):
        validate_init_data(query,token,max_age=10)
