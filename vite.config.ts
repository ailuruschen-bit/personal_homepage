import { defineConfig } from 'vite';

export default defineConfig({
  // Static assets live in public/assets/ and keep their paths after the build,
  // so they can be referenced directly as /assets/xxx.webp
  build: { target: 'es2020' },
});
