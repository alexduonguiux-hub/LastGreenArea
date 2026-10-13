import type Phaser from 'phaser';
import { Actor } from './Actor';
import { axis, isRunning, type Keys } from '../core/input';

export type Stance = 'dung' | 'khom' | 'bo';

/** Tốc độ px/s theo tư thế (docs/PLAN.md B1). */
export const SPEED: Record<Stance, number> = { dung: 58, khom: 34, bo: 18 };
export const RUN_SPEED = 96;

/** Hàm kiểm tra một điểm chân có đi được không (CollisionGrid.canStand). */
export type Walkable = (x: number, y: number) => boolean;

export interface CharacterDef {
  name: string;
  actor: string;
  role: string;
  skills: string[];
  color: string;
}

export class Player extends Actor {
  readonly key: string;
  readonly def: CharacterDef;
  stance: Stance = 'dung';
  moving = false;
  running = false;
  /** hành động đang khóa điều khiển: ném đá, hạ gục */
  busy: 'nem' | 'ha' | null = null;
  rocks = 5;
  walkable: Walkable = () => true;
  /** gọi đúng khung thả đá (khung 6/8 của "Ném đá") */
  onThrowRelease?: (x: number, y: number, face: 1 | -1, target: { x: number; y: number } | null) => void;
  onBusyEnd?: (what: 'nem' | 'ha') => void;
  private throwTarget: { x: number; y: number } | null = null;

  constructor(scene: Phaser.Scene, key: string, def: CharacterDef, x: number, y: number) {
    super(scene, def.actor, x, y, 'di-xuong');
    this.key = key;
    this.def = def;
    this.idle();
    this.on('animationupdate', (_a: Phaser.Animations.Animation, frame: Phaser.Animations.AnimationFrame) => {
      if (this.busy === 'nem' && frame.index === 6) this.onThrowRelease?.(this.x, this.y, this.face, this.throwTarget);
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

  hasSkill(skill: string): boolean {
    return this.def.skills.includes(skill);
  }

  setStance(s: Stance): void {
    if (s === this.stance) return;
    this.stance = s;
    this.current = '';
    this.playAnim(s === 'bo' ? 'bo-nup' : s === 'khom' ? 'khom-trai' : 'di-sang-trai');
    this.idle();
  }

  cycleStance(): Stance {
    this.setStance(this.stance === 'dung' ? 'khom' : this.stance === 'khom' ? 'bo' : 'dung');
    return this.stance;
  }

  /** Ném đá (có thể nhắm vào điểm): trả false nếu hết đá hoặc đang bận/bò. */
  throwRock(target: { x: number; y: number } | null = null): boolean {
    if (this.busy || this.stance === 'bo' || this.rocks <= 0) return false;
    this.rocks--;
    this.busy = 'nem';
    this.throwTarget = target;
    if (target && Math.abs(target.x - this.x) > 2) this.setFace(target.x > this.x ? 1 : -1);
    this.playAnim('nem-da', { force: true });
    return true;
  }

  /** Hạ từ sau: quay mặt theo hướng nạn nhân rồi phát hoạt ảnh khóa siết. */
  takedown(face: 1 | -1): void {
    this.busy = 'ha';
    this.setFace(face);
    this.playAnim('khoa-siet-tu-sau', { force: true });
  }

  /** Điều khiển bằng phím (thủ lĩnh). */
  update(keys: Keys, dtMs: number): void {
    if (this.busy) {
      this.moving = false;
      this.running = false;
      return;
    }
    const a = axis(keys);
    const run = isRunning(keys) && this.stance === 'dung';
    this.step(a.x, a.y, run, dtMs / 1000);
  }

  /** Đi về phía điểm (người đi theo, lệnh kế hoạch). Trả true khi tới nơi. */
  moveTo(tx: number, ty: number, dtMs: number, run = false, arrive = 4): boolean {
    if (this.busy) return false;
    const dx = tx - this.x;
    const dy = ty - this.y;
    const d = Math.hypot(dx, dy);
    if (d <= arrive) {
      this.step(0, 0, false, 0);
      return true;
    }
    const dt = dtMs / 1000;
    const sp = run && this.stance === 'dung' ? RUN_SPEED : SPEED[this.stance];
    const stepLen = Math.min(d, sp * dt);
    this.step(dx / d, dy / d, run, stepLen / sp);
    return Math.hypot(tx - this.x, ty - this.y) <= arrive;
  }

  /** Bước theo vector (ax, ay) đơn vị/0 trong dt giây, có trượt dọc tường và chọn hoạt ảnh. */
  private step(ax: number, ay: number, run: boolean, dt: number): void {
    this.moving = ax !== 0 || ay !== 0;
    this.running = run && this.moving && this.stance === 'dung';
    if (!this.moving) {
      this.idle();
      return;
    }
    const len = Math.hypot(ax, ay);
    const sp = this.running ? RUN_SPEED : SPEED[this.stance];
    const nx = this.x + (ax / len) * sp * dt;
    const ny = this.y + (ay / len) * sp * dt;
    if (this.walkable(nx, this.y)) this.x = nx; // trượt dọc tường: thử từng trục
    if (this.walkable(this.x, ny)) this.y = ny;
    if (Math.abs(ax) > 0.3) this.setFace(ax > 0 ? 1 : -1);
    this.pickAnim(ax, ay, this.running);
  }

  private pickAnim(ax: number, ay: number, run: boolean): void {
    if (this.stance === 'bo') {
      this.playAnim('bo-nup');
      return;
    }
    const vertical = Math.abs(ay) > Math.abs(ax) * 1.2;
    if (this.stance === 'khom') {
      // hoạt ảnh khom dẫn xuất bằng code từ khung đi (art/legacy_import.crouch_anims)
      this.playAnim(vertical && ay < 0 ? 'khom-len' : vertical && ay > 0 ? 'khom-xuong' : 'khom-trai');
      return;
    }
    if (vertical && ay < 0) {
      // "Đi lên" chưa có trong sheet bàn giao (A2 sẽ sinh); tạm dùng "Chạy lên" chậm lại.
      if (!this.playAnim('di-len')) this.playAnim('chay-len', { frameRate: run ? 12 : 6 });
    } else if (vertical && ay > 0) {
      this.playAnim(run ? 'chay-xuong' : 'di-xuong');
    } else {
      this.playAnim(run ? 'chay' : 'di-sang-trai');
    }
  }
}
