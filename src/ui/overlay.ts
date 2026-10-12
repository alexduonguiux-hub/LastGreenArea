/**
 * Lớp DOM đè lên canvas: mọi chữ tiếng Việt vẽ ở độ phân giải hiển thị (CLAUDE.md), không vẽ trong Phaser.
 * Hộp cố định (góc trên trái, trên phải, giữa, dưới) và "marker" bám theo tọa độ thế giới (dấu ?, !, nhãn).
 * A4/B5 thay bằng bộ thành phần v10 từ atlas.
 */
import { GAME_H, GAME_W } from '../main';

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

export interface Camera {
  scrollX: number;
  scrollY: number;
}

export const overlay = {
  topLeft(title: string, sub: string) {
    return box('top-left', `<div class="v10-title">${title}</div><div>${sub}</div>`);
  },
  topRight(html: string) {
    return box('top-right', html);
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
  removeCenter() {
    root.querySelector('.v10-box.center')?.remove();
  },
  /** Thanh phân đoạn 10 ô; color là token CSS. */
  segments(value01: number, color: string): string {
    const n = Math.round(Math.max(0, Math.min(1, value01)) * 10);
    return `<div class="v10-seg">${Array.from({ length: 10 }, (_, i) => `<i style="${i < n ? `background:${color}` : ''}"></i>`).join('')}</div>`;
  },
  /** Marker bám thế giới: đặt/cập nhật theo id; gọi mỗi khung với camera hiện tại. */
  marker(id: string, worldX: number, worldY: number, cam: Camera, html: string, cls = '') {
    let el = root.querySelector<HTMLDivElement>(`.v10-marker[data-id="${id}"]`);
    if (!el) {
      el = document.createElement('div');
      el.className = 'v10-marker';
      el.dataset.id = id;
      root.appendChild(el);
    }
    if (el.innerHTML !== html) el.innerHTML = html;
    el.className = `v10-marker ${cls}`;
    el.style.left = `${((worldX - cam.scrollX) / GAME_W) * 100}%`;
    el.style.top = `${((worldY - cam.scrollY) / GAME_H) * 100}%`;
  },
  removeMarker(id: string) {
    root.querySelector(`.v10-marker[data-id="${id}"]`)?.remove();
  },
  clear() {
    root.innerHTML = '';
  },
};
