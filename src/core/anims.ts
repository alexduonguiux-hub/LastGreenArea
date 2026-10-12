import type Phaser from 'phaser';
import { ATLAS } from './atlas';

/** Một hoạt ảnh trong public/data/anims.json (sinh bởi art/build.py). */
export interface AnimDef {
  name: string;
  actor: string;
  frames: string[];
  fps: number;
  loop: boolean;
  anchor: [number, number];
  source?: string;
}
export type AnimTable = Record<string, AnimDef>;

/** Cấu hình Phaser cho một hoạt ảnh. Hàm thuần để test được không cần Phaser. */
export function animConfig(id: string, a: AnimDef): Phaser.Types.Animations.Animation {
  return {
    key: id,
    frames: a.frames.map((frame) => ({ key: ATLAS, frame })),
    frameRate: a.fps,
    repeat: a.loop ? -1 : 0,
  };
}

/** Đăng ký toàn bộ bảng hoạt ảnh vào AnimationManager, bỏ qua khóa đã có. */
export function registerAnims(anims: Phaser.Animations.AnimationManager, table: AnimTable): number {
  let n = 0;
  for (const [id, a] of Object.entries(table)) {
    if (anims.exists(id)) continue;
    anims.create(animConfig(id, a));
    n++;
  }
  return n;
}

/** Id hoạt ảnh của một diễn viên: actorId = "char/duong", anim = "di-xuong". */
export function animId(actorId: string, anim: string): string {
  return `${actorId}/${anim}`;
}
