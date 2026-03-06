"""Sensor platform for HoYoverse integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    GAME_NAMES,
    GAME_GENSHIN, GAME_HSR, GAME_ZZZ, GAME_HI3,
    SENSOR_GENSHIN_RESIN, SENSOR_GENSHIN_RESIN_RECOVERY,
    SENSOR_GENSHIN_COMMISSIONS, SENSOR_GENSHIN_COMMISSION_CLAIMED,
    SENSOR_GENSHIN_REALM_CURRENCY, SENSOR_GENSHIN_EXPEDITIONS,
    SENSOR_GENSHIN_TRANSFORMER, SENSOR_GENSHIN_TROUNCE,
    SENSOR_GENSHIN_STORED_ATTENDANCE,
    SENSOR_HSR_STAMINA, SENSOR_HSR_STAMINA_RECOVERY,
    SENSOR_HSR_RESERVE_STAMINA, SENSOR_HSR_DAILY_TRAINING,
    SENSOR_HSR_ECHO_OF_WAR, SENSOR_HSR_EXPEDITIONS,
    SENSOR_HSR_ROGUE, SENSOR_HSR_ROGUE_TOURN, SENSOR_HSR_GRID_FIGHT,
    SENSOR_ZZZ_ENERGY, SENSOR_ZZZ_ENERGY_RECOV, SENSOR_ZZZ_VITALITY,
    SENSOR_ZZZ_CARD_SIGN, SENSOR_ZZZ_BOUNTY, SENSOR_ZZZ_INVESTIGATION,
    SENSOR_ZZZ_VHS_SALE, SENSOR_ZZZ_WEEKLY_TASK,
    SENSOR_ZZZ_ABYSS_REFRESH, SENSOR_ZZZ_CAFE, SENSOR_ZZZ_MEMBER_CARD,
    SENSOR_HI3_STAMINA, SENSOR_HI3_STAMINA_RECOVERY,
    SENSOR_HI3_BOUNTY, SENSOR_HI3_COCOON_WEEKLY,
)
from .coordinator import HoyoverseCoordinator


@dataclass(frozen=True)
class HoyoSensorDescription(SensorEntityDescription):
    """Extended sensor description."""
    game: str = ""
    value_fn: Callable[[dict[str, Any]], Any] | None = None
    attr_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


# --------------------------------------------------------------------------- #
# Genshin Impact                                                                #
# --------------------------------------------------------------------------- #
def _genshin_resin_attrs(d: dict) -> dict:
    return {
        "max_resin": d.get("max_resin", 200),
        "recovery_time_seconds": int(d.get("resin_recovery_time", 0)),
    }

def _genshin_realm_attrs(d: dict) -> dict:
    return {
        "max_realm_currency": d.get("max_home_coin", 2400),
        "recovery_time_seconds": int(d.get("home_coin_recovery_time", 0)),
    }

def _genshin_transformer(d: dict) -> str:
    t = d.get("transformer", {})
    if not t.get("obtained"):
        return "Not obtained"
    r = t.get("recovery_time", {})
    if r.get("reached"):
        return "Ready"
    total = r.get("Day", 0)*86400 + r.get("Hour", 0)*3600 + r.get("Minute", 0)*60 + r.get("Second", 0)
    h, m = divmod(total // 60, 60)
    d2 = h // 24; h2 = h % 24
    return f"{d2}d {h2}h {m}m" if d2 else f"{h2}h {m}m"

GENSHIN_SENSORS: list[HoyoSensorDescription] = [
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_RESIN,
        name="Original Resin",
        game=GAME_GENSHIN,
        icon="mdi:flask",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("current_resin"),
        attr_fn=_genshin_resin_attrs,
    ),
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_RESIN_RECOVERY,
        name="Resin Recovery Time",
        game=GAME_GENSHIN,
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda d: int(d.get("resin_recovery_time", 0)),
    ),
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_COMMISSIONS,
        name="Daily Commissions",
        game=GAME_GENSHIN,
        icon="mdi:clipboard-check",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("finished_task_num", 0),
        attr_fn=lambda d: {
            "total": d.get("total_task_num", 4),
            "extra_reward_claimed": d.get("is_extra_task_reward_received", False),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_COMMISSION_CLAIMED,
        name="Commission Reward Claimed",
        game=GAME_GENSHIN,
        icon="mdi:gift",
        value_fn=lambda d: "Yes" if d.get("is_extra_task_reward_received") else "No",
    ),
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_REALM_CURRENCY,
        name="Realm Currency",
        game=GAME_GENSHIN,
        icon="mdi:home-city",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("current_home_coin"),
        attr_fn=_genshin_realm_attrs,
    ),
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_EXPEDITIONS,
        name="Expeditions",
        game=GAME_GENSHIN,
        icon="mdi:map-marker-path",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("current_expedition_num", 0),
        attr_fn=lambda d: {
            "max": d.get("max_expedition_num", 5),
            "max_remaining_time": max(
                (int(e.get("remained_time", 0)) for e in d.get("expeditions", [])),
                default=0,
            ),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_TRANSFORMER,
        name="Parametric Transformer",
        game=GAME_GENSHIN,
        icon="mdi:atom-variant",
        value_fn=_genshin_transformer,
    ),
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_TROUNCE,
        name="Trounce Blossom Discount",
        game=GAME_GENSHIN,
        icon="mdi:flower",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("remain_resin_discount_num", 0),
        attr_fn=lambda d: {"max": d.get("resin_discount_num_limit", 3)},
    ),
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_STORED_ATTENDANCE,
        name="Stored Attendance",
        game=GAME_GENSHIN,
        icon="mdi:star-circle",
        value_fn=lambda d: d.get("daily_task", {}).get("stored_attendance", "0"),
    ),
]

# --------------------------------------------------------------------------- #
# Honkai: Star Rail                                                              #
# --------------------------------------------------------------------------- #
HSR_SENSORS: list[HoyoSensorDescription] = [
    HoyoSensorDescription(
        key=SENSOR_HSR_STAMINA,
        name="Trailblaze Power",
        game=GAME_HSR,
        icon="mdi:lightning-bolt",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("current_stamina"),
        attr_fn=lambda d: {
            "max_stamina": d.get("max_stamina", 300),
            "recovery_time_seconds": d.get("stamina_recover_time", 0),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_HSR_STAMINA_RECOVERY,
        name="Trailblaze Power Recovery",
        game=GAME_HSR,
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda d: d.get("stamina_recover_time", 0),
    ),
    HoyoSensorDescription(
        key=SENSOR_HSR_RESERVE_STAMINA,
        name="Reserve Trailblaze Power",
        game=GAME_HSR,
        icon="mdi:battery-charging",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("current_reserve_stamina", 0),
        attr_fn=lambda d: {"is_full": d.get("is_reserve_stamina_full", False)},
    ),
    HoyoSensorDescription(
        key=SENSOR_HSR_DAILY_TRAINING,
        name="Daily Training",
        game=GAME_HSR,
        icon="mdi:book-open-variant",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("current_train_score", 0),
        attr_fn=lambda d: {"max": d.get("max_train_score", 500)},
    ),
    HoyoSensorDescription(
        key=SENSOR_HSR_ECHO_OF_WAR,
        name="Echo of War (Weekly)",
        game=GAME_HSR,
        icon="mdi:sword-cross",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("weekly_cocoon_cnt", 0),
        attr_fn=lambda d: {"max": d.get("weekly_cocoon_limit", 3)},
    ),
    HoyoSensorDescription(
        key=SENSOR_HSR_EXPEDITIONS,
        name="Assignments",
        game=GAME_HSR,
        icon="mdi:map-marker-path",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("accepted_epedition_num", 0),
        attr_fn=lambda d: {"max": d.get("total_expedition_num", 4)},
    ),
    HoyoSensorDescription(
        key=SENSOR_HSR_ROGUE,
        name="Simulated Universe",
        game=GAME_HSR,
        icon="mdi:orbit",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("current_rogue_score", 0),
        attr_fn=lambda d: {"max": d.get("max_rogue_score", 14000)},
    ),
    HoyoSensorDescription(
        key=SENSOR_HSR_ROGUE_TOURN,
        name="Divergent Universe",
        game=GAME_HSR,
        icon="mdi:axis-arrow",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("rogue_tourn_weekly_cur", 0),
        attr_fn=lambda d: {
            "max": d.get("rogue_tourn_weekly_max", 2000),
            "exp_is_full": d.get("rogue_tourn_exp_is_full", False),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_HSR_GRID_FIGHT,
        name="Currency Wars",
        game=GAME_HSR,
        icon="mdi:cash-multiple",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("grid_fight_weekly_cur", 0),
        attr_fn=lambda d: {"max": d.get("grid_fight_weekly_max", 18000)},
    ),
]

# --------------------------------------------------------------------------- #
# Zenless Zone Zero                                                              #
# --------------------------------------------------------------------------- #
def _zzz_energy(d: dict) -> Any:
    return d.get("energy", {}).get("progress", {}).get("current")

def _zzz_energy_recovery(d: dict) -> int:
    return d.get("energy", {}).get("restore", 0)

def _zzz_energy_attrs(d: dict) -> dict:
    prog = d.get("energy", {}).get("progress", {})
    return {
        "max": prog.get("max", 240),
        "recovery_time_seconds": d.get("energy", {}).get("restore", 0),
    }

ZZZ_SENSORS: list[HoyoSensorDescription] = [
    HoyoSensorDescription(
        key=SENSOR_ZZZ_ENERGY,
        name="Battery Charge",
        game=GAME_ZZZ,
        icon="mdi:battery-charging-80",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_zzz_energy,
        attr_fn=_zzz_energy_attrs,
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_ENERGY_RECOV,
        name="Battery Recovery Time",
        game=GAME_ZZZ,
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=_zzz_energy_recovery,
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_VITALITY,
        name="Engagement Value",
        game=GAME_ZZZ,
        icon="mdi:run",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("vitality", {}).get("current"),
        attr_fn=lambda d: {"max": d.get("vitality", {}).get("max", 400)},
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_CARD_SIGN,
        name="Card Punch",
        game=GAME_ZZZ,
        icon="mdi:card-account-details",
        value_fn=lambda d: (
            "Done" if d.get("card_sign") == "CardSignDone" else "Not Done"
        ),
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_BOUNTY,
        name="Bounty Commission",
        game=GAME_ZZZ,
        icon="mdi:clipboard-list",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("bounty_commission", {}).get("num", 0),
        attr_fn=lambda d: {"max": d.get("bounty_commission", {}).get("total", 8000)},
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_INVESTIGATION,
        name="Investigation Points",
        game=GAME_ZZZ,
        icon="mdi:magnify",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (d.get("survey_points") or {}).get("num", 0),
        attr_fn=lambda d: {
            "max": (d.get("survey_points") or {}).get("total", 5000),
            "is_max_level": (d.get("survey_points") or {}).get("is_max_level", False),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_VHS_SALE,
        name="VHS Store",
        game=GAME_ZZZ,
        icon="mdi:filmstrip",
        value_fn=lambda d: {
            "SaleStateDoing": "Open",
            "SaleStateDone": "Revenue Available",
        }.get(d.get("vhs_sale", {}).get("sale_state", ""), "Closed"),
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_WEEKLY_TASK,
        name="Weekly Task",
        game=GAME_ZZZ,
        icon="mdi:calendar-week",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("weekly_task", {}).get("cur_point", 0),
        attr_fn=lambda d: {"max": d.get("weekly_task", {}).get("max_point", 2100)},
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_ABYSS_REFRESH,
        name="Shiyu Defense Reset",
        game=GAME_ZZZ,
        icon="mdi:timer-sand",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda d: d.get("abyss_refresh", 0),
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_CAFE,
        name="Cafe",
        game=GAME_ZZZ,
        icon="mdi:coffee",
        value_fn=lambda d: (
            "Done" if d.get("cafe_state") == "CafeStateDone" else "Not Done"
        ),
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_MEMBER_CARD,
        name="Inter-Knot Membership",
        game=GAME_ZZZ,
        icon="mdi:card-account-details-star",
        value_fn=lambda d: (
            "Active" if (d.get("member_card") or {}).get("is_open") else "Inactive"
        ),
        attr_fn=lambda d: {
            "exp_time": (d.get("member_card") or {}).get("exp_time"),
        },
    ),
]

# --------------------------------------------------------------------------- #
# Honkai Impact 3rd                                                              #
# --------------------------------------------------------------------------- #
HI3_SENSORS: list[HoyoSensorDescription] = [
    HoyoSensorDescription(
        key=SENSOR_HI3_STAMINA,
        name="Stamina",
        game=GAME_HI3,
        icon="mdi:lightning-bolt-circle",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("current_stamina"),
        attr_fn=lambda d: {
            "max_stamina": d.get("max_stamina", 180),
            "recovery_time_seconds": d.get("stamina_recover_time", 0),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_HI3_STAMINA_RECOVERY,
        name="Stamina Recovery Time",
        game=GAME_HI3,
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda d: d.get("stamina_recover_time", 0),
    ),
    HoyoSensorDescription(
        key=SENSOR_HI3_BOUNTY,
        name="Bounty",
        game=GAME_HI3,
        icon="mdi:clipboard-list",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("current_bounty_num", 0),
        attr_fn=lambda d: {"max": d.get("max_bounty_num", 0)},
    ),
    HoyoSensorDescription(
        key=SENSOR_HI3_COCOON_WEEKLY,
        name="Weekly Elite Dungeon",
        game=GAME_HI3,
        icon="mdi:castle",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("current_weekly_cocoon", 0),
        attr_fn=lambda d: {"max": d.get("max_weekly_cocoon", 0)},
    ),
]

# All sensors by game
ALL_SENSORS: dict[str, list[HoyoSensorDescription]] = {
    GAME_GENSHIN: GENSHIN_SENSORS,
    GAME_HSR: HSR_SENSORS,
    GAME_ZZZ: ZZZ_SENSORS,
    GAME_HI3: HI3_SENSORS,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HoYoverse sensors from config entry."""
    coordinator: HoyoverseCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[HoyoSensor] = []

    for game, descriptions in ALL_SENSORS.items():
        if coordinator.data and coordinator.data.get(game) is not None:
            for desc in descriptions:
                entities.append(HoyoSensor(coordinator, desc, entry.entry_id))

    async_add_entities(entities)


class HoyoSensor(CoordinatorEntity[HoyoverseCoordinator], SensorEntity):
    """A sensor entity for one HoYoverse data point."""

    entity_description: HoyoSensorDescription

    def __init__(
        self,
        coordinator: HoyoverseCoordinator,
        description: HoyoSensorDescription,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_has_entity_name = True
        self.entity_id = f"sensor.{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry_id}_{description.game}")},
            name=GAME_NAMES[description.game],
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> Any:
        data = (self.coordinator.data or {}).get(self.entity_description.game)
        if data is None:
            return None
        fn = self.entity_description.value_fn
        if fn:
            try:
                return fn(data)
            except Exception:  # noqa: BLE001
                return None
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        data = (self.coordinator.data or {}).get(self.entity_description.game)
        if data is None:
            return None
        fn = self.entity_description.attr_fn
        if fn:
            try:
                return fn(data)
            except Exception:  # noqa: BLE001
                return None
        return None
