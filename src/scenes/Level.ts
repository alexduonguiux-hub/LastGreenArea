import Phaser from 'phaser';
import { createKeys, type Keys } from '../core/input';
import { ATLAS } from '../core/atlas';
import { clearSave, formatTime, loadSave, writeSave, type SaveData } from '../core/save';
import type { CharacterDef, Player } from '../entities/Player';
import { Enemy, type StealthConfig } from '../entities/Enemy';
import { Rock } from '../entities/Rock';
import { Npc } from '../entities/Npc';
import { CollisionGrid, type LevelData } from '../world/CollisionGrid';
import { Pickups, ITEM_LABEL } from '../world/Pickups';
import { NoiseSystem } from '../stealth/Noise';
import { drawCone } from '../stealth/VisionCone';
import { CMD_LABEL, MAX_CMDS, PlanMode, type Cmd } from '../stealth/PlanMode';
import { Squad } from '../squad/Squad';
import { Beats, BEATS, SIDE_OBJECTIVES } from '../levels/level1';
import { Dialogue, portraitCanvas, type Line } from '../ui/dialogue';
import { overlay } from '../ui/overlay';
import { Hud, type HudState } from '../ui/hud';

const STANCE_LABEL = { dung: 'Đứng', khom: 'Khom', bo: 'Bò' } as const;
const LEVEL_COLOR = { 'an-minh': 0xf05040, 'nghi-ngo': 0xf0c83c, 'bao-dong': 0xf04650 } as const;
const ORDER = ['duong', 'hung', 'ny', 'son'];
const LEVEL_ID = 'level1';

interface StartData {
  fromSave?: boolean;
}

