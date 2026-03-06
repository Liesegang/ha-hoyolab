"""Constants for the HoYoverse integration."""
from __future__ import annotations

DOMAIN = "hoyoverse"
PLATFORMS = ["sensor"]
UPDATE_INTERVAL_MINUTES = 15

# Config keys
CONF_LTOKEN = "ltoken"
CONF_LTUID = "ltuid"

CONF_GENSHIN_UID = "genshin_uid"
CONF_GENSHIN_SERVER = "genshin_server"
CONF_HSR_UID = "hsr_uid"
CONF_HSR_SERVER = "hsr_server"
CONF_ZZZ_UID = "zzz_uid"
CONF_ZZZ_SERVER = "zzz_server"
CONF_HI3_UID = "hi3_uid"
CONF_HI3_SERVER = "hi3_server"

# Game identifiers
GAME_GENSHIN = "genshin"
GAME_HSR = "hsr"
GAME_ZZZ = "zzz"
GAME_HI3 = "hi3"

GAME_NAMES = {
    GAME_GENSHIN: "Genshin Impact",
    GAME_HSR: "Honkai: Star Rail",
    GAME_ZZZ: "Zenless Zone Zero",
    GAME_HI3: "Honkai Impact 3rd",
}

# Server options (kept for config_flow UI)
GENSHIN_SERVERS = {
    "os_asia": "Asia",
    "os_usa": "North America",
    "os_euro": "Europe",
    "os_cht": "TW/HK/MO",
}

HSR_SERVERS = {
    "prod_official_asia": "Asia",
    "prod_official_usa": "North America",
    "prod_official_euro": "Europe",
    "prod_official_cht": "TW/HK/MO",
}

ZZZ_SERVERS = {
    "prod_gf_jp": "Asia",
    "prod_gf_us": "North America",
    "prod_gf_eu": "Europe",
    "prod_gf_cht": "TW/HK/MO",
}

HI3_SERVERS = {
    "overseas01": "Global",
}

# Sensor keys
# Genshin
SENSOR_GENSHIN_RESIN = "genshin_resin"
SENSOR_GENSHIN_RESIN_RECOVERY = "genshin_resin_recovery_time"
SENSOR_GENSHIN_COMMISSIONS = "genshin_commissions"
SENSOR_GENSHIN_COMMISSION_CLAIMED = (
    "genshin_commission_reward_claimed"
)
SENSOR_GENSHIN_REALM_CURRENCY = "genshin_realm_currency"
SENSOR_GENSHIN_EXPEDITIONS = "genshin_expeditions"
SENSOR_GENSHIN_TRANSFORMER = "genshin_transformer_ready"
SENSOR_GENSHIN_TROUNCE = "genshin_trounce_blossom"
SENSOR_GENSHIN_STORED_ATTENDANCE = "genshin_stored_attendance"

# HSR
SENSOR_HSR_STAMINA = "hsr_stamina"
SENSOR_HSR_STAMINA_RECOVERY = "hsr_stamina_recovery_time"
SENSOR_HSR_RESERVE_STAMINA = "hsr_reserve_stamina"
SENSOR_HSR_DAILY_TRAINING = "hsr_daily_training"
SENSOR_HSR_ECHO_OF_WAR = "hsr_echo_of_war"
SENSOR_HSR_EXPEDITIONS = "hsr_expeditions"
SENSOR_HSR_ROGUE = "hsr_simulated_universe"
SENSOR_HSR_ROGUE_TOURN = "hsr_divergent_universe"
SENSOR_HSR_GRID_FIGHT = "hsr_currency_wars"

# ZZZ
SENSOR_ZZZ_ENERGY = "zzz_battery_charge"
SENSOR_ZZZ_ENERGY_RECOV = "zzz_battery_recovery_time"
SENSOR_ZZZ_VITALITY = "zzz_engagement"
SENSOR_ZZZ_CARD_SIGN = "zzz_card_punch"
SENSOR_ZZZ_BOUNTY = "zzz_bounty"
SENSOR_ZZZ_INVESTIGATION = "zzz_investigation_points"
SENSOR_ZZZ_VHS_SALE = "zzz_vhs_store"
SENSOR_ZZZ_WEEKLY_TASK = "zzz_weekly_task"
SENSOR_ZZZ_ABYSS_REFRESH = "zzz_abyss_refresh"
SENSOR_ZZZ_CAFE = "zzz_cafe"
SENSOR_ZZZ_MEMBER_CARD = "zzz_member_card"

# HI3
SENSOR_HI3_STAMINA = "hi3_stamina"
SENSOR_HI3_STAMINA_RECOVERY = "hi3_stamina_recovery_time"
SENSOR_HI3_BOUNTY = "hi3_bounty"
SENSOR_HI3_COCOON_WEEKLY = "hi3_weekly_elite_dungeon"
