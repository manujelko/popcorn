import os

from dotenv import load_dotenv

load_dotenv()


def getenv(envvar: str) -> str:
    value = os.getenv(envvar)
    if value is None:
        raise EnvironmentError(f"{envvar} should be defined")
    return value


SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
