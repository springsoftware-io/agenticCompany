# React Documentation

**Official Docs:** https://react.dev/

## Overview
React is a JavaScript library for building user interfaces. We use React 18.3 for the Seed Planter frontend.

## Key Features
- Component-based architecture
- Virtual DOM for performance
- Hooks for state and side effects
- Concurrent rendering
- Server components support

## Basic Component

```jsx
function Welcome({ name }) {
  return <h1>Hello, {name}</h1>;
}
```

## Hooks

### useState
Manage component state.

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
}
```

### useEffect
Handle side effects (data fetching, subscriptions, etc.).

```jsx
import { useEffect, useState } from 'react';

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(data => setUser(data));
  }, [userId]); // Re-run when userId changes
  
  if (!user) return <div>Loading...</div>;
  return <div>{user.name}</div>;
}
```

### useContext
Share data across components without prop drilling.

```jsx
import { createContext, useContext } from 'react';

const ThemeContext = createContext('light');

function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Toolbar />
    </ThemeContext.Provider>
  );
}

function Toolbar() {
  const theme = useContext(ThemeContext);
  return <div className={theme}>Toolbar</div>;
}
```

### useRef
Access DOM elements or persist values across renders.

```jsx
import { useRef } from 'react';

function TextInput() {
  const inputRef = useRef(null);
  
  const focusInput = () => {
    inputRef.current.focus();
  };
  
  return (
    <>
      <input ref={inputRef} />
      <button onClick={focusInput}>Focus Input</button>
    </>
  );
}
```

### useMemo
Memoize expensive calculations.

```jsx
import { useMemo } from 'react';

function ExpensiveComponent({ items }) {
  const total = useMemo(() => {
    return items.reduce((sum, item) => sum + item.price, 0);
  }, [items]);
  
  return <div>Total: ${total}</div>;
}
```

### useCallback
Memoize callback functions.

```jsx
import { useCallback, useState } from 'react';

function Parent() {
  const [count, setCount] = useState(0);
  
  const handleClick = useCallback(() => {
    setCount(c => c + 1);
  }, []); // Function won't change between renders
  
  return <Child onClick={handleClick} />;
}
```

## Event Handling

```jsx
function Button() {
  const handleClick = (e) => {
    e.preventDefault();
    console.log('Button clicked');
  };
  
  return <button onClick={handleClick}>Click me</button>;
}
```

## Conditional Rendering

```jsx
function Greeting({ isLoggedIn }) {
  return (
    <div>
      {isLoggedIn ? (
        <h1>Welcome back!</h1>
      ) : (
        <h1>Please sign in.</h1>
      )}
    </div>
  );
}
```

## Lists and Keys

```jsx
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>{todo.text}</li>
      ))}
    </ul>
  );
}
```

## Forms

```jsx
function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log({ email, password });
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

## Custom Hooks

```jsx
import { useState, useEffect } from 'react';

function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err);
        setLoading(false);
      });
  }, [url]);
  
  return { data, loading, error };
}

// Usage
function UserProfile({ userId }) {
  const { data, loading, error } = useFetch(`/api/users/${userId}`);
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  return <div>{data.name}</div>;
}
```

## Error Boundaries

```jsx
import { Component } from 'react';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('Error:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong.</h1>;
    }
    return this.props.children;
  }
}

// Usage
<ErrorBoundary>
  <MyComponent />
</ErrorBoundary>
```

## Lazy Loading

```jsx
import { lazy, Suspense } from 'react';

const LazyComponent = lazy(() => import('./LazyComponent'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LazyComponent />
    </Suspense>
  );
}
```

## React 18 Features

### Concurrent Rendering
React 18 enables concurrent rendering by default.

### useTransition
Mark updates as non-urgent.

```jsx
import { useTransition, useState } from 'react';

function SearchResults() {
  const [isPending, startTransition] = useTransition();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  
  const handleChange = (e) => {
    setQuery(e.target.value);
    startTransition(() => {
      // This update is non-urgent
      setResults(searchItems(e.target.value));
    });
  };
  
  return (
    <>
      <input value={query} onChange={handleChange} />
      {isPending && <div>Loading...</div>}
      <Results items={results} />
    </>
  );
}
```

### useDeferredValue
Defer updating part of the UI.

```jsx
import { useDeferredValue, useState } from 'react';

function SearchPage() {
  const [query, setQuery] = useState('');
  const deferredQuery = useDeferredValue(query);
  
  return (
    <>
      <input value={query} onChange={e => setQuery(e.target.value)} />
      <Results query={deferredQuery} />
    </>
  );
}
```

## Best Practices

1. **Keep components small** and focused on a single responsibility
2. **Use functional components** with hooks (avoid class components)
3. **Lift state up** when multiple components need the same data
4. **Use keys properly** in lists (stable, unique identifiers)
5. **Avoid inline functions** in render for performance
6. **Use React DevTools** for debugging
7. **Memoize expensive calculations** with useMemo
8. **Extract custom hooks** for reusable logic
9. **Handle loading and error states** properly
10. **Use TypeScript** for better type safety

## Performance Optimization

```jsx
import { memo } from 'react';

// Prevent unnecessary re-renders
const MemoizedComponent = memo(function MyComponent({ data }) {
  return <div>{data}</div>;
});
```

## Resources
- Official Docs: https://react.dev/
- Learn React: https://react.dev/learn
- API Reference: https://react.dev/reference/react
- React DevTools: https://react.dev/learn/react-developer-tools

## Version Used in SeedGPT
```
react==18.3.1
react-dom==18.3.1
```
