import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { Beats, inRect, type Level1Data } from './level1';

const level = JSON.parse(readFileSync('public/data/levels/level1.json', 'utf8')) as Level1Data & {
  spawn: Record<string, [number, number]>;
  exit: [number, number];
  grid: string[];
  checkpoints: Record<string, [number, number]>;
};
const mid = (r: [number, number, number, number]) => [(r[0] + r[2]) / 2, (r[1] + r[3]) / 2] as const;

describe('Beats màn 1', () => {
  it('đi hết 4 nhịp theo đúng thứ tự, vòng lặp phải xa rồi mới về', () => {
    const b = new Beats(level);
    const t = level.triggers;
    expect(b.update(...mid(t['trai-ve']))).toEqual([]); // ở trại ngay đầu: chưa có gì
    expect(b.update(...mid(t['rung']))).toEqual([]); // chưa quay về thì chưa qua nhịp 2
    expect(b.update(...mid(t['vong-xa']))).toEqual([]);
    expect(b.update(...mid(t['trai-ve']))).toEqual([{ kind: 'loop-return' }]);
    expect(b.update(...mid(t['trai-ve']))).toEqual([]); // không lặp lại
    const e1 = b.update(...mid(t['rung']));
    expect(e1[0]).toMatchObject({ kind: 'beat', beat: 1, checkpoint: 'rung' });
    expect(b.update(...mid(t['qua-cau']))).toEqual([]); // phải tới đầu cầu trước
    expect(b.update(...mid(t['dau-cau']))[0]).toMatchObject({ kind: 'beat', beat: 2 });
    expect(b.update(...mid(t['qua-cau']))[0]).toMatchObject({ kind: 'beat', beat: 3, checkpoint: 'ben-kia' });
    expect(b.update(...mid(t['loi-ra']))).toEqual([{ kind: 'win' }]);
    expect(b.update(...mid(t['loi-ra']))).toEqual([]);
  });

  it('nạp điểm lưu ở nhịp 2 thì bỏ qua vòng lặp', () => {
    const b = new Beats(level);
    expect(b.startAt(2)).toMatchObject({ kind: 'beat', beat: 2, checkpoint: 'dau-cau' });
    expect(b.update(...mid(level.triggers['qua-cau']))[0]).toMatchObject({ beat: 3 });
  });

  it('vùng kích hoạt và điểm lưu nằm trên ô đi được', () => {
    const cell = (x: number, y: number) => level.grid[Math.floor(y / 16)][Math.floor(x / 16)];
    for (const [k, r] of Object.entries(level.triggers)) {
      const [x, y] = mid(r);
      expect(inRect(r, x, y)).toBe(true);
      // ít nhất một ô trong vùng đi được
      let ok = false;
      for (let yy = r[1]; yy <= r[3] && !ok; yy += 16) for (let xx = r[0]; xx <= r[2] && !ok; xx += 16) if ('.o='.includes(cell(xx, yy))) ok = true;
      expect(ok, `trigger ${k}`).toBe(true);
    }
    for (const [k, [x, y]] of Object.entries(level.checkpoints)) expect('.o='.includes(cell(x, y)), `checkpoint ${k}`).toBe(true);
  });
});
