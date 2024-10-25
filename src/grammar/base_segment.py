import csv
from abc import ABC
from typing import Any, List

from pydantic import BaseModel, model_validator, ConfigDict, field_validator


class BaseSegment(BaseModel, ABC):
    symbol: str

    model_config = ConfigDict(
        extra="forbid",  # disallow extra fields
        frozen=True,  # make immutable
    )

    @field_validator("*", mode="before")
    @classmethod
    def parse_bool(cls, item: Any) -> Any:
        if item == "+":
            return True
        elif item == "-":
            return False
        return item

    def __getitem__(self, key: int | str):
        if type(key) == str:
            if key in self.model_fields_set:
                # todo: save this as a dict on init, instead of using getattr
                return getattr(self, key)
            else:
                raise KeyError(key)
        if type(key) == int:
            # todo: calculate this list once on init, instead of recalculating every time
            features = [x for x in self.model_dump().values() if type(x) == bool]
            return features[key]
