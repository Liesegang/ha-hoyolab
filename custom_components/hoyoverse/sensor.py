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
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    DOMAIN,
    GAME_NAMES,
    GAME_GENSHIN, GAME_HSR, GAME_ZZZ, GAME_HI3,
    SENSOR_GENSHIN_RESIN, SENSOR_GENSHIN_RESIN_RECOVERY,
    SENSOR_GENSHIN_COMMISSIONS,
    SENSOR_GENSHIN_COMMISSION_CLAIMED,
    SENSOR_GENSHIN_REALM_CURRENCY,
    SENSOR_GENSHIN_EXPEDITIONS,
    SENSOR_GENSHIN_TRANSFORMER, SENSOR_GENSHIN_TROUNCE,
    SENSOR_GENSHIN_STORED_ATTENDANCE,
    SENSOR_HSR_STAMINA, SENSOR_HSR_STAMINA_RECOVERY,
    SENSOR_HSR_RESERVE_STAMINA, SENSOR_HSR_DAILY_TRAINING,
    SENSOR_HSR_ECHO_OF_WAR, SENSOR_HSR_EXPEDITIONS,
    SENSOR_HSR_ROGUE, SENSOR_HSR_ROGUE_TOURN,
    SENSOR_HSR_GRID_FIGHT,
    SENSOR_ZZZ_ENERGY, SENSOR_ZZZ_ENERGY_RECOV,
    SENSOR_ZZZ_VITALITY,
    SENSOR_ZZZ_CARD_SIGN, SENSOR_ZZZ_BOUNTY,
    SENSOR_ZZZ_INVESTIGATION,
    SENSOR_ZZZ_VHS_SALE, SENSOR_ZZZ_WEEKLY_TASK,
    SENSOR_ZZZ_ABYSS_REFRESH, SENSOR_ZZZ_CAFE,
    SENSOR_ZZZ_MEMBER_CARD,
    SENSOR_HI3_STAMINA, SENSOR_HI3_STAMINA_RECOVERY,
    SENSOR_HI3_BOUNTY, SENSOR_HI3_COCOON_WEEKLY,
)
from .coordinator import HoyoverseCoordinator


@dataclass(frozen=True)
class HoyoSensorDescription(SensorEntityDescription):
    """Extended sensor description."""
    game: str = ""
    value_fn: Callable[[Any], Any] | None = None
    attr_fn: Callable[[Any], dict[str, Any]] | None = None


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #
def _td_seconds(td) -> int:
    """Convert timedelta to total seconds (int)."""
    if td is None:
        return 0
    if hasattr(td, "total_seconds"):
        return int(td.total_seconds())
    return int(td)


