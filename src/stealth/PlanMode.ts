import type { Player } from '../entities/Player';
import type { Enemy } from '../entities/Enemy';
import type { CollisionGrid } from '../world/CollisionGrid';
import { findPath } from '../world/Pathfind';

export type Cmd =
  | { kind: 'di'; x: number; y: number }
  | { kind: 'cho'; s: number }
  | { kind: 'nem'; x: number; y: number }
  | { kind: 'ha' };

export const CMD_LABEL: Record<Cmd['kind'], string> = { di: 'Đi tới', cho: 'Chờ', nem: 'Ném đá', ha: 'Hạ gục' };
export const MAX_CMDS = 3;

/** Chế độ kế hoạch: xếp tối đa 3 lệnh cho mỗi người, thực thi đồng loạt theo thời gian thực. */
export class PlanMode {
  active = false;
  executing = false;
  selected = 0;
  queues: Cmd[][];
  tool: 'di' | 'nem' = 'di';
  private runners: Runner[] = [];

  constructor(private readonly members: Player[], private readonly grid: CollisionGrid) {
    this.queues = members.map(() => []);
  }

  enter(leaderIdx: number): void {
    this.active = true;
    this.selected = leaderIdx;
    this.tool = 'di';
    this.queues = this.members.map(() => []);
  }

  cancel(): void {
    this.active = false;
  }

  /** Vị trí kết thúc dự kiến của một người sau các lệnh đã xếp. */
  endPos(i: number): { x: number; y: number } {
    const m = this.members[i];
    let p = { x: m.x, y: m.y };
    for (const c of this.queues[i]) if (c.kind === 'di') p = { x: c.x, y: c.y };
    return p;
  }

  add(cmd: Cmd): boolean {
    const q = this.queues[this.selected];
    if (q.length >= MAX_CMDS) return false;
    if (cmd.kind === 'nem' && this.members[this.selected].rocks <= 0) return false;
    q.push(cmd);
    return true;
  }

  removeLast(): void {
    this.queues[this.selected].pop();
  }

  /** Đường đi dự kiến (để vẽ) của người i. */
  previewPath(i: number): { x: number; y: number }[][] {
    const out: { x: number; y: number }[][] = [];
    let from = { x: this.members[i].x, y: this.members[i].y };
    for (const c of this.queues[i]) {
      if (c.kind !== 'di') continue;
      const p = findPath(this.grid, from.x, from.y, c.x, c.y);
      if (p) out.push([from, ...p]);
      from = { x: c.x, y: c.y };
    }
    return out;
  }

  execute(enemies: Enemy[], onThrow: (m: Player, at: { x: number; y: number }) => void, onTakedown: (m: Player, e: Enemy) => boolean): void {
    this.active = false;
    this.executing = true;
    this.runners = this.members.map((m, i) => new Runner(m, [...this.queues[i]], this.grid, enemies, onThrow, onTakedown));
  }

  update(dtMs: number): void {
    if (!this.executing) return;
    let busy = false;
    for (const r of this.runners) if (!r.update(dtMs)) busy = true;
    if (!busy) this.executing = false;
  }
}

class Runner {
  private path: { x: number; y: number }[] | null = null;
  private wait = 0;

  constructor(
    private readonly m: Player,
    private readonly q: Cmd[],
    private readonly grid: CollisionGrid,
    private readonly enemies: Enemy[],
    private readonly onThrow: (m: Player, at: { x: number; y: number }) => void,
    private readonly onTakedown: (m: Player, e: Enemy) => boolean,
  ) {}

  /** Trả true khi xong hết lệnh. */
  update(dtMs: number): boolean {
    if (this.m.busy) return false;
    const c = this.q[0];
    if (!c) return true;
    switch (c.kind) {
      case 'di': {
        if (!this.path) this.path = findPath(this.grid, this.m.x, this.m.y, c.x, c.y) ?? [];
        const next = this.path[0];
        if (!next) {
          this.done();
          break;
        }
        if (this.m.moveTo(next.x, next.y, dtMs, false, 3)) this.path.shift();
        break;
      }
      case 'cho':
        this.wait += dtMs / 1000;
        if (this.wait >= c.s) this.done();
        break;
      case 'nem':
        this.onThrow(this.m, { x: c.x, y: c.y });
        this.done();
        break;
      case 'ha': {
        const e = this.enemies.find((en) => en.canBeTakenDown(this.m.x, this.m.y));
        if (e) this.onTakedown(this.m, e);
        this.done();
        break;
      }
    }
    return false;
  }

  private done(): void {
    this.q.shift();
    this.path = null;
    this.wait = 0;
  }
}
