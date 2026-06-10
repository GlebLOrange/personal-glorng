"""Named extraction profiles that pre-fill handler options."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import Any

from app.core.data_extractor.profiles.pipe_embed import (
    PIPE_EMBED_FIELD_NAMES,
    PIPE_EMBED_LIST_FIELDS,
    transform_pipe_embed_record,
)
from app.core.data_extractor.types import ExtractOptions
from app.core.exceptions import ValidationError

RecordTransform = Callable[[dict[str, Any]], dict[str, Any]]

_PROFILE_OPTIONS: dict[str, Callable[[ExtractOptions], ExtractOptions]] = {
    "pipe_embed": lambda opts: replace(
        opts,
        profile="pipe_embed",
        field_delimiter="|",
        list_delimiter=";",
        field_names=PIPE_EMBED_FIELD_NAMES,
        list_fields=PIPE_EMBED_LIST_FIELDS,
    ),
}

_RECORD_TRANSFORMS: dict[str, RecordTransform] = {
    "pipe_embed": transform_pipe_embed_record,
}


def known_profiles() -> tuple[str, ...]:
    return tuple(sorted(_PROFILE_OPTIONS))


def apply_profile(profile: str | None, options: ExtractOptions) -> ExtractOptions:
    if not profile:
        return options
    factory = _PROFILE_OPTIONS.get(profile)
    if factory is None:
        supported = ", ".join(known_profiles())
        raise ValidationError(
            f"Unknown profile '{profile}'. Supported: {supported}",
        )
    return factory(options)


def transform_record(profile: str | None, record: dict[str, Any]) -> dict[str, Any]:
    if not profile:
        return record
    transform = _RECORD_TRANSFORMS.get(profile)
    if transform is None:
        return record
    return transform(record)
