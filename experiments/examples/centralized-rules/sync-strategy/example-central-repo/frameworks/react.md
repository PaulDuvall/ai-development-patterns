# React Development Rules

Framework-specific rules for React projects.

## Component Structure

### Functional Components
- ✅ Always use functional components with hooks
- ❌ No class components (legacy)
- ✅ One component per file
- ✅ Named exports for components

```tsx
// CORRECT - Functional component with hooks
export function UserProfile({ userId }: { userId: number }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId).then(setUser).finally(() => setLoading(false));
  }, [userId]);

  if (loading) return <LoadingSpinner />;
  if (!user) return <UserNotFound />;

  return <div className="user-profile">...</div>;
}

// WRONG - Class component (legacy)
class UserProfile extends React.Component {
  ...
}
```

### File Organization
```
src/
├── components/
│   ├── UserProfile/
│   │   ├── UserProfile.tsx       # Component
│   │   ├── UserProfile.test.tsx  # Tests
│   │   ├── UserProfile.module.css # Styles
│   │   └── index.ts              # Re-export
│   └── shared/
│       ├── Button/
│       ├── Input/
│       └── Modal/
├── hooks/
│   ├── useAuth.ts
│   ├── useApi.ts
│   └── useForm.ts
├── pages/
│   ├── Home.tsx
│   └── Dashboard.tsx
└── utils/
    ├── api.ts
    └── validation.ts
```

## Type Safety

### TypeScript
- ✅ Required for all React projects
- ✅ Strict mode enabled in `tsconfig.json`
- ✅ Type all props, state, and hooks

```tsx
// Component props interface
interface UserCardProps {
  user: User;
  onEdit: (userId: number) => void;
  isAdmin?: boolean;  // Optional prop
}

export function UserCard({ user, onEdit, isAdmin = false }: UserCardProps) {
  return (
    <div className="user-card">
      <h2>{user.name}</h2>
      {isAdmin && <button onClick={() => onEdit(user.id)}>Edit</button>}
    </div>
  );
}
```

### Avoid `any`
```tsx
// WRONG - Using any
function SearchResults({ data }: { data: any }) {
  return data.map((item: any) => <div>{item.name}</div>);
}

// CORRECT - Proper typing
interface SearchItem {
  id: number;
  name: string;
  description: string;
}

function SearchResults({ data }: { data: SearchItem[] }) {
  return data.map(item => <div key={item.id}>{item.name}</div>);
}
```

## State Management

### Local State (useState)
Use for component-specific state:
```tsx
function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}
```

### Global State (Context API)
Use for app-wide state (avoid prop drilling >2 levels):
```tsx
// contexts/AuthContext.tsx
interface AuthContextType {
  user: User | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (credentials: Credentials) => {
    const user = await authApi.login(credentials);
    setUser(user);
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

### When to Use Redux/Zustand
- Complex state with many interdependencies
- Need for time-travel debugging
- Large team needing strict state patterns

For most projects, Context API is sufficient.

## Hooks

### Custom Hooks
Extract reusable logic into custom hooks:
```tsx
// hooks/useApi.ts
function useApi<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    fetch(url)
      .then(res => res.json())
      .then(data => {
        if (!cancelled) {
          setData(data);
          setLoading(false);
        }
      })
      .catch(err => {
        if (!cancelled) {
          setError(err);
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;  // Cleanup on unmount
    };
  }, [url]);

  return { data, loading, error };
}

// Usage
function UserList() {
  const { data, loading, error } = useApi<User[]>('/api/users');

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return <ul>{data?.map(user => <li key={user.id}>{user.name}</li>)}</ul>;
}
```

### Hook Rules
- ✅ Always call hooks at top level (not in conditionals/loops)
- ✅ Only call hooks in functional components or custom hooks
- ✅ Use ESLint plugin: `eslint-plugin-react-hooks`

## Styling

### CSS Modules (Preferred)
```tsx
// UserCard.module.css
.card {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 16px;
}

.cardTitle {
  font-size: 18px;
  font-weight: bold;
}

// UserCard.tsx
import styles from './UserCard.module.css';

export function UserCard({ user }: { user: User }) {
  return (
    <div className={styles.card}>
      <h2 className={styles.cardTitle}>{user.name}</h2>
    </div>
  );
}
```

### Tailwind CSS (Alternative)
If using Tailwind:
```tsx
export function UserCard({ user }: { user: User }) {
  return (
    <div className="border border-gray-300 rounded-lg p-4">
      <h2 className="text-lg font-bold">{user.name}</h2>
    </div>
  );
}
```

Avoid inline styles except for dynamic values:
```tsx
// OK for dynamic values
<div style={{ width: `${percentage}%` }} />

