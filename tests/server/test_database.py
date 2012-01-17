import datetime
from oauth2u.server import database

def test_find_client_return_None_if_no_client_id_found():
    assert database.find_client('no-client-id') is None


def test_should_save_and_retrieve_clients_informations():
    client_information =  {
        'authorization_code': 'authorization-code',
        'authorization_code_generation_date': datetime.datetime.utcnow(),
        'redirect_uri': 'http://example.com/redirect-uri',
        'redirect_uri_with_code': 'http://example.com/redirect-uri?code=authorization-code'
        }

    database.save_client_information('client-id-1', **client_information)
    assert client_information == database.find_client('client-id-1')


def new_client_authorization_code_are_not_marked_as_used():
    database.save_client_information('client-id-1', 
                                     'authorization-code',
                                     datetime.datetime.utcnow(),
                                     'http://example.com/redirect-uri',
                                     'http://example.com/redirect-uri?code=authorization-code')
    assert not database.is_authorization_code_used('client-id-1')


def test_should_mark_client_authorization_code_as_used():
    database.save_client_information('client-id-1', 
                                     'authorization-code',
                                     datetime.datetime.utcnow(),
                                     'http://example.com/redirect-uri',
                                     'http://example.com/redirect-uri?code=authorization-code')
    database.mark_authorization_code_as_used('client-id-1')

    assert database.is_authorization_code_used('client-id-1')
