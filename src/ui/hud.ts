/**
 * HUD v10 trên lớp DOM, ghép từ thành phần 9-slice sinh trong atlas (src/ui/v10.css).
 * Bố cục theo mockup assets/ui/v10_hud.png: Nhiệm vụ (trái trên), tên màn (giữa trên), đồng hồ + bản đồ nhỏ (phải trên),
 * thông báo (phải), Đội (trái dưới), thanh hành động (giữa dưới), Ba lô (phải dưới).
 * DOM dựng một lần; mỗi khung chỉ đổi chữ/giá trị khi khác trước để tránh churn.
 */
import type { CollisionGrid } from '../world/CollisionGrid';

export interface HudMember {
  name: string;
  color: string;
  portrait: HTMLCanvasElement | null;
  hp: number; // 0–1
  sl: number; // 0–1
  rocks: number;
}
export interface HudState {
  levelName: string;
  objective: string;
  side: { label: string; have: number; need: number }[];
  members: HudMember[];
  leader: number;
  stance: 'dung' | 'khom' | 'bo';
  hidden: boolean;
  time: string;
  detect: number; // 0–1
  detectLevel: 'an-minh' | 'nghi-ngo' | 'bao-dong' | 'down' | null;
  executing: boolean;
  inventory: { id: string; label: string; count: number; icon: () => HTMLCanvasElement | null }[];
  nearPickup: string | null;
  canTakedown: boolean;
}

const STANCES: [HudState['stance'], string][] = [
  ['dung', 'Đứng'],
  ['khom', 'Khom'],
  ['bo', 'Bò'],
];
const LEVEL_SEG = { 'an-minh': 'ok', 'nghi-ngo': 'warn', 'bao-dong': 'bad', down: 'off' } as const;
const LEVEL_TEXT = { 'an-minh': 'Ẩn mình', 'nghi-ngo': 'Nghi ngờ', 'bao-dong': 'Báo động', down: 'Bị hạ' } as const;

export class Hud {
  private el: HTMLDivElement;
  private mini!: HTMLCanvasElement;
  private miniBase: HTMLCanvasElement | null = null;
  private miniScale = 1;
  private toasts: { el: HTMLDivElement; t: number }[] = [];
  private cache = new Map<string, string>();
  private teamBuilt = false;

  constructor(root: HTMLElement) {
    this.el = document.createElement('div');
    this.el.className = 'hud';
    this.el.innerHTML = `
      <section class="v10-panel hud-mission"><span class="v10-title">Nhiệm vụ</span>
        <div class="hud-level" data-k="level"></div>
        <div class="hud-obj"><span class="v10-check-off" data-k="objcheck"></span><span data-k="objective"></span></div>
        <div class="hud-side" data-k="side"></div>
      </section>
      <div class="v10-title hud-name" data-k="name"></div>
      <section class="v10-panel hud-clock"><span data-k="time">0:00</span></section>
      <section class="v10-panel hud-map"><span class="v10-title">Bản đồ</span><canvas class="hud-mini" width="100" height="60"></canvas></section>
      <div class="hud-toasts" data-k="toasts"></div>
      <section class="v10-panel hud-team"><span class="v10-title">Đội</span><div class="hud-cards" data-k="cards"></div></section>
      <section class="v10-panel hud-actions"><span class="v10-title" data-k="leader"></span>
        <div class="hud-stances" data-k="stances"></div>
        <div class="hud-slots" data-k="slots"></div>
        <div class="hud-detect"><span class="v10-sub">Phát hiện</span><span class="hud-detbar" data-k="detbar"></span><span data-k="detlabel"></span></div>
      </section>
      <section class="v10-panel hud-bag"><span class="v10-title">Ba lô</span>
        <div class="hud-tabs"><span class="v10-tab-active">Vật phẩm</span><span class="v10-tab-normal">Vũ khí</span><span class="v10-tab-normal">Chìa khóa</span></div>
        <div class="hud-grid" data-k="bag"></div>
      </section>`;
    root.appendChild(this.el);
    this.mini = this.el.querySelector('.hud-mini')!;
  }

