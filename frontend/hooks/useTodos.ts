'use client';

/**
 * useTodos Hook - Complete Todo CRUD operations with optimistic updates
 * Follows patterns from API skill and UI skill
 *
 * Features:
 * - Auto-fetch todos on mount
 * - Optimistic UI updates for all mutations
 * - Error handling with rollback on failure
 * - Confirmation dialog before delete
 * - Type-safe return values
 */

import { useEffect, useState, useCallback } from 'react';
import { api, handleError } from '@/lib/api';
import { Todo, TodoCreate, TodoUpdate, TodoListResponse, PriorityLevel } from '@/types/todo';

/**
 * Filter type for priority filtering
 */
export type PriorityFilter = PriorityLevel | null;

/**
 * Hook return type with all todo operations
 */
interface UseTodosReturn {
  todos: Todo[];
  loading: boolean;
  error: string | null;
  filter: PriorityFilter;
  setFilter: (filter: PriorityFilter) => void;
  fetchTodos: () => Promise<void>;
  createTodo: (data: TodoCreate) => Promise<Todo | null>;
  updateTodo: (id: string, data: TodoUpdate) => Promise<Todo | null>;
  deleteTodo: (id: string) => Promise<boolean>;
  toggleComplete: (id: string) => Promise<void>;
  togglePriority: (id: string, newPriority: PriorityLevel) => Promise<void>;
}

/**
 * Main hook for managing todo state and operations
 */
export function useTodos(): UseTodosReturn {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<PriorityFilter>(null);

  /**
   * Fetch all todos from the API with optional priority filter
   */
  const fetchTodos = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Build query parameters based on filter
      const queryParams = filter ? `?priority=${filter}` : '';
      const data = await api.get<TodoListResponse>(`/api/todos${queryParams}`);
      setTodos(data);
    } catch (err) {
      const errorMessage = handleError(err);
      setError(errorMessage);
      console.error('Failed to fetch todos:', err);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  /**
   * Create a new todo with optimistic update
   */
  const createTodo = useCallback(async (data: TodoCreate): Promise<Todo | null> => {
    setError(null);

    // Optimistic update: Add temporary todo to state
    const tempId = `temp-${Date.now()}`;
    const optimisticTodo: Todo = {
      id: tempId,
      user_id: '', // Will be set by backend
      title: data.title,
      description: data.description || null,
      completed: data.completed || false,
      priority: data.priority || 'normal',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    setTodos(prev => [optimisticTodo, ...prev]);

    try {
      // Make API request
      const newTodo = await api.post<Todo>('/api/todos', data);

      // Replace optimistic todo with real todo from server
      setTodos(prev =>
        prev.map(todo => (todo.id === tempId ? newTodo : todo))
      );

      return newTodo;
    } catch (err) {
      // Rollback: Remove optimistic todo on error
      setTodos(prev => prev.filter(todo => todo.id !== tempId));

      const errorMessage = handleError(err);
      setError(errorMessage);
      console.error('Failed to create todo:', err);
      return null;
    }
  }, []);

  /**
   * Update an existing todo with optimistic update
   */
  const updateTodo = useCallback(async (
    id: string,
    data: TodoUpdate
  ): Promise<Todo | null> => {
    setError(null);

    // Store original todo for rollback
    const originalTodo = todos.find(todo => todo.id === id);
    if (!originalTodo) {
      setError('Todo not found');
      return null;
    }

    // Optimistic update: Update todo in state
    const optimisticTodo: Todo = {
      ...originalTodo,
      ...data,
      updated_at: new Date().toISOString(),
    };

    setTodos(prev =>
      prev.map(todo => (todo.id === id ? optimisticTodo : todo))
    );

    try {
      // Make API request
      const updatedTodo = await api.patch<Todo>(`/api/todos/${id}`, data);

      // Update with server response
      setTodos(prev =>
        prev.map(todo => (todo.id === id ? updatedTodo : todo))
      );

      return updatedTodo;
    } catch (err) {
      // Rollback: Restore original todo on error
      setTodos(prev =>
        prev.map(todo => (todo.id === id ? originalTodo : todo))
      );

      const errorMessage = handleError(err);
      setError(errorMessage);
      console.error('Failed to update todo:', err);
      return null;
    }
  }, [todos]);

  /**
   * Delete a todo with confirmation and optimistic update
   */
  const deleteTodo = useCallback(async (id: string): Promise<boolean> => {
    setError(null);

    // Find todo to delete
    const todoToDelete = todos.find(todo => todo.id === id);
    if (!todoToDelete) {
      setError('Todo not found');
      return false;
    }

    // Confirmation dialog
    const confirmed = window.confirm(
      `Are you sure you want to delete "${todoToDelete.title}"?`
    );

    if (!confirmed) {
      return false;
    }

    // Optimistic update: Remove todo from state
    setTodos(prev => prev.filter(todo => todo.id !== id));

    try {
      // Make API request
      await api.delete(`/api/todos/${id}`);
      return true;
    } catch (err) {
      // Rollback: Restore deleted todo on error
      setTodos(prev => {
        // Insert todo back in original position
        const index = prev.findIndex(todo =>
          new Date(todo.created_at) < new Date(todoToDelete.created_at)
        );

        if (index === -1) {
          return [...prev, todoToDelete];
        }

        return [
          ...prev.slice(0, index),
          todoToDelete,
          ...prev.slice(index),
        ];
      });

      const errorMessage = handleError(err);
      setError(errorMessage);
      console.error('Failed to delete todo:', err);
      return false;
    }
  }, [todos]);

  /**
   * Toggle todo completion status
   * Convenience method for common operation
   */
  const toggleComplete = useCallback(async (id: string): Promise<void> => {
    const todo = todos.find(t => t.id === id);
    if (!todo) {
      setError('Todo not found');
      return;
    }

    await updateTodo(id, { completed: !todo.completed });
  }, [todos, updateTodo]);

  /**
   * Toggle todo priority
   * Updates priority and throws error on failure for PriorityToggle component
   */
  const togglePriority = useCallback(async (id: string, newPriority: PriorityLevel): Promise<void> => {
    const result = await updateTodo(id, { priority: newPriority });

    if (!result) {
      // updateTodo failed - throw error to trigger rollback in PriorityToggle
      throw new Error('Failed to update priority');
    }
  }, [updateTodo]);

  /**
   * Auto-fetch todos on component mount
   */
  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  return {
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
  };
}
