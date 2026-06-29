import json
import os
from decimal import Decimal
from typing import Optional, Tuple

# USD per 1,000,000 tokens: model -> (input_rate, output_rate)
MODEL_PRICING = {
    "gemini-2.5-flash": (0.30, 2.50),
    "gemini-2.5-flash-lite": (0.10, 0.40),
    "gemini-2.5-pro": (1.25, 10.00),
    "gemini-1.5-flash": (0.075, 0.30),
    "gemini-1.5-pro": (1.25, 5.00),
}


def _rates(model: str) -> Optional[Tuple[float, float]]:
    if not model:
        return None
    if model in MODEL_PRICING:
        return MODEL_PRICING[model]
    # Fall back to a prefix match (e.g. "gemini-2.5-flash-preview-..." -> flash)
    for key, rates in MODEL_PRICING.items():
        if model.startswith(key):
            return rates
    return None


def estimate_cost(
    model: str, prompt_tokens: int, completion_tokens: int
) -> Optional[Decimal]:
    """Return estimated USD cost, or None if the model price is unknown."""
    rates = _rates(model or "")
    if rates is None:
        return None
    in_rate, out_rate = rates
    cost = (
        Decimal(int(prompt_tokens or 0)) * Decimal(str(in_rate))
        + Decimal(int(completion_tokens or 0)) * Decimal(str(out_rate))
    ) / Decimal(1_000_000)
    return cost.quantize(Decimal("0.000001"))
