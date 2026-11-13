from collections.abc import Collection, Sequence
from typing import Any, Protocol, overload

from .repositories import (
    ResourceRepository,
    SourceRepository,
    UserRepository,
)

type ResourceQueryParams = Any
type SourceQueryParams = Any
type MergeQueryParams = Any


class PersistenceFacade[TResource, TSource, TMerge, TId](Protocol):
    __resource_model__: type[TResource]
    __source_model__: type[TSource]
    _users: UserRepository
    _resources: ResourceRepository[TResource, TId]
    _sources: SourceRepository[TSource]

    async def query_resources(
        self, params: ResourceQueryParams, offset: int = 0, limit: int | None = None
    ) -> Collection[TResource]:
        pass

    async def query_resource_values(self, params: ResourceQueryParams) -> Collection[TResource]:
        """For filter options."""
        pass

    async def query_sources(
        self, params: SourceQueryParams, offset: int = 0, limit: int | None = None
    ) -> Collection[TSource]:
        pass

    async def query_merges(
        self, params: MergeQueryParams, offset: int = 0, limit: int | None = None
    ) -> Collection[TMerge]:
        pass

    async def get_resource(self, id: TId) -> TResource:
        pass

    async def get_source(self, id: TId) -> TSource:
        pass

    async def get_merge(self, id: TId) -> TMerge:
        pass

    @overload
    async def merge_resources(self, resources: Sequence[TResource], /) -> TResource:
        pass

    @overload
    async def merge_resources(self, ids: Sequence[TId], /) -> TResource:
        pass

    async def undo_merge(self, id: TId): ...

    async def unmerge_resource(self, id: TId): ...

    async def attach_source_to_resource(self): ...
