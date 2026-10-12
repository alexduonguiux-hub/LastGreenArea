import { describe, expect, it } from 'vitest';
import { DetectionMeter } from './Detection';
import { inCone } from './VisionCone';
import { NoiseSystem } from './Noise';
import { CollisionGrid } from '../world/CollisionGrid';

const cfg = { suspect: 0.4, fillBase: 1.6, stance: { dung: 1, khom: 0.6, bo: 0.35 }, decay: 0.4 };

describe('DetectionMeter', () => {
  it('đứng sát mặt: báo động trong dưới 1 giây; bò ở mép tầm: lâu hơn nhiều', () => {
    const a = new DetectionMeter(cfg);
    let t = 0;
    while (a.level !== 'bao-dong' && t < 10) {
      a.update(0.05, true, 0, 'dung');
      t += 0.05;
    }
    expect(t).toBeLessThan(1);
    const b = new DetectionMeter(cfg);
    t = 0;
    while (b.level !== 'nghi-ngo' && t < 10) {
      b.update(0.05, true, 0.9, 'bo');
      t += 0.05;
    }
    expect(t).toBeGreaterThan(1.5);
  });

  it('giảm dần khi mất dấu', () => {
    const m = new DetectionMeter(cfg);
    m.value = 0.5;
    m.update(1, false, 0, 'dung');
    expect(m.value).toBeCloseTo(0.1);
    expect(m.level).toBe('an-minh');
  });
});

describe('inCone', () => {
  const c = { angle: 90, range: 140 };
  it('trước mặt thấy, sau lưng không, ngoài tầm không', () => {
    expect(inCone(c, 100, 100, -1, 40, 100)).toBeGreaterThan(0);
    expect(inCone(c, 100, 100, -1, 160, 100)).toBe(-1);
    expect(inCone(c, 100, 100, 1, 160, 100)).toBeGreaterThan(0);
    expect(inCone(c, 100, 100, 1, 300, 100)).toBe(-1);
    expect(inCone(c, 100, 100, 1, 150, 170)).toBe(-1); // lệch 54°, ngoài nửa góc 45°
  });
  it('cây chắn tầm nhìn', () => {
    const g = new CollisionGrid(['..........', '....#.....', '..........'], 16);
    expect(inCone(c, 8, 24, 1, 120, 24, g)).toBe(-1);
    expect(inCone(c, 8, 8, 1, 120, 8, g)).toBeGreaterThan(0);
  });
});

describe('NoiseSystem', () => {
  it('phát và nghe trong bán kính, tự tắt sau 0.6 s', () => {
    const ns = new NoiseSystem();
    const heard: number[] = [];
    ns.onNoise((n) => heard.push(n.r));
    const n = ns.emit(0, 0, 120, 'rock');
    expect(heard).toEqual([120]);
    expect(NoiseSystem.hears(n, 100, 0)).toBe(true);
    expect(NoiseSystem.hears(n, 130, 0)).toBe(false);
    ns.update(0.7);
    expect(ns.active.length).toBe(0);
  });
});
