class MemoryDataBase(object):
    DATABASE = {}

    def find_client(self, client_id):
        return self.DATABASE.get(client_id)

    def save_new_client(self, client_id, default_redirect_uri):
        self.DATABASE.setdefault(client_id, {})
        self.DATABASE[client_id]['default_redirect_uri'] = default_redirect_uri
        self.DATABASE[client_id].setdefault('authorization_codes', {})

    def save_new_authorization_code(self, auth_code, client_id, state, redirect_uri):
        auth_code_info = {
            'redirect_uri': redirect_uri,'state':state
            }
        self.DATABASE[client_id].setdefault('authorization_codes', {})
        self.DATABASE[client_id]['authorization_codes'][auth_code] = auth_code_info

    def client_has_authorization_code(self, client_id, auth_code):
        return auth_code in self.DATABASE[client_id]['authorization_codes']

    def client_authorization_codes_count(self, client_id):
        return len(self.DATABASE[client_id]['authorization_codes'])

    def mark_client_authorization_code_as_used(self, client_id, auth_code):
        self.DATABASE[client_id]['authorization_codes'][auth_code]['used'] = True

    def is_client_authorization_code_used(self, client_id, auth_code):
        return self.DATABASE[client_id]['authorization_codes'][auth_code].get('used', False)

    def client_has_redirect_uri_for_code(self, client_id, auth_code, redirect_uri):
        return self.DATABASE[client_id]['authorization_codes'][auth_code]['redirect_uri'] == redirect_uri

    def get_state(self, client_id, auth_code):
        return self.DATABASE[client_id]['authorization_codes'][auth_code]['state']

    def get_redirect_uri(self, client_id, auth_code):
        return self.DATABASE[client_id]['authorization_codes'][auth_code]['redirect_uri']
