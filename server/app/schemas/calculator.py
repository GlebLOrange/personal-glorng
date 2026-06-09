from typing import Literal

from pydantic import BaseModel, ConfigDict

CalculatorOp = Literal["+", "-", "*", "/"]


class CalculatorRequest(BaseModel):
    a: float
    b: float
    op: CalculatorOp

    model_config = ConfigDict(
        json_schema_extra={"example": {"a": 10, "b": 5, "op": "+"}}
    )


class CalculatorResponse(BaseModel):
    a: float
    b: float
    op: CalculatorOp
    result: float

    model_config = ConfigDict(
        json_schema_extra={"example": {"a": 10, "b": 5, "op": "+", "result": 15}}
    )
