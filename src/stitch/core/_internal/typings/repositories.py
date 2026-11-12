from collections.abc import Collection
from typing import Any, Protocol


class UserRepository(Protocol): ...


type Params = Any


class ResourceRepository[T, TId](Protocol):
    async def create(self) -> T: ...

    async def get_one(self, id: TId) -> T: ...

    async def get_many(self, id: TId) -> Collection[T]: ...

    async def query(
        self, params: Params, limit: int = 0, offset: int | None = None
    ) -> Collection[T]: ...

    async def update(self, id: TId, item: T) -> T: ...


class SourceRepository[T](Protocol): ...
