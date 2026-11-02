"""Schemas for the admin maintenance endpoints."""

from typing import Literal

from pydantic import BaseModel, Field

MaintenanceStatus = Literal["idle", "running", "ok", "failed"]
MaintenanceJob = Literal["backup", "stale", "sync", "cleanup", "seed"]


class MaintenanceStatusResponse(BaseModel):
    """Public site key plus run status for the admin panel."""

    site_key: str = ""
    enabled: bool = False
    host_jobs_ready: bool = False
    status: MaintenanceStatus = "idle"
    detail: str = ""
    job: str = ""
    report: str = ""


class MaintenanceRunRequest(BaseModel):
    """Turnstile token and which maintenance job to run."""

    turnstile_token: str = Field(min_length=1, max_length=2048)
    job: MaintenanceJob


class MaintenanceRunResponse(BaseModel):
    """Accepted run acknowledgement."""

    status: MaintenanceStatus
    detail: str = ""
    job: str = ""
    report: str = ""
