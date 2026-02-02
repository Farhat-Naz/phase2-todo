"use client";

/**
 * PriorityFilter Component
 *
 * Allows users to filter todos by priority level.
 * Features:
 * - Tab-based UI for "All Tasks" and "High Priority"
 * - Active state styling
 * - Keyboard accessible
 * - Responsive design
 *
 * Follows UI Skill patterns for accessible tab navigation.
 */

export type FilterType = "all" | "high";

interface PriorityFilterProps {
  currentFilter: FilterType;
  onFilterChange: (filter: FilterType) => void;
  highPriorityCount?: number;
}

export function PriorityFilter({
  currentFilter,
  onFilterChange,
  highPriorityCount = 0,
}: PriorityFilterProps) {
  return (
    <div
      role="tablist"
      aria-label="Filter todos by priority"
      className="inline-flex rounded-lg bg-gray-100 dark:bg-gray-800 p-1 gap-1"
    >
      {/* All Tasks Tab */}
      <button
        role="tab"
        aria-selected={currentFilter === "all"}
        aria-controls="todo-list"
        onClick={() => onFilterChange("all")}
        className={`
          px-4 py-2 rounded-md text-sm font-medium
          transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
          ${
            currentFilter === "all"
              ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm"
              : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
          }
        `}
      >
        All Tasks
      </button>

      {/* High Priority Tab */}
      <button
        role="tab"
        aria-selected={currentFilter === "high"}
        aria-controls="todo-list"
        onClick={() => onFilterChange("high")}
        className={`
          px-4 py-2 rounded-md text-sm font-medium
          transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
          inline-flex items-center gap-2
          ${
            currentFilter === "high"
              ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm"
              : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
          }
        `}
      >
        High Priority
        {highPriorityCount > 0 && (
          <span
            className={`
              inline-flex items-center justify-center
              min-w-[20px] h-5 px-1.5 rounded-full text-xs font-medium
              ${
                currentFilter === "high"
                  ? "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400"
                  : "bg-red-50 text-red-600 dark:bg-red-900/10 dark:text-red-500"
              }
            `}
          >
            {highPriorityCount}
          </span>
        )}
      </button>
    </div>
  );
}
