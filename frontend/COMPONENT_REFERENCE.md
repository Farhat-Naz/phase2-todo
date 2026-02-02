# Component Reference Guide

Quick reference for all Todo UI components.

## Type Definitions

### `types/todo.ts`

```typescript
import { Todo, TodoCreate, TodoUpdate } from '@/types/todo';

// Full todo object from API
const todo: Todo = {
  id: "123",
  user_id: "user-456",
  title: "Buy groceries",
  description: "Milk, eggs, bread",
  completed: false,
  created_at: "2024-01-08T10:00:00Z",
  updated_at: "2024-01-08T10:00:00Z",
};

// Create new todo
const createData: TodoCreate = {
  title: "New todo",
  description: "Optional description",
  completed: false, // optional, defaults to false
};

// Update existing todo
const updateData: TodoUpdate = {
  title: "Updated title", // optional
  description: "Updated description", // optional
  completed: true, // optional
};
```

## Hooks

### `useTodos()`

```typescript
import { useTodos } from '@/hooks/useTodos';

function MyComponent() {
  const {
    todos,         // Todo[] - Array of todos
    loading,       // boolean - Loading state
    error,         // string | null - Error message
    fetchTodos,    // () => Promise<void>
    createTodo,    // (data: TodoCreate) => Promise<Todo | null>
    updateTodo,    // (id: string, data: TodoUpdate) => Promise<Todo | null>
    deleteTodo,    // (id: string) => Promise<boolean>
    toggleComplete,// (id: string) => Promise<Todo | null>
  } = useTodos();

  // Todos auto-fetched on mount
  // All mutations use optimistic updates
  // Delete confirms before executing
}
```

## UI Components

### Button (Existing)

```typescript
import { Button } from '@/components/ui/Button';

<Button
  variant="primary" // primary | secondary | outline | ghost | danger
  size="md"         // sm | md | lg
  isLoading={false}
  leftIcon={<Icon />}
  rightIcon={<Icon />}
  onClick={() => {}}
>
  Click me
</Button>
```

### Input (Existing)

```typescript
import { Input } from '@/components/ui/Input';

<Input
  label="Email"
  type="email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  error="Invalid email"
  helperText="We'll never share your email"
  leftIcon={<Icon />}
  rightIcon={<Icon />}
  placeholder="you@example.com"
  required
/>
```

### Card (Existing)

```typescript
import { Card } from '@/components/ui/Card';

<Card
  variant="default"  // default | bordered | elevated
  padding="md"       // none | sm | md | lg
  hover={true}
>
  <h3>Card Title</h3>
  <p>Card content</p>
</Card>
```

### Checkbox (New)

```typescript
import { Checkbox } from '@/components/ui/Checkbox';

<Checkbox
  label="Accept terms"
  checked={accepted}
  onChange={(e) => setAccepted(e.target.checked)}
  disabled={false}
/>
```

### Textarea (New)

```typescript
import { Textarea } from '@/components/ui/Textarea';

<Textarea
  label="Description"
  value={description}
  onChange={(e) => setDescription(e.target.value)}
  error="Too long"
  helperText="Max 2000 characters"
  placeholder="Enter description"
  rows={3}
  maxLength={2000}
/>
```

### LoadingSpinner (New)

```typescript
import { LoadingSpinner } from '@/components/features/shared/LoadingSpinner';

<LoadingSpinner
  size="md"    // sm | md | lg
  text="Loading todos..."
  className="my-8"
/>
```

## Feature Components

### TodoForm

```typescript
import { TodoForm } from '@/components/features/todos/TodoForm';
import { TodoCreate } from '@/types/todo';

function MyComponent() {
  const handleSubmit = async (data: TodoCreate) => {
    // Create todo
    await createTodo(data);
  };

  return (
    <TodoForm
      onSubmit={handleSubmit}
      initialData={undefined}  // Optional: for edit mode
      loading={false}
    />
  );
}
```

**Features**:
- Title input (required, max 500 chars)
- Description textarea (optional, max 2000 chars)
- Validation with error messages
- Auto-clear on success
- Character counter
- Keyboard shortcuts (Enter to submit)

### TodoItem

