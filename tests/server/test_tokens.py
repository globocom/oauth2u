import re
from oauth2u.tokens import generate_authorization_code


def test_should_generate_alphanumeric_code_greater_than_19_chars(monkeypatch):
    code = generate_authorization_code()
    assert re.match(r'[a-zA-Z0-9]{20,}', code)
