import json

from pydantic import BaseModel, root_validator


class JsonStringModel(BaseModel):
    @root_validator(pre=True)
    def parse_json(cls, values):  # pylint: disable=no-self-argument
        if isinstance(values, str):
            try:
                return json.loads(values)
            except json.JSONDecodeError:
                pass
        return values
