import type Phaser from 'phaser';
import { Player, type CharacterDef } from '../entities/Player';
import type { Keys } from '../core/input';

const SPACING = 24; // px giữa các người trong hàng

/** Đội 4 người: thủ lĩnh đi theo phím, người còn lại bám theo vệt đường của thủ lĩnh, copy tư thế. */
export class Squad {
  readonly members: Player[] = [];
  leaderIdx = 0;
  private trail: { x: number; y: number }[] = [];
  /** tắt điều khiển tự động (khi chế độ kế hoạch đang thực thi) */
  autoFollow = true;

  constructor(scene: Phaser.Scene, defs: Record<string, CharacterDef>, spawn: Record<string, [number, number]>, order: string[]) {
    for (const key of order) {
      const [x, y] = spawn[key];
      this.members.push(new Player(scene, key, defs[key], x, y));
    }
    this.trail = [{ x: this.leader.x, y: this.leader.y }];
  }

  get leader(): Player {
    return this.members[this.leaderIdx];
  }

  setLeader(i: number): Player {
    if (i < 0 || i >= this.members.length || i === this.leaderIdx) return this.leader;
    this.leaderIdx = i;
    this.trail = [{ x: this.leader.x, y: this.leader.y }];
    return this.leader;
  }

  byKey(key: string): Player | undefined {
    return this.members.find((m) => m.key === key);
  }

  /** Mục tiêu cho Biến Thể: vị trí, tư thế, có đang ẩn trong bụi. */
  targets(hides: (x: number, y: number) => boolean) {
    return this.members.map((m) => ({ x: m.x, y: m.y, stance: m.stance, hidden: m.stance !== 'dung' && hides(m.x, m.y), member: m }));
  }

  update(keys: Keys, dtMs: number): void {
    const L = this.leader;
    L.update(keys, dtMs);
    this.recordTrail();
    if (!this.autoFollow) return;
    let behind = 0;
    for (const m of this.members) {
      if (m === L) continue;
      behind++;
      if (m.stance !== L.stance) m.setStance(L.stance);
      const p = this.trailPoint(behind * SPACING);
      if (p) m.moveTo(p.x, p.y, dtMs, L.running, 3);
    }
  }

  private recordTrail(): void {
    const L = this.leader;
    const last = this.trail[this.trail.length - 1];
    if (Math.hypot(L.x - last.x, L.y - last.y) >= 4) {
      this.trail.push({ x: L.x, y: L.y });
      if (this.trail.length > 200) this.trail.shift();
    }
  }

  /** Điểm trên vệt cách thủ lĩnh một quãng (đo ngược từ cuối). */
  private trailPoint(dist: number): { x: number; y: number } | null {
    let acc = 0;
    for (let i = this.trail.length - 1; i > 0; i--) {
      const a = this.trail[i];
      const b = this.trail[i - 1];
      const seg = Math.hypot(a.x - b.x, a.y - b.y);
      if (acc + seg >= dist) {
        const t = (dist - acc) / seg;
        return { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t };
      }
      acc += seg;
    }
    return this.trail.length > 1 ? this.trail[0] : null;
  }
}
