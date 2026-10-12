import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { animConfig, type AnimTable } from './anims';

interface AtlasJson {
  textures: { image: string; size: { w: number; h: number }; frames: { filename: string }[] }[];
  meta: { page: number; frames: number; anims: number };
}

const atlas = JSON.parse(readFileSync('public/data/atlas.json', 'utf8')) as AtlasJson;
const anims = JSON.parse(readFileSync('public/data/anims.json', 'utf8')) as AnimTable;
const frameIds = new Set(atlas.textures.flatMap((t) => t.frames.map((f) => f.filename)));

describe('atlas + anims (file sinh bởi art/build.py)', () => {
  it('mọi trang là 2048×2048 và số khung khớp meta', () => {
    for (const t of atlas.textures) expect([t.size.w, t.size.h]).toEqual([2048, 2048]);
    expect(frameIds.size).toBe(atlas.meta.frames);
    expect(frameIds.has('env/conifer-0')).toBe(true);
    expect(Object.keys(anims).length).toBe(atlas.meta.anims);
  });

  it('mọi hoạt ảnh trỏ tới khung có thật, đúng thứ tự', () => {
    for (const [id, a] of Object.entries(anims)) {
      expect(a.frames.length).toBeGreaterThan(0);
      a.frames.forEach((f, i) => {
        expect(frameIds.has(f), `${id} thiếu khung ${f}`).toBe(true);
        expect(f).toBe(`${id}/${i}`);
      });
    }
  });

  it('màn 1 có đủ hoạt ảnh cần cho B0–B2', () => {
    for (const id of [
      'char/duong/di-xuong',
      'char/duong/di-sang-trai',
      'char/duong/chay',
      'char/duong/bo-nup',
      'char/duong/nem-da',
      'char/duong/khoa-siet-tu-sau',
      'enemy/ke-lang-thang/le-buoc-trai',
      'enemy/ke-lang-thang/bi-ha',
      'npc/mai/lo-lung',
      'fx/tieng-dong-nem-da',
    ])
      expect(anims[id], `thiếu ${id}`).toBeDefined();
  });
});

describe('animConfig', () => {
  it('lặp vô hạn khi loop, một lần khi không', () => {
    const c = animConfig('char/duong/di-xuong', anims['char/duong/di-xuong']);
    expect(c.repeat).toBe(-1);
    expect(c.frameRate).toBe(10);
    expect((c.frames as { key: string; frame: string }[])[3]).toEqual({ key: 'atlas', frame: 'char/duong/di-xuong/3' });
    expect(animConfig('x', anims['enemy/ke-lang-thang/bi-ha']).repeat).toBe(0);
  });
});
