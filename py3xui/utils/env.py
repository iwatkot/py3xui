"""This module contains utility functions for parsing environment variables."""

import os
from typing import Any, Callable


def parse_env(
    keys: list[str], postprocess_fn: Callable[[str], Any], raise_if_not_found: bool = True
) -> Any:
    """Parse the environment for the first key that is found and return the value after
    postprocessing it.

    Arguments:
        keys (list[str]): The keys to search for in the environment.
        postprocess_fn (Callable[[str], Any]): The postprocessing function to apply to the value.
        raise_if_not_found (bool): Whether to raise an error if the environment
            variable is not found. Defaults to True.

    Raises:
        ValueError: If none of the keys are found in the environment and raise_if_not_found is True.

    Returns:
        Any | None: The postprocessed value or None.
    """
    for k in keys:
        if k in os.environ:
            return postprocess_fn(os.environ[k])
    if raise_if_not_found:
        raise ValueError(f"None of the keys {keys} were found in the environment.")
    return None


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


def xui_token() -> str | None:
    """Get the XUI secret token from the environment using the following keys:
    - XUI_TOKEN

    Returns:
        str | None: The XUI secret token or None if not found
    """
    return parse_env(
        keys=["XUI_TOKEN"],
        postprocess_fn=lambda x: x,
        raise_if_not_found=False,
    )


def tls_verify() -> bool | None:
    """Get the TLS verification setting from the environment using the following keys:
    - TLS_VERIFY

    Returns:
        bool | None: True if verification is required, False otherwise, or None if not set.
    """
    return parse_env(
        keys=["TLS_VERIFY"],
        postprocess_fn=lambda x: x.lower() in ["true", "1", "yes"],  # string to boolean
        raise_if_not_found=False,
    )


def tls_cert_path() -> str | None:
    """Get the path to the TLS certificate from the environment using the following keys:
    - TLS_CERT_PATH

    Returns:
        str | None: The path to the TLS certificate file, or None if not set.
    """
    return parse_env(
        keys=["TLS_CERT_PATH"],
        postprocess_fn=lambda x: x,
        raise_if_not_found=False,
    )
