import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  // The base must match repo name since we are deploying the site to https://nextstrain.github.io/forecasts-ncov/
  // See vite docs on deploying to GH pages: https://vitejs.dev/guide/static-deploy.html#github-pages
  base: "/forecasts-ncov/",
  plugins: [react()],
})
