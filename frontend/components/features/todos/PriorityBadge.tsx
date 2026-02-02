"use client";

/**
 * PriorityBadge Component
 *
 * Visual indicator for high priority todos with full accessibility support.
 * Features:
 * - WCAG AA compliant colors (4.5:1 contrast ratio)
 * - AlertCircle icon with "HIGH" text label
 * - Screen reader support (role="status", aria-label)
 * - RTL layout support for Urdu
 * - Responsive design (320px+)
 *
 * Only displays for high priority todos (returns null for normal priority).
 */

import { AlertCircle } from "lucide-react";
import { PriorityLevel } from "@/types/todo";

interface PriorityBadgeProps {
  priority: PriorityLevel;
  className?: string;
}

export function PriorityBadge({ priority, className = "" }: PriorityBadgeProps) {
  // Only show badge for high priority todos
  if (priority !== "high") {
    return null;
  }

  return (
    <span
      role="status"
      aria-label="High priority"
      className={`
        inline-flex items-center gap-1.5 px-2.5 py-1
        rounded-md text-xs font-medium
        bg-red-50 text-red-700
        dark:bg-red-900/20 dark:text-red-400
        whitespace-nowrap
        ${className}
      `}
      title="High priority task"
    >
      <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" aria-hidden="true" />
      <span>HIGH</span>
    </span>
  );
}
