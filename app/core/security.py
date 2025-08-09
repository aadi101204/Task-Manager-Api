from authlib.jose import jwt
import uuid
from datetime import datetime, timedelta
from app.core.config import SECRET_KEY, ALGORITHM

def create_access_token(data: dict):
    header = {"alg": ALGORITHM}
    payload = data.copy()
    now = datetime.now()
    expire = now + timedelta(minutes=30)
    payload.update({
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "jti": str(uuid.uuid4())
    })
    token = jwt.encode(header, payload, SECRET_KEY)
    return token.decode("utf-8") if isinstance(token, bytes) else token

def decode_access_token(token: str):
    try:
        claims = jwt.decode(token, SECRET_KEY)
        claims.validate()
        return claims
    except Exception as e:
        return str(e)