/** B4: màn 1 đầy đủ 4 nhịp, hội thoại, nhặt đồ, điểm lưu, Mai dẫn đường, Hoàn thành / Bị phát hiện. */
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
  private pickups!: Pickups;
  private beats!: Beats;
  private dialogue!: Dialogue;
  private mai!: Npc;
  private fog!: HTMLDivElement;
  private hud!: Hud;
  private lastSay = '';
  private caught = false;
  private won = false;
  private runNoiseT = 0;
  private objective = '';
  private inventory: Record<string, number> = {};
  private stats = { time: 0, detected: 0 };
  private startData: StartData = {};

  constructor() {
    super('Level');
  }

  init(data: StartData): void {
    this.startData = data ?? {};
  }

  create(): void {
    this.caught = false;
    this.won = false;
    this.enemies = [];
    this.noise = new NoiseSystem();
    this.inventory = {};
    this.stats = { time: 0, detected: 0 };
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

    // điểm lưu
    const save = loadSave();
    const resume = save && save.level === LEVEL_ID && this.startData.fromSave !== false ? save : null;
    const startBeat = resume ? resume.beat : 0;
    const cpKey = resume ? resume.checkpoint : 'trai';
    const [cx, cy] = this.level.checkpoints[cpKey] ?? this.level.spawn.duong;

    this.keys = createKeys(this);
    const spawn: Record<string, [number, number]> = resume
      ? Object.fromEntries(ORDER.map((k, i) => [k, this.standNear(cx - 30 * (i % 2) - 10 * i, cy + 18 * Math.floor(i / 2) + 8 * i)]))
      : this.level.spawn;
    this.squad = new Squad(this, defs, spawn, ORDER);
    for (const m of this.squad.members) {
      m.rocks = resume ? resume.rocks : cfg.rocks;
      m.walkable = (x, y) => this.grid.canStand(x, y);
      m.onThrowRelease = (x, y, face, target) => {
        new Rock(this, x + face * 10, y, face, (lx, ly) => this.rockLanded(lx, ly), target);
      };
    }
    if (resume) {
      this.inventory = { ...resume.inventory };
      this.stats = { ...resume.stats };
      this.squad.setLeader(resume.leader);
    }
    this.plan = new PlanMode(this.squad.members, this.grid);
    this.pickups = new Pickups(this, this.level.pickups, new Set(resume ? (resume.inventory.__taken as unknown as number[]) ?? [] : []));

    for (const [, pt] of Object.entries(this.level.patrol)) {
      const e = new Enemy(this, `enemy/${pt.type}`, pt.points, cfg, this.grid);
      e.onCatch = (v) => this.onCaught(v);
      e.onState = (s) => {
        if (s === 'alert') {
          this.stats.detected++;
          this.say('Bị phát hiện! Kẻ Lang Thang lao tới.');
        } else if (s === 'investigate') this.say('Kẻ Lang Thang nghe tiếng động, đi kiểm tra.');
        else if (s === 'lost') this.say('Nó mất dấu. Trốn kỹ cho đến khi nó quay về tuần tra.');
      };
      this.noise.onNoise((n) => e.hear(n));
      this.enemies.push(e);
    }

    this.mai = new Npc(this, 'npc/mai', this.level.mai.appear[0], this.level.mai.appear[1]);

    const cam = this.cameras.main;
    cam.setBounds(0, 0, w, h);
    cam.startFollow(this.squad.leader, true, 1, 1);
    cam.setRoundPixels(true);

    overlay.clear();
    const ui = document.getElementById('ui')!;
    this.fog = document.createElement('div');
    this.fog.className = 'fog';
    ui.appendChild(this.fog);
    this.dialogue = new Dialogue(ui, (who) => this.speaker(who));
    this.hud = new Hud(ui);
    this.hud.buildMinimap(this.grid);
    this.lastSay = '';

    this.beats = new Beats(this.level);
    this.bindKeys();
    const first = this.beats.startAt(startBeat);
    if (resume) {
      this.fog.style.opacity = '0.35';
      if (startBeat >= 1) {
        this.mai.appear();
        this.mai.setPosition(...this.level.mai.path[Math.min(startBeat - 1, 1)]);
        this.mai.lead(this.level.mai.path.slice(startBeat >= 3 ? 2 : 1));
      }
      this.objective = BEATS[startBeat].objective;
      this.say(`Tiếp tục từ điểm lưu: ${BEATS[startBeat].objective.toLowerCase()}.`);
    } else {
      this.applyBeat(first.beat, first.objective, first.dialogue, first.checkpoint);
    }
  }

  private standNear(x: number, y: number): [number, number] {
    for (let r = 0; r < 60; r += 8) for (const [dx, dy] of [[0, 0], [r, 0], [-r, 0], [0, r], [0, -r], [r, r], [-r, r]]) if (this.grid.canStand(x + dx, y + dy)) return [x + dx, y + dy];
    return [x, y];
  }

  private speaker(who: string) {
    const defs = this.cache.json.get('characters') as Record<string, CharacterDef>;
    const d = defs[who];
    const actor = d ? d.actor : who === 'mai' ? 'npc/mai' : `npc/${who}`;
    const anim = who === 'mai' ? 'lo-lung' : 'di-xuong';
    let portrait: HTMLCanvasElement | null = null;
    const fr = this.textures.getFrame(ATLAS, `${actor}/${anim}/0`);
    if (fr) portrait = portraitCanvas(fr.source.image as HTMLImageElement, { x: fr.cutX, y: fr.cutY, w: fr.cutWidth, h: fr.cutHeight }, 2);
    return { name: d ? d.name : who === 'mai' ? 'Mai' : who, color: d ? d.color : 'var(--tick)', portrait };
  }

  private talk(key: string, onDone?: () => void): void {
    const all = this.cache.json.get('dialogue1') as Record<string, Line[]>;
    this.dialogue.start(all[key] ?? [], onDone);
  }

  private applyBeat(beat: number, objective: string, dialogue: string, checkpoint: string): void {
    this.objective = objective;
    this.saveCheckpoint(beat, checkpoint);
    if (beat === 1) {
      this.mai.lead(this.level.mai.path.slice(0, 2));
      this.talk(dialogue);
    } else if (beat === 3) {
      this.mai.lead(this.level.mai.path.slice(2));
      this.talk(dialogue);
    } else this.talk(dialogue);
    this.say(`Nhiệm vụ mới: ${objective}`, 'quest');
  }

  private saveCheckpoint(beat: number, checkpoint: string): void {
    const d: SaveData = {
      level: LEVEL_ID,
      checkpoint,
      beat,
      inventory: { ...this.inventory, __taken: this.pickups.takenIndices() as unknown as number },
      rocks: this.squad.leader.rocks,
      leader: this.squad.leaderIdx,
      stats: { ...this.stats },
      savedAt: Date.now(),
    };
    writeSave(d);
  }

  private bindKeys(): void {
    const kb = this.input.keyboard!;
    const busyUI = () => this.caught || this.won || this.dialogue.active || this.plan.executing;
    kb.on('keydown-C', () => {
      if (busyUI() || this.plan.active) return;
      this.say(`Tư thế: ${STANCE_LABEL[this.squad.leader.cycleStance()]}`);
    });
    kb.on('keydown-SPACE', () => {
      if (this.dialogue.active) {
        this.dialogue.next();
        return;
      }
      if (busyUI() || this.plan.active) return;
      if (!this.squad.leader.throwRock()) this.say(this.squad.leader.rocks <= 0 ? 'Hết đá. Nhặt thêm dọc đường mòn (E).' : 'Không ném được lúc này.');
    });
    kb.on('keydown-E', () => {
      if (busyUI() || this.plan.active) return;
      this.interact(this.squad.leader);
    });
    for (let i = 0; i < 4; i++)
      kb.on(`keydown-${['ONE', 'TWO', 'THREE', 'FOUR'][i]}`, () => {
        if (busyUI()) return;
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
      if (busyUI()) return;
      if (this.plan.active) this.plan.cancel();
      else {
        this.plan.enter(this.squad.leaderIdx);
        this.say('Kế hoạch: xếp lệnh cho từng người rồi Enter.');
      }
    });
    kb.on('keydown-ESC', () => {
      if (this.plan.active) this.plan.cancel();
    });
    kb.on('keydown-ENTER', () => {
      if (this.dialogue.active) {
        this.dialogue.next();
        return;
      }
      if (this.caught) {
        this.scene.restart({ fromSave: true });
        return;
      }
      if (this.won) {
        clearSave();
        this.scene.restart({ fromSave: false });
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
    kb.on('keydown-F5', () => {
      clearSave();
      this.scene.restart({ fromSave: false });
    });
    kb.on('keydown-F6', () => {
      // phím thử: nhảy tới nhịp kế (lưu điểm lưu tương ứng rồi nạp lại)
      if (busyUI()) return;
      const next = Math.min(BEATS.length - 1, this.beats.beat + 1);
      this.saveCheckpoint(next, BEATS[next].key);
      this.scene.restart({ fromSave: true });
    });
    this.input.on('pointerdown', (p: Phaser.Input.Pointer) => {
      if (this.dialogue.active) return;
      if (!this.plan.active) return;
      const cmd: Cmd = this.plan.tool === 'nem' ? { kind: 'nem', x: p.worldX, y: p.worldY } : { kind: 'di', x: p.worldX, y: p.worldY };
      if (!this.plan.add(cmd)) this.say(cmd.kind === 'nem' ? 'Hết đá hoặc đã đủ 3 lệnh.' : 'Mỗi người tối đa 3 lệnh.');
    });
  }

  /** E: ưu tiên hạ từ sau nếu có thể, không thì nhặt đồ gần. */
  private interact(m: Player): void {
    if (m.busy) return;
    const e = this.enemies.find((en) => en.canBeTakenDown(m.x, m.y));
    if (e) {
      this.doTakedown(m, e);
      return;
    }
    const it = this.pickups.nearest(m.x, m.y, 28);
    if (!it) {
      this.say('Không có gì để nhặt. Hạ từ sau: đứng sau lưng Biến Thể, cách dưới 22 px.');
      return;
    }
    this.pickups.take(it);
    const item = it.def.item;
    if (item === 'da-nem') {
      m.rocks++;
      this.say(`Nhặt được: Đá ném ×${m.rocks}`, 'item');
    } else {
      this.inventory[item] = (this.inventory[item] ?? 0) + 1;
      const side = SIDE_OBJECTIVES.find((s) => s.item === item);
      this.say(`Nhặt được: ${ITEM_LABEL[item] ?? item}${side ? ` ${this.inventory[item]}/${side.need}` : ''}`, 'item');
    }
  }

  private executePlan(): void {
    const total = this.plan.queues.reduce((s, q) => s + q.length, 0);
    if (!total) {
      this.say('Chưa có lệnh nào. Bấm vào bản đồ để thêm Đi tới.');
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

  private say(text: string, kind: 'info' | 'quest' | 'item' = 'info'): void {
    if (text === this.lastSay) return;
    this.lastSay = text;
    this.hud.notify(text, kind);
  }

  /** Icon 16 px của vật phẩm từ atlas (canvas mới mỗi lần vì canvas không clone được bitmap). */
  private itemIcon(item: string): HTMLCanvasElement | null {
    const fr = this.textures.getFrame(ATLAS, `item/${item}`);
    return fr ? portraitCanvas(fr.source.image as HTMLImageElement, { x: fr.cutX, y: fr.cutY, w: fr.cutWidth, h: fr.cutHeight }, 1) : null;
  }

  private rockLanded(x: number, y: number): void {
    this.noise.emit(x, y, this.level.stealth.noise.rock, 'rock');
    const fx = this.add.sprite(x, y, ATLAS, 'fx/tieng-dong-nem-da/0').setDepth(y + 2);
    fx.play('fx/tieng-dong-nem-da');
    fx.once('animationcomplete', () => fx.destroy());
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
    if (this.caught || this.won) return;
    this.caught = true;
    const m = this.squad.members.find((mm) => mm.x === victim.x && mm.y === victim.y) ?? this.squad.leader;
    m.busy = 'ha';
    m.playAnim('trung-don-nga', { force: true });
    overlay.center('Bị phát hiện', `Kẻ Lang Thang đã tóm được ${m.def.name}.`);
    document.querySelector('.v10-box.center')?.insertAdjacentHTML('beforeend', `<div class="v10-center-actions"><kbd>Enter</kbd> thử lại từ điểm lưu "${BEATS[this.beats.beat].objective}"</div>`);
  }

  private onWin(): void {
    if (this.won) return;
    this.won = true;
    this.talk('win', () => {
      const inv = (k: string) => this.inventory[k] ?? 0;
      overlay.center('Hoàn thành · Đường Mòn Sương', 'Cả đội ra khỏi rừng theo ánh sáng xanh.');
      document.querySelector('.v10-box.center')?.insertAdjacentHTML(
        'beforeend',
        `<div class="v10-stats"><span>Thời gian</span><b>${formatTime(this.stats.time)}</b><span>Bị phát hiện</span><b>${this.stats.detected} lần</b><span>Đá khắc ký hiệu</span><b>${inv('da-khac-ky-hieu')}/3</b><span>Mảnh Ký Ức</span><b>${inv('manh-ky-uc')}/6</b><span>Ảnh bốn người</span><b>${inv('anh-bon-nguoi') ? 'có' : 'chưa'}</b></div><div class="v10-center-actions"><kbd>Enter</kbd> chơi lại từ đầu · màn 2 đang xây</div>`,
      );
    });
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
    for (const [, r] of Object.entries(this.level.triggers)) g.lineStyle(1, 0xff3aa8, 0.8).strokeRect(r[0], r[1], r[2] - r[0], r[3] - r[1]);
    for (const e of this.enemies) g.lineStyle(1, 0xff3aa8, 0.9).strokeCircle(e.x, e.y, this.level.stealth.takedown.dist);
  }

  private drawPlan(): void {
    const g = this.planLayer;
    g.clear();
    const cam = this.cameras.main;
    this.squad.members.forEach((m, i) => {
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

  private drawHud(dt: number): void {
    const cam = this.cameras.main;
    const L = this.squad.leader;
    const hidden = L.stance !== 'dung' && this.grid.hides(L.x, L.y);
    let e: Enemy | undefined;
    let bd = Infinity;
    for (const en of this.enemies) {
      const d = Math.hypot(en.x - L.x, en.y - L.y);
      if (d < bd) {
        bd = d;
        e = en;
      }
    }
    const near = this.plan.active ? null : this.pickups.nearest(L.x, L.y, 28);
    const inv = Object.entries(this.inventory)
      .filter(([k]) => !k.startsWith('__'))
      .map(([id, count]) => ({ id, label: ITEM_LABEL[id] ?? id, count, icon: () => this.itemIcon(id) }));
    const state: HudState = {
      levelName: this.level.name,
      objective: this.objective,
      side: SIDE_OBJECTIVES.map((o) => ({ label: o.label, have: this.inventory[o.item] ?? 0, need: o.need })),
      members: this.squad.members.map((m) => ({ name: m.def.name, color: m.def.color, portrait: this.speaker(m.key).portrait, hp: 1, sl: m.running ? 0.8 : 1, rocks: m.rocks })),
      leader: this.squad.leaderIdx,
      stance: L.stance,
      hidden,
      time: formatTime(this.stats.time),
      detect: e ? e.meter.value : 0,
      detectLevel: e ? (e.state === 'down' ? 'down' : e.level) : null,
      executing: this.plan.executing,
      inventory: inv,
      nearPickup: near ? (ITEM_LABEL[near.def.item] ?? near.def.item) : null,
      canTakedown: this.enemies.some((en) => en.canBeTakenDown(L.x, L.y)) && L.hasSkill('ha-tu-sau'),
    };
    this.hud.update(state);
    this.hud.tickToasts(dt);
    const dots = this.squad.members.map((m) => ({ x: m.x, y: m.y, color: m === L ? '#3eecff' : '#d8f4ff', big: m === L }));
    for (const en of this.enemies) if (en.state !== 'down') dots.push({ x: en.x, y: en.y, color: '#f04650', big: false });
    if (this.mai.visibleNow) dots.push({ x: this.mai.x, y: this.mai.y, color: '#50dc78', big: true });
    dots.push({ x: this.level.exit[0], y: this.level.exit[1] + 8, color: '#f0c83c', big: true });
    this.hud.drawMinimap(dots);
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
    } else document.querySelector('#ui .v10-box.top-right')?.remove();
    for (const en of this.enemies) {
      const id = `m-${en.actorId}-${this.enemies.indexOf(en)}`;
      if (en.state === 'down' || en.level === 'an-minh') overlay.removeMarker(id);
      else overlay.marker(id, en.x, en.y - 70, cam, `<span class="v10-marker-${en.level === 'bao-dong' ? 'x' : 'q'}"></span>`, en.level === 'bao-dong' ? 'x' : 'q');
    }
    if (near) overlay.marker('pick', near.def.x, near.def.y - 18, cam, `E · ${ITEM_LABEL[near.def.item] ?? near.def.item}`, 'label');
    else overlay.removeMarker('pick');
  }

  update(_time: number, delta: number): void {
    const dt = delta / 1000;
    const frozen = this.caught || this.won || this.plan.active || this.dialogue.active;
    if (!frozen) {
      this.stats.time += dt;
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
      this.mai.updateLead(delta, L.x, L.y);
      for (const ev of this.beats.update(L.x, L.y)) {
        if (ev.kind === 'beat') this.applyBeat(ev.beat, ev.objective, ev.dialogue, ev.checkpoint);
        else if (ev.kind === 'loop-return') {
          this.fog.style.opacity = '0.35';
          this.mai.appear();
          this.talk('vong-ve');
          this.objective = 'Đi theo ánh sáng xanh';
        } else if (ev.kind === 'win') this.onWin();
      }
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
    if (this.mai.visibleNow) {
      this.fxLayer.fillStyle(0x3eecff, 0.12).fillEllipse(this.mai.x, this.mai.y - 22, 56, 70);
      this.fxLayer.fillStyle(0x3eecff, 0.08).fillEllipse(this.mai.x, this.mai.y - 22, 90, 110);
    }
    this.drawPlan();
    this.drawDebug();
    this.drawHud(dt);
  }
}
