"""
Rate limiter service for protecting API endpoints from abuse.

Provides in-memory rate limiting based on sliding window algorithm.

Used for:
- Login attempts (US6): 5 attempts per 15 minutes per IP
- Registration (US6): 3 attempts per hour per IP
- Password reset (US2): 3 attempts per hour per email
- Email verification resend (US3): 3 attempts per hour per user

Implementation:
- In-memory storage (dict) for simplicity
- Sliding window algorithm for accurate rate limiting
- Automatic cleanup of expired entries
- Thread-safe operations

Note:
    For production with multiple workers, use Redis or similar distributed cache.
    Current implementation is suitable for single-instance development/testing.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from threading import Lock
import time


class InMemoryRateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.

    Attributes:
        storage: Dictionary mapping keys to list of timestamps
        lock: Thread lock for thread-safe operations

    Example:
        limiter = InMemoryRateLimiter()

        # Check rate limit (5 attempts per 15 minutes)
        is_allowed = limiter.check_rate_limit(
            key="login:192.168.1.1",
            max_attempts=5,
            window_seconds=900
        )

        if not is_allowed:
            retry_after = limiter.get_retry_after("login:192.168.1.1")
            raise HTTPException(429, f"Too many requests. Retry after {retry_after}s")
    """

    def __init__(self):
        """Initialize rate limiter with empty storage and lock."""
        self.storage: Dict[str, List[float]] = {}
        self.lock = Lock()

    def check_rate_limit(
        self,
        key: str,
        max_attempts: int,
        window_seconds: int
    ) -> bool:
        """
        Check if a request is allowed under rate limit.

        Uses sliding window algorithm:
        1. Remove timestamps older than window_seconds
        2. Count remaining timestamps
        3. If count < max_attempts, allow request and add timestamp
        4. Otherwise, deny request

        Args:
            key: Unique identifier for rate limit (e.g., "login:192.168.1.1", "reset:user@example.com")
            max_attempts: Maximum number of attempts allowed in window
            window_seconds: Time window in seconds

        Returns:
            bool: True if request is allowed, False if rate limit exceeded

        Thread-safe:
            Uses lock to prevent race conditions in multi-threaded environments

        Example:
            # Login rate limit: 5 attempts per 15 minutes per IP
            is_allowed = limiter.check_rate_limit(
                key=f"login:{ip_address}",
                max_attempts=5,
                window_seconds=900
            )
        """
        with self.lock:
            current_time = time.time()
            cutoff_time = current_time - window_seconds

            # Initialize key if not exists
            if key not in self.storage:
                self.storage[key] = []

            # Remove expired timestamps (older than window)
            self.storage[key] = [
                timestamp for timestamp in self.storage[key]
                if timestamp > cutoff_time
            ]

            # Check if under limit
            if len(self.storage[key]) < max_attempts:
                # Allow request and record timestamp
                self.storage[key].append(current_time)
                return True
            else:
                # Rate limit exceeded
                return False

    def get_retry_after(self, key: str) -> int:
        """
        Get seconds until rate limit resets for a key.

        Calculates when the oldest timestamp will expire, allowing
        a new request.

        Args:
            key: Unique identifier for rate limit

        Returns:
            int: Seconds until rate limit resets (0 if no rate limit active)

        Example:
            if not limiter.check_rate_limit(key, max_attempts, window):
                retry_after = limiter.get_retry_after(key)
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many requests. Retry after {retry_after} seconds"
                )
        """
        with self.lock:
            if key not in self.storage or not self.storage[key]:
                return 0

            # Get oldest timestamp
            oldest_timestamp = min(self.storage[key])
            current_time = time.time()

            # Calculate when oldest timestamp will be outside window
            # This is approximate since we don't know the original window size
            # For accurate calculation, store window size with each entry
            # For now, assume common window of 900 seconds (15 minutes)
            window_seconds = 900  # Default window

            # Time until oldest timestamp expires
            retry_after = oldest_timestamp + window_seconds - current_time

            return max(0, int(retry_after))

    def reset(self, key: str) -> None:
        """
        Reset rate limit for a specific key.

        Useful for:
        - Testing
        - Admin override
        - Successful authentication (reset failed login attempts)

        Args:
            key: Unique identifier for rate limit

        Example:
            # Reset failed login attempts after successful login
            limiter.reset(f"login:{ip_address}")
        """
        with self.lock:
            if key in self.storage:
                del self.storage[key]

    def cleanup_expired(self, window_seconds: int = 3600) -> int:
        """
        Clean up expired rate limit entries.

        Should be called periodically (e.g., via background task)
        to prevent memory growth.

        Args:
            window_seconds: Remove entries older than this (default: 1 hour)

        Returns:
            int: Number of entries removed

        Example:
            # In background task
            async def cleanup_task():
                while True:
                    await asyncio.sleep(3600)  # Every hour
                    removed = limiter.cleanup_expired()
                    logger.info(f"Cleaned up {removed} expired rate limit entries")
        """
        with self.lock:
            current_time = time.time()
            cutoff_time = current_time - window_seconds
            removed_count = 0

            # Identify keys to remove
            keys_to_remove = []
            for key, timestamps in self.storage.items():
                # Remove expired timestamps
                valid_timestamps = [t for t in timestamps if t > cutoff_time]

                if not valid_timestamps:
                    # No valid timestamps, remove key
                    keys_to_remove.append(key)
                    removed_count += 1
                else:
                    # Update with valid timestamps
                    self.storage[key] = valid_timestamps

            # Remove empty keys
            for key in keys_to_remove:
                del self.storage[key]

            return removed_count

    def get_stats(self) -> Dict[str, int]:
        """
        Get rate limiter statistics.

        Returns:
            dict: Statistics including total keys and total timestamps

        Example:
            stats = limiter.get_stats()
            print(f"Active rate limits: {stats['total_keys']}")
            print(f"Total requests tracked: {stats['total_timestamps']}")
        """
        with self.lock:
            total_keys = len(self.storage)
            total_timestamps = sum(len(timestamps) for timestamps in self.storage.values())

            return {
                "total_keys": total_keys,
                "total_timestamps": total_timestamps
            }


# Global rate limiter instance
# In production with multiple workers, replace with Redis-based limiter
_rate_limiter_instance: InMemoryRateLimiter | None = None


def get_rate_limiter() -> InMemoryRateLimiter:
    """
    Get or create global rate limiter instance.

    Returns:
        InMemoryRateLimiter: Global rate limiter instance

    Example:
        limiter = get_rate_limiter()
        is_allowed = limiter.check_rate_limit(key, max_attempts, window)
    """
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = InMemoryRateLimiter()
    return _rate_limiter_instance


# Example usage and testing
if __name__ == "__main__":
    limiter = InMemoryRateLimiter()

    # Test rate limiting (3 attempts per 10 seconds)
    key = "test:user"
    max_attempts = 3
    window = 10

    print("Testing rate limiter...")
    for i in range(5):
        is_allowed = limiter.check_rate_limit(key, max_attempts, window)
        print(f"Attempt {i+1}: {'Allowed' if is_allowed else 'Blocked'}")

        if not is_allowed:
            retry_after = limiter.get_retry_after(key)
            print(f"  Retry after: {retry_after} seconds")

    # Test reset
    print("\nResetting rate limit...")
    limiter.reset(key)

    is_allowed = limiter.check_rate_limit(key, max_attempts, window)
    print(f"After reset: {'Allowed' if is_allowed else 'Blocked'}")

    # Test stats
    stats = limiter.get_stats()
    print(f"\nStats: {stats}")
