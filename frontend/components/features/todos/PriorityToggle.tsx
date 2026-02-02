"use client";

/**
 * PriorityToggle Component
 *
 * Allows users to toggle todo priority between "high" and "normal".
 * Features:
 * - Optimistic UI updates with error rollback
 * - Keyboard accessible (Tab navigation, Enter/Space to toggle)
 * - Screen reader announcements
 * - 44x44px minimum touch target for mobile
 * - Loading state during API request
 *
 * Follows UI Skill patterns for accessibility and optimistic updates.
 */

import { useState } from "react";
import { Star } from "lucide-react";
import { PriorityLevel } from "@/types/todo";

interface PriorityToggleProps {
  todoId: string;
  currentPriority: PriorityLevel;
  onToggle: (todoId: string, newPriority: PriorityLevel) => Promise<void>;
  disabled?: boolean;
}

export function PriorityToggle({
  todoId,
  currentPriority,
  onToggle,
  disabled = false,
}: PriorityToggleProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [optimisticPriority, setOptimisticPriority] = useState<PriorityLevel | null>(null);

  const displayPriority = optimisticPriority ?? currentPriority;
  const isHighPriority = displayPriority === "high";

  const handleToggle = async () => {
    if (disabled || isLoading) return;

    const newPriority: PriorityLevel = isHighPriority ? "normal" : "high";

    // Optimistic UI update
    setOptimisticPriority(newPriority);
    setIsLoading(true);

    try {
      await onToggle(todoId, newPriority);

      // Success - clear optimistic state
      setOptimisticPriority(null);

      // Screen reader announcement (via aria-live region)
      const announcement = newPriority === "high"
        ? "Marked as high priority"
        : "Priority removed";
      announceToScreenReader(announcement);
    } catch (error) {
      // Error - rollback optimistic update
      setOptimisticPriority(null);

      // Error announcement
      announceToScreenReader("Failed to update priority. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Support Enter and Space keys for keyboard accessibility
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleToggle();
    }
  };

  return (
    <>
      <button
        type="button"
        onClick={handleToggle}
        onKeyDown={handleKeyDown}
        disabled={disabled || isLoading}
        aria-label={isHighPriority ? "Remove high priority" : "Mark as high priority"}
        aria-pressed={isHighPriority}
        className={`
          relative inline-flex items-center justify-center
          min-w-[44px] min-h-[44px] p-2
          rounded-md transition-all
          focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
          disabled:opacity-50 disabled:cursor-not-allowed
          ${isHighPriority
            ? "text-orange-600 hover:text-orange-700 hover:bg-orange-50"
            : "text-gray-400 hover:text-gray-600 hover:bg-gray-50"
          }
        `}
        title={isHighPriority ? "Remove high priority" : "Mark as high priority"}
      >
        <Star
          className={`w-5 h-5 transition-all ${isHighPriority ? "fill-current" : ""}`}
          aria-hidden="true"
        />

        {/* Loading indicator */}
        {isLoading && (
          <span className="absolute inset-0 flex items-center justify-center bg-white/80 rounded-md">
            <span className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </span>
        )}
      </button>

      {/* Screen reader announcements (aria-live region) */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
        id={`priority-status-${todoId}`}
      />
    </>
  );
}

/**
 * Announce message to screen readers via aria-live region
 */
function announceToScreenReader(message: string) {
  // Find all aria-live regions and update them
  const liveRegions = document.querySelectorAll('[role="status"][aria-live="polite"]');
  liveRegions.forEach((region) => {
    region.textContent = message;

    // Clear after 3 seconds to avoid repetition
    setTimeout(() => {
      region.textContent = "";
    }, 3000);
  });
}
