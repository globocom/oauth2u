
DATABASE = {}

def save_client_information(client_id, authorization_code,
                            authorization_code_generation_date,
                            redirect_uri,
                            redirect_uri_with_code):
    DATABASE[client_id] = {
        'authorization_code': authorization_code,
        'authorization_code_generation_date': authorization_code_generation_date,
        'redirect_uri': redirect_uri,
        'redirect_uri_with_code': redirect_uri_with_code,
        }

def find_client(client_id):
    return DATABASE.get(client_id)

def mark_authorization_code_as_used(client_id):
    DATABASE[client_id]['authorization_code_user'] = True

def is_authorization_code_used(client_id):
    return DATABASE[client_id].get('authorization_code_user', False)
