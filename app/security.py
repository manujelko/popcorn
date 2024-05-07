import datetime as dt

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
from zoneinfo import ZoneInfo

from .env import ALGORITHM, SECRET_KEY
from .models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, *, session: Session) -> User | None:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: dt.timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = dt.datetime.now(tz=ZoneInfo("UTC")) + expires_delta
    else:
        expire = dt.datetime.now(tz=ZoneInfo("UTC")) + dt.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
