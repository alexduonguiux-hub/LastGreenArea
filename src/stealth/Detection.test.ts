import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { DetectionMeter } from './Detection';
import { inCone } from './VisionCone';
import { NoiseSystem } from './Noise';
import { CollisionGrid } from '../world/CollisionGrid';
import type { StealthConfig } from '../entities/Enemy';

const stealth = (JSON.parse(readFileSync('public/data/levels/level1.json', 'utf8')) as { stealth: StealthConfig }).stealth;
const cfg = stealth.detect;

describe('DetectionMeter', () => {
  it('đứng sát mặt: báo động trong dưới 1 giây; bò (đang nhích) ở mép tầm: hơn 1 giây mới nghi ngờ', () => {
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
    expect(t).toBeGreaterThan(1.0);
  });

  it('giảm dần khi mất dấu', () => {
    const m = new DetectionMeter(cfg);
    m.value = 0.5;
    m.update(1, false, 0, 'dung');
    expect(m.value).toBeCloseTo(0.5 - cfg.decay);
    expect(m.level).toBe('an-minh');
  });

  it('vùng gần (Commandos): lộ mặt là báo động ngay, kể cả đang bò', () => {
    const m = new DetectionMeter(cfg);
    expect(m.update(0.016, true, 0.1, 'bo', true)).toBe('bao-dong');
    expect(m.value).toBe(1);
  });

  it('đi ngang ở nửa tầm: báo động trong khoảng 1 giây; chạy nhanh hơn đi', () => {
    const time = (stance: string) => {
      const m = new DetectionMeter(cfg);
      let t = 0;
      while (m.level !== 'bao-dong' && t < 10) {
        m.update(0.05, true, 0.5, stance);
        t += 0.05;
      }
      return t;
    };
    expect(time('dung')).toBeLessThan(1.1);
    expect(time('chay')).toBeLessThan(time('dung'));
    expect(time('khom')).toBeGreaterThan(time('dung'));
  });
});

describe('hằng số ẩn nấp màn 1 (levels/level1.json)', () => {
  it('bước chân: Chạy xa hơn Đi xa hơn Khom; Bò im; chạy nghe được ngoài tầm nhìn', () => {
    const st = stealth.noise.step;
    expect(st.chay).toBeGreaterThan(st.dung);
    expect(st.dung).toBeGreaterThan(st.khom);
    expect(st.khom).toBeGreaterThan(0);
    expect(st.bo).toBe(0);
    expect(st.chay).toBeGreaterThanOrEqual(stealth.vision.range * 0.9); // chạy = tự tố cáo từ xa
    expect(st.khom).toBeLessThan(stealth.takedown.dist); // khom tới sát lưng để hạ gục mà không bị nghe
    for (const k of Object.keys(st)) expect(stealth.noise.stepEvery[k]).toBeGreaterThan(0);
  });
  it('vùng gần nằm trong tầm nhìn và rộng hơn tầm hạ gục', () => {
    expect(stealth.vision.near).toBeGreaterThan(stealth.takedown.dist * 2);
    expect(stealth.vision.near).toBeLessThan(stealth.vision.range / 2);
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
  it('nón màn 1 (100°): đi ngang cách 2 ô trên/dưới đường tuần tra vẫn bị thấy', () => {
    const v = stealth.vision;
    expect(inCone(v, 100, 100, 1, 160, 132)).toBeGreaterThan(0); // 28°, trong nửa góc 50°
    expect(inCone(v, 100, 100, 1, 130, 160)).toBe(-1); // 63°: ra ngoài
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
