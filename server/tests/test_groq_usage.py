"""Unit tests for Groq usage parsing and list-price estimates."""

from app.services.ai_chat import (
    GroqUsage,
    _parse_stream_line,
    estimate_groq_cost_usd,
    parse_groq_usage,
)


def test_parse_groq_usage_splits_cached_and_reasoning() -> None:
    """Map provider usage fields into uncached, cached, and reasoning counts."""
    usage = parse_groq_usage(
        {
            "prompt_tokens": 100,
            "completion_tokens": 40,
            "prompt_tokens_details": {"cached_tokens": 70},
            "completion_tokens_details": {"reasoning_tokens": 15},
        },
    )
    assert usage == GroqUsage(
        prompt_tokens=100,
        cached_tokens=70,
        uncached_tokens=30,
        completion_tokens=40,
        reasoning_tokens=15,
    )


def test_parse_groq_usage_clamps_cached_above_prompt() -> None:
    """Ignore cached counts larger than the prompt total."""
    usage = parse_groq_usage(
        {
            "prompt_tokens": 10,
            "completion_tokens": 2,
            "prompt_tokens_details": {"cached_tokens": 99},
        },
    )
    assert usage is not None
    assert usage.cached_tokens == 10
    assert usage.uncached_tokens == 0


def test_parse_groq_usage_rejects_non_objects() -> None:
    """Return None when usage is missing or malformed."""
    assert parse_groq_usage(None) is None
    assert parse_groq_usage("nope") is None


def test_estimate_groq_cost_usd_uses_cached_rate() -> None:
    """Bill cached tokens at half the uncached input list price."""
    usage = GroqUsage(
        prompt_tokens=1_000_000,
        cached_tokens=500_000,
        uncached_tokens=500_000,
        completion_tokens=1_000_000,
        reasoning_tokens=0,
    )
    # 0.5 * 0.15 + 0.5 * 0.075 + 1.0 * 0.60 = 0.7125
    assert estimate_groq_cost_usd("openai/gpt-oss-120b", usage) == 0.7125


def test_estimate_groq_cost_usd_unknown_model() -> None:
    """Skip dollar estimates for models without a known list price."""
    usage = GroqUsage(1, 0, 1, 1, 0)
    assert estimate_groq_cost_usd("unknown-model", usage) is None


def test_parse_stream_line_reads_usage_without_text() -> None:
    """Capture a final usage-only SSE chunk without inventing text."""
    line = (
        'data: {"choices":[],"usage":{"prompt_tokens":12,"completion_tokens":3,'
        '"prompt_tokens_details":{"cached_tokens":8}}}'
    )
    text, usage = _parse_stream_line(line)
    assert text is None
    assert usage == GroqUsage(
        prompt_tokens=12,
        cached_tokens=8,
        uncached_tokens=4,
        completion_tokens=3,
        reasoning_tokens=0,
    )
