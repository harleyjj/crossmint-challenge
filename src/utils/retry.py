"""Retry logic with exponential backoff."""

import logging
import time
from functools import wraps
from typing import Any, Callable, Tuple, Type


def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Factor by which to multiply the wait time after each failure
        exceptions: Tuple of exception types to catch and retry on
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = logging.getLogger(func.__module__)

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}: {e}")
                        raise

                    wait_time = backoff_factor**attempt
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. "
                        f"Retrying in {wait_time:.1f}s..."
                    )
                    time.sleep(wait_time)

        return wrapper

    return decorator


def retry_on_condition(
    condition: Callable[[Any], bool], max_retries: int = 3, backoff_factor: float = 2.0
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for retrying functions based on return value condition.

    Args:
        condition: Function that returns True if retry is needed
        max_retries: Maximum number of retry attempts
        backoff_factor: Factor by which to multiply the wait time after each failure
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = logging.getLogger(func.__module__)

            for attempt in range(max_retries):
                result = func(*args, **kwargs)

                if not condition(result):
                    return result

                if attempt == max_retries - 1:
                    logger.error(
                        f"All {max_retries} attempts failed for {func.__name__} based on condition"
                    )
                    return result

                wait_time = backoff_factor**attempt
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} for {func.__name__} did not meet condition. "
                    f"Retrying in {wait_time:.1f}s..."
                )
                time.sleep(wait_time)

        return wrapper

    return decorator
