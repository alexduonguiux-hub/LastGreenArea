/**
 * Kịch bản màn 1 · Đường Mòn Sương: 4 nhịp hướng dẫn (docs/level_design.md "Build màn 1").
 * Phần thuần (Beats) không phụ thuộc Phaser để test: nhận vị trí thủ lĩnh + cờ, trả về sự kiện.
 */
export type Rect = [number, number, number, number];

export interface Level1Data {
  triggers: Record<string, Rect>;
  checkpoints: Record<string, [number, number]>;
}

export interface BeatStart {
  kind: 'beat';
  beat: number;
  checkpoint: string;
  objective: string;
  dialogue: string;
}
export type BeatEvent = BeatStart | { kind: 'loop-return' } | { kind: 'win' };

export const BEATS = [
  { key: 'trai', objective: 'Theo đường mòn ra khỏi rừng', dialogue: 'intro' },
  { key: 'rung', objective: 'Đi theo ánh sáng xanh', dialogue: 'rung' },
  { key: 'dau-cau', objective: 'Qua cầu mà không bị phát hiện', dialogue: 'dau-cau' },
  { key: 'ben-kia', objective: 'Đi theo Mai ra khỏi rừng', dialogue: 'ben-kia' },
] as const;

export const SIDE_OBJECTIVES = [
  { item: 'da-khac-ky-hieu', label: 'Đá khắc ký hiệu', need: 3 },
  { item: 'manh-ky-uc', label: 'Mảnh Ký Ức', need: 1 },
  { item: 'anh-bon-nguoi', label: 'Ảnh bốn người', need: 1 },
] as const;

export function inRect(r: Rect, x: number, y: number): boolean {
  return x >= r[0] && x <= r[2] && y >= r[1] && y <= r[3];
}

export class Beats {
  beat = 0;
  loopFar = false;
  loopReturned = false;
  won = false;

  constructor(private readonly data: Level1Data) {}

  /** Khởi động ở một nhịp (nạp điểm lưu). */
  startAt(beat: number): BeatStart {
    this.beat = beat;
    if (beat >= 1) this.loopReturned = this.loopFar = true;
    const b = BEATS[beat];
    return { kind: 'beat', beat, checkpoint: b.key, objective: b.objective, dialogue: b.dialogue };
  }

  /** Gọi mỗi khung với vị trí thủ lĩnh; trả về các sự kiện mới. */
  update(x: number, y: number): BeatEvent[] {
    const t = this.data.triggers;
    const out: BeatEvent[] = [];
    if (this.won) return out;
    if (this.beat === 0) {
      if (!this.loopFar && inRect(t['vong-xa'], x, y)) this.loopFar = true;
      if (this.loopFar && !this.loopReturned && inRect(t['trai-ve'], x, y)) {
        this.loopReturned = true;
        out.push({ kind: 'loop-return' });
      }
      if (this.loopReturned && inRect(t['rung'], x, y)) out.push(this.advance());
    } else if (this.beat === 1) {
      if (inRect(t['dau-cau'], x, y)) out.push(this.advance());
    } else if (this.beat === 2) {
      if (inRect(t['qua-cau'], x, y)) out.push(this.advance());
    } else if (this.beat === 3) {
      if (inRect(t['loi-ra'], x, y)) {
        this.won = true;
        out.push({ kind: 'win' });
      }
    }
    return out;
  }

  private advance(): BeatStart {
    this.beat++;
    const b = BEATS[this.beat];
    return { kind: 'beat', beat: this.beat, checkpoint: b.key, objective: b.objective, dialogue: b.dialogue };
  }
}
