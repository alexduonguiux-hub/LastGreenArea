import type Phaser from 'phaser';
import { Actor } from './Actor';
import { DetectionMeter, type DetectLevel } from '../stealth/Detection';
import { inCone, type ConeConfig } from '../stealth/VisionCone';
import type { Noise } from '../stealth/Noise';
import type { CollisionGrid } from '../world/CollisionGrid';

export type EnemyState = 'patrol' | 'listen' | 'suspect' | 'investigate' | 'look' | 'alert' | 'lost' | 'down';

export interface StealthConfig {
  vision: ConeConfig;
  detect: { suspect: number; fillBase: number; stance: Record<string, number>; decay: number };
  noise: { rock: number; run: number };
  speed: { patrol: number; investigate: number; alert: number };
  listenEvery: number;
  listenFor: number;
  lookFor: number;
  downFor: number;
  takedown: { dist: number };
  rocks: number;
}

export interface Target {
  x: number;
  y: number;
  stance: string;
  hidden: boolean; // đang khom/bò trong bụi
}

/**
 * Kẻ Lang Thang (màn 1): tuần tra giữa các điểm, dừng nghe ngóng theo nhịp, nhìn thấy thì nghi ngờ rồi báo động,
 * nghe tiếng động thì đi kiểm tra, mất dấu thì quay về tuần tra. Bị hạ từ sau thì nằm một lúc rồi dậy.
 */
export class Enemy extends Actor {
  state: EnemyState = 'patrol';
  readonly meter: DetectionMeter;
  private wp = 0;
  private timer = 0;
  private cadence = 0;
  private target: { x: number; y: number } | null = null;
  private lastSeen: { x: number; y: number } | null = null;
  readonly waypoints: [number, number][];
  private readonly cfg: StealthConfig;
  private readonly grid: CollisionGrid;
  /** gọi khi tóm được mục tiêu */
  onCatch?: (victim: Target) => void;
  onState?: (s: EnemyState) => void;

  constructor(scene: Phaser.Scene, actorId: string, waypoints: [number, number][], cfg: StealthConfig, grid: CollisionGrid) {
    super(scene, actorId, waypoints[0][0], waypoints[0][1], 'le-buoc-trai');
    this.waypoints = waypoints;
    this.cfg = cfg;
    this.grid = grid;
    this.meter = new DetectionMeter(cfg.detect);
    this.setFace(1);
    this.playAnim('le-buoc-trai');
  }

  get level(): DetectLevel {
    return this.meter.level;
  }

  get isActive(): boolean {
    return this.state !== 'down';
  }

  /** Mục tiêu có đang ở sau lưng, trong tầm hạ gục không. */
  canBeTakenDown(tx: number, ty: number): boolean {
    if (!this.isActive) return false;
    const d = Math.hypot(tx - this.x, ty - this.y);
    const behind = Math.sign(tx - this.x) !== this.face || Math.abs(tx - this.x) < 4;
    return d <= this.cfg.takedown.dist && behind;
  }

  takedown(): void {
    this.go('down');
    this.meter.reset();
    this.timer = this.cfg.downFor;
    this.playAnim('bi-ha', { force: true });
  }

  hear(n: Noise): void {
    if (!this.isActive || this.state === 'alert') return;
    if (Math.hypot(n.x - this.x, n.y - this.y) > n.r) return;
    this.target = { x: n.x, y: n.y };
    this.go('investigate');
  }

  private go(s: EnemyState): void {
    if (s === this.state) return;
    this.state = s;
    this.onState?.(s);
  }

  private walkTo(tx: number, ty: number, sp: number, dt: number): boolean {
    const d = Math.hypot(tx - this.x, ty - this.y);
    if (d < 3) return true;
    const nx = this.x + ((tx - this.x) / d) * sp * dt;
    const ny = this.y + ((ty - this.y) / d) * sp * dt;
    if (this.grid.canStand(nx, this.y)) this.x = nx;
    if (this.grid.canStand(this.x, ny)) this.y = ny;
    if (Math.abs(tx - this.x) > 2) this.setFace(tx > this.x ? 1 : -1);
    return false;
  }

