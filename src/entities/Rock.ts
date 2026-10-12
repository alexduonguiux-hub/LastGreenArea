import Phaser from 'phaser';

const VY0 = -110;
const G = 260;
const START_H = 30; // ném từ ngang vai
const LAND_DROP = 8;

/** Thời gian bay từ lúc thả tới lúc chạm đất (nghiệm dương của parabol). */
export function flightTime(): number {
  // y(t) = -START_H + VY0 t + G t²/2 = LAND_DROP
  const a = G / 2;
  const b = VY0;
  const c = -START_H - LAND_DROP;
  return (-b + Math.sqrt(b * b - 4 * a * c)) / (2 * a);
}

/** Viên đá ném: parabol đơn giản; có đích thì tính vận tốc ngang để rơi đúng đích. */
export class Rock extends Phaser.GameObjects.Rectangle {
  vx: number;
  vy = VY0;
  private readonly groundY: number;
  private readonly onLand: (x: number, y: number) => void;

  constructor(scene: Phaser.Scene, x: number, y: number, face: 1 | -1, onLand: (x: number, y: number) => void, target?: { x: number; y: number } | null) {
    super(scene, x, y - START_H, 4, 4, 0xb0b4bc);
    scene.add.existing(this);
    const t = flightTime();
    this.groundY = (target ? target.y : y) + LAND_DROP;
    this.vx = target ? (target.x - x) / t : face * 150;
    if (target) {
      // đích xa/gần theo trục y: bù bằng cách rơi tại y đích (vẫn parabol theo thời gian t)
      this.vy = (this.groundY - (y - START_H) - (G * t * t) / 2) / t;
    }
    this.setDepth(this.groundY);
    this.onLand = onLand;
  }

  preUpdate(_time: number, delta: number): void {
    const dt = delta / 1000;
    this.vy += G * dt;
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    if (this.y >= this.groundY) {
      this.onLand(this.x, this.groundY);
      this.destroy();
    }
  }
}
