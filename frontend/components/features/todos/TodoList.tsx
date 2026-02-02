'use client';

/**
 * TodoList Component - Main todo management interface
 *
 * Features:
 * - VoiceInput for voice commands (create/complete todos)
 * - TodoForm for creating new todos
 * - TodoItem for each todo
 * - Priority filtering with URL persistence
 * - Loading state with spinner
 * - Error state with retry button
 * - Empty state with helpful message
 * - Separates completed/incomplete todos
 * - Reverse chronological order (newest first)
 * - Responsive grid/list layout
 * - Multi-language support (English/Urdu)
 */

import { useEffect } from 'react';
import { useSearchParams, useRouter, usePathname } from 'next/navigation';
import { useTodos } from '@/hooks/useTodos';
import { TodoForm } from './TodoForm';
import { TodoItem } from './TodoItem';
import { VoiceInput } from './VoiceInput';
import { PriorityFilter, FilterType } from './PriorityFilter';
import { LoadingSpinner } from '@/components/features/shared/LoadingSpinner';
import { Button } from '@/components/ui/Button';
import { TodoCreate } from '@/types/todo';

export function TodoList() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const {
    todos,
    loading,
    error,
    filter,
    setFilter,
    fetchTodos,
    createTodo,
    updateTodo,
    deleteTodo,
    toggleComplete,
    togglePriority,
  } = useTodos();

  /**
   * Initialize filter from URL on mount
   */
  useEffect(() => {
    const priorityParam = searchParams.get('priority');
    if (priorityParam === 'high') {
      setFilter('high');
    } else {
      setFilter(null);
    }
  }, []); // Only run on mount

  /**
   * Handle todo creation
   */
  const handleCreateTodo = async (data: TodoCreate) => {
    await createTodo(data);
  };

  /**
   * Handle filter change and update URL
   */
  const handleFilterChange = (newFilter: FilterType) => {
    const newFilterValue = newFilter === 'all' ? null : newFilter;
    setFilter(newFilterValue);

    // Update URL query parameters
    const params = new URLSearchParams(searchParams.toString());
    if (newFilterValue === 'high') {
      params.set('priority', 'high');
    } else {
      params.delete('priority');
    }

    const newUrl = `${pathname}${params.toString() ? `?${params.toString()}` : ''}`;
    router.push(newUrl, { scroll: false });
  };

  /**
   * Separate completed and incomplete todos
   * Note: When filter is active, API already returns filtered results
   */
  const incompleteTodos = todos
    .filter(todo => !todo.completed)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  const completedTodos = todos
    .filter(todo => todo.completed)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  /**
   * Count high priority incomplete todos (for all todos, not just filtered)
   */
  const highPriorityCount = incompleteTodos.filter(todo => todo.priority === 'high').length;

  /**
   * Loading state
   */
  if (loading && todos.length === 0) {
    return (
      <div className="w-full max-w-3xl mx-auto py-12">
        <LoadingSpinner size="lg" text="Loading your todos..." />
      </div>
    );
  }

  /**
   * Error state
   */
  if (error && todos.length === 0) {
    return (
      <div className="w-full max-w-3xl mx-auto py-12">
        <div className="bg-error-light dark:bg-error-dark/20 border border-error dark:border-error-dark rounded-lg p-6 text-center">
          <svg
            className="mx-auto h-12 w-12 text-error mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <h3 className="text-lg font-semibold text-error dark:text-error-light mb-2">
            Failed to load todos
          </h3>
          <p className="text-sm text-error-dark dark:text-error-light mb-4">
            {error}
          </p>
          <Button onClick={fetchTodos} variant="primary" size="md">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-3xl mx-auto space-y-8">
      {/* Voice input section */}
      <div className="bg-gradient-to-br from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 rounded-xl shadow-md p-6 border border-primary-200 dark:border-primary-800">
        <div className="flex items-center gap-3 mb-4">
          <svg
            className="h-6 w-6 text-primary-600 dark:text-primary-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
            />
          </svg>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Voice Commands
          </h2>
        </div>
        <VoiceInput />
      </div>

      {/* Create new todo form */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Create New Todo
        </h2>
        <TodoForm onSubmit={handleCreateTodo} />
      </div>

      {/* Priority filter */}
      {todos.length > 0 && (
        <div className="flex justify-center">
          <PriorityFilter
            currentFilter={filter === null ? 'all' : 'high'}
            onFilterChange={handleFilterChange}
            highPriorityCount={highPriorityCount}
          />
        </div>
      )}

      {/* Error banner (when there are todos but an error occurred) */}
      {error && todos.length > 0 && (
        <div className="bg-error-light dark:bg-error-dark/20 border border-error dark:border-error-dark rounded-lg p-4">
          <p className="text-sm text-error-dark dark:text-error-light">
            {error}
          </p>
        </div>
      )}

      {/* Empty state - No todos at all */}
      {todos.length === 0 && !loading && !error && !filter && (
        <div className="bg-gray-50 dark:bg-gray-800 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-600 p-12 text-center">
          <svg
            className="mx-auto h-16 w-16 text-gray-400 dark:text-gray-500 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
            />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            No todos yet
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Create your first task to get started!
          </p>
        </div>
      )}

      {/* Empty state - No high priority todos */}
      {todos.length === 0 && !loading && !error && filter === 'high' && (
        <div className="bg-gray-50 dark:bg-gray-800 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-600 p-12 text-center">
          <svg
            className="mx-auto h-16 w-16 text-gray-400 dark:text-gray-500 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
            />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            No high priority tasks
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            All your high priority tasks are complete, or you haven't marked any tasks as high priority yet.
          </p>
          <Button
            onClick={() => handleFilterChange('all')}
            variant="ghost"
            size="md"
            className="mt-4"
          >
            View All Tasks
          </Button>
        </div>
      )}

      {/* Incomplete todos section */}
      {incompleteTodos.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Active Tasks
            </h2>
            <div className="flex items-center gap-2">
              {highPriorityCount > 0 && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400">
                  {highPriorityCount} urgent {highPriorityCount === 1 ? 'task' : 'tasks'}
                </span>
              )}
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200">
                {incompleteTodos.length}
              </span>
            </div>
          </div>

          <div className="space-y-3">
            {incompleteTodos.map((todo) => (
              <TodoItem
                key={todo.id}
                todo={todo}
                onToggle={toggleComplete}
                onUpdate={updateTodo}
                onDelete={deleteTodo}
                onTogglePriority={togglePriority}
              />
            ))}
          </div>
        </div>
      )}

      {/* Completed todos section */}
      {completedTodos.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Completed Tasks
            </h2>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-light text-success-dark dark:bg-success-dark dark:text-success-light">
              {completedTodos.length}
            </span>
          </div>

          <div className="space-y-3">
            {completedTodos.map((todo) => (
              <TodoItem
                key={todo.id}
                todo={todo}
                onToggle={toggleComplete}
                onUpdate={updateTodo}
                onDelete={deleteTodo}
                onTogglePriority={togglePriority}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
