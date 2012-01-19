import datetime
from oauth2u.server import database

def test_find_client_return_None_if_no_client_id_found():
    assert database.find_client('no-client-id') is None


def test_should_save_and_retrieve_client_authorization_code():
    assert not database.find_client('client-id')

    database.save_new_authorization_code(
        'auth-code-1nmb21', 'client-id',
        'http://example.com/return',
        'http://example.com/return?code=auth-code-1nmb21')

    assert database.find_client('client-id')
    assert 1 == database.client_authorization_codes_count('client-id')
    assert database.client_has_authorization_code('client-id', 'auth-code-1nmb21')


def test_new_client_authorization_code_are_not_marked_as_used():
    database.save_new_authorization_code(
        'auth-code-1nmb21', 'client-id',
        'http://example.com/return',
        'http://example.com/return?code=auth-code-1nmb21')

    assert database.client_has_authorization_code('client-id', 'auth-code-1nmb21')
    assert not database.is_client_authorization_code_used('client-id', 'auth-code-1nmb21')


def test_should_mark_client_authorization_code_as_used():
    database.save_new_authorization_code(
        'auth-code-1nmb21', 'client-id',
        'http://example.com/return',
        'http://example.com/return?code=auth-code-1nmb21')
    database.mark_client_authorization_code_as_used('client-id', 'auth-code-1nmb21')

    assert database.client_has_authorization_code('client-id', 'auth-code-1nmb21')
    assert database.is_client_authorization_code_used('client-id', 'auth-code-1nmb21')
