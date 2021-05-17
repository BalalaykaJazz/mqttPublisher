"""
Client authorization on the server
"""

import hmac
from config import get_settings


def client_authenticate(client_user: str, received_token_hash: str) -> bool:
    """
    Login and password verification.
    User must be specified in the system.
    The password received from the client must match the server password.
    """

    correct_token_hash = users.get(client_user)

    if not correct_token_hash or not received_token_hash:
        return False

    return hmac.compare_digest(correct_token_hash, received_token_hash)


users = get_settings("registered_users")
