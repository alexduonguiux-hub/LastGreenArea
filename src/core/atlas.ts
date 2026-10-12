import type Phaser from 'phaser';

/** Khóa texture của ma trận atlas (N trang 2048, xem docs/ART.md). */
export const ATLAS = 'atlas';
export const ANIMS_JSON = 'anims';

/** Nạp N trang atlas + manifest (TexturePacker multiatlas) + bảng hoạt ảnh. Đường dẫn tương đối với index.html. */
export function loadAtlas(load: Phaser.Loader.LoaderPlugin): void {
  load.multiatlas(ATLAS, 'data/atlas.json', 'assets/');
  load.json(ANIMS_JSON, 'data/anims.json');
}
