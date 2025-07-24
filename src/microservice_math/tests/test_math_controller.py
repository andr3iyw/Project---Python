import pytest
import asyncio
from app.controllers import math_controller

@pytest.mark.asyncio
async def test_compute_pow():
    result = await math_controller.compute_pow(2, 4)
    assert result == 16

@pytest.mark.asyncio
async def test_compute_factorial():
    assert await math_controller.compute_factorial(0) == 1
    assert await math_controller.compute_factorial(1) == 1
    assert await math_controller.compute_factorial(3) == 6
    assert await math_controller.compute_factorial(5) == 120

@pytest.mark.asyncio
async def test_compute_fibonacci():
    assert await math_controller.compute_fibonacci(0) == 0
    assert await math_controller.compute_fibonacci(1) == 1
    assert await math_controller.compute_fibonacci(6) == 8
    assert await math_controller.compute_fibonacci(10) == 55