  destroy(): void {
    this.el.remove();
  }

  private q<T extends HTMLElement = HTMLElement>(k: string): T {
    return this.el.querySelector<T>(`[data-k="${k}"]`)!;
  }

  private set(k: string, html: string): void {
    if (this.cache.get(k) === html) return;
    this.cache.set(k, html);
    this.q(k).innerHTML = html;
  }

  /** Vẽ nền bản đồ nhỏ một lần từ lưới va chạm. */
  buildMinimap(grid: CollisionGrid): void {
    const c = document.createElement('canvas');
    c.width = grid.cols;
    c.height = grid.rows;
    const x = c.getContext('2d')!;
    const col: Record<string, string> = { '.': '#1b3a2a', '#': '#0f2418', o: '#2d5a34', '~': '#3e96ff', '=': '#8a6a3a' };
    for (let r = 0; r < grid.rows; r++) for (let cc = 0; cc < grid.cols; cc++) {
      x.fillStyle = col[grid.cellAt(cc, r)] ?? '#1b3a2a';
      x.fillRect(cc, r, 1, 1);
    }
    this.miniBase = c;
    this.miniScale = grid.cell;
    this.mini.width = grid.cols;
    this.mini.height = grid.rows;
  }

  drawMinimap(dots: { x: number; y: number; color: string; big?: boolean }[]): void {
    if (!this.miniBase) return;
    const x = this.mini.getContext('2d')!;
    x.imageSmoothingEnabled = false;
    x.drawImage(this.miniBase, 0, 0);
    for (const d of dots) {
      x.fillStyle = d.color;
      const px = Math.floor(d.x / this.miniScale);
      const py = Math.floor(d.y / this.miniScale);
      x.fillRect(px - (d.big ? 1 : 0), py - (d.big ? 1 : 0), d.big ? 3 : 2, d.big ? 3 : 2);
    }
  }

  notify(text: string, kind: 'info' | 'quest' | 'item' = 'info'): void {
    const el = document.createElement('div');
    el.className = `v10-panel hud-toast ${kind}`;
    el.innerHTML = `<span class="v10-led-${kind === 'quest' ? 'warn' : kind === 'item' ? 'ok' : 'bad'}"></span> ${text}`;
    this.q('toasts').prepend(el);
    this.toasts.unshift({ el, t: 0 });
    while (this.toasts.length > 4) this.toasts.pop()!.el.remove();
  }

  tickToasts(dt: number): void {
    for (let i = this.toasts.length - 1; i >= 0; i--) {
      const t = this.toasts[i];
      t.t += dt;
      if (t.t > 6) {
        t.el.remove();
        this.toasts.splice(i, 1);
      } else if (t.t > 5) t.el.style.opacity = String(6 - t.t);
    }
  }

