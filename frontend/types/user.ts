/**
 * User entity interface matching backend schema
 */
export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  updated_at: string;
}

/**
 * User registration request payload
 */
export interface UserRegister {
  email: string;
  password: string;
  name: string;
}

/**
 * User login request payload
 */
export interface UserLogin {
  email: string;
  password: string;
}

/**
 * Authentication token response from backend
 */
export interface AuthToken {
  access_token: string;
  token_type: string;
  user: User;
}

/**
 * Current user session state
 */
export interface UserSession {
  user: User;
  accessToken: string;
  expiresAt: number;
}
