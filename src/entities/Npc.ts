import type Phaser from 'phaser';
import { Actor } from './Actor';

/** Mai: ánh sáng xanh dẫn đường. Hiện ra, lơ lửng, đi trước theo lộ trình và chờ đội tới gần. */
export class Npc extends Actor {
  private path: [number, number][] = [];
  private speed = 40;
  visibleNow = false;

  constructor(scene: Phaser.Scene, actorId: string, x: number, y: number) {
    super(scene, actorId, x, y, 'lo-lung');
    this.setVisible(false);
    this.setAlpha(0.85);
  }

  appear(): void {
    this.visibleNow = true;
    this.setVisible(true);
    if (!this.playAnim('hien-ra', { force: true })) this.playAnim('lo-lung');
    this.once('animationcomplete', () => this.playAnim('lo-lung', { force: true }));
  }

  /** Đi trước tới các điểm; dừng lại chờ nếu đội cách quá xa. */
  lead(path: [number, number][]): void {
    this.path = [...path];
  }

  updateLead(dtMs: number, squadX: number, squadY: number, wait = 220): void {
    if (!this.visibleNow || !this.path.length) return;
    const far = Math.hypot(this.x - squadX, this.y - squadY) > wait;
    if (far) return;
    const [tx, ty] = this.path[0];
    const dx = tx - this.x;
    const dy = ty - this.y;
    const d = Math.hypot(dx, dy);
    if (d < 4) {
      this.path.shift();
      return;
    }
    const step = Math.min(d, (this.speed * dtMs) / 1000);
    this.x += (dx / d) * step;
    this.y += (dy / d) * step;
    if (Math.abs(dx) > 2) this.setFace(dx > 0 ? 1 : -1);
  }

  get arrived(): boolean {
    return this.visibleNow && this.path.length === 0;
  }
}
