import type Phaser from 'phaser';

/** Phím của game (CLAUDE.md / HUD v10): WASD hoặc mũi tên đi, Shift chạy, C tư thế, Space ném, E hành động, 1–4 đổi người. */
export interface Keys {
  up: Phaser.Input.Keyboard.Key[];
  down: Phaser.Input.Keyboard.Key[];
  left: Phaser.Input.Keyboard.Key[];
  right: Phaser.Input.Keyboard.Key[];
  run: Phaser.Input.Keyboard.Key[];
  stance: Phaser.Input.Keyboard.Key;
  throw: Phaser.Input.Keyboard.Key;
  action: Phaser.Input.Keyboard.Key;
  slots: Phaser.Input.Keyboard.Key[];
}

export function createKeys(scene: Phaser.Scene): Keys {
  const kb = scene.input.keyboard!;
  const k = (name: string) => kb.addKey(name);
  return {
    up: [k('W'), k('UP')],
    down: [k('S'), k('DOWN')],
    left: [k('A'), k('LEFT')],
    right: [k('D'), k('RIGHT')],
    run: [k('SHIFT')],
    stance: k('C'),
    throw: k('SPACE'),
    action: k('E'),
    slots: [k('ONE'), k('TWO'), k('THREE'), k('FOUR')],
  };
}

const any = (ks: Phaser.Input.Keyboard.Key[]) => ks.some((x) => x.isDown);

/** Trục di chuyển -1/0/1 theo x và y. */
export function axis(keys: Keys): { x: number; y: number } {
  return {
    x: (any(keys.right) ? 1 : 0) - (any(keys.left) ? 1 : 0),
    y: (any(keys.down) ? 1 : 0) - (any(keys.up) ? 1 : 0),
  };
}

export const isRunning = (keys: Keys) => any(keys.run);
