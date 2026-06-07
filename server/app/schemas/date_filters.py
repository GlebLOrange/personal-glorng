"""Shared query models for date and month filters."""

from datetime import date
from typing import Annotated, Self

from fastapi import Query
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from app.services.tool_expense import ToolExpenseService

_MONTH_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"


class DateRangeFilter(BaseModel):
    """Inclusive calendar date range for list filters."""

    model_config = ConfigDict(extra="forbid")

    date_from: date | None = Field(
        None,
        description="Inclusive start date (YYYY-MM-DD).",
    )
    date_to: date | None = Field(
        None,
        description="Inclusive end date (YYYY-MM-DD).",
    )

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if (
            self.date_from is not None
            and self.date_to is not None
            and self.date_from > self.date_to
        ):
            msg = "date_from must not be after date_to"
            raise ValueError(msg)
        return self


class ExpenseDateFilter(DateRangeFilter):
    """Expense list/summary/export date filters."""

    month: str | None = Field(
        None,
        pattern=_MONTH_PATTERN,
        description=(
            "Filter by calendar month (YYYY-MM). Takes precedence over date range."
        ),
    )

    def resolved_bounds(self) -> tuple[date | None, date | None]:
        if self.month:
            return ToolExpenseService.month_date_bounds(self.month)
        return self.date_from, self.date_to


class AuditDateFilter(DateRangeFilter):
    """Audit event list date filters."""


def _parse_filter(model: type[DateRangeFilter], **kwargs: object) -> DateRangeFilter:
    try:
        return model(**kwargs)
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc


def expense_date_filter(
    month: Annotated[
        str | None,
        Query(
            pattern=_MONTH_PATTERN,
            description="Filter by calendar month (YYYY-MM).",
        ),
    ] = None,
    date_from: Annotated[
        date | None,
        Query(description="Inclusive start date (YYYY-MM-DD)."),
    ] = None,
    date_to: Annotated[
        date | None,
        Query(description="Inclusive end date (YYYY-MM-DD)."),
    ] = None,
) -> ExpenseDateFilter:
    """Build validated expense date filters from query params."""
    result = _parse_filter(
        ExpenseDateFilter,
        month=month,
        date_from=date_from,
        date_to=date_to,
    )
    return result  # type: ignore[return-value]


def audit_date_filter(
    date_from: Annotated[
        date | None,
        Query(description="Inclusive start date (YYYY-MM-DD)."),
    ] = None,
    date_to: Annotated[
        date | None,
        Query(description="Inclusive end date (YYYY-MM-DD)."),
    ] = None,
) -> AuditDateFilter:
    """Build validated audit date filters from query params."""
    result = _parse_filter(
        AuditDateFilter,
        date_from=date_from,
        date_to=date_to,
    )
    return result  # type: ignore[return-value]
