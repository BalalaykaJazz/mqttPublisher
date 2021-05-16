"""
Client authorization on the server
"""

import hmac
import base64
from config import get_settings

CODE = "latin_1"


def client_authenticate(client_user: str, client_token_b64: str) -> bool:
    """
    Login and password verification.
    User must be specified in the system.
    The password received from the client must match the server password.
    """

    server_token_b64 = users.get(client_user)

    if not server_token_b64:
        return False

    correct_token_hash = base64.b64decode(server_token_b64)
    received_token_hash = base64.b64decode(client_token_b64)

    return hmac.compare_digest(correct_token_hash, received_token_hash)


users = get_settings("registered_users")
