import os
from typing import Callable, TypeVar, cast

from dotenv import load_dotenv

load_dotenv()


T = TypeVar("T")


def getenv(
    envvar: str,
    /,
    *,
    default: str | None = None,
    allowed_values: list[str] | None = None,
    converter: Callable[[str], T] | None = None,
) -> T:
    """
    Fetches an environment variable and returns its value, converted to a specified
    type if given, only if it's one of the allowed values, otherwise returns the default
    value or raises an error.

    Args:
        envvar: The name of the environment variable.
        default: The default value to return if the environment variable is not set.
        allowed_values: A collection of strings representing allowed values.
        converter: An instance of `Converter` used to convert the value into the
            desired type. By default converts it keeps it as a string.

    Returns:
        The converted value of the environment variable or the default value.

    Raises:
        KeyError: If the environment variable's value is not set and no default is
            provided.
        ValueError: If the value is not in the allowed values or if conversion fails.
    """
    value = os.getenv(envvar, default)

    if value is None:
        if default:
            value = default
        else:
            raise KeyError(
                f"environment variable {envvar} not set and no default value provided"
            )

    if allowed_values is not None and value not in allowed_values:
        raise ValueError(
            "value {value} for environment variable {envvar} is not in allowed values"
        )

    try:
        if converter is None:
            return cast(T, value)
        else:
            return converter(value)
    except ValueError as e:
        raise ValueError(f"conversion error for value {value}") from e


SECRET_KEY: str = getenv("SECRET_KEY")
ALGORITHM: str = getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES: int = getenv(
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    default="30",
    converter=lambda x: int(x),
)
LOG_LEVEL: str = getenv(
    "LOG_LEVEL",
    default="INFO",
    allowed_values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
)
