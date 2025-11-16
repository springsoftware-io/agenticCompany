# TailwindCSS Documentation

**Official Docs:** https://tailwindcss.com/

## Overview
TailwindCSS is a utility-first CSS framework. We use Tailwind 3.4 for styling the Seed Planter frontend.

## Key Features
- Utility-first approach
- Responsive design utilities
- Dark mode support
- JIT (Just-In-Time) compiler
- Custom design system
- No unused CSS in production

## Installation

### With Vite
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Configuration Files

**tailwind.config.js:**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#10B981',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
```

**postcss.config.js:**
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### CSS Entry Point

**src/index.css:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## Core Concepts

### Utility Classes
```jsx
<div className="flex items-center justify-between p-4 bg-blue-500 text-white rounded-lg shadow-md">
  <h1 className="text-2xl font-bold">Hello World</h1>
  <button className="px-4 py-2 bg-white text-blue-500 rounded hover:bg-gray-100">
    Click me
  </button>
</div>
```

### Responsive Design
```jsx
<div className="w-full md:w-1/2 lg:w-1/3">
  {/* Full width on mobile, half on tablet, third on desktop */}
</div>
```

Breakpoints:
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

### Dark Mode
```javascript
// tailwind.config.js
export default {
  darkMode: 'class', // or 'media'
  // ...
}
```

```jsx
<div className="bg-white dark:bg-gray-900 text-black dark:text-white">
  Content adapts to dark mode
</div>
```

### Hover, Focus, and Other States
```jsx
<button className="bg-blue-500 hover:bg-blue-600 focus:ring-2 focus:ring-blue-300 active:bg-blue-700 disabled:opacity-50">
  Button
</button>
```

## Layout

### Flexbox
```jsx
<div className="flex flex-col md:flex-row gap-4 items-center justify-between">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>
```

### Grid
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div>Card 1</div>
  <div>Card 2</div>
  <div>Card 3</div>
</div>
```

### Container
```jsx
<div className="container mx-auto px-4">
  {/* Centered container with padding */}
</div>
```

## Spacing

### Padding & Margin
```jsx
<div className="p-4">Padding all sides</div>
<div className="px-4 py-2">Padding x and y</div>
<div className="pt-4 pr-2 pb-4 pl-2">Individual sides</div>
<div className="m-4">Margin all sides</div>
<div className="mx-auto">Center horizontally</div>
```

Scale: 0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 56, 64

## Typography

```jsx
<h1 className="text-4xl font-bold text-gray-900 leading-tight">
  Heading
</h1>
<p className="text-base text-gray-600 leading-relaxed">
  Paragraph text
</p>
<span className="text-sm font-medium text-blue-500 uppercase tracking-wide">
  Label
</span>
```

## Colors

```jsx
<div className="bg-blue-500 text-white border-2 border-blue-700">
  {/* Background, text, and border colors */}
</div>
```

Color shades: 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950

## Borders & Shadows

```jsx
<div className="border border-gray-300 rounded-lg shadow-md">
  Card with border and shadow
</div>

<div className="border-2 border-t-4 border-blue-500 rounded-xl shadow-lg">
  Custom borders
</div>
```

## Custom Components

### Using @apply
```css
@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:ring-2 focus:ring-blue-300;
  }
  
  .card {
    @apply p-6 bg-white rounded-lg shadow-md;
  }
}
```

### Using JavaScript
```jsx
const buttonClasses = "px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"

function Button({ children }) {
  return <button className={buttonClasses}>{children}</button>
}
```

## Conditional Classes

### With clsx
```jsx
import clsx from 'clsx'

function Button({ primary, disabled }) {
  return (
    <button className={clsx(
      'px-4 py-2 rounded',
      primary ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800',
      disabled && 'opacity-50 cursor-not-allowed'
    )}>
      Click me
    </button>
  )
}
```

### With tailwind-merge
```jsx
import { twMerge } from 'tailwind-merge'

function Button({ className, ...props }) {
  return (
    <button 
      className={twMerge('px-4 py-2 bg-blue-500 text-white rounded', className)}
      {...props}
    />
  )
}
```

## Animations

```jsx
<div className="transition duration-300 ease-in-out hover:scale-105">
  Hover to scale
</div>

<div className="animate-spin">
  Spinning loader
</div>

<div className="animate-pulse">
  Pulsing skeleton
</div>
```

## Custom Theme

```javascript
// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        }
      },
      spacing: {
        '128': '32rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        }
      }
    }
  }
}
```

## Plugins

### Official Plugins
```bash
npm install -D @tailwindcss/forms
npm install -D @tailwindcss/typography
npm install -D @tailwindcss/aspect-ratio
npm install -D @tailwindcss/container-queries
```

```javascript
// tailwind.config.js
export default {
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

## Production Optimization

Tailwind automatically purges unused CSS in production based on your `content` configuration.

### Safelist Classes
```javascript
// tailwind.config.js
export default {
  safelist: [
    'bg-red-500',
    'text-3xl',
    {
      pattern: /bg-(red|green|blue)-(100|500|900)/,
    }
  ],
}
```

## Best Practices

1. **Use consistent spacing scale** (4, 8, 16, 24, 32, etc.)
2. **Leverage responsive utilities** for mobile-first design
3. **Extract common patterns** into components
4. **Use semantic color names** in theme config
5. **Keep utility classes readable** with proper formatting
6. **Use @apply sparingly** (prefer composition)
7. **Configure purge properly** to remove unused styles
8. **Use dark mode** for better UX

## Common Patterns

### Card Component
```jsx
<div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
  <h2 className="text-xl font-bold mb-2">Card Title</h2>
  <p className="text-gray-600">Card content goes here.</p>
</div>
```

### Button Variants
```jsx
// Primary
<button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
  Primary
</button>

// Secondary
<button className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300">
  Secondary
</button>

// Outline
<button className="px-4 py-2 border-2 border-blue-500 text-blue-500 rounded hover:bg-blue-50">
  Outline
</button>
```

### Form Input
```jsx
<input 
  type="text"
  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
  placeholder="Enter text"
/>
```

## Resources
- Official Docs: https://tailwindcss.com/docs
- Playground: https://play.tailwindcss.com/
- Component Examples: https://tailwindui.com/
- Cheat Sheet: https://nerdcave.com/tailwind-cheat-sheet

## Version Used in SeedGPT
```
tailwindcss==3.4.14
postcss==8.4.47
autoprefixer==10.4.20
clsx==2.1.1
tailwind-merge==2.5.4
```
