"""Config flow for HoYoverse integration."""
from __future__ import annotations

import logging
from typing import Any

import genshin
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
)

from .const import (
    DOMAIN,
    CONF_LTOKEN, CONF_LTUID,
    CONF_GENSHIN_UID, CONF_GENSHIN_SERVER,
    CONF_HSR_UID, CONF_HSR_SERVER,
    CONF_ZZZ_UID, CONF_ZZZ_SERVER,
    CONF_HI3_UID, CONF_HI3_SERVER,
    GENSHIN_SERVERS, HSR_SERVERS,
    ZZZ_SERVERS, HI3_SERVERS,
)

_LOGGER = logging.getLogger(__name__)

STEP_CREDENTIALS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_LTOKEN): str,
        vol.Required(CONF_LTUID): str,
    }
)


def _build_game_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(
                CONF_GENSHIN_UID, default=""
            ): str,
            vol.Optional(
                CONF_GENSHIN_SERVER, default=""
            ): vol.In(
                {**GENSHIN_SERVERS, "": "--- Disabled ---"}
            ),
            vol.Optional(
                CONF_HSR_UID, default=""
            ): str,
            vol.Optional(
                CONF_HSR_SERVER, default=""
            ): vol.In(
                {**HSR_SERVERS, "": "--- Disabled ---"}
            ),
            vol.Optional(
                CONF_ZZZ_UID, default=""
            ): str,
            vol.Optional(
                CONF_ZZZ_SERVER, default=""
            ): vol.In(
                {**ZZZ_SERVERS, "": "--- Disabled ---"}
            ),
            vol.Optional(
                CONF_HI3_UID, default=""
            ): str,
            vol.Optional(
                CONF_HI3_SERVER, default=""
            ): vol.In(
                {**HI3_SERVERS, "": "--- Disabled ---"}
            ),
        }
    )


async def _validate_cookie(
    ltoken: str, ltuid: str,
) -> str | None:
    """Validate cookie via genshin.py."""
    client = genshin.Client(
        cookies={
            "ltoken_v2": ltoken,
            "ltuid_v2": ltuid,
        },
        lang="en-us",
    )
    try:
        await client.get_game_accounts()
    except genshin.errors.InvalidCookies:
        return "invalid_cookie"
    except Exception:  # noqa: BLE001
        return "cannot_connect"
    return None


class HoyoverseConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HoYoverse."""

    VERSION = 1

    def __init__(self) -> None:
        self._credentials: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Step 1: credentials (ltoken + ltuid)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            ltoken = user_input[CONF_LTOKEN].strip()
            ltuid = user_input[CONF_LTUID].strip()

            error = await _validate_cookie(
                ltoken, ltuid
            )
            if error:
                errors["base"] = error
            else:
                self._credentials = {
                    CONF_LTOKEN: ltoken,
                    CONF_LTUID: ltuid,
                }
                return await self.async_step_games()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_CREDENTIALS_SCHEMA,
            errors=errors,
        )

    async def async_step_games(
        self, user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Step 2: per-game UID + server."""
        errors: dict[str, str] = {}

        if user_input is not None:
            for uid_key, server_key, label in [
                (
                    CONF_GENSHIN_UID,
                    CONF_GENSHIN_SERVER,
                    "Genshin",
                ),
                (
                    CONF_HSR_UID,
                    CONF_HSR_SERVER,
                    "HSR",
                ),
                (
                    CONF_ZZZ_UID,
                    CONF_ZZZ_SERVER,
                    "ZZZ",
                ),
                (
                    CONF_HI3_UID,
                    CONF_HI3_SERVER,
                    "HI3",
                ),
            ]:
                uid = user_input.get(
                    uid_key, ""
                ).strip()
                srv = user_input.get(
                    server_key, ""
                ).strip()
                if bool(uid) != bool(srv):
                    errors["base"] = (
                        "uid_server_mismatch"
                    )
                    break

            if not errors:
                config_data = {
                    **self._credentials,
                    **user_input,
                }
                await self.async_set_unique_id(
                    self._credentials[CONF_LTUID]
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=(
                        "HoYoverse"
                        f" ({self._credentials[CONF_LTUID]})"
                    ),
                    data=config_data,
                )

        return self.async_show_form(
            step_id="games",
            data_schema=_build_game_schema(),
            errors=errors,
        )
