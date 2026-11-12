from typing import Protocol, Literal


class IResource[TId](Protocol):
    @classmethod
    def model_class(cls): ...

    @property
    def model(self): ...

    @property
    def stored(self) -> bool: ...

    @property
    def id_type(self) -> type[TId]: ...


class FreeResource[TId](IResource[TId], Protocol):
    @property
    def stored(self) -> Literal[False]: ...


class PersistedResource[TId](IResource[TId], Protocol):
    @property
    def id(self) -> TId: ...

    @property
    def stored(self) -> Literal[True]: ...


type Resource[TId] = FreeResource[TId] | PersistedResource[TId]
