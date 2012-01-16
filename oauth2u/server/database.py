AUTHORIZATIONS = {}


def save_authorization(code, client_id, redirect_uri):
    AUTHORIZATIONS[code] = {'client_id': client_id, 'redirect_uri': redirect_uri}


def find_authorization(code):
    return AUTHORIZATIONS.get(code)
