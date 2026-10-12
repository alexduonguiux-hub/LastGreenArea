import type Phaser from 'phaser';
import { Actor } from './Actor';
import { axis, isRunning, type Keys } from '../core/input';

export type Stance = 'dung' | 'khom' | 'bo';

/** Tốc độ px/s theo tư thế (docs/PLAN.md B1). */
export const SPEED: Record<Stance, number> = { dung: 58, khom: 34, bo: 18 };
export const RUN_SPEED = 96;

/** Hàm kiểm tra một điểm chân có đi được không (CollisionGrid.canStand). */
export type Walkable = (x: number, y: number) => boolean;

export class Player extends Actor {
  stance: Stance = 'dung';
  moving = false;
  running = false;
  /** hành động đang khóa điều khiển: ném đá, hạ gục */
  busy: 'nem' | 'ha' | null = null;
  rocks = 5;
  walkable: Walkable = () => true;
  /** gọi đúng khung thả đá (khung 6/8 của "Ném đá") */
  onThrowRelease?: (x: number, y: number, face: 1 | -1) => void;
  onBusyEnd?: (what: 'nem' | 'ha') => void;

  constructor(scene: Phaser.Scene, actorId: string, x: number, y: number) {
    super(scene, actorId, x, y, 'di-xuong');
    this.idle();
    this.on('animationupdate', (_a: Phaser.Animations.Animation, frame: Phaser.Animations.AnimationFrame) => {
      if (this.busy === 'nem' && frame.index === 6) this.onThrowRelease?.(this.x, this.y, this.face);
    });
    this.on('animationcomplete', () => {
      if (!this.busy) return;
      const what = this.busy;
      this.busy = null;
      this.current = '';
      this.playAnim('di-sang-trai');
      this.idle();
      this.onBusyEnd?.(what);
    });
  }

  cycleStance(): Stance {
    this.stance = this.stance === 'dung' ? 'khom' : this.stance === 'khom' ? 'bo' : 'dung';
    this.current = '';
    this.playAnim(this.stance === 'bo' ? 'bo-nup' : 'di-sang-trai');
    this.idle();
    return this.stance;
  }

  /** Ném đá: trả false nếu hết đá hoặc đang bận/bò. */
  throwRock(): boolean {
    if (this.busy || this.stance === 'bo' || this.rocks <= 0) return false;
    this.rocks--;
    this.busy = 'nem';
    this.playAnim('nem-da', { force: true });
    return true;
  }

  /** Hạ từ sau: quay mặt theo hướng nạn nhân rồi phát hoạt ảnh khóa siết. */
  takedown(face: 1 | -1): void {
    this.busy = 'ha';
    this.setFace(face);
    this.playAnim('khoa-siet-tu-sau', { force: true });
  }

  update(keys: Keys, dtMs: number): void {
    if (this.busy) {
      this.moving = false;
      this.running = false;
      return;
    }
    const dt = dtMs / 1000;
    const a = axis(keys);
    const run = isRunning(keys) && this.stance === 'dung';
    this.moving = a.x !== 0 || a.y !== 0;
    this.running = run && this.moving;
    if (!this.moving) {
      this.idle();
      return;
    }
    const len = Math.hypot(a.x, a.y);
    const sp = run ? RUN_SPEED : SPEED[this.stance];
    const nx = this.x + (a.x / len) * sp * dt;
    const ny = this.y + (a.y / len) * sp * dt;
    if (this.walkable(nx, this.y)) this.x = nx; // trượt dọc tường: thử từng trục
    if (this.walkable(this.x, ny)) this.y = ny;
    if (a.x !== 0) this.setFace(a.x > 0 ? 1 : -1);
    this.pickAnim(a, run);
  }

  private pickAnim(a: { x: number; y: number }, run: boolean): void {
    if (this.stance === 'bo') {
      this.playAnim('bo-nup');
      return;
    }
    if (a.y < 0) {
      // "Đi lên" chưa có trong sheet bàn giao (A2 sẽ sinh); tạm dùng "Chạy lên" chậm lại.
      if (!this.playAnim('di-len')) this.playAnim('chay-len', { frameRate: run ? 12 : 6 });
    } else if (a.y > 0) {
      this.playAnim(run ? 'chay-xuong' : 'di-xuong');
    } else {
      this.playAnim(run ? 'chay' : 'di-sang-trai');
    }
  }
}
