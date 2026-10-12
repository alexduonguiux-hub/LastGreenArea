/**
 * Hộp thoại v10 trên lớp DOM: chân dung (vẽ từ khung atlas lên canvas nhỏ), tên, câu thoại.
 * Enter / Space / bấm chuột để sang câu kế; hết thoại thì gọi onDone.
 */
export interface Line {
  who: string;
  text: string;
}
export interface Speaker {
  name: string;
  color: string;
  portrait: HTMLCanvasElement | null;
}

export class Dialogue {
  private el: HTMLDivElement | null = null;
  private lines: Line[] = [];
  private i = 0;
  private onDone?: () => void;
  active = false;

  constructor(
    private readonly root: HTMLElement,
    private readonly speakers: (who: string) => Speaker,
  ) {}

  start(lines: Line[], onDone?: () => void): void {
    if (!lines.length) {
      onDone?.();
      return;
    }
    this.lines = lines;
    this.i = 0;
    this.onDone = onDone;
    this.active = true;
    if (!this.el) {
      this.el = document.createElement('div');
      this.el.className = 'v10-box v10-panel dialog';
      this.el.addEventListener('pointerdown', () => this.next());
      this.root.appendChild(this.el);
    }
    this.render();
  }

  next(): void {
    if (!this.active) return;
    this.i++;
    if (this.i >= this.lines.length) {
      this.close();
      return;
    }
    this.render();
  }

  close(): void {
    this.active = false;
    this.el?.remove();
    this.el = null;
    const d = this.onDone;
    this.onDone = undefined;
    d?.();
  }

  private render(): void {
    if (!this.el) return;
    const l = this.lines[this.i];
    const s = this.speakers(l.who);
    this.el.innerHTML = '';
    const pv = document.createElement('div');
    pv.className = 'portrait';
    if (s.portrait) pv.appendChild(s.portrait);
    const body = document.createElement('div');
    body.className = 'body';
    body.innerHTML = `<div class="who" style="color:${s.color}">${s.name}</div><div class="text">${l.text}</div><div class="v10-hint more">${this.i + 1}/${this.lines.length} · <kbd>Enter</kbd> tiếp</div>`;
    this.el.append(pv, body);
  }
}

/** Vẽ một khung atlas (đã cắt viền) lên canvas phóng ×scale, dùng làm chân dung. */
export function portraitCanvas(
  image: HTMLImageElement | HTMLCanvasElement,
  frame: { x: number; y: number; w: number; h: number },
  scale = 2,
): HTMLCanvasElement {
  const c = document.createElement('canvas');
  c.width = frame.w * scale;
  c.height = frame.h * scale;
  const ctx = c.getContext('2d')!;
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(image, frame.x, frame.y, frame.w, frame.h, 0, 0, c.width, c.height);
  return c;
}
