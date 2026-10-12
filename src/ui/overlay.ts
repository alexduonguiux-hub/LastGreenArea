/**
 * Lớp DOM đè lên canvas: mọi chữ tiếng Việt vẽ ở độ phân giải hiển thị (CLAUDE.md), không vẽ trong Phaser.
 * B0 chỉ có ba hộp: góc trên trái, giữa (nạp), dưới (gợi ý phím). A4/B5 thay bằng bộ thành phần v10 từ atlas.
 */
let root: HTMLElement;

export function mountOverlay(): void {
  root = document.getElementById('ui')!;
}

function box(cls: string, html: string): HTMLDivElement {
  let el = root.querySelector<HTMLDivElement>(`.v10-box.${cls}`);
  if (!el) {
    el = document.createElement('div');
    el.className = `v10-box ${cls}`;
    root.appendChild(el);
  }
  el.innerHTML = html;
  return el;
}

export const overlay = {
  topLeft(title: string, sub: string) {
    return box('top-left', `<div class="v10-title">${title}</div><div>${sub}</div>`);
  },
  bottom(hintHtml: string) {
    return box('bottom', `<div class="v10-hint">${hintHtml}</div>`);
  },
  center(title: string, sub: string, bar = false) {
    const el = box('center', `<div class="v10-title">${title}</div><div>${sub}</div>${bar ? '<div class="v10-bar"><i></i></div>' : ''}`);
    return {
      progress(p: number) {
        const i = el.querySelector<HTMLElement>('.v10-bar i');
        if (i) i.style.width = `${Math.round(p * 100)}%`;
      },
      remove() {
        el.remove();
      },
    };
  },
  clear() {
    root.innerHTML = '';
  },
};
