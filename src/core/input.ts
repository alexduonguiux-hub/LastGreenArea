import type Phaser from 'phaser';

/**
 * Phím của game (CLAUDE.md / HUD v10): WASD hoặc mũi tên đi, Shift bật/tắt Chạy (bấm một lần, không giữ),
 * C xoay tư thế Đi / Khom / Bò, Space ném, E hành động, 1–4 đổi người. Shift và C xử lý bằng keydown trong Level.
 */
export interface Keys {
  up: Phaser.Input.Keyboard.Key[];
  down: Phaser.Input.Keyboard.Key[];
  left: Phaser.Input.Keyboard.Key[];
  right: Phaser.Input.Keyboard.Key[];
  stance: Phaser.Input.Keyboard.Key;
  run: Phaser.Input.Keyboard.Key;
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
    stance: k('C'),
    run: k('SHIFT'),
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
