import Phaser from 'phaser';
import { ATLAS } from '../core/atlas';

export interface PickupDef {
  item: string;
  x: number;
  y: number;
}

export const ITEM_LABEL: Record<string, string> = {
  'da-khac-ky-hieu': 'Đá khắc ký hiệu',
  'manh-ky-uc': 'Mảnh Ký Ức',
  'anh-bon-nguoi': 'Ảnh bốn người',
  'da-nem': 'Đá ném',
};

/** Vật phẩm trên bản đồ: icon 16 px từ atlas (item/*); đá ném chưa có icon (A3) nên vẽ tạm bằng hình. */
export class Pickups {
  readonly items: { def: PickupDef; obj: Phaser.GameObjects.GameObject & { x: number; y: number }; taken: boolean }[] = [];

  constructor(scene: Phaser.Scene, defs: PickupDef[], already: Set<number>) {
    defs.forEach((def, i) => {
      const id = `item/${def.item}`;
      const has = scene.textures.get(ATLAS).has(id);
      const obj = has
        ? scene.add.image(def.x, def.y, ATLAS, id).setOrigin(0.5, 1).setDepth(def.y)
        : scene.add.ellipse(def.x, def.y - 3, 10, 7, 0x9aa0a8).setDepth(def.y);
      if (def.item === 'manh-ky-uc') scene.tweens.add({ targets: obj, alpha: 0.5, yoyo: true, repeat: -1, duration: 700 });
      const taken = already.has(i);
      if (taken) obj.setVisible(false);
      this.items.push({ def, obj, taken });
    });
  }

  /** Vật phẩm gần (x,y) nhất trong bán kính, chưa nhặt. */
  nearest(x: number, y: number, r = 20) {
    let best: (typeof this.items)[number] | null = null;
    let bd = r;
    for (const it of this.items) {
      if (it.taken) continue;
      const d = Math.hypot(it.def.x - x, it.def.y - y);
      if (d < bd) {
        bd = d;
        best = it;
      }
    }
    return best;
  }

  take(it: (typeof this.items)[number]): number {
    it.taken = true;
    (it.obj as Phaser.GameObjects.Image).setVisible(false);
    return this.items.indexOf(it);
  }

  takenIndices(): number[] {
    return this.items.map((it, i) => (it.taken ? i : -1)).filter((i) => i >= 0);
  }
}
