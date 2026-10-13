/** Đồng hồ phát hiện 3 mức của một Biến Thể đối với một mục tiêu. Hàm thuần, test được. */
export type DetectLevel = 'an-minh' | 'nghi-ngo' | 'bao-dong';

export interface DetectConfig {
  suspect: number; // ngưỡng Nghi ngờ (0–1)
  fillBase: number; // tốc độ đầy khi mục tiêu sát mặt (đơn vị/giây)
  stance: Record<string, number>; // hệ số theo tư thế
  decay: number; // tốc độ giảm khi không thấy
}

export class DetectionMeter {
  value = 0;

  constructor(private readonly cfg: DetectConfig) {}

  /**
   * @param seen mục tiêu đang trong nón nhìn và có đường nhìn
   * @param dist01 khoảng cách chuẩn hóa 0 (sát) → 1 (mép tầm)
   * @param stance tư thế mục tiêu
   * @param instant mục tiêu lộ trong vùng gần của nón (Commandos: thấy là báo động ngay)
   */
  update(dt: number, seen: boolean, dist01: number, stance: string, instant = false): DetectLevel {
    if (seen && instant) this.value = 1;
    else if (seen) {
      const k = this.cfg.stance[stance] ?? 1;
      this.value = Math.min(1, this.value + dt * k * Math.max(0.2, this.cfg.fillBase - dist01));
    } else {
      this.value = Math.max(0, this.value - dt * this.cfg.decay);
    }
    return this.level;
  }

  get level(): DetectLevel {
    if (this.value >= 1) return 'bao-dong';
    if (this.value >= this.cfg.suspect) return 'nghi-ngo';
    return 'an-minh';
  }

  reset(): void {
    this.value = 0;
  }
}

export const LEVEL_LABEL: Record<DetectLevel, string> = { 'an-minh': 'Ẩn mình', 'nghi-ngo': 'Nghi ngờ', 'bao-dong': 'Báo động' };
