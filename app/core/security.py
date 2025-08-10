from authlib.jose import jwt
import uuid
from datetime import datetime, timedelta
from app.core.config import SECRET_KEY, ALGORITHM
from app.models.user import User
from fastapi import Depends,HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


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


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print(token)
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception
    
    print(payload)
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user