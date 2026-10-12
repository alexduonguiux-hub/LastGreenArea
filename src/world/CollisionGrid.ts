/**
 * Lưới va chạm 16 px của một màn, nạp từ `grid` trong levels/*.json (sinh bởi art/maps).
 *   '.' đi được · '#' chặn và chắn tầm nhìn · 'o' bụi: đi được, khom/bò trong đó thì ẩn
 *   '~' nước: chặn · '=' cầu: đi được
 */
export type Cell = '.' | '#' | 'o' | '~' | '=';

export interface LevelData {
  name: string;
  size: [number, number];
  cell: number;
  ground: string;
  grid: string[];
  objects: { id: string; x: number; y: number }[];
  spawn: Record<string, [number, number]>;
  zones: Record<string, [number, number, number, number]>;
  bridge: [number, number, number, number];
  patrol: Record<string, { type: string; points: [number, number][] }>;
  mai: { appear: [number, number]; path: [number, number][] };
  exit: [number, number];
  triggers: Record<string, [number, number, number, number]>;
  checkpoints: Record<string, [number, number]>;
  pickups: { item: string; x: number; y: number }[];
}

export class CollisionGrid {
  readonly cols: number;
  readonly rows: number;
  readonly cell: number;
  private readonly rowsData: string[];

  constructor(grid: string[], cell: number) {
    this.rowsData = grid;
    this.rows = grid.length;
    this.cols = grid[0]?.length ?? 0;
    this.cell = cell;
  }

  static fromLevel(level: LevelData): CollisionGrid {
    return new CollisionGrid(level.grid, level.cell);
  }

  /** Ô tại tọa độ pixel; ngoài bản đồ coi như chặn. */
  at(x: number, y: number): Cell {
    const c = Math.floor(x / this.cell);
    const r = Math.floor(y / this.cell);
    if (c < 0 || r < 0 || c >= this.cols || r >= this.rows) return '#';
    return this.rowsData[r][c] as Cell;
  }

  cellAt(col: number, row: number): Cell {
    if (col < 0 || row < 0 || col >= this.cols || row >= this.rows) return '#';
    return this.rowsData[row][col] as Cell;
  }

  isWalkable(x: number, y: number): boolean {
    const c = this.at(x, y);
    return c === '.' || c === 'o' || c === '=';
  }

  /** Điểm chân có thể đứng: kiểm tra một dải ngang quanh chân (nhân vật rộng ~12 px). */
  canStand(x: number, y: number, halfW = 6): boolean {
    return this.isWalkable(x - halfW, y) && this.isWalkable(x + halfW, y) && this.isWalkable(x, y - 2);
  }

  blocksSight(x: number, y: number): boolean {
    return this.at(x, y) === '#';
  }

  hides(x: number, y: number): boolean {
    return this.at(x, y) === 'o';
  }

  /** Có đường nhìn thẳng từ (x0,y0) tới (x1,y1) không (bước 8 px, dừng ở ô '#'). */
  lineOfSight(x0: number, y0: number, x1: number, y1: number, step = 8): boolean {
    const dx = x1 - x0;
    const dy = y1 - y0;
    const n = Math.max(1, Math.ceil(Math.hypot(dx, dy) / step));
    for (let i = 1; i < n; i++) {
      const t = i / n;
      if (this.blocksSight(x0 + dx * t, y0 + dy * t)) return false;
    }
    return true;
  }

  /** Duyệt các ô trong một hình chữ nhật pixel (cho debug overlay, minimap). */
  forEachCell(x0: number, y0: number, x1: number, y1: number, fn: (col: number, row: number, cell: Cell) => void): void {
    const c0 = Math.max(0, Math.floor(x0 / this.cell));
    const r0 = Math.max(0, Math.floor(y0 / this.cell));
    const c1 = Math.min(this.cols - 1, Math.floor(x1 / this.cell));
    const r1 = Math.min(this.rows - 1, Math.floor(y1 / this.cell));
    for (let r = r0; r <= r1; r++) for (let c = c0; c <= c1; c++) fn(c, r, this.rowsData[r][c] as Cell);
  }
}
