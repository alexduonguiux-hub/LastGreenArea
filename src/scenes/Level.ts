import Phaser from 'phaser';
import { createKeys, type Keys } from '../core/input';
import { ATLAS } from '../core/atlas';
import type { CharacterDef, Player } from '../entities/Player';
import { Enemy, type StealthConfig } from '../entities/Enemy';
import { Rock } from '../entities/Rock';
import { CollisionGrid, type LevelData } from '../world/CollisionGrid';
import { NoiseSystem } from '../stealth/Noise';
import { drawCone } from '../stealth/VisionCone';
import { LEVEL_LABEL } from '../stealth/Detection';
import { CMD_LABEL, MAX_CMDS, PlanMode, type Cmd } from '../stealth/PlanMode';
import { Squad } from '../squad/Squad';
import { overlay } from '../ui/overlay';

const STANCE_LABEL = { dung: 'Đứng', khom: 'Khom', bo: 'Bò' } as const;
const LEVEL_COLOR = { 'an-minh': 0xf05040, 'nghi-ngo': 0xf0c83c, 'bao-dong': 0xf04650 } as const;
const LEVEL_CSS = { 'an-minh': 'var(--ok)', 'nghi-ngo': 'var(--warn)', 'bao-dong': 'var(--bad)' } as const;
const ORDER = ['duong', 'hung', 'ny', 'son'];

/** B3: đội 4 người, đổi thủ lĩnh 1–4, đi theo hàng, chế độ kế hoạch (Tab) thực thi đồng loạt. */
export class Level extends Phaser.Scene {
  private keys!: Keys;
  private squad!: Squad;
  private plan!: PlanMode;
  private enemies: Enemy[] = [];
  private grid!: CollisionGrid;
  private level!: LevelData & { stealth: StealthConfig };
  private noise = new NoiseSystem();
  private cones!: Phaser.GameObjects.Graphics;
  private fxLayer!: Phaser.GameObjects.Graphics;
  private planLayer!: Phaser.GameObjects.Graphics;
  private debug?: Phaser.GameObjects.Graphics;
  private caught = false;
  private runNoiseT = 0;
  private status = '';

  constructor() {
    super('Level');
  }

  create(): void {
    this.caught = false;
    this.enemies = [];
    this.noise = new NoiseSystem();
    this.level = this.cache.json.get('level1') as LevelData & { stealth: StealthConfig };
    this.grid = CollisionGrid.fromLevel(this.level);
    const defs = this.cache.json.get('characters') as Record<string, CharacterDef>;
    const [w, h] = this.level.size;
    const cfg = this.level.stealth;

    this.add.image(0, 0, 'ground-level1').setOrigin(0, 0).setDepth(-1000);
    this.cones = this.add.graphics().setDepth(-500);
    this.fxLayer = this.add.graphics().setDepth(-400);
    this.planLayer = this.add.graphics().setDepth(9000);
    for (const o of this.level.objects) this.add.image(o.x, o.y, ATLAS, o.id).setDepth(o.y);

    this.keys = createKeys(this);
    this.squad = new Squad(this, defs, this.level.spawn, ORDER);
    for (const m of this.squad.members) {
      m.rocks = cfg.rocks;
      m.walkable = (x, y) => this.grid.canStand(x, y);
      m.onThrowRelease = (x, y, face, target) => {
        new Rock(this, x + face * 10, y, face, (lx, ly) => this.rockLanded(lx, ly), target);
      };
    }
    this.plan = new PlanMode(this.squad.members, this.grid);

    for (const [id, wps] of Object.entries(this.level.patrol)) {
      const e = new Enemy(this, `enemy/${id}`, wps, cfg, this.grid);
      e.onCatch = (v) => this.onCaught(v);
      e.onState = (s) => {
        if (s === 'alert') this.say('Bị phát hiện! Kẻ Lang Thang lao tới.');
        else if (s === 'investigate') this.say('Kẻ Lang Thang nghe tiếng động, đi kiểm tra.');
        else if (s === 'lost') this.say('Nó mất dấu. Trốn kỹ cho đến khi nó quay về tuần tra.');
      };
      this.noise.onNoise((n) => e.hear(n));
      this.enemies.push(e);
    }

    const cam = this.cameras.main;
    cam.setBounds(0, 0, w, h);
    cam.startFollow(this.squad.leader, true, 1, 1);
    cam.setRoundPixels(true);

    overlay.clear();
    this.say('Cả đội ở trại. Kẻ Lang Thang canh đầu cầu phía tây.');
    this.bindKeys();
  }

