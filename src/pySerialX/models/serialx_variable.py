from dataclasses import dataclass
from typing import TypeVar, Generic, Type

T = TypeVar("T")

@dataclass
class SerialXVariables(Generic[T]):
    name: str
    type: Type[T]
    value: T
    can_set: bool