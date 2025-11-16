# Vite Documentation

**Official Docs:** https://vitejs.dev/

## Overview
Vite is a next-generation frontend build tool that provides fast development server and optimized production builds. We use Vite 5.4 for the Seed Planter frontend.

## Key Features
- Lightning-fast HMR (Hot Module Replacement)
- Native ES modules in development
- Optimized production builds with Rollup
- Built-in TypeScript support
- Plugin ecosystem
- CSS pre-processors support

## Project Setup

### Create New Project
```bash
npm create vite@latest my-app -- --template react
cd my-app
npm install
npm run dev
```

### Available Templates
- `vanilla`, `vanilla-ts`
- `react`, `react-ts`
- `vue`, `vue-ts`
- `preact`, `preact-ts`
- `lit`, `lit-ts`
- `svelte`, `svelte-ts`

## Configuration

### vite.config.js
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom']
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  }
})
```

## Development Server

### Start Dev Server
```bash
npm run dev
# or
vite
```

### Options
```bash
vite --port 3000
vite --host 0.0.0.0  # Expose to network
vite --open          # Auto-open browser
```

## Environment Variables

### .env Files
```bash
# .env
VITE_API_URL=http://localhost:8000

# .env.production
VITE_API_URL=https://api.production.com
```

### Usage in Code
```javascript
const apiUrl = import.meta.env.VITE_API_URL
const isDev = import.meta.env.DEV
const isProd = import.meta.env.PROD
```

**Important:** Only variables prefixed with `VITE_` are exposed to client code.

## Building for Production

```bash
npm run build
# or
vite build
```

### Build Options
```bash
vite build --mode production
vite build --outDir custom-dist
vite build --sourcemap
```

### Preview Production Build
```bash
npm run preview
# or
vite preview
```

## Static Assets

### Importing Assets
```javascript
// URL import
import imgUrl from './img.png'

// Raw import
import shaderString from './shader.glsl?raw'

// Worker import
import Worker from './worker?worker'
```

### Public Directory
Files in `/public` are served at root path:
```
public/
  favicon.ico
  robots.txt
```

Access: `<img src="/favicon.ico" />`

## CSS Support

### CSS Modules
```javascript
import styles from './style.module.css'

function Component() {
  return <div className={styles.container}>Hello</div>
}
```

### PostCSS
```javascript
// postcss.config.js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  }
}
```

### Pre-processors
```bash
npm install -D sass
# or
npm install -D less
# or
npm install -D stylus
```

Then import directly:
```javascript
import './styles.scss'
```

## Plugins

### React Plugin
```javascript
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()]
})
```

### Common Plugins
```bash
# PWA
npm install -D vite-plugin-pwa

# SVG as React components
npm install -D vite-plugin-svgr

# Compression
npm install -D vite-plugin-compression
```

## Code Splitting

### Dynamic Imports
```javascript
// Automatic code splitting
const AdminPanel = lazy(() => import('./AdminPanel'))
```

### Manual Chunks
```javascript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'ui-library': ['lucide-react']
        }
      }
    }
  }
})
```

## Optimization

### Dependency Pre-bundling
Vite automatically pre-bundles dependencies for faster page loads.

### Force Re-optimize
```bash
vite --force
```

### Exclude from Pre-bundling
```javascript
export default defineConfig({
  optimizeDeps: {
    exclude: ['some-large-dep']
  }
})
```

## TypeScript Support

Vite supports TypeScript out of the box:
```typescript
// vite-env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

## Docker Integration

### Dockerfile
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Build with Args
```bash
docker build --build-arg VITE_API_URL=https://api.prod.com -t app .
```

## Performance Tips

1. **Use dynamic imports** for code splitting
2. **Optimize images** before importing
3. **Use CSS modules** to avoid global styles
4. **Enable compression** in production
5. **Lazy load routes** and components
6. **Use production mode** for builds
7. **Minimize bundle size** with tree shaking

## Common Commands

```bash
# Development
npm run dev

# Build
npm run build

# Preview production build
npm run preview

# Lint (if configured)
npm run lint

# Clean cache and rebuild
rm -rf node_modules/.vite
npm run dev -- --force
```

## Troubleshooting

### Port Already in Use
```bash
vite --port 3001
```

### Clear Cache
```bash
rm -rf node_modules/.vite
```

### CORS Issues
Configure proxy in `vite.config.js`:
```javascript
server: {
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```

## Best Practices

1. **Use environment variables** for configuration
2. **Enable source maps** in production for debugging
3. **Configure proxy** for API calls in development
4. **Use path aliases** for cleaner imports
5. **Optimize assets** before committing
6. **Keep dependencies updated**
7. **Use production builds** for deployment
8. **Monitor bundle size** regularly

## Migration from CRA

Key differences from Create React App:
- Use `import.meta.env` instead of `process.env`
- Prefix env vars with `VITE_`
- Use `index.html` in root (not in `/public`)
- Update import paths if needed

## Resources
- Official Docs: https://vitejs.dev/
- Config Reference: https://vitejs.dev/config/
- Plugin List: https://vitejs.dev/plugins/
- GitHub: https://github.com/vitejs/vite

## Version Used in SeedGPT
```
vite==5.4.10
@vitejs/plugin-react==4.3.3
```
