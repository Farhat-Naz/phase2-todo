/**
 * Todo type definitions
 * Follows TypeScript strict mode with no 'any' types
 */

/**
 * Priority level for todos
 * "high" = urgent tasks that need immediate attention
 * "normal" = regular tasks (default)
 */
export type PriorityLevel = "high" | "normal";

/**
 * Complete Todo entity from the backend API
 */
export interface Todo {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  priority: PriorityLevel;
  created_at: string;
  updated_at: string;
}

/**
 * Todo creation payload
 * All fields except title are optional
 */
export interface TodoCreate {
  title: string;
  description?: string;
  completed?: boolean;
  priority?: PriorityLevel;
}

/**
 * Todo update payload
 * All fields are optional for partial updates
 */
export interface TodoUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
  priority?: PriorityLevel;
}

/**
 * Todo list response from API
 * Backend returns array of todos
 */
export type TodoListResponse = Todo[];
