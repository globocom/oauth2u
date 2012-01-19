import uuid


def generate_authorization_code():
    return generate_uuid_without_dashes()

def generate_access_token():
    return generate_uuid_without_dashes()

def generate_uuid_without_dashes():
	return str(uuid.uuid4()).replace('-', '')