  update(s: HudState): void {
    this.set('level', s.levelName);
    this.set('objective', s.objective);
    this.set('side', s.side.map((o) => `<div class="${o.have >= o.need ? 'done' : ''}"><span class="v10-check-${o.have >= o.need ? 'on' : 'off'}"></span>${o.label} <b>${o.have}/${o.need}</b></div>`).join(''));
    this.set('name', s.levelName);
    this.set('time', s.time);
    const L = s.members[s.leader];
    this.set('leader', `${L.name} · ${s.leader === 0 ? 'Trưởng nhóm' : 'Điều khiển'}`);
    this.set('stances', STANCES.map(([k, label]) => `<div class="${k === s.stance ? 'v10-choice-sel' : 'v10-choice'}">${label}${k === s.stance && s.hidden ? ' · ẩn' : ''}</div>`).join(''));
    const slots = [
      { key: 'Space', label: `Ném đá ×${L.rocks}`, on: L.rocks > 0 },
      { key: 'E', label: s.canTakedown ? 'Hạ gục' : s.nearPickup ? `Nhặt ${s.nearPickup}` : 'Nhặt / Hạ gục', on: s.canTakedown || !!s.nearPickup },
      { key: 'Tab', label: s.executing ? 'Đang thực thi' : 'Kế hoạch', on: true },
      { key: 'C', label: 'Tư thế', on: true },
    ];
    this.set('slots', slots.map((sl) => `<div class="${sl.on ? 'v10-slot-sel' : 'v10-slot'} hud-slot"><span class="v10-keycap">${sl.key}</span><span class="lbl">${sl.label}</span></div>`).join(''));
    const seg = s.detectLevel ? LEVEL_SEG[s.detectLevel] : 'off';
    const n = Math.round(s.detect * 10);
    this.set('detbar', `<i class="v10-seg-${seg === 'off' ? 'off' : seg}" style="width:calc(var(--px)*5*${n})"></i><i class="v10-seg-off" style="width:calc(var(--px)*5*${10 - n})"></i>`);
    this.set('detlabel', s.detectLevel ? LEVEL_TEXT[s.detectLevel] : '');
    // thẻ đội: dựng một lần (chân dung), sau đó chỉ đổi lớp và thanh
    const cards = this.q('cards');
    if (!this.teamBuilt) {
      cards.innerHTML = s.members
        .map((m, i) => `<div class="hud-card" data-i="${i}"><div class="pf"></div><div class="info"><div class="nm"><b>${i + 1}</b> ${m.name}</div><div class="bar"><span>HP</span><i data-b="hp"></i></div><div class="bar"><span>SL</span><i data-b="sl"></i></div></div></div>`)
        .join('');
      s.members.forEach((m, i) => {
        const pf = cards.querySelector<HTMLElement>(`[data-i="${i}"] .pf`)!;
        if (m.portrait) {
          // canvas chân dung vẽ ở ×2: hiển thị đúng 1 px game = --px
          m.portrait.style.width = `calc(var(--px) * ${m.portrait.width / 2})`;
          pf.appendChild(m.portrait);
        }
      });
      this.teamBuilt = true;
    }
    s.members.forEach((m, i) => {
      const card = cards.querySelector<HTMLElement>(`[data-i="${i}"]`)!;
      const cls = i === s.leader ? 'hud-card v10-card-sel' : 'hud-card v10-card';
      if (card.className !== cls) card.className = cls;
      const hp = Math.round(m.hp * 10);
      const sl = Math.round(m.sl * 10);
      const hpHtml = `<i class="v10-seg-bad" style="width:calc(var(--px)*5*${hp})"></i><i class="v10-seg-off" style="width:calc(var(--px)*5*${10 - hp})"></i>`;
      const slHtml = `<i class="v10-seg-warn" style="width:calc(var(--px)*5*${sl})"></i><i class="v10-seg-off" style="width:calc(var(--px)*5*${10 - sl})"></i>`;
      const hpEl = card.querySelector<HTMLElement>('[data-b="hp"]')!;
      const slEl = card.querySelector<HTMLElement>('[data-b="sl"]')!;
      if (hpEl.innerHTML !== hpHtml) hpEl.innerHTML = hpHtml;
      if (slEl.innerHTML !== slHtml) slEl.innerHTML = slHtml;
    });
    // ba lô: 10 ô
    const key = s.inventory.map((it) => `${it.id}:${it.count}`).join('|');
    if (this.cache.get('bagkey') !== key) {
      this.cache.set('bagkey', key);
      const bag = this.q('bag');
      bag.innerHTML = '';
      for (let i = 0; i < 10; i++) {
        const it = s.inventory[i];
        const d = document.createElement('div');
        d.className = `hud-bagslot ${it ? 'v10-slot-sel' : 'v10-slot'}`;
        if (it) {
          const ic = it.icon();
          if (ic) d.appendChild(ic);
          d.insertAdjacentHTML('beforeend', `<b>${it.count}</b>`);
          d.title = it.label;
        }
        bag.appendChild(d);
      }
    }
  }
}
