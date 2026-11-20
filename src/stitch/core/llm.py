import asyncio
from collections.abc import Collection
from datetime import UTC, datetime
from functools import lru_cache

from openai import AsyncOpenAI

from ._internal.llm import (
    AISuggestable,
    AzureResponsesError,
    FieldSuggestion,
    LLMConfigurationError,
    LLMSettings,
    ModelOutputError,
    _suggest,
)

__all__ = [
    "AISuggestable",
    "AzureResponsesError",
    "FieldSuggestion",
    "LLMConfigurationError",
    "LLMSettings",
    "ModelOutputError",
    "get_llm_client",
    "get_llm_settings",
    "suggest_missing_field_values",
]


@lru_cache
def get_llm_settings() -> LLMSettings:
    return LLMSettings()


@lru_cache
def get_llm_client() -> AsyncOpenAI:
    settings = get_llm_settings()
    if not settings.azure_openai_configured:
        raise LLMConfigurationError("Azure OpenAI settings are not configured.")
    assert settings.azure_openai_base_url is not None
    assert settings.azure_openai_api_key is not None
    return AsyncOpenAI(
        base_url=str(settings.azure_openai_base_url),
        api_key=settings.azure_openai_api_key.get_secret_value(),
        timeout=settings.azure_openai_timeout_seconds,
        max_retries=0,
    )


async def suggest_missing_field_values(
    *,
    resource_id: int,
    detail_view: AISuggestable,
    fields: Collection[str],
) -> list[FieldSuggestion]:

    requested = set(fields)
    targets = [
        field
        for field in detail_view.suggestable_fields
        if field in requested and getattr(detail_view.data, field) is None
    ]
    if not targets:
        return []

    client = get_llm_client()
    observed_at = datetime.now(UTC)
    calls = [
        _suggest(
            client=client,
            resource_id=resource_id,
            field=field,
            detail_view=detail_view,
            observed_at=observed_at,
            settings=get_llm_settings(),
        )
        for field in targets
    ]
    return list(await asyncio.gather(*calls))
