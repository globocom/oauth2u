
DATABASE = {}

def find_client(client_id):
    return DATABASE.get(client_id)

def save_new_authorization_code(auth_code, client_id, redirect_uri, redirect_uri_with_code):
    DATABASE.setdefault(client_id, {})
    auth_code_info = {
        'redirect_uri': redirect_uri,
        'redirect_uri_with_code': redirect_uri_with_code,
        }
    DATABASE[client_id].setdefault('authorization_codes', {})
    DATABASE[client_id]['authorization_codes'][auth_code] = auth_code_info

def client_has_authorization_code(client_id, auth_code):
    return auth_code in DATABASE[client_id]['authorization_codes']

def client_authorization_codes_count(client_id):
    return len(DATABASE[client_id]['authorization_codes'])

def mark_client_authorization_code_as_used(client_id, auth_code):
    DATABASE[client_id]['authorization_codes'][auth_code]['used'] = True

def is_client_authorization_code_used(client_id, auth_code):
    return DATABASE[client_id]['authorization_codes'][auth_code].get('used', False)

def client_has_redirect_uri_for_code(client_id, auth_code, redirect_uri):
    return DATABASE[client_id]['authorization_codes'][auth_code]['redirect_uri'] == redirect_uri

def get_redirect_uri_with_code(client_id, auth_code):
    return DATABASE[client_id]['authorization_codes'][auth_code]['redirect_uri_with_code']