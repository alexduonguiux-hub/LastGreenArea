import Phaser from 'phaser';
import { ATLAS } from '../core/atlas';
import { animId } from '../core/anims';

/**
 * Sprite LPC lấy từ ma trận atlas.
 * - Neo chân (32,60) nằm trong manifest (anchor) nên Phaser tự đặt origin theo từng khung.
 * - Hướng phải = lật ngang khung hướng trái (CLAUDE.md).
 * - depth = y của chân để xếp lớp theo chiều sâu.
 */
export class Actor extends Phaser.GameObjects.Sprite {
  readonly actorId: string;
  face: 1 | -1 = -1;
  current = '';

  constructor(scene: Phaser.Scene, actorId: string, x: number, y: number, firstAnim: string) {
    super(scene, x, y, ATLAS, `${animId(actorId, firstAnim)}/0`);
    this.actorId = actorId;
    scene.add.existing(this);
    this.setDepth(y);
  }

  /** Phát hoạt ảnh theo tên ngắn ("di-xuong"); trả false nếu diễn viên không có hoạt ảnh đó. */
  playAnim(anim: string, opts: { frameRate?: number; force?: boolean } = {}): boolean {
    const id = animId(this.actorId, anim);
    if (!this.scene.anims.exists(id)) return false;
    if (this.current === id && !opts.force) return true;
    this.current = id;
    this.play({ key: id, frameRate: opts.frameRate });
    return true;
  }

  hasAnim(anim: string): boolean {
    return this.scene.anims.exists(animId(this.actorId, anim));
  }

  /** Dừng ở khung đầu của hoạt ảnh hiện tại (đứng yên). */
  idle(): void {
    if (!this.current) return;
    this.anims.stop();
    this.setFrame(`${this.current}/0`);
  }

  setFace(f: 1 | -1): void {
    this.face = f;
    this.setFlipX(f > 0);
  }

  preUpdate(time: number, delta: number): void {
    super.preUpdate(time, delta);
    this.setDepth(this.y);
  }
}
