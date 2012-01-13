import oauth2u


def test_should_have_optional_port():
    server = oauth2u.Server()
    assert 8000 == server.port


def test_should_accept_custom_port():
    server = oauth2u.Server(8888)
    assert 8888 == server.port

