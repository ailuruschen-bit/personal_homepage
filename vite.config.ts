import { defineConfig } from 'vite';

export default defineConfig({
  // 静态资源放在 public/assets/，构建后路径不变，便于直接引用 /assets/xxx.png
  build: { target: 'es2020' },
});
