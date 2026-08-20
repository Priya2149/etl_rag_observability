from collections.abc import Callable
from dataclasses import dataclass
from time import sleep as default_sleep
from typing import TypeVar

from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    RateLimitError,
)

ResultT = TypeVar("ResultT")


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 2
    base_delay_seconds: float = 0.5

    def delay_for(self, retry_number: int) -> float:
        return self.base_delay_seconds * (2 ** retry_number)


def is_transient_error(exc: Exception) -> bool:
    if isinstance(
        exc,
        (APIConnectionError, APITimeoutError, InternalServerError, RateLimitError),
    ):
        return True

    status_code = getattr(exc, "status_code", None)
    return status_code in {408, 409, 429} or (
        isinstance(status_code, int) and status_code >= 500
    )


def call_with_retry(
    operation: Callable[[], ResultT],
    policy: RetryPolicy,
    sleep: Callable[[float], None] = default_sleep,
) -> ResultT:
    retry_number = 0

    while True:
        try:
            return operation()
        except Exception as exc:
            if not is_transient_error(exc) or retry_number >= policy.max_retries:
                raise
            sleep(policy.delay_for(retry_number))
            retry_number += 1