  private bindKeys(): void {
    const kb = this.input.keyboard!;
    kb.on('keydown-C', () => {
      if (this.plan.active || this.plan.executing) return;
      this.say(`Tư thế: ${STANCE_LABEL[this.squad.leader.cycleStance()]}`);
    });
    kb.on('keydown-SPACE', () => {
      if (this.caught || this.plan.active || this.plan.executing) return;
      if (!this.squad.leader.throwRock()) this.say(this.squad.leader.rocks <= 0 ? 'Hết đá.' : 'Không ném được lúc này.');
    });
    kb.on('keydown-E', () => {
      if (this.plan.active || this.plan.executing) return;
      this.tryTakedown(this.squad.leader);
    });
    for (let i = 0; i < 4; i++)
      kb.on(`keydown-${['ONE', 'TWO', 'THREE', 'FOUR'][i]}`, () => {
        if (this.plan.executing) return;
        if (this.plan.active) {
          this.plan.selected = i;
          return;
        }
        const m = this.squad.setLeader(i);
        this.cameras.main.startFollow(m, true, 1, 1);
        this.say(`Điều khiển ${m.def.name} · ${m.def.role}.`);
      });
    kb.on('keydown-TAB', (ev: KeyboardEvent) => {
      ev.preventDefault();
      if (this.caught || this.plan.executing) return;
      if (this.plan.active) this.plan.cancel();
      else {
        this.plan.enter(this.squad.leaderIdx);
        this.say('Kế hoạch: chọn người 1–4, bấm vào bản đồ để thêm "Đi tới". T: ném đá vào điểm bấm · H: hạ gục · G: chờ 2 s · Backspace xóa · Enter thực thi · Esc hủy.');
      }
    });
    kb.on('keydown-ESC', () => {
      if (this.plan.active) this.plan.cancel();
    });
    kb.on('keydown-ENTER', () => {
      if (this.caught) {
        this.scene.restart();
        return;
      }
      if (this.plan.active) this.executePlan();
    });
    kb.on('keydown-T', () => {
      if (this.plan.active) this.plan.tool = this.plan.tool === 'nem' ? 'di' : 'nem';
    });
    kb.on('keydown-H', () => {
      if (this.plan.active && !this.plan.add({ kind: 'ha' })) this.say('Mỗi người tối đa 3 lệnh.');
    });
    kb.on('keydown-G', () => {
      if (this.plan.active && !this.plan.add({ kind: 'cho', s: 2 })) this.say('Mỗi người tối đa 3 lệnh.');
    });
    kb.on('keydown-BACKSPACE', () => {
      if (this.plan.active) this.plan.removeLast();
    });
    kb.on('keydown-F3', () => this.toggleDebug());
    kb.on('keydown-F4', () => {
      if (this.plan.active || this.plan.executing) return;
      const [bx0, by0, , by1] = this.level.bridge;
      const L = this.squad.leader;
      L.setPosition(bx0 - 230, (by0 + by1) / 2 + 40);
      this.squad.members.forEach((m, i) => {
        if (m !== L) m.setPosition(L.x - 30 - i * 22, L.y + 20 + (i % 2) * 18);
      });
      this.squad.setLeader(this.squad.leaderIdx);
      this.say('Đã nhảy cả đội tới gần đầu cầu (phím thử).');
    });
    this.input.on('pointerdown', (p: Phaser.Input.Pointer) => {
      if (!this.plan.active) return;
      const cmd: Cmd = this.plan.tool === 'nem' ? { kind: 'nem', x: p.worldX, y: p.worldY } : { kind: 'di', x: p.worldX, y: p.worldY };
      if (!this.plan.add(cmd)) this.say(cmd.kind === 'nem' ? 'Hết đá hoặc đã đủ 3 lệnh.' : 'Mỗi người tối đa 3 lệnh.');
    });
  }

  private executePlan(): void {
    const total = this.plan.queues.reduce((s, q) => s + q.length, 0);
    if (!total) {
      this.say('Chưa có lệnh nào. Bấm vào bản đồ để thêm "Đi tới".');
      return;
    }
    this.squad.autoFollow = false;
    this.plan.execute(
      this.enemies,
      (m, at) => {
        if (!m.throwRock(at)) this.say(`${m.def.name} không ném được (hết đá hoặc đang bò).`);
      },
      (m, e) => this.doTakedown(m, e),
    );
    this.say('Đang thực thi kế hoạch…');
  }

  private say(text: string): void {
    this.status = text;
  }

  private rockLanded(x: number, y: number): void {
    this.noise.emit(x, y, this.level.stealth.noise.rock, 'rock');
    const fx = this.add.sprite(x, y, ATLAS, 'fx/tieng-dong-nem-da/0').setDepth(y + 2);
    fx.play('fx/tieng-dong-nem-da');
    fx.once('animationcomplete', () => fx.destroy());
  }

