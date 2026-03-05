/**
 * hoyoverse-card
 * A Lovelace card for Home Assistant showing HoYoverse game stamina & counters.
 * Supports: Genshin Impact, Honkai: Star Rail, Zenless Zone Zero, Honkai Impact 3rd
 */

const GAME_CONFIG = {
  genshin: {
    name: "Genshin Impact",
    entityPrefix: "genshin_impact",
    accent: "#e2b96f",
    bg: "linear-gradient(135deg, #1a1005 0%, #2d1f00 100%)",
    headerBg: "rgba(226,185,111,0.12)",
    icon: `<svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor">
      <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
    </svg>`,
    emoji: "\u{1F33F}",
    stamina: { entitySuffix: "original_resin", label: "Original Resin", max: 200, icon: "\u{1F9EA}" },
    extras: [
      { entitySuffix: "daily_commissions", label: "Commissions", max_attr: "total", icon: "\u{1F4CB}" },
      { entitySuffix: "realm_currency", label: "Realm Currency", max_attr: "max_realm_currency", icon: "\u{1F3E0}" },
      { entitySuffix: "expeditions", label: "Expeditions", max_attr: "max", icon: "\u{1F5FA}\uFE0F" },
      { entitySuffix: "parametric_transformer", label: "Transformer", icon: "\u2697\uFE0F", isText: true },
    ],
    recoveryEntitySuffix: "resin_recovery_time",
  },
  hsr: {
    name: "Honkai: Star Rail",
    entityPrefix: "honkai_star_rail",
    accent: "#a78bfa",
    bg: "linear-gradient(135deg, #0d0a1a 0%, #1a0d2e 100%)",
    headerBg: "rgba(167,139,250,0.12)",
    emoji: "\u26A1",
    stamina: { entitySuffix: "trailblaze_power", label: "Trailblaze Power", max: 240, icon: "\u26A1" },
    extras: [
      { entitySuffix: "reserve_trailblaze_power", label: "Reserve Power", icon: "\u{1F50B}", isRaw: true },
      { entitySuffix: "daily_training", label: "Daily Training", max_attr: "max", icon: "\u{1F4DA}" },
      { entitySuffix: "echo_of_war_weekly", label: "Echo of War", max_attr: "max", icon: "\u2694\uFE0F" },
      { entitySuffix: "assignments", label: "Assignments", max_attr: "max", icon: "\u{1F5FA}\uFE0F" },
    ],
    recoveryEntitySuffix: "trailblaze_power_recovery",
  },
  zzz: {
    name: "Zenless Zone Zero",
    entityPrefix: "zenless_zone_zero",
    accent: "#f5d44f",
    bg: "linear-gradient(135deg, #0a0a05 0%, #1a1800 100%)",
    headerBg: "rgba(245,212,79,0.10)",
    emoji: "\u{1F50B}",
    stamina: { entitySuffix: "battery_charge", label: "Battery Charge", max: 240, icon: "\u{1F50B}" },
    extras: [
      { entitySuffix: "engagement_value", label: "Engagement", max_attr: "max", icon: "\u{1F4AA}" },
      { entitySuffix: "card_punch", label: "Card Punch", icon: "\u{1F0CF}", isText: true },
      { entitySuffix: "bounty_commission", label: "Bounty", max_attr: "max", icon: "\u{1F4DC}" },
      { entitySuffix: "investigation_points", label: "Investigation", max_attr: "max", icon: "\u{1F50D}" },
    ],
    recoveryEntitySuffix: "battery_recovery_time",
  },
  hi3: {
    name: "Honkai Impact 3rd",
    entityPrefix: "honkai_impact_3rd",
    accent: "#f87171",
    bg: "linear-gradient(135deg, #0f0505 0%, #200a0a 100%)",
    headerBg: "rgba(248,113,113,0.12)",
    emoji: "\u{1F300}",
    stamina: { entitySuffix: "stamina", label: "Stamina", max: 180, icon: "\u26A1" },
    extras: [
      { entitySuffix: "bounty", label: "Bounty", max_attr: "max", icon: "\u{1F4DC}" },
      { entitySuffix: "weekly_elite_dungeon", label: "Weekly Dungeon", max_attr: "max", icon: "\u{1F3F0}" },
    ],
    recoveryEntitySuffix: "stamina_recovery_time",
  },
};

