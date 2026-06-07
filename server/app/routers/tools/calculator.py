"""Public calculator tool (rate limited, no capability gate)."""

import math
from typing import Any

from fastapi import APIRouter, Depends

from app.core.exceptions import ValidationError
from app.core.rate_limit import rate_limit_api

router = APIRouter(
    prefix="/calculator",
    tags=["calculator"],
    dependencies=[Depends(rate_limit_api)],
)

ALLOWED_OPS = {"+", "-", "*", "/"}
_MAX_FLOAT = 1e15


@router.post(
    "",
    summary="Evaluate arithmetic expression",
    description="Public calculator endpoint (rate limited).",
)
async def calculate(
    a: float,
    b: float,
    op: str,
) -> dict[str, Any]:
    if op not in ALLOWED_OPS:
        raise ValidationError(f"Invalid operator: {op}. Allowed: {ALLOWED_OPS}")

    if any(math.isnan(v) or math.isinf(v) for v in (a, b)):
        raise ValidationError("NaN and Infinity are not allowed")

    if abs(a) > _MAX_FLOAT or abs(b) > _MAX_FLOAT:
        raise ValidationError(f"Values must be between -{_MAX_FLOAT} and {_MAX_FLOAT}")

    if op == "/" and b == 0:
        raise ValidationError("Division by zero")

    match op:
        case "+":
            result = a + b
        case "-":
            result = a - b
        case "*":
            result = a * b
        case "/":
            result = a / b
        case _:
            raise ValidationError(f"Unhandled operator: {op}")

    if math.isnan(result) or math.isinf(result):
        raise ValidationError("Result is out of representable range")

    return {"a": a, "b": b, "op": op, "result": result}
