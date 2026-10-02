"""Schemas for the admin DB maintenance endpoints."""

from typing import Literal

from pydantic import BaseModel, Field

MaintenanceStatus = Literal["idle", "running", "ok", "failed"]


class MaintenanceStatusResponse(BaseModel):
    """Public site key plus run status for the admin panel."""

    site_key: str = ""
    enabled: bool = False
    status: MaintenanceStatus = "idle"
    detail: str = ""


class MaintenanceRunRequest(BaseModel):
    """Turnstile token from the admin panel widget."""

    turnstile_token: str = Field(min_length=1, max_length=2048)


class MaintenanceRunResponse(BaseModel):
    """Accepted run acknowledgement."""

    status: MaintenanceStatus
    detail: str = ""
