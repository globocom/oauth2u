AUTHORIZATIONS = {}


def save_authorization(code, client_id, redirect_uri):
    AUTHORIZATIONS[code] = {
        'client_id': client_id,
        'redirect_uri': redirect_uri}


def find_authorization(code):
    return AUTHORIZATIONS.get(code)


def is_code_used(code):
    return AUTHORIZATIONS[code].get('used', False)


def mark_as_used(code):
    AUTHORIZATIONS[code]['used'] = True
