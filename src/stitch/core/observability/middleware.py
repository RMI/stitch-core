"""Per-request context and logging middleware (requires `rmi-stitch-core[asgi]`)."""

from stitch.core._internal.observability.middleware import (
    RequestContextMiddleware,
    request_id_var,
    route_var,
    scenario_var,
)

__all__ = [
    "RequestContextMiddleware",
    "request_id_var",
    "route_var",
    "scenario_var",
]
