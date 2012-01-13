import uuid


def generate_authorization_code():
    return str(uuid.uuid4()).replace('-', '')
