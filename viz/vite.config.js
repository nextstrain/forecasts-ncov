import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// LOCAL_LIB=1 redirects @nextstrain/evofr-viz imports to the sibling
// forecasts-viz repo source, giving full HMR while editing the library.
const useLocalLib = !!process.env.LOCAL_LIB;
const localLibRoot = path.resolve(__dirname, '../../forecasts-viz');

const localLibAlias = useLocalLib ? {
  '@nextstrain/evofr-viz/dist/index.css': path.resolve(localLibRoot, 'src/lib/styles/styles.css'),
  '@nextstrain/evofr-viz': path.resolve(localLibRoot, 'src/lib/index.js'),
} : {};

export default defineConfig({
  // The base must match repo name since we are deploying the site to https://nextstrain.github.io/forecasts-ncov/
  // See vite docs on deploying to GH pages: https://vitejs.dev/guide/static-deploy.html#github-pages
  base: '/forecasts-ncov/',
  plugins: [
    // Library source files use the .js extension but contain JSX, so the
    // React plugin needs to transform .js as well.
    react({ include: /\.(jsx?|tsx?)$/ }),
  ],
  resolve: {
    alias: localLibAlias,
    dedupe: ['react', 'react-dom'],
  },
  // In LOCAL_LIB mode the library aliases to source `.js` files containing
  // JSX. Skip Vite's dep pre-bundling for it so plugin-react's Babel
  // transform handles those files instead of esbuild.
  optimizeDeps: useLocalLib ? {
    exclude: ['@nextstrain/evofr-viz'],
  } : undefined,
  server: useLocalLib ? {
    fs: { allow: [__dirname, localLibRoot] },
  } : undefined,
});
