import Phaser from 'phaser';
import { Preload } from './scenes/Preload';
import { Level } from './scenes/Level';
import { mountOverlay } from './ui/overlay';

/** Độ phân giải gốc (CLAUDE.md): 800×450, phóng nguyên lần, không làm mượt. */
export const GAME_W = 800;
export const GAME_H = 450;

mountOverlay();

// 1 px game = --px px CSS trên lớp UI (lớp UI luôn phủ đúng canvas 800×450 đã phóng)
const stage = document.getElementById('stage')!;
const setPx = () => document.getElementById('ui')!.style.setProperty('--px', `${stage.clientWidth / GAME_W}px`);
new ResizeObserver(setPx).observe(stage);
setPx();

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
