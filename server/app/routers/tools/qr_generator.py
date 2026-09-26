"""Public QR code generator (Segno, rate limited, ephemeral)."""

from fastapi import APIRouter, Depends

from app.core.rate_limit import rate_limit_api
from app.schemas.qr_generator import QrCodeCreate, QrCodeGenerateResponse
from app.services.qr_generator import generate_qr

router = APIRouter(
    prefix="/qr-generator",
    tags=["qr-generator"],
    dependencies=[Depends(rate_limit_api)],
)


@router.post(
    "",
    response_model=QrCodeGenerateResponse,
    status_code=200,
    summary="Generate QR code",
    description=(
        "Public QR generation (rate limited). Inline SVG in JSON; payload not stored."
    ),
)
async def generate_qr_code(data: QrCodeCreate) -> QrCodeGenerateResponse:
    return generate_qr(data)
