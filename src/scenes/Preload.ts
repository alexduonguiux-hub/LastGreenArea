import Phaser from 'phaser';
import { ANIMS_JSON, loadAtlas } from '../core/atlas';
import { registerAnims, type AnimTable } from '../core/anims';
import { overlay } from '../ui/overlay';

/** Nạp atlas, bản đồ, bảng hoạt ảnh; thanh nạp theo token v10. */
export class Preload extends Phaser.Scene {
  constructor() {
    super('Preload');
  }

  preload(): void {
    const { width, height } = this.scale;
    const g = this.add.graphics();
    const box = overlay.center('Vùng Xanh Cuối Cùng', 'Đang nạp ma trận atlas…', true);
    this.load.on('progress', (p: number) => {
      g.clear();
      g.fillStyle(0x1e2838).fillRect(width / 2 - 100, height / 2 + 30, 200, 4);
      g.fillStyle(0x3eecff).fillRect(width / 2 - 100, height / 2 + 30, 200 * p, 4);
      box.progress(p);
    });
    this.load.on('complete', () => {
      g.destroy();
      box.remove();
    });

    loadAtlas(this.load);
    this.load.image('ground-level1', 'assets/maps/level1_ground.png');
    this.load.json('level1', 'data/levels/level1.json');
  }

  create(): void {
    const table = this.cache.json.get(ANIMS_JSON) as AnimTable;
    registerAnims(this.anims, table);
    this.scene.start('Level');
  }
}
