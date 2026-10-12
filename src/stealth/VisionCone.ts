import type Phaser from 'phaser';
import type { CollisionGrid } from '../world/CollisionGrid';

export interface ConeConfig {
  angle: number; // độ, toàn góc mở
  range: number; // px
}

/** Mục tiêu có nằm trong nón (tâm ở (x,y), hướng face = ±1) và có đường nhìn không. Trả khoảng cách chuẩn hóa hoặc -1. */
export function inCone(
  cfg: ConeConfig,
  x: number,
  y: number,
  face: 1 | -1,
  tx: number,
  ty: number,
  grid?: CollisionGrid,
): number {
  const dx = tx - x;
  const dy = ty - y;
  const dist = Math.hypot(dx, dy);
  if (dist > cfg.range) return -1;
  if (dist < 1) return 0;
  const ang = Math.atan2(dy, dx); // 0 = phải
  const center = face > 0 ? 0 : Math.PI;
  let diff = Math.abs(ang - center);
  if (diff > Math.PI) diff = 2 * Math.PI - diff;
  if (diff > (cfg.angle / 2) * (Math.PI / 180)) return -1;
  if (grid && !grid.lineOfSight(x, y, tx, ty)) return -1;
  return dist / cfg.range;
}

/** Vẽ nón nhìn bị cắt bởi ô chặn (lấy mẫu tia), màu theo mức phát hiện. */
export function drawCone(
  g: Phaser.GameObjects.Graphics,
  cfg: ConeConfig,
  x: number,
  y: number,
  face: 1 | -1,
  color: number,
  alpha: number,
  grid: CollisionGrid,
  rays = 24,
): void {
  const half = (cfg.angle / 2) * (Math.PI / 180);
  const center = face > 0 ? 0 : Math.PI;
  const pts: { x: number; y: number }[] = [{ x, y }];
  for (let i = 0; i <= rays; i++) {
    const a = center - half + (2 * half * i) / rays;
    const cx = Math.cos(a);
    const cy = Math.sin(a);
    let r = cfg.range;
    for (let d = 8; d <= cfg.range; d += 8) {
      if (grid.blocksSight(x + cx * d, y + cy * d)) {
        r = d - 4;
        break;
      }
    }
    pts.push({ x: x + cx * r, y: y + cy * r });
  }
  g.fillStyle(color, alpha).fillPoints(pts, true);
}
