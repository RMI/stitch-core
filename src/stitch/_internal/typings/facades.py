from typing import Any, Protocol

from .repositories import ResourceRepository, SourceRepository, UserRepository

type ResourceQueryParams = Any
type SourceQueryParams = Any
type MergeQueryParams = Any


class PersistenceFacade[TResource, TSource, TMerge](Protocol):
    _users: UserRepository
    _resources: ResourceRepository
    _sources: SourceRepository

    async def query_resources(
        self, params: ResourceQueryParams, offset: int, limit: int
    ) -> TResource:
        pass

    async def query_sources(
        self, params: SourceQueryParams, offset: int, limit: int
    ) -> TSource:
        pass

    async def query_merges(
        self, params: MergeQueryParams, offset: int, limit: int
    ) -> TMerge:
        pass

    async def get_resource(self):
        pass

    async def get_source(self):
        pass

    async def get_merge(self):
        pass
