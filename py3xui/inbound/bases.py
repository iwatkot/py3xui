"""This module contains the base classes for the inbound models."""

import json

from pydantic import BaseModel, model_validator


class JsonStringModel(BaseModel):
    """Base class for models that have a JSON string as a field."""

    @model_validator(mode="before")
    def model_validate(
        cls,
        values,
    ):  # pylint: disable=no-self-argument, arguments-differ
        if isinstance(values, str):
            try:
                return json.loads(values)
            except json.JSONDecodeError:
                pass
        return values
