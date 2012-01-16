import uuid


def generate_authorization_code():
    return str(uuid.uuid4()).replace('-', '')

def generate_access_token():
    return str(uuid.uuid4()).replace('-', '')
