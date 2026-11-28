import { defineConfig } from 'vite';

export default defineConfig({
  // Static assets live in public/assets/ and keep their paths after the build,
  // so they can be referenced directly as /assets/xxx.webp
  build: { target: 'es2020' },
  // Listen on the local network too, so a phone or another computer on the
  // same Wi-Fi can open the dev server (and the preview of a build)
  server: { host: true },
  preview: { host: true },
});
