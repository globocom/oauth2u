import datetime
from oauth2u.server.database import MemoryDataBase

database = MemoryDataBase()

def test_find_client_return_None_if_no_client_id_found():
    assert database.find_client('no-client-id') is None


def test_should_save_and_retrieve_client_id():
    assert not database.find_client('client-id')
    callback_uri = 'http://callback.com'
    database.save_new_client('client-id', callback_uri)
    client = database.find_client('client-id')
    assert client['default_redirect_uri'] == callback_uri


def test_newly_created_client_has_no_authorization_codes():
    database.save_new_client('client-id', 'http://example.com/callback')
    assert 0 == database.client_authorization_codes_count('client-id')


def test_should_save_and_retrieve_client_authorization_code():
    database.save_new_authorization_code(
        'auth-code-1nmb21', 'client-id', 'my-state',
        'http://example.com/return')

    assert database.find_client('client-id')
    assert 1 == database.client_authorization_codes_count('client-id')
    assert database.client_has_authorization_code('client-id', 'auth-code-1nmb21')


def test_new_client_authorization_code_are_not_marked_as_used():
    database.save_new_authorization_code(
        'auth-code-1nmb21', 'client-id', 'my-state',
        'http://example.com/return')

    assert database.client_has_authorization_code('client-id', 'auth-code-1nmb21')
    assert not database.is_client_authorization_code_used('client-id', 'auth-code-1nmb21')


def test_should_mark_client_authorization_code_as_used():
    database.save_new_authorization_code(
        'auth-code-1nmb21', 'client-id', 'my-state',
        'http://example.com/return')
    database.mark_client_authorization_code_as_used('client-id', 'auth-code-1nmb21')

    assert database.client_has_authorization_code('client-id', 'auth-code-1nmb21')
    assert database.is_client_authorization_code_used('client-id', 'auth-code-1nmb21')


def test_should_get_redirect_uri_given_client_id_and_authorization_code():
    database.save_new_authorization_code(
        'auth-code', 'client-id', 'my-state',
        'http://example.com/return')
    uri = database.get_redirect_uri('client-id', 'auth-code')
    assert 'http://example.com/return' == uri


def test_should_get_state_given_client_id_and_authorization_code():
    database.save_new_authorization_code(
        'auth-code', 'client-id', 'my-state',
        'http://example.com/return')
    state = database.get_state('client-id', 'auth-code')
    assert 'my-state' == state
