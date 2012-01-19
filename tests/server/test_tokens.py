import re
from oauth2u.tokens import generate_authorization_code, generate_access_token


def test_authorization_code_should_be_alphanumeric_code_greater_than_19_chars():
    code = generate_authorization_code()
    assert re.match(r'[a-zA-Z0-9]{20,}', code)

def test_access_token_should_be_alphanumeric_code_greater_than_19_chars():
    code = generate_access_token()
    assert re.match(r'[a-zA-Z0-9]{20,}', code)