  updateAI(dt: number, targets: Target[]): void {
    const cfg = this.cfg;
    if (this.state === 'down') {
      this.timer -= dt;
      if (this.timer <= 0) {
        this.go('patrol');
        this.playAnim('le-buoc-trai', { force: true });
      }
      return;
    }
    // nhìn: lấy người lộ nhất trong đội
    const sensing = this.state !== 'listen' && this.state !== 'look';
    let t: Target = targets[0];
    let dist01 = -1;
    if (sensing) {
      for (const tg of targets) {
        if (tg.hidden) continue;
        const d = inCone(cfg.vision, this.x, this.y - 12, this.face, tg.x, tg.y - 12, this.grid);
        if (d >= 0 && (dist01 < 0 || d < dist01)) {
          dist01 = d;
          t = tg;
        }
      }
    }
    const seen = dist01 >= 0;
    if (!seen) {
      // khi không thấy ai, đuổi theo người gần nhất lúc báo động
      let bd = Infinity;
      for (const tg of targets) {
        const d = Math.hypot(tg.x - this.x, tg.y - this.y);
        if (d < bd) {
          bd = d;
          t = tg;
        }
      }
    }
    const lvl = this.meter.update(dt, seen, Math.max(0, dist01), t.stance);
    if (seen) this.lastSeen = { x: t.x, y: t.y };
    if (lvl === 'bao-dong' && this.state !== 'alert') this.go('alert');
    else if (lvl === 'nghi-ngo' && (this.state === 'patrol' || this.state === 'listen')) {
      this.target = { x: t.x, y: t.y };
      this.go('suspect');
    }

    switch (this.state) {
      case 'patrol': {
        const [wx, wy] = this.waypoints[this.wp];
        this.cadence += dt;
        if (this.walkTo(wx, wy, cfg.speed.patrol, dt)) {
          this.wp = (this.wp + 1) % this.waypoints.length;
          this.go('listen');
          this.timer = cfg.listenFor;
        } else if (this.cadence >= cfg.listenEvery) {
          this.cadence = 0;
          this.go('listen');
          this.timer = cfg.listenFor * 0.75;
        }
        break;
      }
      case 'listen':
        this.timer -= dt;
        if (this.timer <= 0) {
          this.setFace(this.face > 0 ? -1 : 1); // quay đầu
          this.go('patrol');
          this.cadence = 0;
          // sau khi quay đầu, tiếp tục tới điểm kế tiếp theo hướng vừa nhìn nếu hợp lý
          const [wx] = this.waypoints[this.wp];
          if (Math.sign(wx - this.x) !== this.face && this.waypoints.length > 1) this.wp = (this.wp + 1) % this.waypoints.length;
        }
        break;
      case 'suspect':
        if (lvl === 'an-minh') this.go('patrol');
        else if (this.target && this.walkTo(this.target.x, this.target.y, cfg.speed.investigate, dt)) {
          this.go('look');
          this.timer = cfg.lookFor;
        }
        break;
      case 'investigate':
        if (this.target && this.walkTo(this.target.x, this.target.y, cfg.speed.investigate, dt)) {
          this.go('look');
          this.timer = cfg.lookFor;
        }
        break;
      case 'look':
        this.timer -= dt;
        if (this.timer > cfg.lookFor * 0.5 && this.timer < cfg.lookFor * 0.5 + dt) this.setFace(this.face > 0 ? -1 : 1);
        if (this.timer <= 0) this.go('patrol');
        break;
      case 'alert':
        if (seen) this.walkTo(t.x, t.y, cfg.speed.alert, dt);
        else if (this.lastSeen && this.walkTo(this.lastSeen.x, this.lastSeen.y, cfg.speed.alert, dt)) {
          this.go('lost');
          this.timer = cfg.lookFor;
        }
        for (const tg of targets) if (Math.hypot(tg.x - this.x, tg.y - this.y) < 14) this.onCatch?.(tg);
        break;
      case 'lost':
        this.timer -= dt;
        if (seen) this.go('alert');
        else if (this.timer <= 0) {
          this.meter.reset();
          this.go('patrol');
        }
        break;
    }
    // hoạt ảnh: đi khi di chuyển, khung đầu khi đứng nghe
    if (this.state === 'listen' || this.state === 'look' || this.state === 'lost') this.idle();
    else this.playAnim('le-buoc-trai');
  }
}
