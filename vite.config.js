import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  base: '/Personal-Website/',
  build: {
    rollupOptions: {
      input: {
        main: fileURLToPath(new URL('./index.html', import.meta.url)),
        artStudy: fileURLToPath(new URL('./art-study.html', import.meta.url)),
      },
    },
  },
});
