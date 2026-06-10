"""Public password generator tool (rate limited, no capability gate)."""

from fastapi import APIRouter, Depends

from app.core.rate_limit import rate_limit_api
from app.schemas.password_generator import (
    PasswordGeneratorRequest,
    PasswordGeneratorResponse,
)
from app.services.password_generator import generate_password

router = APIRouter(
    prefix="/password-generator",
    tags=["password-generator"],
    dependencies=[Depends(rate_limit_api)],
)


@router.post(
    "",
    response_model=PasswordGeneratorResponse,
    summary="Generate a random password",
    description="Public password generator endpoint (rate limited).",
)
async def generate(data: PasswordGeneratorRequest) -> PasswordGeneratorResponse:
    password = generate_password(
        data.length,
        uppercase=data.uppercase,
        lowercase=data.lowercase,
        digits=data.digits,
        symbols=data.symbols,
        exclude_ambiguous=data.exclude_ambiguous,
    )
    return PasswordGeneratorResponse(password=password, length=len(password))
