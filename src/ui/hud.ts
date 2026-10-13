/**
 * HUD v10 trên lớp DOM, ghép từ thành phần 9-slice và icon sinh trong atlas (src/ui/v10.css).
 * Bố cục theo moodboard assets/ui/v10_hud.png: Nhiệm vụ (trái trên), băng rôn tên màn (giữa trên), đồng hồ + bản đồ nhỏ
 * (phải trên), thông báo một dòng có icon (phải), Đội 2×2 (trái dưới), bảng hành động: cột tư thế có icon + 4 ô hành động
 * vuông lớn có icon và phím ở góc (giữa dưới), Ba lô 2×6 có thanh cuộn (phải dưới).
 * DOM dựng một lần; mỗi khung chỉ đổi chữ/giá trị khi khác trước để tránh churn.
 */
import type { CollisionGrid } from '../world/CollisionGrid';

export type HudStance = 'chay' | 'dung' | 'khom' | 'bo';
/** Icon cho ô hành động: lớp CSS của glyph trong atlas (v10-icon-*) hoặc hàm tạo canvas 16 px. */
export type HudIcon = string | (() => HTMLCanvasElement | null) | null;

export interface HudMember {
  name: string;
  color: string;
  portrait: HTMLCanvasElement | null;
  hp: number; // 0–1
  sl: number; // 0–1
  rocks: number;
  stance: HudStance;
}
export interface HudSlot {
  key: string;
  label: string;
  on: boolean;
  icon: HudIcon;
}
export interface HudState {
  levelName: string;
  objective: string;
  side: { label: string; have: number; need: number }[];
  members: HudMember[];
  leader: number;
  stance: HudStance;
  hidden: boolean;
  time: string;
  detect: number; // 0–1
  detectLevel: 'an-minh' | 'nghi-ngo' | 'bao-dong' | 'down' | null;
  executing: boolean;
  slots: HudSlot[];
  inventory: { id: string; label: string; count: number; icon: () => HTMLCanvasElement | null }[];
}

const STANCES: [HudStance, string][] = [
  ['chay', 'Chạy'],
  ['dung', 'Đi'],
  ['khom', 'Khom'],
  ['bo', 'Bò'],
];
const LEVEL_SEG = { 'an-minh': 'ok', 'nghi-ngo': 'warn', 'bao-dong': 'bad', down: 'off' } as const;
const LEVEL_TEXT = { 'an-minh': 'Ẩn mình', 'nghi-ngo': 'Nghi ngờ', 'bao-dong': 'Báo động', down: 'Bị hạ' } as const;
const BAG_SLOTS = 12;

const segs = (color: string, v: number) => {
  const n = Math.round(Math.max(0, Math.min(1, v)) * 10);
  return `<i class="v10-seg-${color}" style="width:calc(var(--px)*5*${n})"></i><i class="v10-seg-off" style="width:calc(var(--px)*5*${10 - n})"></i>`;
};

export class Hud {
  private el: HTMLDivElement;
  private mini!: HTMLCanvasElement;
  private miniBase: HTMLCanvasElement | null = null;
  private miniScale = 1;
  private toasts: { el: HTMLDivElement; t: number }[] = [];
  private cache = new Map<string, string>();
  private teamBuilt = false;
  private slotIcons: (HudIcon | undefined)[] = [];

