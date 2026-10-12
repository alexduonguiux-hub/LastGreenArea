import Phaser from 'phaser';
import { createKeys, type Keys } from '../core/input';
import { ATLAS } from '../core/atlas';
import { Player } from '../entities/Player';
import { Enemy, type StealthConfig } from '../entities/Enemy';
import { Rock } from '../entities/Rock';
import { CollisionGrid, type LevelData } from '../world/CollisionGrid';
import { NoiseSystem } from '../stealth/Noise';
import { drawCone } from '../stealth/VisionCone';
import { LEVEL_LABEL } from '../stealth/Detection';
import { overlay } from '../ui/overlay';

const STANCE_LABEL = { dung: 'Đứng', khom: 'Khom', bo: 'Bò' } as const;
const LEVEL_COLOR = { 'an-minh': 0xf05040, 'nghi-ngo': 0xf0c83c, 'bao-dong': 0xf04650 } as const;
const LEVEL_CSS = { 'an-minh': 'var(--ok)', 'nghi-ngo': 'var(--warn)', 'bao-dong': 'var(--bad)' } as const;

/** B2: màn 1 với Kẻ Lang Thang tuần tra, nón nhìn, đồng hồ phát hiện, ném đá, hạ từ sau, bị phát hiện. */
export class Level extends Phaser.Scene {
  private keys!: Keys;
  private player!: Player;
  private enemies: Enemy[] = [];
  private grid!: CollisionGrid;
  private level!: LevelData & { stealth: StealthConfig };
  private noise = new NoiseSystem();
  private cones!: Phaser.GameObjects.Graphics;
  private fxLayer!: Phaser.GameObjects.Graphics;
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
    const [w, h] = this.level.size;
    const cfg = this.level.stealth;

    this.add.image(0, 0, 'ground-level1').setOrigin(0, 0).setDepth(-1000);
    this.cones = this.add.graphics().setDepth(-500);
    this.fxLayer = this.add.graphics().setDepth(-400);
    for (const o of this.level.objects) this.add.image(o.x, o.y, ATLAS, o.id).setDepth(o.y);

    this.keys = createKeys(this);
    const [sx, sy] = this.level.spawn.duong;
    this.player = new Player(this, 'char/duong', sx, sy);
    this.player.rocks = cfg.rocks;
    this.player.walkable = (x, y) => this.grid.canStand(x, y);
    this.player.onThrowRelease = (x, y, face) => {
      new Rock(this, x + face * 10, y, face, (lx, ly) => this.rockLanded(lx, ly));
    };
    this.player.onBusyEnd = (what) => {
      if (what === 'nem') this.say(`Còn ${this.player.rocks} viên đá.`);
    };

    for (const [id, wps] of Object.entries(this.level.patrol)) {
      const e = new Enemy(this, `enemy/${id}`, wps, cfg, this.grid);
      e.onCatch = () => this.onCaught();
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
    cam.startFollow(this.player, true, 1, 1);
    cam.setRoundPixels(true);

    overlay.clear();
    overlay.topLeft(this.level.name, 'B2 · lõi ẩn nấp');
    overlay.bottom(
      '<kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> đi · <kbd>Shift</kbd> chạy · <kbd>C</kbd> tư thế · <kbd>Space</kbd> ném đá · <kbd>E</kbd> hạ từ sau · <kbd>F3</kbd> lưới · <kbd>F4</kbd> tới đầu cầu',
    );
    this.say('Kẻ Lang Thang canh đầu cầu phía tây. Khom sau bụi, ném đá đánh lạc hướng, hoặc vòng ra sau lưng.');

    const kb = this.input.keyboard!;
    kb.on('keydown-C', () => this.say(`Tư thế: ${STANCE_LABEL[this.player.cycleStance()]}`));
    kb.on('keydown-SPACE', () => {
      if (this.caught) return;
      if (!this.player.throwRock()) this.say(this.player.rocks <= 0 ? 'Hết đá.' : 'Không ném được lúc này.');
    });
    kb.on('keydown-E', () => this.tryTakedown());
    kb.on('keydown-F3', () => this.toggleDebug());
    kb.on('keydown-F4', () => {
      const [bx0, by0, , by1] = this.level.bridge;
      this.player.setPosition(bx0 - 230, (by0 + by1) / 2 + 40);
      this.say('Đã nhảy tới gần đầu cầu (phím thử).');
    });
    kb.on('keydown-ENTER', () => {
      if (this.caught) this.scene.restart();
    });
  }

  private say(text: string): void {
    this.status = text;
  }

