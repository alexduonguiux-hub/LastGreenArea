/** Tiếng động trong màn: ai phát, ở đâu, bán kính. Biến Thể trong bán kính sẽ đi điều tra. */
export interface Noise {
  x: number;
  y: number;
  r: number;
  kind: 'rock' | 'run';
  t: number; // tuổi (giây), để vẽ vòng lan
}

export class NoiseSystem {
  readonly active: Noise[] = [];
  private listeners: ((n: Noise) => void)[] = [];

  emit(x: number, y: number, r: number, kind: Noise['kind']): Noise {
    const n: Noise = { x, y, r, kind, t: 0 };
    this.active.push(n);
    for (const l of this.listeners) l(n);
    return n;
  }

  onNoise(fn: (n: Noise) => void): void {
    this.listeners.push(fn);
  }

  update(dt: number, life = 0.6): void {
    for (const n of this.active) n.t += dt;
    for (let i = this.active.length - 1; i >= 0; i--) if (this.active[i].t > life) this.active.splice(i, 1);
  }

  static hears(n: Noise, x: number, y: number): boolean {
    return Math.hypot(n.x - x, n.y - y) <= n.r;
  }
}
