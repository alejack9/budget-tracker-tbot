from typing import TYPE_CHECKING, cast

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Infrastructure (database)
    database_url: PostgresDsn

    # Interfaces (Telegram bot)
    bot_token: str
    allowed_chat_ids: list[int]

    types: list[str] = Field(default_factory=lambda: ["need", "want", "goal"])
    categories: list[str] = Field(
        default_factory=lambda: [
            "food",
            "gifts",
            "health",
            "home",
            "transportation",
            "personal",
            "utilities",
            "travel",
            "debt",
            "other",
            "family",
            "wardrobe",
            "investments",
        ]
    )

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("allowed_chat_ids", mode="before")
    @classmethod
    def split_allowed_chat_ids(cls, v: str | list[int]) -> list[int]:
        if isinstance(v, list):
            return v
        return [int(item.strip()) for item in str(v).split(",") if item.strip()]

    @field_validator("types", mode="before")
    @classmethod
    def split_types(cls, v: str | list[str] | None) -> list[str]:
        if v is None:
            return []
        if isinstance(v, list):
            return [str(item).strip() for item in v if str(item).strip()]
        return [item.strip() for item in str(v).split(",") if item.strip()]

    @field_validator("categories", mode="before")
    @classmethod
    def split_categories(cls, v: str | list[str] | None) -> list[str]:
        if v is None:
            return []
        if isinstance(v, list):
            return [str(item).strip() for item in v if str(item).strip()]
        return [item.strip() for item in str(v).split(",") if item.strip()]


if TYPE_CHECKING:
    settings = Settings(
        database_url=cast(PostgresDsn, "postgresql://user:pass@localhost:5432/db"),
        bot_token="",
        allowed_chat_ids=[],
    )
else:
    settings = Settings()
