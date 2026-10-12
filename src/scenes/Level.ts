import Phaser from 'phaser';
import { createKeys, type Keys } from '../core/input';
import { Player } from '../entities/Player';
import { overlay } from '../ui/overlay';
import { GAME_H, GAME_W } from '../main';

/** B0: nền cầu màn 1 + Dương đi 4 hướng. B1 thêm lưới va chạm, camera cuộn, tư thế. */
export class Level extends Phaser.Scene {
  private keys!: Keys;
  private player!: Player;

  constructor() {
    super('Level');
  }

  create(): void {
    this.add.image(0, 0, 'bg-level1').setOrigin(0, 0).setDepth(-1000);
    this.keys = createKeys(this);
    this.player = new Player(this, 'char/duong', 560, 268);
    // B0: chỉ giới hạn trong màn hình; B1 thay bằng CollisionGrid (nước, cây, cầu).
    this.player.walkable = (x, y) => x >= 24 && x <= GAME_W - 24 && y >= 190 && y <= GAME_H - 12;
    this.cameras.main.setBounds(0, 0, GAME_W, GAME_H);

    overlay.topLeft('Đường Mòn Sương', 'B0 · Dương đi 4 hướng từ ma trận atlas');
    overlay.bottom(
      '<kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> đi · <kbd>Shift</kbd> chạy · "Đi lên" tạm dùng "Chạy lên" chậm cho đến khi A2 sinh hoạt ảnh riêng',
    );
    this.input.keyboard!.on('keydown-C', () => {
      this.player.stance = this.player.stance === 'dung' ? 'khom' : this.player.stance === 'khom' ? 'bo' : 'dung';
      overlay.topLeft('Đường Mòn Sương', `Tư thế: ${{ dung: 'Đứng', khom: 'Khom', bo: 'Bò' }[this.player.stance]}`);
    });
  }

  update(_time: number, delta: number): void {
    this.player.update(this.keys, delta);
  }
}
