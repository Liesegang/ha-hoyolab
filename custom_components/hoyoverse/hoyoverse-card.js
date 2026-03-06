/**
 * hoyoverse-card
 * A Lovelace card for Home Assistant showing HoYoverse game stamina & counters.
 * Supports: Genshin Impact, Honkai: Star Rail, Zenless Zone Zero, Honkai Impact 3rd
 */

const ICON_BASE = "/hoyoverse/icons";

const GAME_CONFIG = {
  genshin: {
    name: "Genshin Impact",
    accent: "#5b9bd5",
    icon: `${ICON_BASE}/genshin.png`,
    stamina: { entityId: "sensor.genshin_resin", label: "Original Resin", max: 200, icon: "\u{1F9EA}" },
    extras: [
      { id: "commissions", entityId: "sensor.genshin_commissions", label: "Commissions", max_attr: "total", icon: "\u{1F4CB}", doneWhen: "max" },
      { id: "realm_currency", entityId: "sensor.genshin_realm_currency", label: "Realm Currency", max_attr: "max_realm_currency", icon: "\u{1F3E0}", timeAttr: "recovery_time_seconds" },
      { id: "trounce", entityId: "sensor.genshin_trounce_blossom", label: "Trounce Blossom", max_attr: "max", icon: "\u{1F338}", doneWhen: "zero" },
      { id: "expeditions", entityId: "sensor.genshin_expeditions", label: "Expeditions", max_attr: "max", icon: "\u{1F5FA}\uFE0F", timeAttr: "max_remaining_time", doneWhen: "max" },
      { id: "transformer", entityId: "sensor.genshin_transformer_ready", label: "Transformer", icon: "\u2697\uFE0F", isText: true, doneWhen: "hasTime" },
    ],
    recoveryEntityId: "sensor.genshin_resin_recovery_time",
  },
  hsr: {
    name: "Honkai: Star Rail",
    accent: "#a78bfa",
    icon: `${ICON_BASE}/hsr.png`,
    stamina: { entityId: "sensor.hsr_stamina", label: "Trailblaze Power", max: 300, icon: "\u26A1", showReserve: true },
    extras: [
      { id: "daily_training", entityId: "sensor.hsr_daily_training", label: "Daily Training", max_attr: "max", icon: "\u{1F4DA}", doneWhen: "max" },
      { id: "echo_of_war", entityId: "sensor.hsr_echo_of_war", label: "Echo of War", max_attr: "max", icon: "\u2694\uFE0F", doneWhen: "zero" },
      { id: "simulated_universe", entityId: "sensor.hsr_simulated_universe", label: "Simulated Universe", max_attr: "max", icon: "\u{1F30C}", doneWhen: "max" },
      { id: "divergent_universe", entityId: "sensor.hsr_divergent_universe", label: "Divergent Universe", max_attr: "max", icon: "\u{1F300}", doneWhen: "max" },
      { id: "currency_wars", entityId: "sensor.hsr_currency_wars", label: "Currency Wars", max_attr: "max", icon: "\u{1F4B0}", doneWhen: "max" },
    ],
    recoveryEntityId: "sensor.hsr_stamina_recovery_time",
  },
  zzz: {
    name: "Zenless Zone Zero",
    accent: "#e8882d",
    icon: `${ICON_BASE}/zzz.png`,
    stamina: { entityId: "sensor.zzz_battery_charge", label: "Battery Charge", max: 240, icon: "\u{1F50B}" },
    extras: [
      { id: "engagement", entityId: "sensor.zzz_engagement", label: "Engagement", max_attr: "max", icon: "\u{1F4AA}", doneWhen: "max" },
      { id: "vhs_store", entityId: "sensor.zzz_vhs_store", label: "VHS Store", icon: "\u{1F4FC}", isText: true, doneWhen: "open" },
      { id: "scratch_card", entityId: "sensor.zzz_card_punch", label: "Scratch Card", icon: "\u{1F0CF}", isText: true, doneWhen: "done" },
      { id: "bounty", entityId: "sensor.zzz_bounty", label: "Bounty", max_attr: "max", icon: "\u{1F4DC}", doneWhen: "max" },
      { id: "weekly_task", entityId: "sensor.zzz_weekly_task", label: "Weekly Task", max_attr: "max", icon: "\u{1F4C5}", doneWhen: "max" },
    ],
    recoveryEntityId: "sensor.zzz_battery_recovery_time",
  },
  hi3: {
    name: "Honkai Impact 3rd",
    accent: "#7b68ee",
    icon: `${ICON_BASE}/hi3.png`,
    stamina: { entityId: "sensor.hi3_stamina", label: "Stamina", max: 180, icon: "\u26A1" },
    extras: [
      { id: "bounty", entityId: "sensor.hi3_bounty", label: "Bounty", max_attr: "max", icon: "\u{1F4DC}" },
      { id: "weekly_dungeon", entityId: "sensor.hi3_weekly_elite_dungeon", label: "Weekly Dungeon", max_attr: "max", icon: "\u{1F3F0}" },
    ],
    recoveryEntityId: "sensor.hi3_stamina_recovery_time",
  },
};

