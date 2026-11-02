"""Create ignored dotenv fixtures needed by the CI test suite."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TESTS = Path(__file__).resolve().parent
TEMPLATE = ROOT / ".env.example"
TEST_JWT_KEY = "ci-jwt-key-with-more-than-thirty-two-characters"
TEST_FERNET_KEY = "ci-fernet-key-with-more-than-thirty-two-characters"
TEST_REDIS_PASSWORD = "ci-test-redis-password-long-enough"
CI_DEFAULTS = {
    "JWT_SECRET": TEST_JWT_KEY,
    "FERNET_SECRET": TEST_FERNET_KEY,
    "REDIS_PASSWORD": TEST_REDIS_PASSWORD,
    "REDIS_URL": f"redis://:{TEST_REDIS_PASSWORD}@127.0.0.1:6379/0",
    "REDIS_CACHE_URL": f"redis://:{TEST_REDIS_PASSWORD}@127.0.0.1:6380/0",
    "UNTRUSTED_URL_TOOLS_ENABLED": "false",
    "UNTRUSTED_URL_TOOLS_EGRESS_ISOLATED": "false",
    "TELEGRAM_ALLOWED_USER_ID": "123456",
    "APP_LOG_PERSIST_MIN_LEVEL": "INFO",
    "LOG_REQUESTS": "true",
}


def write_env(path: Path, **overrides: str) -> None:
    values: dict[str, str] = {}
    for line in TEMPLATE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key, value = stripped.split("=", 1)
            values[key] = value
    values.update(CI_DEFAULTS)
    values.update(overrides)
    for key, value in values.items():
        for reference, replacement in values.items():
            value = value.replace(f"${{{reference}}}", replacement)
        values[key] = value
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(f"{key}={value}" for key, value in values.items()) + "\n",
        encoding="utf-8",
    )


PRODUCTION_BASE = {
    "APP_ENV": "production",
    "JWT_SECRET": TEST_JWT_KEY,
    "FERNET_SECRET": TEST_FERNET_KEY,
    "MONGODB_PASSWORD": "ci-mongodb-password-long-enough",
    "RABBITMQ_PASSWORD": "ci-rabbitmq-password-long-enough",
    "REDIS_PASSWORD": TEST_REDIS_PASSWORD,
    "REDIS_URL": f"redis://:{TEST_REDIS_PASSWORD}@127.0.0.1:6379/0",
    "REDIS_CACHE_URL": f"redis://:{TEST_REDIS_PASSWORD}@127.0.0.1:6380/0",
    "UNTRUSTED_URL_TOOLS_ENABLED": "false",
}

write_env(
    TESTS / ".env.test",
    USE_SQLITE_TESTS="true",
    JWT_SECRET=TEST_JWT_KEY,
    FERNET_SECRET=TEST_FERNET_KEY,
    REDIS_PASSWORD=TEST_REDIS_PASSWORD,
    REDIS_URL=f"redis://:{TEST_REDIS_PASSWORD}@127.0.0.1:6379/0",
    REDIS_CACHE_URL=f"redis://:{TEST_REDIS_PASSWORD}@127.0.0.1:6380/0",
    TELEGRAM_ALLOWED_USER_ID="123456",
    UNTRUSTED_URL_TOOLS_ENABLED="true",
    UNTRUSTED_URL_TOOLS_EGRESS_ISOLATED="true",
)


SCENARIOS: dict[str, dict[str, str]] = {
    "production-csrf.env": PRODUCTION_BASE,
    "production-telegram.env": {
        **PRODUCTION_BASE,
        "TELEGRAM_BOT_TO_DO_TOKEN": "ci-test-token",
        "TELEGRAM_ALLOWED_USER_ID": "0",
    },
    "production-weak-postgres.env": {
        **PRODUCTION_BASE,
        "ENABLE_POSTGRES": "true",
        "DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/test",
        "POSTGRES_PASSWORD": "weak",
    },
    "production-weak-redis.env": {
        **PRODUCTION_BASE,
        "REDIS_PASSWORD": "weak",
        "REDIS_URL": "redis://:${REDIS_PASSWORD}@127.0.0.1:6379/0",
    },
    "ai-chat.env": {"AI_CHAT_ENABLED": "true", "GROQ_API_KEY": "ci-test-key"},
    "ai-search.env": {"AI_SEARCH_ENABLED": "true", "GROQ_API_KEY": "ci-test-key"},
    "fernet.env": {"FERNET_SECRET": TEST_FERNET_KEY},
    "github-public.env": {"GITHUB_PUBLIC_USERNAME": "octocat"},
    "webhooks.env": {"WEBHOOK_SECRETS": '{"ping":"ping-secret"}'},
    "stripe.env": {
        "STRIPE_SECRET_KEY": "sk_test_ci",
        "STRIPE_WEBHOOK_SECRET": "whsec_test",
        "STRIPE_DONATION_AMOUNT_CENTS": "500",
    },
}

for filename, overrides in SCENARIOS.items():
    write_env(TESTS / "env" / filename, **overrides)
