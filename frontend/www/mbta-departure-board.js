/* MBTA Departure Board v1.0.0 — MIT License. No external dependencies. */
class MBTADepartureBoard extends HTMLElement {
  constructor() { super(); this.attachShadow({mode:'open'}); }
  setConfig(config) {
    this.config = {...config, rows: Math.max(1, Math.min(20, Number(config.rows) || 6))};
    this.render();
  }
  set hass(hass) {
    const old = this._hass;
    this._hass = hass;
    if (!old || this.entityIds().some(id => old.states[id] !== hass.states[id])) this.render();
  }
  connectedCallback() { this.render(); this.timer = setInterval(() => this.render(), 15000); }
  disconnectedCallback() { clearInterval(this.timer); }
  entityIds() { return (this.config?.services || []).map(s => s.entity).concat(this.config?.alerts_entity || []); }
  static getStubConfig() { return {station:'South Station', services:[{name:'Red Line',entity:'sensor.mbta_south_station_red',color:'#da291c'},{name:'Silver Line',entity:'sensor.mbta_south_station_silver',color:'#a2aaad'},{name:'Commuter Rail',entity:'sensor.mbta_south_station_rail',color:'#80276c'}], alerts_entity:'sensor.mbta_south_station_alerts'}; }
  getCardSize() { return 12; }
  render() {
    if (!this.config || !this._hass) return;
    const root = this.shadowRoot;
    const expanded = root.querySelector('details')?.open || false;
    const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
    const zone = this.config.time_zone || 'America/New_York';
    let fmt;
    try { fmt = new Intl.DateTimeFormat('en-US',{hour:'numeric',minute:'2-digit',timeZone:zone}); }
    catch { fmt = new Intl.DateTimeFormat('en-US',{hour:'numeric',minute:'2-digit',timeZone:'America/New_York'}); }
    const now = Date.now();
    const blocks = (this.config.services || []).map(service => {
      const entity = this._hass.states[service.entity];
      const missing = !entity;
      const unavailable = missing || entity.state === 'unavailable';
      const stamp = Date.parse(entity?.attributes.updated_at || '');
      const stale = Number.isFinite(stamp) && now - stamp > 180000;
      const rows = Array.isArray(entity?.attributes.departures) ? entity.attributes.departures : [];
      // Exact duplicate rows only; distinguish different trains and departure times.
      const seen = new Set();
      const upcoming = rows.filter(d => {
        const when = Date.parse(d.departure_time);
        const key = JSON.stringify([d.trip_id,d.route_id,d.departure_time,d.direction_id]);
        if (!Number.isFinite(when) || when < now - 30000 || seen.has(key)) return false;
        seen.add(key); return true;
      }).sort((a,b) => Date.parse(a.departure_time)-Date.parse(b.departure_time)).slice(0,this.config.rows);
      const color = /^#[0-9a-f]{6}$/i.test(service.color || '') ? service.color : '#ffb547';
      return `<section><div class="service" style="--line:${color}"><i></i>${esc(service.name)}<span>${unavailable ? 'OFFLINE' : stale ? 'STALE' : 'DEPARTURES'}</span></div>
        <div class="columns"><span>DESTINATION</span><span>TRACK</span><span>DEPARTS</span></div>
        ${unavailable ? `<div class="empty">${missing ? 'ENTITY NOT FOUND — CHECK CONFIGURATION' : 'DATA UNAVAILABLE'}</div>` : upcoming.length ? upcoming.map(d => {
          const mins = Math.max(0,Math.ceil((Date.parse(d.departure_time)-now)/60000));
          const route = /^\d+$/.test(d.route_id || '') ? ({741:'SL1',742:'SL2',743:'SL3',749:'SL5',751:'SL4'}[d.route_id] || d.route_id) : (d.route_id || '').startsWith('Green-') ? d.route_id.slice(6) : '';
          return `<div class="departure"><div class="destination">${route ? `<small class="route">${esc(route)}</small>` : ''}<span>${esc(d.destination)}</span><small class="source">${esc(d.status || '')}${d.status ? ' · ' : ''}${d.realtime ? 'LIVE' : 'SCHEDULED'}${stale ? ' · STALE' : ''}</small></div><div class="track">${esc(d.track || '—')}</div><div class="time">${mins === 0 ? 'DUE' : mins + '<small> MIN</small>'}<small class="clock">${esc(fmt.format(new Date(d.departure_time)))}</small></div></div>`;
        }).join('') : '<div class="empty">NO UPCOMING DEPARTURES</div>'}
        <div class="updated">${Number.isFinite(stamp) ? 'UPDATED '+esc(fmt.format(new Date(stamp))) : 'AWAITING UPDATE'}</div></section>`;
    }).join('');
    const alertEntity = this._hass.states[this.config.alerts_entity];
    const alerts = Array.isArray(alertEntity?.attributes.alerts) ? alertEntity.attributes.alerts : [];
    const alertOffline = !alertEntity || ['unavailable','unknown'].includes(alertEntity.state);
    root.innerHTML = `<style>
      :host{display:block;color:#ffb547;font-family:'Courier New',monospace;font-variant-numeric:tabular-nums}
      *{box-sizing:border-box}ha-card{display:block;background:#080a0b;color:#ffb547;border:1px solid #34312a;border-radius:10px;overflow:hidden;box-shadow:0 8px 28px #0005}
      header{padding:22px 20px 18px;border-bottom:2px solid #ffb547;display:flex;justify-content:space-between;gap:14px;align-items:center;background:#101211}
      .brand{width:37px;height:37px;border:2px solid #ffb547;border-radius:50%;display:grid;place-items:center;font:bold 27px Arial;flex-shrink:0}.heading{flex:1}h1{font-size:24px;letter-spacing:1.5px;margin:0;text-transform:uppercase;line-height:1.15}.tag{font:10px Arial,sans-serif;letter-spacing:2.5px;color:#ba914e;margin-top:7px}.current{font-weight:bold;font-size:15px;white-space:nowrap}
      section{padding:18px 20px 5px}.service{display:flex;align-items:center;gap:9px;text-transform:uppercase;font:bold 13px Arial,sans-serif;letter-spacing:1px;color:#f1c780}.service i{width:7px;height:17px;background:var(--line);display:block}.service>span{margin-left:auto;font:9px Arial,sans-serif;color:#b09163;letter-spacing:1px}
      .columns,.departure{display:grid;grid-template-columns:minmax(0,1fr) 48px 92px;gap:10px}.columns{margin-top:16px;padding-bottom:8px;border-bottom:1px solid #493822;color:#b09163;font:9px Arial,sans-serif;letter-spacing:1.3px}.columns span:nth-child(n+2){text-align:right}
      .departure{min-height:67px;align-items:center;border-bottom:1px solid #27251d;padding:10px 0;background-image:radial-gradient(#ffb54708 .6px,transparent .6px);background-size:4px 4px}.destination{font-weight:bold;font-size:17px;line-height:1.3;overflow-wrap:anywhere;text-transform:uppercase;text-shadow:0 0 9px #ffb5472a}.source{display:block;font:9px Arial,sans-serif;color:#b09163;letter-spacing:1px;margin-top:4px}.route{font-size:11px;border:1px solid #80602e;border-radius:2px;padding:1px 4px;margin-right:7px}.track{text-align:right;font-size:18px}.time{text-align:right;font-size:23px;font-weight:bold;white-space:nowrap;text-shadow:0 0 10px #ffb54735}.time small{font-size:10px}.time .clock{display:block;font:10px Arial,sans-serif;color:#b09163;margin-top:4px}.updated{font:9px Arial,sans-serif;color:#8e7855;text-align:right;padding:8px 0}.empty{font-size:12px;padding:24px 0;color:#b09163}
      details{margin:12px 20px 20px;border:1px solid #594020;border-radius:3px}summary{padding:13px;cursor:pointer;font-size:11px;letter-spacing:1px;line-height:1.5}article{padding:14px;border-top:1px solid #493822;font:12px/1.6 Arial,sans-serif;color:#ddc397}article strong{display:block;color:#ffb547;margin-bottom:7px}article p{margin:0;white-space:pre-wrap}
      @media(max-width:400px){header{padding:18px 14px}h1{font-size:19px}.current{font-size:12px}.brand{width:30px;height:30px;font-size:22px}section{padding:16px 14px 5px}.columns,.departure{grid-template-columns:minmax(0,1fr) 35px 76px;gap:7px}.destination{font-size:14px}.time{font-size:20px}.tag{font-size:8px;letter-spacing:1.7px}details{margin:12px 14px 16px}}
    </style><ha-card><header><div class="brand" aria-hidden="true">T</div><div class="heading"><h1>${esc(this.config.station || 'MBTA')}</h1><div class="tag">BOSTON · DEPARTURE BOARD</div></div><div class="current">${esc(fmt.format(new Date(now)))}</div></header>${blocks}
    ${this.config.alerts_entity ? `<details ${expanded?'open':''}><summary>${alertOffline ? 'SERVICE ALERTS · DATA UNAVAILABLE' : alerts.length ? 'SERVICE ALERTS · '+alerts.length+' ACTIVE — EXPAND' : 'SERVICE ALERTS · NO ACTIVE NOTICES'}</summary>${alerts.map(a=>`<article><strong>${esc(a.header)}</strong><p>${esc(a.description)}</p></article>`).join('')}</details>`:''}</ha-card>`;
  }
}
if (!customElements.get('mbta-departure-board')) customElements.define('mbta-departure-board', MBTADepartureBoard);
window.customCards = window.customCards || [];
window.customCards.push({type:'mbta-departure-board',name:'MBTA Departure Board',description:'Black and amber MBTA station departure board.'});
