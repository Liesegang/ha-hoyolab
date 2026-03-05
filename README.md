# HoYoverse for Home Assistant

![HACS Badge](https://img.shields.io/badge/HACS-Default-orange.svg)

Home Assistant integration + Lovelace card for **Genshin Impact**, **Honkai: Star Rail**, **Zenless Zone Zero**, and **Honkai Impact 3rd**.

> ⚠️ Uses the unofficial HoYoLAB API. This may break if miHoYo changes their endpoints.

![Screenshot](docs/screenshot.png)

---

## Features

| | Genshin Impact | Honkai: Star Rail | Zenless Zone Zero | Honkai Impact 3rd |
|---|---|---|---|---|
| Stamina/Resin | ✅ Original Resin | ✅ Trailblaze Power | ✅ Battery Charge | ✅ Stamina |
| Recovery timer | ✅ | ✅ | ✅ | ✅ |
| Daily tasks | ✅ Commissions | ✅ Daily Training | ✅ Engagement | — |
| Weekly content | ✅ Trounce Blossom | ✅ Echo of War, Simulated/Divergent Universe, Currency Wars | ✅ Bounty, Weekly Task | ✅ Weekly Dungeon |
| Extra counters | ✅ Realm Currency, Transformer, Expeditions | ✅ Reserve Power, Assignments | ✅ VHS Store, Card Punch, Investigation, Cafe | ✅ Bounty |

---

## Installation

### HACS (recommended)

1. In HACS → **Integrations** → Add custom repository → enter this repo URL → Category: **Integration**
2. Search **HoYoverse** → Install
3. Restart Home Assistant

The Lovelace card is bundled with the integration — no separate frontend install needed.

### Manual

Copy `custom_components/hoyoverse/` into your Home Assistant `config/custom_components/` directory and restart.

---

## Setup

### 1. Get your cookie

1. Open [hoyolab.com](https://www.hoyolab.com) and log in
2. Press **F12** → **Console** tab
3. Paste: `document.cookie`
4. Copy the values of `ltoken_v2` and `ltuid_v2`

### 2. Add integration

**Settings → Devices & Services → Add Integration → HoYoverse**

- Enter your `ltoken_v2` and `ltuid_v2`
- For each game you play: enter your in-game UID and select your server

### 3. Add the card

Add via the Lovelace UI card picker (**HoYoverse Card**) or manually in YAML:

```yaml
type: custom:hoyoverse-card
game: genshin   # genshin | hsr | zzz | hi3
```

---

## Card Options

| Option | Required | Description |
|---|---|---|
| `game` | ✅ | `genshin`, `hsr`, `zzz`, or `hi3` |

---

## Sensors Created

Entity IDs follow the pattern `sensor.<key>` (e.g. `sensor.genshin_resin`).

### Genshin Impact
- `genshin_resin` — Current Original Resin
- `genshin_resin_recovery_time` — Seconds until full
- `genshin_commissions` — Daily commissions done
- `genshin_commission_reward_claimed` — Extra reward claimed
- `genshin_realm_currency` — Realm currency (with recovery time)
- `genshin_expeditions` — Active expeditions
- `genshin_transformer_ready` — Parametric transformer status
- `genshin_trounce_blossom` — Trounce blossom discount remaining
- `genshin_stored_attendance` — Stored attendance

### Honkai: Star Rail
- `hsr_stamina` — Trailblaze Power
- `hsr_stamina_recovery_time` — Seconds until full
- `hsr_reserve_stamina` — Reserve power
- `hsr_daily_training` — Daily training score
- `hsr_echo_of_war` — Weekly Echo of War clears
- `hsr_expeditions` — Active assignments
- `hsr_simulated_universe` — Simulated Universe score
- `hsr_divergent_universe` — Divergent Universe score
- `hsr_currency_wars` — Currency Wars score

### Zenless Zone Zero
- `zzz_battery_charge` — Current battery
- `zzz_battery_recovery_time` — Seconds until full
- `zzz_engagement` — Daily engagement value
- `zzz_vhs_store` — VHS store status
- `zzz_card_punch` — Card punch status
- `zzz_bounty` — Bounty commission count
- `zzz_investigation_points` — Investigation points
- `zzz_weekly_task` — Weekly task points
- `zzz_abyss_refresh` — Shiyu Defense reset timer
- `zzz_cafe` — Cafe status
- `zzz_member_card` — Inter-Knot Membership status

### Honkai Impact 3rd
- `hi3_stamina` — Current stamina
- `hi3_stamina_recovery_time` — Seconds until full
- `hi3_bounty` — Bounty count
- `hi3_weekly_elite_dungeon` — Weekly elite dungeon clears

---

## Notes

- Data refreshes every **15 minutes** (HoYoLAB rate limit)
- Your `ltoken_v2` resets if you change your password
- Make sure your HoYoLAB account data is set to **public** in profile settings
