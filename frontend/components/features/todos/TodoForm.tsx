'use client';

/**
 * TodoForm Component - Create new todos
 *
 * Features:
 * - Controlled form with validation
 * - Title required, max 500 chars
 * - Description optional, max 2000 chars
 * - Keyboard shortcuts: Enter to submit, Shift+Enter for newline
 * - Auto-clear on successful creation
 * - Mobile-responsive with accessible form controls
 */

import { useState, FormEvent, KeyboardEvent } from 'react';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Button } from '@/components/ui/Button';
import { TodoCreate } from '@/types/todo';

interface TodoFormProps {
  onSubmit: (data: TodoCreate) => Promise<void>;
  initialData?: TodoCreate;
  loading?: boolean;
}

export function TodoForm({ onSubmit, initialData, loading = false }: TodoFormProps) {
  const [title, setTitle] = useState(initialData?.title || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [errors, setErrors] = useState<{ title?: string; description?: string }>({});

  /**
   * Validate form fields
   */
  const validate = (): boolean => {
    const newErrors: { title?: string; description?: string } = {};

    // Title validation
    if (!title.trim()) {
      newErrors.title = 'Title is required';
    } else if (title.length > 500) {
      newErrors.title = 'Title must be 500 characters or less';
    }

    // Description validation
    if (description && description.length > 2000) {
      newErrors.description = 'Description must be 2000 characters or less';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    const todoData: TodoCreate = {
      title: title.trim(),
      ...(description.trim() && { description: description.trim() }),
    };

    try {
      await onSubmit(todoData);

      // Clear form on success
      if (!initialData) {
        setTitle('');
        setDescription('');
        setErrors({});
      }
    } catch (error) {
      // Error is handled by parent component
      console.error('Form submission error:', error);
    }
  };

  /**
   * Handle keyboard shortcuts
   * Enter: Submit form (only in title input)
   * Shift+Enter: Newline in description
   */
  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as FormEvent);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Title"
        id="todo-title"
        type="text"
        value={title}
        onChange={(e) => {
          setTitle(e.target.value);
          if (errors.title) {
            setErrors(prev => ({ ...prev, title: undefined }));
          }
        }}
        onKeyDown={handleKeyDown}
        placeholder="What needs to be done?"
        error={errors.title}
        maxLength={500}
        disabled={loading}
        required
        aria-label="Todo title"
        aria-required="true"
        aria-invalid={!!errors.title}
      />

      <div className="relative">
        <Textarea
          label="Description (optional)"
          id="todo-description"
          value={description}
          onChange={(e) => {
            setDescription(e.target.value);
            if (errors.description) {
              setErrors(prev => ({ ...prev, description: undefined }));
            }
          }}
          placeholder="Add more details..."
          error={errors.description}
          maxLength={2000}
          disabled={loading}
          rows={3}
          aria-label="Todo description"
          aria-invalid={!!errors.description}
        />
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          {description.length}/2000 characters
        </p>
      </div>

      <div className="flex gap-3">
        <Button
          type="submit"
          variant="primary"
          size="md"
          isLoading={loading}
          disabled={loading || !title.trim()}
          className="flex-1 sm:flex-none sm:min-w-[120px]"
        >
          {initialData ? 'Update Todo' : 'Add Todo'}
        </Button>

        {!initialData && title && (
          <Button
            type="button"
            variant="ghost"
            size="md"
            onClick={() => {
              setTitle('');
              setDescription('');
              setErrors({});
            }}
            disabled={loading}
          >
            Clear
          </Button>
        )}
      </div>

      <p className="text-xs text-gray-500 dark:text-gray-400">
        Press Enter to submit
      </p>
    </form>
  );
}
