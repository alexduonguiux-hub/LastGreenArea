import Phaser from 'phaser';

/** Viên đá ném: parabol đơn giản, chạm "mặt đất" (y khi ném + rơi) thì báo về để tạo tiếng động. */
export class Rock extends Phaser.GameObjects.Rectangle {
  vx: number;
  vy: number;
  private readonly groundY: number;
  private readonly onLand: (x: number, y: number) => void;

  constructor(scene: Phaser.Scene, x: number, y: number, face: 1 | -1, onLand: (x: number, y: number) => void) {
    super(scene, x, y - 30, 4, 4, 0xb0b4bc);
    scene.add.existing(this);
    this.setDepth(y + 1);
    this.vx = face * 150;
    this.vy = -110;
    this.groundY = y + 8;
    this.onLand = onLand;
  }

  preUpdate(_time: number, delta: number): void {
    const dt = delta / 1000;
    this.vy += 260 * dt;
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    this.setDepth(this.groundY);
    if (this.y >= this.groundY) {
      this.onLand(this.x, this.groundY);
      this.destroy();
    }
  }
}
