import { defineConfig } from "vite";
import { fileURLToPath } from "node:url";

export default defineConfig({
  base: "/Personal-Website/",
  build: {
    // three.js is loaded lazily with the 3D island.
    chunkSizeWarningLimit: 700,
    rollupOptions: {
      input: {
        main: fileURLToPath(new URL("./index.html", import.meta.url)),
        artStudy: fileURLToPath(new URL("./art-study.html", import.meta.url)),
        styleStudy: fileURLToPath(new URL("./style-study.html", import.meta.url)),
      },
    },
  },
});