function secondsToHuman(secs) {
  if (!secs || secs <= 0) return "Full \u2713";
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

function isDone(val, attrs, e) {
  if (!e.doneWhen) return null;
  switch (e.doneWhen) {
    case "max": {
      const max = e.max_attr ? attrs[e.max_attr] : null;
      return max != null && Number(val) >= Number(max);
    }
    case "zero":
      return Number(val) <= 0;
    case "done":
      return val === "Done";
    case "open":
      return val === "Open";
    case "hasTime":
      return val !== "Ready" && val !== "Not obtained";
    default:
      return null;
  }
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

  static getStubConfig() {
    return { game: "genshin" };
  }

  static getConfigElement() {
    return document.createElement("hoyoverse-card-editor");
  }

  _getEntity(entityId) {
    if (!this._hass) return null;
    return this._hass.states[entityId] ?? null;
  }

  _accent() {
    const gc = GAME_CONFIG[this._config.game];
    return this._config.accent || gc.accent;
  }

  _isExtraVisible(extraId) {
    const hidden = this._config.hidden_extras;
    if (!hidden || !Array.isArray(hidden)) return true;
    return !hidden.includes(extraId);
  }

  _staminaPercent(current, max) {
    if (current == null || max == null || max === 0) return 0;
    return Math.min(100, Math.round((Number(current) / Number(max)) * 100));
  }

  _renderProgressBar(pct, accent) {
    const color = pct >= 100 ? "var(--success-color, #34d399)" : accent;
    return `
      <div class="bar-track">
        <div class="bar-fill" style="width:${pct}%;background:${color};"></div>
      </div>`;
  }

  _renderStamina(gc, accent) {
    const staminaCfg = gc.stamina;
    const entity = this._getEntity(staminaCfg.entityId);
    const recovEntity = this._getEntity(gc.recoveryEntityId);

    const current = entity ? Number(entity.state) : null;
    const attrs = entity?.attributes || {};
    const max = attrs.max_resin ?? attrs.max_stamina ?? attrs.max ?? staminaCfg.max;
    const recovery = recovEntity ? Number(recovEntity.state) : null;
    const pct = this._staminaPercent(current, max);

    let reserveHtml = "";
    if (staminaCfg.showReserve) {
      const reserveEntity = this._getEntity("sensor.hsr_reserve_stamina");
      const reserve = reserveEntity ? Number(reserveEntity.state) : null;
      const reserveFull = reserveEntity?.attributes?.is_full;
      if (reserve != null) {
        reserveHtml = `
          <div class="reserve-info">
            \u{1F50B} Reserve: ${reserve}/2400${reserveFull ? " (Full)" : ""}
          </div>`;
      }
    }

    return `
      <div class="stamina-section">
        <div class="stamina-header">
          <span class="stamina-icon">${staminaCfg.icon}</span>
          <span class="stamina-label">${staminaCfg.label}</span>
          <span class="stamina-value" style="color:${pct >= 100 ? "var(--success-color, #34d399)" : accent}">
            ${current ?? "\u2014"}/${max}
          </span>
        </div>
        ${this._renderProgressBar(pct, accent)}
        <div class="recovery-time">
          ${pct >= 100
        ? `<span style="color:var(--success-color, #34d399)">\u25CF Full</span>`
        : `\u23F1 ${recovery != null ? secondsToHuman(recovery) : "\u2014"} until full`
      }
        </div>
        ${reserveHtml}
      </div>`;
  }

  _renderExtras(gc, accent) {
    const items = gc.extras
      .filter(e => this._isExtraVisible(e.id))
      .map(e => {
        const entity = this._getEntity(e.entityId);
        if (!entity) return "";

        const val = entity.state;
        const attrs = entity.attributes || {};
        const done = isDone(val, attrs, e);
        const bgClass = done === true ? "extra-done" : done === false ? "extra-not-done" : "";

        if (e.isText) {
          return `
            <div class="extra-item ${bgClass}">
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
        const barColor = pct != null && pct >= 100 ? "var(--success-color, #34d399)" : accent;
        const timeLeft = e.timeAttr && attrs[e.timeAttr] ? secondsToHuman(Number(attrs[e.timeAttr])) : null;

        return `
          <div class="extra-item ${bgClass}">
            <span class="extra-icon">${e.icon}</span>
            <div class="extra-body">
              <div class="extra-label">${e.label}${timeLeft ? ` <span class="extra-time">${timeLeft}</span>` : ""}</div>
              <div class="extra-val" style="color:${barColor}">${display}</div>
              ${pct != null ? `<div class="mini-bar-track"><div class="mini-bar-fill" style="width:${pct}%;background:${barColor}"></div></div>` : ""}
            </div>
          </div>`;
      })
      .filter(Boolean)
      .join("");

    return items
      ? `<div class="extras-grid">${items}</div>`
      : "";
  }

  _getStyles(accent) {
    return `
      :host { display: block; }
      ha-card {
        overflow: hidden;
        font-family: var(--primary-font-family, sans-serif);
      }
      .header {
        padding: 14px 16px;
        display: flex;
        align-items: center;
        gap: 10px;
        border-bottom: 1px solid var(--divider-color, rgba(255,255,255,0.07));
      }
      .header-icon {
        width: 28px;
        height: 28px;
        border-radius: 6px;
        object-fit: contain;
      }
      .header-title {
        font-size: 15px;
        font-weight: 700;
        color: ${accent};
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
        color: var(--primary-text-color, #fff);
        padding: 4px;
        border-radius: 6px;
      }
      .header-refresh:hover { opacity: 1; background: rgba(127,127,127,0.15); }
      .body { padding: 16px; }

      .stamina-section { margin-bottom: 16px; }
      .stamina-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
      .stamina-icon { font-size: 18px; }
      .stamina-label { flex: 1; font-size: 13px; color: var(--secondary-text-color, #b0b0b0); }
      .stamina-value { font-size: 20px; font-weight: 700; }
      .bar-track {
        height: 8px; border-radius: 99px;
        background: var(--divider-color, rgba(255,255,255,0.08));
        overflow: hidden;
        margin-bottom: 6px;
      }
      .bar-fill {
        height: 100%; border-radius: 99px;
        transition: width .4s ease;
      }
      .recovery-time { font-size: 12px; color: var(--secondary-text-color, #888); }
      .reserve-info {
        font-size: 12px;
        color: var(--secondary-text-color, #888);
        margin-top: 4px;
      }


      .extras-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-top: 4px;
      }
      .extra-item {
        background: var(--input-fill-color, rgba(127,127,127,0.08));
        border: 1px solid var(--divider-color, rgba(255,255,255,0.07));
        border-radius: 10px;
        padding: 10px 12px;
        display: flex;
        align-items: flex-start;
        gap: 8px;
      }
      .extra-done {
        background: rgba(52, 211, 153, 0.12);
        border-color: rgba(52, 211, 153, 0.25);
      }
      .extra-not-done {
        background: rgba(248, 113, 113, 0.12);
        border-color: rgba(248, 113, 113, 0.25);
      }
      .extra-icon { font-size: 16px; margin-top: 1px; }
      .extra-body { flex: 1; min-width: 0; }
      .extra-label { font-size: 11px; color: var(--secondary-text-color, #888); margin-bottom: 3px; }
      .extra-time { opacity: 0.7; }
      .extra-val { font-size: 14px; font-weight: 600; color: var(--primary-text-color, #f0f0f0); }
      .mini-bar-track {
        height: 4px; border-radius: 99px;
        background: var(--divider-color, rgba(255,255,255,0.08));
        overflow: hidden;
        margin-top: 5px;
      }
      .mini-bar-fill { height: 100%; border-radius: 99px; }
    `;
  }

  _render() {
    if (!this._config || !this.shadowRoot) return;
    const gc = GAME_CONFIG[this._config.game];
    const accent = this._accent();

    const body = `
      <style>${this._getStyles(accent)}</style>
      <ha-card>
        <div class="header">
          <img class="header-icon" src="${gc.icon}" alt="${gc.name}">
          <span class="header-title">${gc.name}</span>
          <button class="header-refresh" id="refresh-btn" title="Refresh">\u21BB</button>
        </div>
        <div class="body">
          ${this._renderStamina(gc, accent)}
          ${this._renderExtras(gc, accent)}
        </div>
      </ha-card>`;

    this.shadowRoot.innerHTML = body;
    this.shadowRoot
      .getElementById("refresh-btn")
      ?.addEventListener("click", () => {
        const visibleExtras = gc.extras.filter(e => this._isExtraVisible(e.id));
        const ids = [gc.stamina.entityId, gc.recoveryEntityId, ...visibleExtras.map(e => e.entityId)];
        this._hass?.callService("homeassistant", "update_entity", { entity_id: ids });
      });
  }
}

// ---------------------------------------------------------------------------
// Visual Config Editor
// ---------------------------------------------------------------------------

class HoyoverseCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
  }

  _fireChanged() {
    this.dispatchEvent(new CustomEvent("config-changed", {
      detail: { config: { ...this._config } },
      bubbles: true,
      composed: true,
    }));
  }

  _render() {
    const game = this._config.game || "genshin";
    const gc = GAME_CONFIG[game];
    const accent = this._config.accent || gc?.accent || "#5b9bd5";
    const hidden = this._config.hidden_extras || [];

    const gameOptions = Object.entries(GAME_CONFIG).map(
      ([key, g]) => `<option value="${key}" ${game === key ? "selected" : ""}>${g.name}</option>`
    ).join("");

    const extrasToggles = gc ? gc.extras.map(e => {
      const checked = !hidden.includes(e.id);
      return `
        <label class="toggle-row">
          <input type="checkbox" data-extra-id="${e.id}" ${checked ? "checked" : ""}>
          <span>${e.icon} ${e.label}</span>
        </label>`;
    }).join("") : "";

    this.shadowRoot.innerHTML = `
      <style>
        .editor { padding: 16px; }
        .field { margin-bottom: 16px; }
        .field-label {
          display: block;
          font-size: 13px;
          font-weight: 500;
          color: var(--primary-text-color, #333);
          margin-bottom: 4px;
        }
        select, input[type="color"] {
          width: 100%;
          padding: 8px 12px;
          border-radius: 8px;
          border: 1px solid var(--divider-color, #ccc);
          background: var(--input-fill-color, #fff);
          color: var(--primary-text-color, #333);
          font-size: 14px;
          cursor: pointer;
          box-sizing: border-box;
        }
        input[type="color"] {
          height: 40px;
          padding: 4px;
        }
        .color-row {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .color-row input[type="color"] {
          width: 50px;
          flex-shrink: 0;
        }
        .color-row .color-hex {
          flex: 1;
          font-size: 13px;
          color: var(--secondary-text-color, #888);
        }
        .color-row button {
          font-size: 12px;
          padding: 4px 8px;
          border-radius: 6px;
          border: 1px solid var(--divider-color, #ccc);
          background: var(--input-fill-color, #fff);
          color: var(--primary-text-color, #333);
          cursor: pointer;
        }
        .toggle-row {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 6px 0;
          font-size: 13px;
          color: var(--primary-text-color, #333);
          cursor: pointer;
        }
        .toggle-row input[type="checkbox"] {
          width: 16px;
          height: 16px;
          cursor: pointer;
        }
      </style>
      <div class="editor">
        <div class="field">
          <label class="field-label">Game</label>
          <select id="game-select">${gameOptions}</select>
        </div>
        <div class="field">
          <label class="field-label">Accent Color</label>
          <div class="color-row">
            <input type="color" id="accent-color" value="${accent}">
            <span class="color-hex">${accent}</span>
            <button id="reset-color">Reset</button>
          </div>
        </div>
        <div class="field">
          <label class="field-label">Visible Panels</label>
          ${extrasToggles}
        </div>
      </div>`;

    // Game select
    this.shadowRoot.getElementById("game-select")
      .addEventListener("change", (ev) => {
        this._config = { ...this._config, game: ev.target.value };
        delete this._config.accent;
        delete this._config.hidden_extras;
        this._fireChanged();
        this._render();
      });

    // Accent color
    this.shadowRoot.getElementById("accent-color")
      .addEventListener("input", (ev) => {
        this._config = { ...this._config, accent: ev.target.value };
        this._fireChanged();
        this.shadowRoot.querySelector(".color-hex").textContent = ev.target.value;
      });

    // Reset color
    this.shadowRoot.getElementById("reset-color")
      .addEventListener("click", () => {
        delete this._config.accent;
        this._fireChanged();
        this._render();
      });

    // Extra toggles
    this.shadowRoot.querySelectorAll("input[data-extra-id]").forEach(cb => {
      cb.addEventListener("change", () => {
        const id = cb.dataset.extraId;
        let hidden = [...(this._config.hidden_extras || [])];
        if (cb.checked) {
          hidden = hidden.filter(h => h !== id);
        } else {
          if (!hidden.includes(id)) hidden.push(id);
        }
        this._config = { ...this._config, hidden_extras: hidden };
        if (hidden.length === 0) delete this._config.hidden_extras;
        this._fireChanged();
      });
    });
  }
}

customElements.define("hoyoverse-card-editor", HoyoverseCardEditor);
customElements.define("hoyoverse-card", HoyoverseCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "hoyoverse-card",
  name: "HoYoverse Card",
  description: "Display HoYoverse game stamina and counters (Genshin, HSR, ZZZ, HI3)",
  preview: false,
});

console.info(
  `%c HOYOVERSE-CARD %c v1.1.0 `,
  "color:#fff;background:#5b9bd5;font-weight:bold;padding:2px 6px;border-radius:3px 0 0 3px",
  "color:#5b9bd5;background:#1a1a1a;padding:2px 6px;border-radius:0 3px 3px 0"
);