  constructor(root: HTMLElement) {
    this.el = document.createElement('div');
    this.el.className = 'hud';
    this.el.innerHTML = `
      <section class="v10-panel hud-mission"><span class="v10-title">Nhiệm vụ</span>
        <div class="hud-level" data-k="level"></div>
        <div class="hud-obj"><span class="v10-check-off" data-k="objcheck"></span><span data-k="objective"></span></div>
        <div class="hud-side" data-k="side"></div>
      </section>
      <div class="v10-panel hud-name"><span class="chev">«</span><span data-k="name"></span><span class="chev">»</span></div>
      <section class="v10-panel hud-clock"><i class="v10-icon-clock"></i><span data-k="time">0:00</span></section>
      <section class="v10-panel hud-map"><span class="v10-title">Bản đồ</span><canvas class="hud-mini" width="100" height="60"></canvas></section>
      <div class="hud-toasts" data-k="toasts"></div>
      <section class="v10-panel hud-team"><span class="v10-title">Đội</span><div class="hud-cards" data-k="cards"></div></section>
      <section class="v10-panel hud-actions"><span class="v10-title" data-k="leader"></span>
        <div class="hud-act">
          <div class="hud-stances" data-k="stances"></div>
          <div class="hud-slots" data-k="slots"></div>
        </div>
        <div class="hud-detect"><span class="v10-sub">Phát hiện</span><span class="hud-detbar" data-k="detbar"></span><span data-k="detlabel"></span></div>
      </section>
      <section class="v10-panel hud-bag"><span class="v10-title">Ba lô</span>
        <div class="hud-tabs"><span class="v10-tab-active">Vật phẩm</span><span class="v10-tab-normal">Vũ khí</span><span class="v10-tab-normal">Chìa khóa</span></div>
        <div class="hud-bagbody"><div class="hud-grid" data-k="bag"></div><div class="hud-scroll"><i class="v10-scroll-track"></i><b class="v10-scroll-thumb"></b></div></div>
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
    // lưới mờ như moodboard (mỗi 8 ô = 128 px thế giới)
    x.fillStyle = 'rgba(62, 236, 255, 0.18)';
    for (let gx = 0; gx < this.mini.width; gx += 8) x.fillRect(gx, 0, 1, this.mini.height);
    for (let gy = 0; gy < this.mini.height; gy += 8) x.fillRect(0, gy, this.mini.width, 1);
    for (const d of dots) {
      x.fillStyle = d.color;
      const px = Math.floor(d.x / this.miniScale);
      const py = Math.floor(d.y / this.miniScale);
      x.fillRect(px - (d.big ? 1 : 0), py - (d.big ? 1 : 0), d.big ? 3 : 2, d.big ? 3 : 2);
    }
  }

  /** Thông báo một dòng: icon theo loại (nhiệm vụ: cuộn vàng, vật phẩm: hộp xanh, khác: dấu !) + LED. */
  notify(text: string, kind: 'info' | 'quest' | 'item' = 'info'): void {
    const el = document.createElement('div');
    el.className = `v10-panel hud-toast ${kind}`;
    const ico = kind === 'quest' ? 'v10-icon-quest' : kind === 'item' ? 'v10-icon-item' : 'v10-marker-x';
    el.innerHTML = `<i class="${ico}"></i><span class="txt">${text}</span><b class="v10-led-${kind === 'quest' ? 'warn' : kind === 'item' ? 'ok' : 'bad'}"></b>`;
    el.title = text;
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

  private iconEl(icon: HudIcon): HTMLElement | null {
    if (!icon) return null;
    if (typeof icon === 'string') {
      const i = document.createElement('i');
      i.className = icon;
      return i;
    }
    return icon();
  }

  update(s: HudState): void {
    this.set('level', s.levelName);
    this.set('objective', s.objective);
    this.set('side', s.side.map((o) => `<div class="${o.have >= o.need ? 'done' : ''}"><span class="v10-check-${o.have >= o.need ? 'on' : 'off'}"></span>${o.label} <b>${o.have}/${o.need}</b></div>`).join(''));
    this.set('name', s.levelName);
    this.set('time', s.time);
    const L = s.members[s.leader];
    this.set('leader', `${L.name} · ${s.leader === 0 ? 'Trưởng nhóm' : 'Điều khiển'}`);
    this.set(
      'stances',
      STANCES.map(([k, label]) => `<div class="${k === s.stance ? 'v10-choice-sel' : 'v10-choice'}"><i class="v10-icon-${k}"></i><span>${label}${k === s.stance && s.hidden ? ' · ẩn' : ''}</span></div>`).join(''),
    );
    // ô hành động: dựng lại khi phím/nhãn/trạng thái đổi; icon canvas gắn sau vì innerHTML không mang canvas
    const slotKey = s.slots.map((sl, i) => `${sl.key}|${sl.label}|${sl.on}|${typeof sl.icon === 'string' ? sl.icon : sl.icon ? `fn${i}` : ''}`).join('#');
    if (this.cache.get('slotkey') !== slotKey || s.slots.some((sl, i) => sl.icon !== this.slotIcons[i])) {
      this.cache.set('slotkey', slotKey);
      this.slotIcons = s.slots.map((sl) => sl.icon);
      const box = this.q('slots');
      box.innerHTML = '';
      for (const sl of s.slots) {
        const d = document.createElement('div');
        d.className = `hud-slot ${sl.on ? 'on' : ''}`;
        d.innerHTML = `<div class="box ${sl.on ? 'v10-slot-sel' : 'v10-slot'}"><span class="ico"></span><span class="v10-keycap">${sl.key}</span></div><span class="lbl">${sl.label}</span>`;
        const ic = this.iconEl(sl.icon);
        if (ic) d.querySelector('.ico')!.appendChild(ic);
        box.appendChild(d);
      }
    }
    const seg = s.detectLevel ? LEVEL_SEG[s.detectLevel] : 'off';
    this.set('detbar', segs(seg, seg === 'off' ? 0 : s.detect));
    this.set('detlabel', s.detectLevel ? LEVEL_TEXT[s.detectLevel] : '');
    // thẻ đội: dựng một lần (chân dung), sau đó chỉ đổi lớp, thanh và icon tư thế
    const cards = this.q('cards');
    if (!this.teamBuilt) {
      cards.innerHTML = s.members
        .map((m, i) => `<div class="hud-card" data-i="${i}"><b class="num">${i + 1}</b><div class="pf"></div><div class="info"><div class="nm">${m.name}</div><div class="bar"><span>HP</span><i data-b="hp"></i></div><div class="bar"><span>SL</span><i data-b="sl"></i></div></div><i class="st" data-b="st"></i></div>`)
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
      const hpHtml = segs('ok', m.hp);
      const slHtml = segs('warn', m.sl);
      const hpEl = card.querySelector<HTMLElement>('[data-b="hp"]')!;
      const slEl = card.querySelector<HTMLElement>('[data-b="sl"]')!;
      const stEl = card.querySelector<HTMLElement>('[data-b="st"]')!;
      if (hpEl.innerHTML !== hpHtml) hpEl.innerHTML = hpHtml;
      if (slEl.innerHTML !== slHtml) slEl.innerHTML = slHtml;
      const stCls = `st v10-icon-${m.stance}`;
      if (stEl.className !== stCls) stEl.className = stCls;
    });
    // ba lô: 2 hàng × 6 ô + thanh cuộn
    const key = s.inventory.map((it) => `${it.id}:${it.count}`).join('|');
    if (this.cache.get('bagkey') !== key) {
      this.cache.set('bagkey', key);
      const bag = this.q('bag');
      bag.innerHTML = '';
      for (let i = 0; i < BAG_SLOTS; i++) {
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
