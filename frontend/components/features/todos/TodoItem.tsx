'use client';

/**
 * TodoItem Component - Individual todo display and editing
 *
 * Features:
 * - Checkbox for completion toggle
 * - Inline editing mode
 * - Delete with confirmation
 * - Completed state styling (strikethrough, faded)
 * - Accessible keyboard navigation
 * - Mobile-responsive touch targets (44x44px minimum)
 * - Timestamps display
 */

import { useState } from 'react';
import { Checkbox } from '@/components/ui/Checkbox';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Todo, TodoUpdate, PriorityLevel } from '@/types/todo';
import { cn } from '@/lib/utils';
import { PriorityToggle } from './PriorityToggle';
import { PriorityBadge } from './PriorityBadge';

interface TodoItemProps {
  todo: Todo;
  onToggle: (id: string) => Promise<void>;
  onUpdate: (id: string, data: TodoUpdate) => Promise<Todo | null>;
  onDelete: (id: string) => Promise<boolean>;
  onTogglePriority: (id: string, newPriority: PriorityLevel) => Promise<void>;
}

export function TodoItem({ todo, onToggle, onUpdate, onDelete, onTogglePriority }: TodoItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(todo.title);
  const [editDescription, setEditDescription] = useState(todo.description || '');
  const [isUpdating, setIsUpdating] = useState(false);

  /**
   * Handle save button click
   */
  const handleSave = async () => {
    if (!editTitle.trim()) {
      return;
    }

    setIsUpdating(true);

    try {
      await onUpdate(todo.id, {
        title: editTitle.trim(),
        description: editDescription.trim() || undefined,
      });
      setIsEditing(false);
    } catch (error) {
      // Error is handled by parent
      console.error('Failed to update todo:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  /**
   * Handle cancel button click
   */
  const handleCancel = () => {
    setEditTitle(todo.title);
    setEditDescription(todo.description || '');
    setIsEditing(false);
  };

  /**
   * Handle delete button click
   */
  const handleDelete = async () => {
    await onDelete(todo.id);
  };

  /**
   * Handle checkbox toggle
   */
  const handleToggle = async () => {
    await onToggle(todo.id);
  };

  /**
   * Format timestamp for display
   */
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    // Less than a minute
    if (diffInSeconds < 60) {
      return 'just now';
    }

    // Less than an hour
    if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `${minutes} ${minutes === 1 ? 'minute' : 'minutes'} ago`;
    }

    // Less than a day
    if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`;
    }

    // More than a day
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
  };

  return (
    <Card
      padding="md"
      className={cn(
        'transition-all duration-200 hover:shadow-md',
        todo.completed && 'opacity-60'
      )}
    >
      {isEditing ? (
        // Edit mode
        <div className="space-y-4">
          <Input
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            placeholder="Todo title"
            maxLength={500}
            disabled={isUpdating}
            aria-label="Edit todo title"
          />

          <Textarea
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
            placeholder="Description (optional)"
            maxLength={2000}
            rows={3}
            disabled={isUpdating}
            aria-label="Edit todo description"
          />

          <div className="flex gap-2">
            <Button
              onClick={handleSave}
              variant="primary"
              size="sm"
              isLoading={isUpdating}
              disabled={isUpdating || !editTitle.trim()}
            >
              Save
            </Button>
            <Button
              onClick={handleCancel}
              variant="ghost"
              size="sm"
              disabled={isUpdating}
            >
              Cancel
            </Button>
          </div>
        </div>
      ) : (
        // Display mode
        <div className="space-y-3">
          {/* Checkbox, priority toggle, and title */}
          <div className="flex items-start gap-3">
            <div className="flex items-center gap-2 pt-0.5">
              <Checkbox
                checked={todo.completed}
                onChange={handleToggle}
                aria-label={`Mark "${todo.title}" as ${todo.completed ? 'incomplete' : 'complete'}`}
                className="min-w-[20px] min-h-[20px]"
              />
              <PriorityToggle
                todoId={todo.id}
                currentPriority={todo.priority}
                onToggle={onTogglePriority}
                disabled={isUpdating}
              />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h3
                  className={cn(
                    'text-base font-medium break-words',
                    todo.completed
                      ? 'line-through text-gray-400 dark:text-gray-500'
                      : 'text-gray-900 dark:text-gray-100'
                  )}
                >
                  {todo.title}
                </h3>
                <PriorityBadge priority={todo.priority} />
              </div>

              {todo.description && (
                <p
                  className={cn(
                    'mt-1.5 text-sm break-words whitespace-pre-wrap',
                    todo.completed
                      ? 'text-gray-400 dark:text-gray-500'
                      : 'text-gray-600 dark:text-gray-400'
                  )}
                >
                  {todo.description}
                </p>
              )}
            </div>
          </div>

          {/* Timestamp and actions */}
          <div className="flex items-center justify-between gap-3 pl-8">
            <time
              className="text-xs text-gray-500 dark:text-gray-400"
              dateTime={todo.created_at}
              title={new Date(todo.created_at).toLocaleString()}
            >
              {formatDate(todo.created_at)}
            </time>

            <div className="flex gap-2">
              <Button
                onClick={() => setIsEditing(true)}
                variant="ghost"
                size="sm"
                className="min-w-[44px] min-h-[44px]"
                aria-label="Edit todo"
              >
                Edit
              </Button>
              <Button
                onClick={handleDelete}
                variant="ghost"
                size="sm"
                className="text-error hover:text-error-dark min-w-[44px] min-h-[44px]"
                aria-label="Delete todo"
              >
                Delete
              </Button>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
