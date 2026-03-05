# HoYoverse for Home Assistant

![HACS Badge](https://img.shields.io/badge/HACS-Default-orange.svg)

Home Assistant integration + Lovelace card for **Genshin Impact**, **Honkai: Star Rail**, **Zenless Zone Zero**, and **Honkai Impact 3rd**.

> ⚠️ Uses the unofficial HoYoLAB API. This may break if miHoYo changes their endpoints.

---

## Features

| | Genshin Impact | Honkai: Star Rail | Zenless Zone Zero | Honkai Impact 3rd |
|---|---|---|---|---|
| Stamina/Resin | ✅ Original Resin | ✅ Trailblaze Power | ✅ Battery Charge | ✅ Stamina |
| Recovery timer | ✅ | ✅ | ✅ | ✅ |
| Daily tasks | ✅ Commissions | ✅ Daily Training | ✅ Engagement | — |
| Weekly content | — | ✅ Echo of War | ✅ Bounty | ✅ Weekly Dungeon |
| Extra counters | ✅ Realm Currency, Transformer, Expeditions | ✅ Reserve Power, Assignments | ✅ Card Punch, Investigation | ✅ Bounty |

---

## Installation

### HACS (recommended)

1. In HACS → **Integrations**, search **HoYoverse** → Install
2. In HACS → **Frontend (Dashboard)**, search **HoYoverse Card** → Install
3. Restart Home Assistant

### Manual

Copy `custom_components/hoyoverse/` to your HA config and add `dist/hoyoverse-card.js` as a Lovelace resource.

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

All sensors are prefixed with `sensor.hoyoverse_`.

### Genshin Impact
- `genshin_resin` — Current Original Resin
- `genshin_resin_recovery_time` — Seconds until full
- `genshin_commissions` — Daily commissions done
- `genshin_realm_currency` — Realm currency
- `genshin_expeditions` — Active expeditions
- `genshin_transformer_ready` — Parametric transformer status

### Honkai: Star Rail
- `hsr_stamina` — Trailblaze Power
- `hsr_stamina_recovery_time` — Seconds until full
- `hsr_reserve_stamina` — Reserve power
- `hsr_daily_training` — Daily training score
- `hsr_echo_of_war` — Weekly Echo of War clears
- `hsr_expeditions` — Active assignments

### Zenless Zone Zero
- `zzz_battery_charge` — Current battery
- `zzz_battery_recovery_time` — Seconds until full
- `zzz_engagement` — Daily engagement value
- `zzz_card_punch` — Card punch status
- `zzz_bounty` — Bounty commission count
- `zzz_investigation_points` — Investigation points

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
