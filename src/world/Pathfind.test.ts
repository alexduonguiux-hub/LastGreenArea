import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { CollisionGrid, type LevelData } from './CollisionGrid';
import { findPath } from './Pathfind';

describe('findPath (A* 8 hướng)', () => {
  it('vòng qua tường', () => {
    const g = new CollisionGrid(['.....', '.###.', '.....'], 16);
    const p = findPath(g, 8, 8, 72, 8)!;
    expect(p).not.toBeNull();
    expect(p[p.length - 1]).toEqual({ x: 72, y: 8 });
    expect(p.length).toBeGreaterThanOrEqual(4);
    for (const q of p) expect(g.isWalkable(q.x, q.y)).toBe(true);
  });

  it('không đi chéo xuyên góc', () => {
    const g = new CollisionGrid(['.#', '#.'], 16);
    expect(findPath(g, 8, 8, 24, 24)).toBeNull();
  });

  it('đích bị chặn thì tới ô đi được gần nhất', () => {
    const g = new CollisionGrid(['....', '..#.'], 16);
    const p = findPath(g, 8, 8, 40, 24)!;
    expect(p).not.toBeNull();
    expect(g.isWalkable(p[p.length - 1].x, p[p.length - 1].y)).toBe(true);
  });

  it('màn 1: từ trại tới lối ra qua cầu', () => {
    const level = JSON.parse(readFileSync('public/data/levels/level1.json', 'utf8')) as LevelData;
    const g = CollisionGrid.fromLevel(level);
    const p = findPath(g, level.spawn.duong[0], level.spawn.duong[1], level.exit[0], level.exit[1] + 16)!;
    expect(p).not.toBeNull();
    expect(p.some((q) => g.at(q.x, q.y) === '=')).toBe(true);
  });
});
