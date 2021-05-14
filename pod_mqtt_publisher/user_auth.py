"""
Client authorization on the server
"""

import hashlib
import hmac
from config import get_settings

CODE = "latin_1"


def client_authenticate(client_user: str, client_password: str) -> bool:
    """
    Login and password verification.
    User must be specified in the system.
    The password received from the client must match the server password.
    """

    user_password = users.get(client_user)

    if not user_password:
        return False

    raw_client_password = client_password.encode(CODE)

    client_salt = raw_client_password[:32]
    client_key = raw_client_password[32:]

    new_key = hashlib.pbkdf2_hmac("sha256",
                                  user_password.encode(CODE),
                                  client_salt,
                                  100000)

    return hmac.compare_digest(new_key, client_key)


users = get_settings("registered_users")
