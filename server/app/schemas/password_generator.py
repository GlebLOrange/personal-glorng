from pydantic import BaseModel, ConfigDict, Field


class PasswordGeneratorRequest(BaseModel):
    length: int = Field(default=16, ge=8, le=128)
    uppercase: bool = True
    lowercase: bool = True
    digits: bool = True
    symbols: bool = True
    exclude_ambiguous: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "length": 16,
                "uppercase": True,
                "lowercase": True,
                "digits": True,
                "symbols": True,
                "exclude_ambiguous": False,
            }
        }
    )


class PasswordGeneratorResponse(BaseModel):
    password: str
    length: int

    model_config = ConfigDict(
        json_schema_extra={"example": {"password": "aB3!xY9@mN2#pQ7&", "length": 16}}
    )
