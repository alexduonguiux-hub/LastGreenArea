import { defineConfig } from 'vitest/config';

export default defineConfig({
  // Đường dẫn tương đối để build chạy được cả ở GitHub Pages (thư mục con) lẫn mở từ máy.
  base: './',
  server: { port: 5173, host: '127.0.0.1' },
  build: { target: 'es2020', assetsInlineLimit: 0, chunkSizeWarningLimit: 1600 },
  test: { environment: 'node', include: ['src/**/*.test.ts'] },
});
