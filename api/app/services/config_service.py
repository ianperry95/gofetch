"""Service for managing app configuration with DB-first, env-fallback."""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import AppConfig

logger = logging.getLogger(__name__)

# Keys that are considered sensitive (API keys, secrets)
SENSITIVE_KEYS = {
    "miniflux_api_key",
    "openai_api_key",
    "secret_key",
    "miniflux_webhook_secret",
}

# All configurable keys with their metadata
CONFIG_DEFINITIONS = {
    "miniflux_url": {
        "label": "Miniflux URL",
        "type": "url",
        "group": "miniflux",
        "description": "URL of your Miniflux instance",
    },
    "miniflux_api_key": {
        "label": "Miniflux API Key",
        "type": "password",
        "group": "miniflux",
        "description": "API key for Miniflux authentication",
    },
    "openai_api_key": {
        "label": "OpenAI API Key",
        "type": "password",
        "group": "embeddings",
        "description": "Required if using OpenAI embeddings",
    },
    "openai_embedding_model": {
        "label": "OpenAI Embedding Model",
        "type": "text",
        "group": "embeddings",
        "description": "Model name for OpenAI embeddings",
    },
    "embedding_provider": {
        "label": "Embedding Provider",
        "type": "select",
        "options": ["onnx", "openai"],
        "group": "embeddings",
        "description": "Provider for generating embeddings",
    },
}


async def get_config_value(db: AsyncSession, key: str) -> str | None:
    """Get a config value from DB, falling back to env."""
    result = await db.execute(select(AppConfig).where(AppConfig.key == key))
    row = result.scalar_one_or_none()
    if row:
        return row.value.get("value") if isinstance(row.value, dict) else row.value
    return None


async def set_config_value(db: AsyncSession, key: str, value: str) -> None:
    """Set a config value in DB."""
    result = await db.execute(select(AppConfig).where(AppConfig.key == key))
    row = result.scalar_one_or_none()
    if row:
        row.value = {"value": value}
    else:
        row = AppConfig(key=key, value={"value": value})
        db.add(row)
    await db.commit()


async def get_all_config(db: AsyncSession) -> dict[str, Any]:
    """Get all config values, merging DB overrides with env defaults."""
    from app.config import settings

    result = {}
    for key, definition in CONFIG_DEFINITIONS.items():
        # Try DB first
        db_value = await get_config_value(db, key)
        if db_value is not None:
            display_value = db_value
        else:
            # Fall back to env/settings
            display_value = getattr(settings, key, "")

        # Mask sensitive values
        if key in SENSITIVE_KEYS and display_value:
            display_value = mask_value(str(display_value))

        result[key] = {
            **definition,
            "value": display_value,
            "is_set": bool(db_value is not None or getattr(settings, key, "")),
        }
    return result


async def update_config(db: AsyncSession, updates: dict[str, str]) -> dict[str, list[str]]:
    """Update multiple config values. Returns validation errors."""
    errors = {}
    updated = []

    for key, value in updates.items():
        if key not in CONFIG_DEFINITIONS:
            errors.setdefault("unknown", []).append(key)
            continue

        # Don't update masked values (user didn't change them)
        if value and "***" in value:
            continue

        # Empty string means "clear the override"
        if value == "":
            result = await db.execute(select(AppConfig).where(AppConfig.key == key))
            row = result.scalar_one_or_none()
            if row:
                await db.delete(row)
                updated.append(key)
            continue

        await set_config_value(db, key, value)
        updated.append(key)

    if updated:
        await db.commit()

    return {"updated": updated, "errors": errors}


def mask_value(value: str) -> str:
    """Mask a sensitive value for display."""
    if len(value) <= 8:
        return "***"
    return value[:4] + "***" + value[-4:]
