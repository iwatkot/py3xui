import os
from typing import Any, Callable


def parse_env(
    keys: list[str],
    postprocess_fn: Callable[[str], Any],
) -> Any | None:
    """Parse the environment for the first key that is found and return the value after
    postprocessing it.

    Args:
        keys (list[str]): The keys to search for in the environment
        postprocess_fn (Callable[[str], Any]): The postprocessing function to apply to the value

    Returns:
        Any | None: The postprocessed value or None
    """
    for k in keys:
        if k in os.environ:
            return postprocess_fn(os.environ[k])
    return None


def xui_host() -> str | None:
    """Get the XUI host from the environment using the following keys:
    - XUI_HOST

    Returns:
        str | None: The XUI host or None
    """
    return parse_env(
        keys=["XUI_HOST"],
        postprocess_fn=lambda x: x,
    )


def xui_username() -> str | None:
    """Get the XUI username from the environment using the following keys:
    - XUI_USERNAME

    Returns:
        str | None: The XUI username or None
    """
    return parse_env(
        keys=["XUI_USERNAME"],
        postprocess_fn=lambda x: x,
    )


def xui_password() -> str | None:
    """Get the XUI password from the environment using the following keys:
    - XUI_PASSWORD

    Returns:
        str | None: The XUI password or None
    """
    return parse_env(
        keys=["XUI_PASSWORD"],
        postprocess_fn=lambda x: x,
    )
