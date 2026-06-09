"""Public calculator tool (rate limited, no capability gate)."""

import math

from fastapi import APIRouter, Depends

from app.core.exceptions import ValidationError
from app.core.rate_limit import rate_limit_api
from app.schemas.calculator import CalculatorOp, CalculatorRequest, CalculatorResponse

router = APIRouter(
    prefix="/calculator",
    tags=["calculator"],
    dependencies=[Depends(rate_limit_api)],
)

_MAX_FLOAT = 1e15


def _evaluate(a: float, b: float, op: CalculatorOp) -> float:
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

    if math.isnan(result) or math.isinf(result):
        raise ValidationError("Result is out of representable range")

    return result


@router.post(
    "",
    response_model=CalculatorResponse,
    summary="Evaluate arithmetic expression",
    description="Public calculator endpoint (rate limited).",
)
async def calculate(data: CalculatorRequest) -> CalculatorResponse:
    result = _evaluate(data.a, data.b, data.op)
    return CalculatorResponse(a=data.a, b=data.b, op=data.op, result=result)