  private tryTakedown(m: Player): void {
    if (this.caught || m.busy) return;
    const e = this.enemies.find((en) => en.canBeTakenDown(m.x, m.y));
    if (!e) {
      this.say('Phải đứng sau lưng, ngoài nón nhìn, cách dưới 22 px rồi bấm E.');
      return;
    }
    this.doTakedown(m, e);
  }

  private doTakedown(m: Player, e: Enemy): boolean {
    if (!m.hasSkill('ha-tu-sau')) {
      this.say(`${m.def.name} không có kỹ năng hạ từ sau. Chỉ Dương làm được.`);
      return false;
    }
    m.takedown(e.face);
    e.takedown();
    this.say(`${m.def.name} hạ Kẻ Lang Thang từ sau. Nó dậy sau ${this.level.stealth.downFor} giây.`);
    return true;
  }

  private onCaught(victim: { x: number; y: number }): void {
    if (this.caught) return;
    this.caught = true;
    const m = this.squad.members.find((mm) => mm.x === victim.x && mm.y === victim.y) ?? this.squad.leader;
    m.busy = 'ha';
    m.playAnim('trung-don-nga', { force: true });
    overlay.center('Bị phát hiện', `Kẻ Lang Thang đã tóm được ${m.def.name}.`);
    document.querySelector('.v10-box.center')?.insertAdjacentHTML('beforeend', '<div class="v10-center-actions"><kbd>Enter</kbd> thử lại từ điểm lưu</div>');
  }

  private toggleDebug(): void {
    if (this.debug) {
      this.debug.destroy();
      this.debug = undefined;
      return;
    }
    this.debug = this.add.graphics().setDepth(10000);
  }

  private drawDebug(): void {
    const g = this.debug;
    if (!g) return;
    g.clear();
    const cam = this.cameras.main;
    const col: Record<string, number> = { '#': 0xf04650, o: 0x50dc78, '~': 0x3e96ff, '=': 0xf0c83c };
    this.grid.forEachCell(cam.scrollX, cam.scrollY, cam.scrollX + cam.width, cam.scrollY + cam.height, (c, r, cell) => {
      if (cell === '.') return;
      g.fillStyle(col[cell], 0.35).fillRect(c * this.grid.cell, r * this.grid.cell, this.grid.cell - 1, this.grid.cell - 1);
    });
    for (const e of this.enemies) g.lineStyle(1, 0xff3aa8, 0.9).strokeCircle(e.x, e.y, this.level.stealth.takedown.dist);
  }

  private drawPlan(): void {
    const g = this.planLayer;
    g.clear();
    const cam = this.cameras.main;
    const members = this.squad.members;
    members.forEach((m, i) => {
      const q = this.plan.queues[i];
      const color = Phaser.Display.Color.HexStringToColor(m.def.color).color;
      if (!this.plan.active && !this.plan.executing) {
        overlay.removeMarker(`sel-${i}`);
        for (let k = 0; k < MAX_CMDS; k++) overlay.removeMarker(`cmd-${i}-${k}`);
        return;
      }
      if (this.plan.active && i === this.plan.selected) g.lineStyle(1, color, 1).strokeEllipse(m.x, m.y + 1, 26, 12);
      for (const seg of this.plan.previewPath(i)) {
        g.lineStyle(1, color, 0.9);
        for (let k = 1; k < seg.length; k++) if (k % 2) g.lineBetween(seg[k - 1].x, seg[k - 1].y, seg[k].x, seg[k].y);
      }
      let at = { x: m.x, y: m.y };
      q.forEach((c, k) => {
        if (c.kind === 'di' || c.kind === 'nem') {
          g.lineStyle(1, color, 1).strokeCircle(c.x, c.y, c.kind === 'nem' ? 6 : 4);
          if (c.kind === 'nem') g.lineBetween(at.x, at.y - 20, c.x, c.y);
          overlay.marker(`cmd-${i}-${k}`, c.x, c.y - 8, cam, `${k + 1} ${CMD_LABEL[c.kind]}`, 'label');
          if (c.kind === 'di') at = { x: c.x, y: c.y };
        } else overlay.marker(`cmd-${i}-${k}`, at.x, at.y - 70 - k * 14, cam, `${k + 1} ${CMD_LABEL[c.kind]}${c.kind === 'cho' ? ` ${c.s}s` : ''}`, 'label');
      });
      for (let k = q.length; k < MAX_CMDS; k++) overlay.removeMarker(`cmd-${i}-${k}`);
      overlay.marker(`sel-${i}`, m.x, m.y - 66, cam, `${i + 1}`, 'label');
    });
  }