def _transformer_display(n) -> str:
    """Human-readable transformer status."""
    td = n.remaining_transformer_recovery_time
    if td is None:
        return "Not obtained"
    secs = _td_seconds(td)
    if secs <= 0:
        return "Ready"
    h, m = divmod(secs // 60, 60)
    d = h // 24
    h2 = h % 24
    return f"{d}d {h2}h {m}m" if d else f"{h2}h {m}m"


# ------------------------------------------------------------------ #
# Genshin Impact                                                       #
# ------------------------------------------------------------------ #
GENSHIN_SENSORS: list[HoyoSensorDescription] = [
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_RESIN,
        name="Original Resin",
        game=GAME_GENSHIN,
        icon="mdi:flask",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: n.current_resin,
        attr_fn=lambda n: {
            "max_resin": n.max_resin,
            "recovery_time_seconds": _td_seconds(
                n.remaining_resin_recovery_time
            ),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_RESIN_RECOVERY,
        name="Resin Recovery Time",
        game=GAME_GENSHIN,
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda n: _td_seconds(
            n.remaining_resin_recovery_time
        ),
    ),
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_COMMISSIONS,
        name="Daily Commissions",
        game=GAME_GENSHIN,
        icon="mdi:clipboard-check",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: n.completed_commissions,
        attr_fn=lambda n: {
            "total": n.max_commissions,
            "extra_reward_claimed": (
                n.claimed_commission_reward
            ),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_COMMISSION_CLAIMED,
        name="Commission Reward Claimed",
        game=GAME_GENSHIN,
        icon="mdi:gift",
        value_fn=lambda n: (
            "Yes" if n.claimed_commission_reward else "No"
        ),
    ),
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_REALM_CURRENCY,
        name="Realm Currency",
        game=GAME_GENSHIN,
        icon="mdi:home-city",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: n.current_realm_currency,
        attr_fn=lambda n: {
            "max_realm_currency": n.max_realm_currency,
            "recovery_time_seconds": _td_seconds(
                n.remaining_realm_currency_recovery_time
            ),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_EXPEDITIONS,
        name="Expeditions",
        game=GAME_GENSHIN,
        icon="mdi:map-marker-path",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: len(n.expeditions),
        attr_fn=lambda n: {
            "max": n.max_expeditions,
            "max_remaining_time": max(
                (_td_seconds(e.remaining_time)
                 for e in n.expeditions),
                default=0,
            ),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_TRANSFORMER,
        name="Parametric Transformer",
        game=GAME_GENSHIN,
        icon="mdi:atom-variant",
        value_fn=_transformer_display,
    ),
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_TROUNCE,
        name="Trounce Blossom Discount",
        game=GAME_GENSHIN,
        icon="mdi:flower",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: n.remaining_resin_discounts,
        attr_fn=lambda n: {
            "max": n.max_resin_discounts,
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_GENSHIN_STORED_ATTENDANCE,
        name="Stored Attendance",
        game=GAME_GENSHIN,
        icon="mdi:star-circle",
        value_fn=lambda n: n.daily_task.stored_attendance,
    ),
]

# ------------------------------------------------------------------ #
# Honkai: Star Rail                                                    #
# ------------------------------------------------------------------ #
HSR_SENSORS: list[HoyoSensorDescription] = [
    HoyoSensorDescription(
        key=SENSOR_HSR_STAMINA,
        name="Trailblaze Power",
        game=GAME_HSR,
        icon="mdi:lightning-bolt",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: n.current_stamina,
        attr_fn=lambda n: {
            "max_stamina": n.max_stamina,
            "recovery_time_seconds": _td_seconds(
                n.stamina_recover_time
            ),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_HSR_STAMINA_RECOVERY,
        name="Trailblaze Power Recovery",
        game=GAME_HSR,
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda n: _td_seconds(
            n.stamina_recover_time
        ),
    ),
    HoyoSensorDescription(
        key=SENSOR_HSR_RESERVE_STAMINA,
        name="Reserve Trailblaze Power",
        game=GAME_HSR,
        icon="mdi:battery-charging",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: n.current_reserve_stamina,
        attr_fn=lambda n: {
            "is_full": n.is_reserve_stamina_full,
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_HSR_DAILY_TRAINING,
        name="Daily Training",
        game=GAME_HSR,
        icon="mdi:book-open-variant",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: n.current_train_score,
        attr_fn=lambda n: {
            "max": n.max_train_score,
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_HSR_ECHO_OF_WAR,
        name="Echo of War (Weekly)",
        game=GAME_HSR,
        icon="mdi:sword-cross",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: n.remaining_weekly_discounts,
        attr_fn=lambda n: {
            "max": n.max_weekly_discounts,
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_HSR_EXPEDITIONS,
        name="Assignments",
        game=GAME_HSR,
        icon="mdi:map-marker-path",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: n.accepted_expedition_num,
        attr_fn=lambda n: {
            "max": n.total_expedition_num,
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_HSR_ROGUE,
        name="Simulated Universe",
        game=GAME_HSR,
        icon="mdi:orbit",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: n.current_rogue_score,
        attr_fn=lambda n: {
            "max": n.max_rogue_score,
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_HSR_ROGUE_TOURN,
        name="Divergent Universe",
        game=GAME_HSR,
        icon="mdi:axis-arrow",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: (
            n.current_bonus_synchronicity_points
        ),
        attr_fn=lambda n: {
            "max": n.max_bonus_synchronicity_points,
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_HSR_GRID_FIGHT,
        name="Currency Wars",
        game=GAME_HSR,
        icon="mdi:cash-multiple",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: getattr(
            n, "grid_fight_weekly_cur", 0
        ),
        attr_fn=lambda n: {
            "max": getattr(
                n, "grid_fight_weekly_max", 0
            ),
        },
    ),
]

# ------------------------------------------------------------------ #
# Zenless Zone Zero                                                    #
# ------------------------------------------------------------------ #
def _zzz_vhs_state(n) -> str:
    """Map VideoStoreState enum to display string."""
    state = n.video_store_state
    name = getattr(state, "value", str(state))
    return {
        "SaleStateDoing": "Open",
        "SaleStateDone": "Revenue Available",
    }.get(name, "Closed")


ZZZ_SENSORS: list[HoyoSensorDescription] = [
    HoyoSensorDescription(
        key=SENSOR_ZZZ_ENERGY,
        name="Battery Charge",
        game=GAME_ZZZ,
        icon="mdi:battery-charging-80",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: n.battery_charge.current,
        attr_fn=lambda n: {
            "max": n.battery_charge.max,
            "recovery_time_seconds": (
                n.battery_charge.seconds_till_full
            ),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_ENERGY_RECOV,
        name="Battery Recovery Time",
        game=GAME_ZZZ,
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda n: (
            n.battery_charge.seconds_till_full
        ),
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_VITALITY,
        name="Engagement Value",
        game=GAME_ZZZ,
        icon="mdi:run",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: n.engagement.current,
        attr_fn=lambda n: {
            "max": n.engagement.max,
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_CARD_SIGN,
        name="Card Punch",
        game=GAME_ZZZ,
        icon="mdi:card-account-details",
        value_fn=lambda n: (
            "Done" if n.scratch_card_completed else "Not Done"
        ),
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_BOUNTY,
        name="Bounty Commission",
        game=GAME_ZZZ,
        icon="mdi:clipboard-list",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: (
            n.hollow_zero.bounty_commission.cur_completed
            if n.hollow_zero.bounty_commission else 0
        ),
        attr_fn=lambda n: {
            "max": (
                n.hollow_zero.bounty_commission.total
                if n.hollow_zero.bounty_commission else 0
            ),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_INVESTIGATION,
        name="Investigation Points",
        game=GAME_ZZZ,
        icon="mdi:magnify",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: (
            n.hollow_zero.investigation_point.num
            if n.hollow_zero.investigation_point else 0
        ),
        attr_fn=lambda n: {
            "max": (
                n.hollow_zero.investigation_point.total
                if n.hollow_zero.investigation_point
                else 0
            ),
            "is_max_level": (
                n.hollow_zero.investigation_point
                .is_max_level
                if n.hollow_zero.investigation_point
                else False
            ),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_VHS_SALE,
        name="VHS Store",
        game=GAME_ZZZ,
        icon="mdi:filmstrip",
        value_fn=_zzz_vhs_state,
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_WEEKLY_TASK,
        name="Weekly Task",
        game=GAME_ZZZ,
        icon="mdi:calendar-week",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: (
            n.weekly_task.cur_point
            if n.weekly_task else 0
        ),
        attr_fn=lambda n: {
            "max": (
                n.weekly_task.max_point
                if n.weekly_task else 0
            ),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_ABYSS_REFRESH,
        name="Shiyu Defense Reset",
        game=GAME_ZZZ,
        icon="mdi:timer-sand",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda n: _td_seconds(
            getattr(n, "abyss_refresh", 0)
        ),
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_CAFE,
        name="Cafe",
        game=GAME_ZZZ,
        icon="mdi:coffee",
        value_fn=lambda n: (
            "Done"
            if getattr(n, "cafe_state", None)
            and str(n.cafe_state) == "CafeStateDone"
            else "Not Done"
        ),
    ),
    HoyoSensorDescription(
        key=SENSOR_ZZZ_MEMBER_CARD,
        name="Inter-Knot Membership",
        game=GAME_ZZZ,
        icon="mdi:card-account-details-star",
        value_fn=lambda n: (
            "Active" if n.member_card.is_open
            else "Inactive"
        ),
        attr_fn=lambda n: {
            "exp_time": _td_seconds(
                n.member_card.exp_time
            ),
        },
    ),
]

# ------------------------------------------------------------------ #
# Honkai Impact 3rd                                                    #
# ------------------------------------------------------------------ #
HI3_SENSORS: list[HoyoSensorDescription] = [
    HoyoSensorDescription(
        key=SENSOR_HI3_STAMINA,
        name="Stamina",
        game=GAME_HI3,
        icon="mdi:lightning-bolt-circle",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: n.current_stamina,
        attr_fn=lambda n: {
            "max_stamina": n.max_stamina,
            "recovery_time_seconds": (
                n.stamina_recover_time
            ),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_HI3_STAMINA_RECOVERY,
        name="Stamina Recovery Time",
        game=GAME_HI3,
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda n: n.stamina_recover_time,
    ),
    HoyoSensorDescription(
        key=SENSOR_HI3_BOUNTY,
        name="Bounty",
        game=GAME_HI3,
        icon="mdi:clipboard-list",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: getattr(
            n, "current_bounty_num", 0
        ),
        attr_fn=lambda n: {
            "max": getattr(n, "max_bounty_num", 0),
        },
    ),
    HoyoSensorDescription(
        key=SENSOR_HI3_COCOON_WEEKLY,
        name="Weekly Elite Dungeon",
        game=GAME_HI3,
        icon="mdi:castle",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda n: getattr(
            n, "current_weekly_cocoon", 0
        ),
        attr_fn=lambda n: {
            "max": getattr(
                n, "max_weekly_cocoon", 0
            ),
        },
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
    coordinator: HoyoverseCoordinator = (
        hass.data[DOMAIN][entry.entry_id]
    )
    entities: list[HoyoSensor] = []

    for game, descriptions in ALL_SENSORS.items():
        if (coordinator.data
                and coordinator.data.get(game) is not None):
            for desc in descriptions:
                entities.append(
                    HoyoSensor(
                        coordinator, desc, entry.entry_id
                    )
                )

    async_add_entities(entities)


class HoyoSensor(
    CoordinatorEntity[HoyoverseCoordinator],
    SensorEntity,
):
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
        self._attr_unique_id = (
            f"{entry_id}_{description.key}"
        )
        self._attr_has_entity_name = True
        self.entity_id = f"sensor.{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (DOMAIN, f"{entry_id}_{description.game}")
            },
            name=GAME_NAMES[description.game],
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> Any:
        data = (self.coordinator.data or {}).get(
            self.entity_description.game
        )
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
        data = (self.coordinator.data or {}).get(
            self.entity_description.game
        )
        if data is None:
            return None
        fn = self.entity_description.attr_fn
        if fn:
            try:
                return fn(data)
            except Exception:  # noqa: BLE001
                return None
        return None