  private rockLanded(x: number, y: number): void {
    const r = this.level.stealth.noise.rock;
    this.noise.emit(x, y, r, 'rock');
    const fx = this.add.sprite(x, y, ATLAS, 'fx/tieng-dong-nem-da/0').setDepth(y + 2);
    fx.play('fx/tieng-dong-nem-da');
    fx.once('animationcomplete', () => fx.destroy());
  }

  private tryTakedown(): void {
    if (this.caught || this.player.busy) return;
    const p = this.player;
    const e = this.enemies.find((en) => en.canBeTakenDown(p.x, p.y));
    if (!e) {
      this.say('Phải đứng sau lưng, ngoài nón nhìn, cách dưới 22 px rồi bấm E.');
      return;
    }
    p.takedown(e.face);
    e.takedown();
    this.say(`Dương hạ Kẻ Lang Thang từ sau. Nó dậy sau ${this.level.stealth.downFor} giây.`);
  }

  private onCaught(): void {
    if (this.caught) return;
    this.caught = true;
    this.player.busy = 'ha';
    this.player.playAnim('trung-don-nga', { force: true });
    const el = overlay.center('Bị phát hiện', 'Kẻ Lang Thang đã tóm được Dương.');
    void el;
    const box = document.querySelector('.v10-box.center');
    box?.insertAdjacentHTML('beforeend', '<div class="v10-center-actions"><kbd>Enter</kbd> thử lại từ điểm lưu</div>');
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
    g.lineStyle(1, 0x3eecff, 0.9).strokeCircle(this.player.x, this.player.y, 6);
    for (const e of this.enemies) g.lineStyle(1, 0xff3aa8, 0.9).strokeCircle(e.x, e.y, this.level.stealth.takedown.dist);
  }

  private drawHud(): void {
    const cam = this.cameras.main;
    const p = this.player;
    const hidden = p.stance !== 'dung' && this.grid.hides(p.x, p.y);
    const e = this.enemies[0];
    const lvl = e?.state === 'down' ? null : e?.level;
    const label = e?.state === 'down' ? 'Bị hạ' : lvl ? LEVEL_LABEL[lvl] : '';
    overlay.topLeft(this.level.name, `${STANCE_LABEL[p.stance]}${hidden ? ' · đang ẩn trong bụi' : ''} · Đá ×${p.rocks}`);
    overlay.topRight(
      `<div class="v10-sub">Kẻ Lang Thang · phát hiện</div>${overlay.segments(e ? e.meter.value : 0, lvl ? LEVEL_CSS[lvl] : 'var(--dim)')}<div>${label}</div><div class="v10-sub" style="margin-top:6px;max-width:260px">${this.status}</div>`,
    );
    for (const en of this.enemies) {
      const id = `m-${en.actorId}`;
      if (en.state === 'down' || en.level === 'an-minh') overlay.removeMarker(id);
      else overlay.marker(id, en.x, en.y - 70, cam, en.level === 'bao-dong' ? '!' : '?', en.level === 'bao-dong' ? 'x' : 'q');
    }
  }

  update(_time: number, delta: number): void {
    const dt = delta / 1000;
    const p = this.player;
    if (!this.caught) p.update(this.keys, delta);
    // chạy tạo tiếng động nhỏ liên tục
    this.runNoiseT -= dt;
    if (p.running && this.runNoiseT <= 0) {
      this.noise.emit(p.x, p.y, this.level.stealth.noise.run, 'run');
      this.runNoiseT = 0.35;
    }
    this.noise.update(dt);
    const hidden = p.stance !== 'dung' && this.grid.hides(p.x, p.y);
    const target = { x: p.x, y: p.y, stance: p.stance, hidden };
    this.cones.clear();
    for (const e of this.enemies) {
      if (!this.caught) e.updateAI(dt, target);
      if (e.state !== 'down' && e.state !== 'listen' && e.state !== 'look') {
        drawCone(this.cones, this.level.stealth.vision, e.x, e.y - 12, e.face, LEVEL_COLOR[e.level], e.level === 'an-minh' ? 0.2 : 0.3, this.grid);
      }
    }
    // vòng tiếng động
    this.fxLayer.clear();
    for (const n of this.noise.active) {
      const r = 4 + (n.r - 4) * Math.min(1, n.t / 0.6);
      this.fxLayer.lineStyle(1, n.kind === 'rock' ? 0xf0c83c : 0x7896b0, Math.max(0, (n.kind === 'rock' ? 0.8 : 0.4) - n.t));
      this.fxLayer.strokeEllipse(n.x, n.y, r * 2, r);
    }
    this.drawDebug();
    this.drawHud();
  }
}
