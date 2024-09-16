from enum import Enum
from typing import Self, Any


class BaseEnum(Enum):
    @classmethod
    def __missing__(cls, value) -> Self | None:
        for member in cls:
            if isinstance(value, str) and member.value.upper() == value.upper():
                return member

        return None

    @classmethod
    def keys(cls) -> list[str]:
        return cls._member_names_

    @classmethod
    def values(cls) -> list[str]:
        return list(cls._value2member_map_.keys())

    @classmethod
    def to_dict(cls) -> dict[str, dict[str, Any]]:
        return {cls.__name__: {member.name: member. value for member in cls}}
