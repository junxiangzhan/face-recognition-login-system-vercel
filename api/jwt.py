import base64 as __base64
import json as __json
import hmac as __hmac
import random as __random
from typing import Literal as __literal

__secret_key = __random.getrandbits(256).to_bytes(256)


def generateToken(payload) -> str:

    jwt = []
    jwt.append(__base64.b64encode(bytes(__json.dumps({'typ': 'JWT', 'alg': 'sha256'}), 'utf8')))
    jwt.append(__base64.b64encode(bytes(__json.dumps(payload), 'utf8')))

    token = b'.'.join(jwt)
    hmac_token = __hmac.digest(
        __secret_key,
        token,
        'sha256'
    )

    jwt.append(__base64.b64encode(hmac_token))

    return b'.'.join(jwt).decode()


def decodeToken(token: str) -> dict | __literal[False]:

    try:
        header_b64, payload_b64, hmac_token_b64 = token.split('.')
        header_str = __base64.b64decode(header_b64).decode()
        payload = __json.loads(__base64.b64decode(payload_b64))
        hmac_token = __base64.b64decode(hmac_token_b64)

        test_token = __hmac.digest(
            __secret_key,
            '.'.join((header_b64, payload_b64)).encode(),
            'sha256'
        )
    except Exception as e:
        return False

    if header_str != __json.dumps({'typ': 'JWT', 'alg': 'sha256'}):
        return False

    if test_token != hmac_token:
        return False

    return payload
