import Phaser from 'phaser';
import { Preload } from './scenes/Preload';
import { Level } from './scenes/Level';
import { mountOverlay } from './ui/overlay';

/** Độ phân giải gốc (CLAUDE.md): 800×450, phóng nguyên lần, không làm mượt. */
export const GAME_W = 800;
export const GAME_H = 450;

mountOverlay();

new Phaser.Game({
  type: Phaser.AUTO,
  parent: 'game',
  width: GAME_W,
  height: GAME_H,
  backgroundColor: '#080A10',
  pixelArt: true,
  roundPixels: true,
  scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
  scene: [Preload, Level],
});
