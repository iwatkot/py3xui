"""This module contains utility functions for parsing environment variables."""

import os
from typing import Any, Callable


def parse_env(
    keys: list[str],
    postprocess_fn: Callable[[str], Any],
) -> Any:
    """Parse the environment for the first key that is found and return the value after
    postprocessing it.

    Arguments:
        keys (list[str]): The keys to search for in the environment
        postprocess_fn (Callable[[str], Any]): The postprocessing function to apply to the value

    Raises:
        ValueError: If none of the keys are found in the environment

    Returns:
        Any | None: The postprocessed value or None
    """
    for k in keys:
        if k in os.environ:
            return postprocess_fn(os.environ[k])
    raise ValueError(f"None of the keys {keys} were found in the environment.")


def xui_host() -> str:
    """Get the XUI host from the environment using the following keys:
    - XUI_HOST

    Raises:
        ValueError: If none of the keys are found in the environment

    Returns:
        str | None: The XUI host or None
    """
    return parse_env(
        keys=["XUI_HOST"],
        postprocess_fn=lambda x: x,
    )


def xui_username() -> str:
    """Get the XUI username from the environment using the following keys:
    - XUI_USERNAME

    Raises:
        ValueError: If none of the keys are found in the environment

    Returns:
        str | None: The XUI username or None
    """
    return parse_env(
        keys=["XUI_USERNAME"],
        postprocess_fn=lambda x: x,
    )


def xui_password() -> str:
    """Get the XUI password from the environment using the following keys:
    - XUI_PASSWORD

    Raises:
        ValueError: If none of the keys are found in the environment

    Returns:
        str | None: The XUI password or None
    """
    return parse_env(
        keys=["XUI_PASSWORD"],
        postprocess_fn=lambda x: x,
    )