function secondsToHuman(secs) {
  if (!secs || secs <= 0) return "Full \u2713";
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

function formatTime(isoOrSecs) {
  const n = Number(isoOrSecs);
  return isNaN(n) ? (isoOrSecs ?? "\u2014") : secondsToHuman(n);
}

// ---------------------------------------------------------------------------

class HoyoverseCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
    this._hass = null;
  }

  setConfig(config) {
    if (!config.game || !GAME_CONFIG[config.game]) {
      throw new Error(
        `hoyoverse-card: "game" must be one of: ${Object.keys(GAME_CONFIG).join(", ")}`
      );
    }
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() { return 3; }

  // Find entity whose entity_id matches the game prefix and suffix
  _findEntity(suffix) {
    if (!this._hass) return null;
    const gc = GAME_CONFIG[this._config.game];
    const prefix = gc.entityPrefix;
    const states = this._hass.states;
    const key = Object.keys(states).find(
      id => id.startsWith("sensor.") && id.includes(prefix) && id.endsWith(suffix)
    );
    return key ? states[key] : null;
  }

  _staminaPercent(current, max) {
    if (current == null || max == null || max === 0) return 0;
    return Math.min(100, Math.round((Number(current) / Number(max)) * 100));
  }

  _renderProgressBar(pct, accent) {
    const color = pct >= 100 ? "#34d399" : accent;
    return `
      <div class="bar-track">
        <div class="bar-fill" style="width:${pct}%;background:${color};"></div>
      </div>`;
  }

  _renderStamina(gc) {
    const staminaCfg = gc.stamina;
    const entity = this._findEntity(staminaCfg.entitySuffix);
    const recovEntity = this._findEntity(gc.recoveryEntitySuffix);

    const current = entity ? Number(entity.state) : null;
    const max = entity?.attributes?.max_resin
              ?? entity?.attributes?.max_stamina
              ?? staminaCfg.max;
    const recovery = recovEntity ? Number(recovEntity.state) : null;
    const pct = this._staminaPercent(current, max);

    return `
      <div class="stamina-section">
        <div class="stamina-header">
          <span class="stamina-icon">${staminaCfg.icon}</span>
          <span class="stamina-label">${staminaCfg.label}</span>
          <span class="stamina-value" style="color:${pct >= 100 ? "#34d399" : gc.accent}">
            ${current ?? "\u2014"}/${max}
          </span>
        </div>
        ${this._renderProgressBar(pct, gc.accent)}
        <div class="recovery-time">
          ${pct >= 100
            ? `<span style="color:#34d399">\u25CF Full</span>`
            : `\u23F1 ${recovery != null ? secondsToHuman(recovery) : "\u2014"} until full`
          }
        </div>
      </div>`;
  }

  _renderExtras(gc) {
    const items = gc.extras
      .map(e => {
        const entity = this._findEntity(e.entitySuffix);
        if (!entity) return "";

        const val = entity.state;
        const attrs = entity.attributes || {};

        if (e.isText) {
          return `
            <div class="extra-item">
              <span class="extra-icon">${e.icon}</span>
              <div class="extra-body">
                <div class="extra-label">${e.label}</div>
                <div class="extra-val">${val}</div>
              </div>
            </div>`;
        }

        if (e.isRaw) {
          return `
            <div class="extra-item">
              <span class="extra-icon">${e.icon}</span>
              <div class="extra-body">
                <div class="extra-label">${e.label}</div>
                <div class="extra-val">${val}</div>
              </div>
            </div>`;
        }

        const max = e.max_attr ? attrs[e.max_attr] : null;
        const display = max != null ? `${val}/${max}` : val;
        const pct = max ? this._staminaPercent(val, max) : null;
        const barColor = pct != null && pct >= 100 ? "#34d399" : gc.accent;

        return `
          <div class="extra-item">
            <span class="extra-icon">${e.icon}</span>
            <div class="extra-body">
              <div class="extra-label">${e.label}</div>
              <div class="extra-val" style="color:${barColor}">${display}</div>
              ${pct != null ? `<div class="mini-bar-track"><div class="mini-bar-fill" style="width:${pct}%;background:${barColor}"></div></div>` : ""}
            </div>
          </div>`;
      })
      .filter(Boolean)
      .join("");

    return items
      ? `<div class="extras-grid">${items}</div>`
      : `<div class="no-data">No extra data found.<br>Make sure your entities are configured.</div>`;
  }

  _getStyles(gc) {
    return `
      :host { display: block; }
      .card {
        background: ${gc.bg};
        border-radius: 16px;
        overflow: hidden;
        color: #f0f0f0;
        font-family: var(--primary-font-family, sans-serif);
        box-shadow: 0 4px 24px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.06);
      }
      .header {
        background: ${gc.headerBg};
        border-bottom: 1px solid rgba(255,255,255,0.07);
        padding: 14px 18px;
        display: flex;
        align-items: center;
        gap: 10px;
      }
      .header-emoji { font-size: 22px; }
      .header-title {
        font-size: 15px;
        font-weight: 700;
        color: ${gc.accent};
        letter-spacing: 0.02em;
        flex: 1;
      }
      .header-refresh {
        cursor: pointer;
        opacity: 0.5;
        font-size: 16px;
        transition: opacity .2s;
        background: none;
        border: none;
        color: inherit;
        padding: 4px;
        border-radius: 6px;
      }
      .header-refresh:hover { opacity: 1; background: rgba(255,255,255,0.08); }
      .body { padding: 16px 18px; }

      /* Stamina */
      .stamina-section { margin-bottom: 16px; }
      .stamina-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
      .stamina-icon { font-size: 18px; }
      .stamina-label { flex: 1; font-size: 13px; color: #b0b0b0; }
      .stamina-value { font-size: 20px; font-weight: 700; }
      .bar-track {
        height: 8px; border-radius: 99px;
        background: rgba(255,255,255,0.08);
        overflow: hidden;
        margin-bottom: 6px;
      }
      .bar-fill {
        height: 100%; border-radius: 99px;
        transition: width .4s ease;
      }
      .recovery-time { font-size: 12px; color: #888; }

      /* Extras */
      .extras-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-top: 4px;
      }
      .extra-item {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px;
        padding: 10px 12px;
        display: flex;
        align-items: flex-start;
        gap: 8px;
      }
      .extra-icon { font-size: 16px; margin-top: 1px; }
      .extra-body { flex: 1; min-width: 0; }
      .extra-label { font-size: 11px; color: #888; margin-bottom: 3px; }
      .extra-val { font-size: 14px; font-weight: 600; }
      .mini-bar-track {
        height: 4px; border-radius: 99px;
        background: rgba(255,255,255,0.08);
        overflow: hidden;
        margin-top: 5px;
      }
      .mini-bar-fill { height: 100%; border-radius: 99px; }
      .no-data { color: #666; font-size: 13px; text-align: center; padding: 16px 0; }
      .section-divider {
        height: 1px;
        background: rgba(255,255,255,0.06);
        margin: 14px 0;
      }
    `;
  }

  _render() {
    if (!this._config || !this.shadowRoot) return;
    const gc = GAME_CONFIG[this._config.game];

    const body = `
      <style>${this._getStyles(gc)}</style>
      <div class="card">
        <div class="header">
          <span class="header-emoji">${gc.emoji}</span>
          <span class="header-title">${gc.name}</span>
          <button class="header-refresh" id="refresh-btn" title="Refresh">\u21BB</button>
        </div>
        <div class="body">
          ${this._renderStamina(gc)}
          <div class="section-divider"></div>
          ${this._renderExtras(gc)}
        </div>
      </div>`;

    this.shadowRoot.innerHTML = body;
    this.shadowRoot
      .getElementById("refresh-btn")
      ?.addEventListener("click", () => this._hass?.callService("homeassistant", "update_entity", {
        entity_id: Object.keys(this._hass?.states ?? {}).filter(
          id => id.startsWith("sensor.") && id.includes(gc.entityPrefix)
        ),
      }));
  }
}

customElements.define("hoyoverse-card", HoyoverseCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "hoyoverse-card",
  name: "HoYoverse Card",
  description: "Display HoYoverse game stamina and counters (Genshin, HSR, ZZZ, HI3)",
  preview: false,
});

console.info(
  `%c HOYOVERSE-CARD %c v1.0.0 `,
  "color:#fff;background:#e2b96f;font-weight:bold;padding:2px 6px;border-radius:3px 0 0 3px",
  "color:#e2b96f;background:#1a1a1a;padding:2px 6px;border-radius:0 3px 3px 0"
);
