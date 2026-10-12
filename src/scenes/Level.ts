import Phaser from 'phaser';
import { createKeys, type Keys } from '../core/input';
import { ATLAS } from '../core/atlas';
import { Player } from '../entities/Player';
import { CollisionGrid, type LevelData } from '../world/CollisionGrid';
import { overlay } from '../ui/overlay';

const STANCE_LABEL = { dung: 'Đứng', khom: 'Khom', bo: 'Bò' } as const;

/** B1: màn 1 cuộn 1600×960, lưới va chạm, vật thể môi trường từ atlas xếp lớp theo y, debug F3. */
export class Level extends Phaser.Scene {
  private keys!: Keys;
  private player!: Player;
  private grid!: CollisionGrid;
  private level!: LevelData;
  private debug?: Phaser.GameObjects.Graphics;

  constructor() {
    super('Level');
  }

  create(): void {
    this.level = this.cache.json.get('level1') as LevelData;
    this.grid = CollisionGrid.fromLevel(this.level);
    const [w, h] = this.level.size;

    this.add.image(0, 0, 'ground-level1').setOrigin(0, 0).setDepth(-1000);
    // cây, bụi, lều: sprite từ atlas, neo chân đã nằm trong khung → depth = y chân
    for (const o of this.level.objects) this.add.image(o.x, o.y, ATLAS, o.id).setDepth(o.y);

    this.keys = createKeys(this);
    const [sx, sy] = this.level.spawn.duong;
    this.player = new Player(this, 'char/duong', sx, sy);
    this.player.walkable = (x, y) => this.grid.canStand(x, y);

    this.physics?.world?.setBounds(0, 0, w, h);
    const cam = this.cameras.main;
    cam.setBounds(0, 0, w, h);
    cam.startFollow(this.player, true, 1, 1);
    cam.setRoundPixels(true);

    overlay.topLeft(this.level.name, 'B1 · trại → rừng thông → cầu → bên kia suối');
    overlay.bottom(
      '<kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> đi · <kbd>Shift</kbd> chạy · <kbd>C</kbd> tư thế · <kbd>F3</kbd> lưới va chạm',
    );
    this.input.keyboard!.on('keydown-C', () => {
      this.player.stance = this.player.stance === 'dung' ? 'khom' : this.player.stance === 'khom' ? 'bo' : 'dung';
      overlay.topLeft(this.level.name, `Tư thế: ${STANCE_LABEL[this.player.stance]}`);
    });
    this.input.keyboard!.on('keydown-F3', () => this.toggleDebug());
  }

  private toggleDebug(): void {
    if (this.debug) {
      this.debug.destroy();
      this.debug = undefined;
      return;
    }
    this.debug = this.add.graphics().setDepth(10000);
  }

  private drawDebug(): void {
    const g = this.debug;
    if (!g) return;
    g.clear();
    const cam = this.cameras.main;
    const col: Record<string, number> = { '#': 0xf04650, o: 0x50dc78, '~': 0x3e96ff, '=': 0xf0c83c };
    this.grid.forEachCell(cam.scrollX, cam.scrollY, cam.scrollX + cam.width, cam.scrollY + cam.height, (c, r, cell) => {
      if (cell === '.') return;
      g.fillStyle(col[cell], 0.35).fillRect(c * this.grid.cell, r * this.grid.cell, this.grid.cell - 1, this.grid.cell - 1);
    });
    g.lineStyle(1, 0x3eecff, 0.9).strokeCircle(this.player.x, this.player.y, 6);
  }

  update(_time: number, delta: number): void {
    this.player.update(this.keys, delta);
    this.drawDebug();
  }
}
