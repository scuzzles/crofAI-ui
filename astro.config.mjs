// @ts-check
import { defineConfig } from "astro/config";
import svelte from "@astrojs/svelte";

// https://astro.build/config
export default defineConfig({
  prefetch: {
    prefetchAll: true,
  },
  integrations: [svelte()],
  vite: {
    server: {
      proxy: {
        "/v2": {
          target: "https://ai.nahcrof.com",
          changeOrigin: true,
        },
      },
    },
  },
});