  private drawHud(): void {
    const cam = this.cameras.main;
    const L = this.squad.leader;
    const hidden = L.stance !== 'dung' && this.grid.hides(L.x, L.y);
    const e = this.enemies[0];
    const lvl = e?.state === 'down' ? null : e?.level;
    const label = e?.state === 'down' ? 'Bị hạ' : lvl ? LEVEL_LABEL[lvl] : '';
    const team = this.squad.members
      .map((m, i) => `<span style="color:${i === this.squad.leaderIdx ? 'var(--ink)' : 'var(--dim)'}"><b style="color:${m.def.color}">${i + 1}</b> ${m.def.name}</span>`)
      .join(' · ');
    overlay.topLeft(this.level.name, `${team}<br>${STANCE_LABEL[L.stance]}${hidden ? ' · ẩn trong bụi' : ''} · Đá ×${L.rocks}`);
    if (this.plan.active) {
      const rows = this.squad.members
        .map((m, i) => {
          const cmds = this.plan.queues[i].map((c, k) => `<b>${k + 1}</b> ${CMD_LABEL[c.kind]}${c.kind === 'cho' ? ` ${c.s}s` : ''}`).join(' → ') || '—';
          return `<div class="v10-row" aria-selected="${i === this.plan.selected}"><span class="n">${i + 1}</span><span>${m.def.name}</span><span class="cmds">${cmds}</span></div>`;
        })
        .join('');
      overlay.topRight(
        `<span class="v10-tag">Kế hoạch</span> <span class="v10-sub">tạm dừng</span>${rows}<div class="v10-hint" style="margin-top:6px">Bấm bản đồ: <span class="v10-tool" aria-pressed="${this.plan.tool === 'di'}">Đi tới</span> · <kbd>T</kbd> <span class="v10-tool" aria-pressed="${this.plan.tool === 'nem'}">Ném đá</span> · <kbd>H</kbd> hạ gục · <kbd>G</kbd> chờ · <kbd>⌫</kbd> xóa · <kbd>Enter</kbd> thực thi · <kbd>Esc</kbd> hủy</div>`,
      );
    } else {
      overlay.topRight(
        `<div class="v10-sub">Kẻ Lang Thang · phát hiện</div>${overlay.segments(e ? e.meter.value : 0, lvl ? LEVEL_CSS[lvl] : 'var(--dim)')}<div>${label}${this.plan.executing ? ' · <span class="v10-tag">đang thực thi</span>' : ''}</div><div class="v10-sub" style="margin-top:6px;max-width:260px">${this.status}</div>`,
      );
    }
    overlay.bottom(
      '<kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> đi · <kbd>Shift</kbd> chạy · <kbd>C</kbd> tư thế · <kbd>Space</kbd> ném đá · <kbd>E</kbd> hạ từ sau · <kbd>1</kbd>–<kbd>4</kbd> đổi người · <kbd>Tab</kbd> kế hoạch · <kbd>F3</kbd> lưới · <kbd>F4</kbd> tới đầu cầu',
    );
    for (const en of this.enemies) {
      const id = `m-${en.actorId}`;
      if (en.state === 'down' || en.level === 'an-minh') overlay.removeMarker(id);
      else overlay.marker(id, en.x, en.y - 70, cam, en.level === 'bao-dong' ? '!' : '?', en.level === 'bao-dong' ? 'x' : 'q');
    }
  }

  update(_time: number, delta: number): void {
    const dt = delta / 1000;
    const frozen = this.caught || this.plan.active;
    if (!frozen) {
      if (this.plan.executing) {
        this.plan.update(delta);
        if (!this.plan.executing) {
          this.squad.autoFollow = true;
          this.squad.setLeader(this.squad.leaderIdx);
          this.say('Kế hoạch xong.');
        }
      } else this.squad.update(this.keys, delta);
      const L = this.squad.leader;
      this.runNoiseT -= dt;
      if (L.running && this.runNoiseT <= 0) {
        this.noise.emit(L.x, L.y, this.level.stealth.noise.run, 'run');
        this.runNoiseT = 0.35;
      }
      this.noise.update(dt);
      const targets = this.squad.targets((x, y) => this.grid.hides(x, y));
      for (const e of this.enemies) e.updateAI(dt, targets);
    }
    this.cones.clear();
    for (const e of this.enemies) {
      if (e.state !== 'down' && e.state !== 'listen' && e.state !== 'look') {
        drawCone(this.cones, this.level.stealth.vision, e.x, e.y - 12, e.face, LEVEL_COLOR[e.level], e.level === 'an-minh' ? 0.2 : 0.3, this.grid);
      }
    }
    this.fxLayer.clear();
    for (const n of this.noise.active) {
      const r = 4 + (n.r - 4) * Math.min(1, n.t / 0.6);
      this.fxLayer.lineStyle(1, n.kind === 'rock' ? 0xf0c83c : 0x7896b0, Math.max(0, (n.kind === 'rock' ? 0.8 : 0.4) - n.t));
      this.fxLayer.strokeEllipse(n.x, n.y, r * 2, r);
    }
    this.drawPlan();
    this.drawDebug();
    this.drawHud();
  }
}