// WRONG for static styles
<div style={{ padding: '16px', border: '1px solid #ccc' }} />
```

## Testing

### React Testing Library
Focus on testing user behavior, not implementation:
```tsx
// UserProfile.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserProfile } from './UserProfile';

describe('UserProfile', () => {
  it('displays user name and email', async () => {
    render(<UserProfile userId={123} />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('john@example.com')).toBeInTheDocument();
    });
  });

  it('allows editing user info when Edit clicked', async () => {
    const user = userEvent.setup();
    render(<UserProfile userId={123} />);

    await user.click(screen.getByRole('button', { name: /edit/i }));

    expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
  });
});
```

### What to Test
- ✅ User interactions (clicks, form submissions)
- ✅ Conditional rendering based on props/state
- ✅ API integration (use MSW for mocking)
- ❌ Implementation details (state variable names, function calls)

### Snapshot Tests
Use sparingly for stable UI only:
```tsx
it('matches snapshot for user card', () => {
  const { container } = render(<UserCard user={mockUser} />);
  expect(container).toMatchSnapshot();
});
```

## Performance

### Memoization
Use `useMemo` and `useCallback` only when needed:
```tsx
function ExpensiveComponent({ items, onSelect }: Props) {
  // Memoize expensive calculation
  const sortedItems = useMemo(() => {
    return items.sort((a, b) => a.score - b.score);
  }, [items]);

  // Memoize callback to prevent child re-renders
  const handleSelect = useCallback((id: number) => {
    onSelect(id);
  }, [onSelect]);

  return <ItemList items={sortedItems} onSelect={handleSelect} />;
}
```

### React.memo
Prevent unnecessary re-renders:
```tsx
export const UserCard = React.memo(function UserCard({ user }: Props) {
  return <div>...</div>;
});
```

### Code Splitting
```tsx
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./pages/Dashboard'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Dashboard />
    </Suspense>
  );
}
```

## API Calls

### Use SWR or React Query
```tsx
import useSWR from 'swr';

function UserProfile({ userId }: { userId: number }) {
  const { data, error, isLoading } = useSWR(
    `/api/users/${userId}`,
    fetcher
  );

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return <div>{data.name}</div>;
}
```

### Benefits
- Automatic caching
- Revalidation on focus
- Request deduplication
- Error retry logic

## Accessibility

### Semantic HTML
```tsx
// CORRECT
<button onClick={handleClick}>Submit</button>
<nav>
  <ul>
    <li><a href="/home">Home</a></li>
  </ul>
</nav>

// WRONG - div soup
<div onClick={handleClick}>Submit</div>
<div>
  <div>
    <div onClick={() => navigate('/home')}>Home</div>
  </div>
</div>
```

### ARIA Labels
```tsx
<button aria-label="Close modal" onClick={onClose}>
  <XIcon />
</button>

<input
  type="text"
  aria-label="Search users"
  placeholder="Search..."
/>
```

### Keyboard Navigation
Ensure all interactive elements are keyboard accessible:
```tsx
function Modal({ onClose }: Props) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  return <div role="dialog" aria-modal="true">...</div>;
}
```

## Common Anti-Patterns

### ❌ Prop Drilling
```tsx
// WRONG
<App>
  <Header user={user} />
  <Main user={user} />
    <Sidebar user={user} />
      <UserMenu user={user} />
</App>

// CORRECT - Use Context
<AuthProvider>
  <App>
    <Header />
    <Main />
  </App>
</AuthProvider>
```

### ❌ Mutating State Directly
```tsx
// WRONG
const [items, setItems] = useState([1, 2, 3]);
items.push(4);  // Direct mutation!
setItems(items);

// CORRECT
setItems([...items, 4]);
```

### ❌ Missing Key Props
```tsx
// WRONG
{items.map(item => <div>{item.name}</div>)}

// CORRECT
{items.map(item => <div key={item.id}>{item.name}</div>)}
```

## Tools & Configuration

### ESLint
```json
{
  "extends": [
    "react-app",
    "react-app/jest",
    "plugin:react-hooks/recommended"
  ]
}
```

### TypeScript Config
```json
{
  "compilerOptions": {
    "strict": true,
    "jsx": "react-jsx",
    "module": "esnext",
    "moduleResolution": "node"
  }
}
```

### Required Dependencies
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/user-event": "^14.5.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "typescript": "^5.0.0"
  }
}
```
