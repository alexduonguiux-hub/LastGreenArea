import type Phaser from 'phaser';
import { Actor } from './Actor';
import { axis, isRunning, type Keys } from '../core/input';

export type Stance = 'dung' | 'khom' | 'bo';

/** Tốc độ px/s theo tư thế (docs/PLAN.md B1). */
export const SPEED: Record<Stance, number> = { dung: 58, khom: 34, bo: 18 };
export const RUN_SPEED = 96;

/** Hàm kiểm tra một điểm chân có đi được không; B1 thay bằng CollisionGrid. */
export type Walkable = (x: number, y: number) => boolean;

export class Player extends Actor {
  stance: Stance = 'dung';
  moving = false;
  walkable: Walkable = () => true;

  constructor(scene: Phaser.Scene, actorId: string, x: number, y: number) {
    super(scene, actorId, x, y, 'di-xuong');
    this.idle();
  }

  update(keys: Keys, dtMs: number): void {
    const dt = dtMs / 1000;
    const a = axis(keys);
    const run = isRunning(keys) && this.stance === 'dung';
    this.moving = a.x !== 0 || a.y !== 0;
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
