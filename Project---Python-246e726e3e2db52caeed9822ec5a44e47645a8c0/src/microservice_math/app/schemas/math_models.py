from pydantic import BaseModel, field_validator

class PowInput(BaseModel):
    base: float
    exponent: float

class FactorialInput(BaseModel):
    n: int

    @field_validator("n")
    def validate_positive(cls, v):
        if v < 0:
            raise ValueError("n must be non-negative")
        return v

class FibonacciInput(BaseModel):
    n: int

    @field_validator("n")
    def validate_positive(cls, v):
        if v < 0:
            raise ValueError("n must be non-negative")
        return v