/** Điểm lưu trong localStorage. Mọi truy cập bọc try/catch: chế độ riêng tư hoặc bị chặn thì game vẫn chạy. */
export interface SaveData {
  level: string;
  checkpoint: string;
  beat: number;
  inventory: Record<string, number>;
  rocks: number;
  leader: number;
  stats: { time: number; detected: number };
  savedAt: number;
}

const KEY = 'vung-xanh.save';

export function loadSave(): SaveData | null {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    const d = JSON.parse(raw) as SaveData;
    return d && typeof d.level === 'string' ? d : null;
  } catch {
    return null;
  }
}

export function writeSave(d: SaveData): boolean {
  try {
    localStorage.setItem(KEY, JSON.stringify(d));
    return true;
  } catch {
    return false;
  }
}

export function clearSave(): void {
  try {
    localStorage.removeItem(KEY);
  } catch {
    /* bỏ qua */
  }
}

export function formatTime(sec: number): string {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}