```typescript
import { TodoItem } from '@/components/features/todos/TodoItem';
import { Todo, TodoUpdate } from '@/types/todo';

function MyComponent() {
  const handleToggle = async (id: string) => {
    await toggleComplete(id);
  };

  const handleUpdate = async (id: string, data: TodoUpdate) => {
    await updateTodo(id, data);
  };

  const handleDelete = async (id: string) => {
    await deleteTodo(id);
  };

  return (
    <TodoItem
      todo={todo}
      onToggle={handleToggle}
      onUpdate={handleUpdate}
      onDelete={handleDelete}
    />
  );
}
```

**Features**:
- Checkbox for completion toggle
- Inline editing (click Edit button)
- Delete with confirmation
- Strikethrough when completed
- Relative timestamps
- Mobile-friendly touch targets

### TodoList

```typescript
import { TodoList } from '@/components/features/todos/TodoList';

function DashboardPage() {
  return <TodoList />;
}
```

**Features**:
- Self-contained (uses useTodos hook internally)
- TodoForm for creating todos
- Displays all todos with TodoItem
- Loading/error/empty states
- Separates active/completed todos
- No props required

## Pages

### Dashboard Page

```typescript
// app/(dashboard)/page.tsx
import { TodoList } from '@/components/features/todos/TodoList';

export const metadata = {
  title: 'My Todos',
};

export default function DashboardPage() {
  return (
    <div>
      <h1>My Todos</h1>
      <TodoList />
    </div>
  );
}
```

### Dashboard Layout

```typescript
// app/(dashboard)/layout.tsx
// Server Component with header and logout
// No props needed - wraps all dashboard pages
```

## Common Patterns

### Creating a Todo

```typescript
const { createTodo } = useTodos();

const handleCreate = async () => {
  const newTodo = await createTodo({
    title: "Buy milk",
    description: "2% milk from store",
  });

  if (newTodo) {
    console.log("Created:", newTodo.id);
  }
};
```

### Updating a Todo

```typescript
const { updateTodo } = useTodos();

const handleUpdate = async (id: string) => {
  const updatedTodo = await updateTodo(id, {
    title: "Buy organic milk",
  });

  if (updatedTodo) {
    console.log("Updated:", updatedTodo.id);
  }
};
```

### Deleting a Todo

```typescript
const { deleteTodo } = useTodos();

const handleDelete = async (id: string) => {
  // Shows confirmation dialog automatically
  const success = await deleteTodo(id);

  if (success) {
    console.log("Deleted successfully");
  }
};
```

### Toggling Completion

```typescript
const { toggleComplete } = useTodos();

const handleToggle = async (id: string) => {
  const updatedTodo = await toggleComplete(id);

  if (updatedTodo) {
    console.log("Toggled to:", updatedTodo.completed);
  }
};
```

### Filtering Todos

```typescript
const { todos } = useTodos();

// Active todos only
const activeTodos = todos.filter(todo => !todo.completed);

// Completed todos only
const completedTodos = todos.filter(todo => todo.completed);

// Sort by date (newest first)
const sortedTodos = [...todos].sort((a, b) =>
  new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
);
```

## Styling Utilities

### Using cn() for class merging

```typescript
import { cn } from '@/lib/utils';

<div className={cn(
  'base-class',
  condition && 'conditional-class',
  'override-class'
)}>
  Content
</div>
```

## Accessibility

All components include:
- ARIA labels and attributes
- Keyboard navigation support
- Focus management
- Screen reader text
- Semantic HTML
- Minimum touch targets (44x44px)

## Responsive Design

Mobile-first breakpoints:
- `sm`: 640px (mobile landscape)
- `md`: 768px (tablet)
- `lg`: 1024px (desktop)
- `xl`: 1280px (large desktop)

Example:
```typescript
<div className="px-4 sm:px-6 lg:px-8">
  // Responsive padding
</div>
```

## Error Handling

All API calls handle errors automatically:
- Network errors show "Network error" message
- API errors show user-friendly messages
- Optimistic updates rollback on error
- Error states display with retry options

## Performance

- Optimistic updates for instant feedback
- Minimal re-renders with proper memo
- Auto-fetch only on mount
- No polling (use WebSocket for real-time if needed)

## Best Practices

1. Always use the `useTodos` hook for state management
2. Let the hook handle optimistic updates
3. Use TypeScript types for all props and state
4. Follow existing component patterns
5. Test on mobile devices (320px width minimum)
6. Ensure keyboard navigation works
7. Check color contrast for accessibility
