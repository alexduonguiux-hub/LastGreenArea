import type { CollisionGrid } from './CollisionGrid';

/** A* 8 hướng trên lưới 16 px; đi chéo chỉ khi hai ô kề cũng đi được. Trả về danh sách điểm pixel (tâm ô), bỏ điểm đầu. */
export function findPath(grid: CollisionGrid, x0: number, y0: number, x1: number, y1: number, maxNodes = 20000): { x: number; y: number }[] | null {
  const c = grid.cell;
  const sc = Math.floor(x0 / c);
  const sr = Math.floor(y0 / c);
  let gc = Math.floor(x1 / c);
  let gr = Math.floor(y1 / c);
  const ok = (col: number, row: number) => {
    const t = grid.cellAt(col, row);
    return t === '.' || t === 'o' || t === '=';
  };
  if (!ok(gc, gr)) {
    // đích bị chặn: tìm ô đi được gần nhất trong bán kính 3 ô
    let best: [number, number] | null = null;
    let bd = Infinity;
    for (let r = gr - 3; r <= gr + 3; r++)
      for (let col = gc - 3; col <= gc + 3; col++)
        if (ok(col, r)) {
          const d = (col - gc) ** 2 + (r - gr) ** 2;
          if (d < bd) {
            bd = d;
            best = [col, r];
          }
        }
    if (!best) return null;
    [gc, gr] = best;
  }
  const key = (col: number, row: number) => row * grid.cols + col;
  const open: number[] = [];
  const gScore = new Map<number, number>();
  const fScore = new Map<number, number>();
  const came = new Map<number, number>();
  const h = (col: number, row: number) => {
    const dx = Math.abs(col - gc);
    const dy = Math.abs(row - gr);
    return Math.max(dx, dy) + 0.414 * Math.min(dx, dy);
  };
  const start = key(sc, sr);
  const goal = key(gc, gr);
  gScore.set(start, 0);
  fScore.set(start, h(sc, sr));
  open.push(start);
  const closed = new Set<number>();
  let expanded = 0;
  while (open.length) {
    // chọn f nhỏ nhất (lưới nhỏ nên quét tuyến tính là đủ)
    let bi = 0;
    for (let i = 1; i < open.length; i++) if ((fScore.get(open[i]) ?? Infinity) < (fScore.get(open[bi]) ?? Infinity)) bi = i;
    const cur = open[bi];
    open[bi] = open[open.length - 1];
    open.pop();
    if (cur === goal) {
      const path: { x: number; y: number }[] = [];
      let k = cur;
      while (k !== start) {
        path.push({ x: (k % grid.cols) * c + c / 2, y: Math.floor(k / grid.cols) * c + c / 2 });
        k = came.get(k)!;
      }
      return path.reverse();
    }
    closed.add(cur);
    if (++expanded > maxNodes) return null;
    const cc = cur % grid.cols;
    const cr = Math.floor(cur / grid.cols);
    for (let dr = -1; dr <= 1; dr++)
      for (let dc = -1; dc <= 1; dc++) {
        if (!dc && !dr) continue;
        const nc = cc + dc;
        const nr = cr + dr;
        if (!ok(nc, nr)) continue;
        if (dc && dr && !(ok(cc + dc, cr) && ok(cc, cr + dr))) continue;
        const nk = key(nc, nr);
        if (closed.has(nk)) continue;
        const tentative = (gScore.get(cur) ?? Infinity) + (dc && dr ? 1.414 : 1);
        if (tentative < (gScore.get(nk) ?? Infinity)) {
          came.set(nk, cur);
          gScore.set(nk, tentative);
          fScore.set(nk, tentative + h(nc, nr));
          if (!open.includes(nk)) open.push(nk);
        }
      }
  }
  return null;
}
