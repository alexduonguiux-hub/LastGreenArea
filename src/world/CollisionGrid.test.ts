import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { CollisionGrid, type LevelData } from './CollisionGrid';

const level = JSON.parse(readFileSync('public/data/levels/level1.json', 'utf8')) as LevelData;
const grid = CollisionGrid.fromLevel(level);

describe('CollisionGrid (lưới 16 px)', () => {
  it('phân loại ô theo ký tự', () => {
    const g = new CollisionGrid(['#.o', '~=.'], 16);
    expect(g.at(0, 0)).toBe('#');
    expect(g.isWalkable(20, 5)).toBe(true);
    expect(g.hides(40, 5)).toBe(true);
    expect(g.isWalkable(5, 20)).toBe(false); // nước
    expect(g.isWalkable(20, 20)).toBe(true); // cầu
    expect(g.at(-1, 0)).toBe('#'); // ngoài bản đồ
    expect(g.at(100, 100)).toBe('#');
  });

  it('đường nhìn bị ô # chặn', () => {
    const g = new CollisionGrid(['.....', '..#..', '.....'], 16);
    expect(g.lineOfSight(8, 24, 72, 24)).toBe(false);
    expect(g.lineOfSight(8, 8, 72, 8)).toBe(true);
  });
});

describe('màn 1 (sinh bởi art/maps/level1.py)', () => {
  it('kích thước 1600×960, lưới 100×60', () => {
    expect(level.size).toEqual([1600, 960]);
    expect(grid.cols).toBe(100);
    expect(grid.rows).toBe(60);
  });

  it('điểm xuất phát, tuần tra, Mai và vật phẩm đều đứng được', () => {
    for (const [name, [x, y]] of Object.entries(level.spawn)) expect(grid.canStand(x, y), `spawn ${name}`).toBe(true);
    for (const pt of Object.values(level.patrol)) for (const p of pt.points) expect(grid.canStand(p[0], p[1]), `patrol ${p}`).toBe(true);
    expect(grid.canStand(level.mai.appear[0], level.mai.appear[1])).toBe(true);
    for (const [k, [x, y]] of Object.entries(level.checkpoints)) expect(grid.canStand(x, y), `checkpoint ${k}`).toBe(true);
    for (const p of level.pickups) expect(grid.isWalkable(p.x, p.y), `pickup ${p.item}`).toBe(true);
  });

  it('cầu là lối duy nhất qua suối: mọi hàng khác đều có nước chặn ngang', () => {
    const [bx0, by0, bx1, by1] = level.bridge;
    for (let r = 1; r < grid.rows - 1; r++) {
      const y = r * level.cell + 8;
      const row = level.grid[r];
      if (y >= by0 && y <= by1) {
        expect(row.includes('='), `hàng ${r} phải có cầu`).toBe(true);
        continue;
      }
      // trong khoảng x của suối, hàng này phải có ít nhất một ô nước và không có ô cầu
      const seg = row.slice(Math.floor((bx0 + 40) / level.cell), Math.floor((bx1 - 40) / level.cell));
      expect(seg.includes('~'), `hàng ${r} không có nước`).toBe(true);
      expect(seg.includes('='), `hàng ${r} có cầu lạ`).toBe(false);
    }
  });

  it('từ trại đi tới được lối ra (BFS trên ô đi được)', () => {
    const start = level.spawn.duong;
    const goal = level.exit;
    const seen = new Set<string>();
    const q: [number, number][] = [[Math.floor(start[0] / 16), Math.floor(start[1] / 16)]];
    const gc = Math.floor(goal[0] / 16);
    const gr = Math.min(grid.rows - 1, Math.floor(goal[1] / 16));
    let found = false;
    while (q.length && !found) {
      const [c, r] = q.shift()!;
      const k = `${c},${r}`;
      if (seen.has(k)) continue;
      seen.add(k);
      if (Math.abs(c - gc) <= 2 && Math.abs(r - gr) <= 2) found = true;
      for (const [dc, dr] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const cell = grid.cellAt(c + dc, r + dr);
        if (cell === '.' || cell === 'o' || cell === '=') q.push([c + dc, r + dr]);
      }
    }
    expect(found).toBe(true);
  });
});
