import json
from datetime import datetime

from openai import AsyncOpenAI, OpenAIError
from pydantic import ValidationError

from .errors import AzureResponsesError, LLMConfigurationError, ModelOutputError
from .model import FieldSuggestion, SuggestedValue
from .settings import LLMSettings
from .typings import AISuggestable

__all__ = [
    "AISuggestable",
    "AzureResponsesError",
    "FieldSuggestion",
    "LLMConfigurationError",
    "LLMSettings",
    "ModelOutputError",
    "SuggestedValue",
]


async def _suggest(
    *,
    client: AsyncOpenAI,
    resource_id: int,
    field: str,
    detail_view: AISuggestable,
    observed_at: datetime,
    settings: LLMSettings,
) -> FieldSuggestion:
    field_info = type(detail_view.data).model_fields[field]
    description = field_info.description or field
    coalesced = json.dumps(detail_view.data.model_dump(mode="json"))
    sources = json.dumps([source.model_dump(mode="json") for source in detail_view.source_data])
    try:
        response = await client.responses.parse(
            model=settings.azure_openai_model or "",
            instructions=(
                f"You infer the `{field}` value for one oil and gas field. That field "
                f"means: {description} Search the public web for evidence and cite "
                f"every page you use. Return a null value unless a public citation "
                f"supports it. Infer no field other than `{field}`."
            ),
            input=(
                f"Coalesced Stitch record:\n{coalesced}\n\nSource records behind it:\n{sources}"
            ),
            tools=[{"type": "web_search"}],
            text_format=SuggestedValue[field_info.annotation],
            store=False,
        )
    except OpenAIError as exc:
        raise AzureResponsesError("Azure Responses request failed.") from exc
    except ValidationError as exc:
        raise ModelOutputError("Model output did not match the field schema.") from exc

    parsed = response.output_parsed
    if parsed is None:
        raise ModelOutputError("Model returned no parsed output.")

    cited = bool(parsed.citations)
    return FieldSuggestion(
        resource_id=resource_id,
        field=field,
        value=parsed.value if cited else None,
        citations=parsed.citations if cited else [],
        model=response.model,
        rationale=parsed.rationale,
        observed_at=observed_at,
        foundry_response=response.model_dump(mode="json"),
    )
