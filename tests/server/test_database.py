from oauth2u.server import database


def test_find_should_return_none_if_no_authorization_is_created():
    auth = database.find_authorization(code='1234')

    assert auth is None


def test_should_be_able_to_save_and_retrieve_authorizations():
    database.save_authorization(code='1234', client_id='client1',
                                redirect_uri='http://callback/return')

    auth = database.find_authorization(code='1234')

    assert 'client1' == auth['client_id']
    assert 'http://callback/return' == auth['redirect_uri']

def test_new_authorizations_are_not_flagged_as_used():
    database.save_authorization(code='1234', client_id='client1',
                                redirect_uri='http://callback/return')

    assert False == database.is_code_used('1234')

def test_should_be_possible_to_mark_authorization_as_used():
    database.save_authorization(code='1234', client_id='client1',
                                redirect_uri='http://callback/return')

    database.mark_as_used(code='1234')

    assert True == database.is_code_used('1234')
