from collections.abc import Collection, Iterable
from typing import Protocol

from pydantic import BaseModel


class AISuggestable[T: BaseModel, S: BaseModel](Protocol):
    @property
    def data(self) -> T: ...

    @property
    def source_data(self) -> Iterable[S]: ...

    @property
    def suggestable_fields(self) -> Collection[str]: ...
