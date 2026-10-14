import time
from typing import Tuple

from redis import Redis


class TokenBucketLimiter:
    def __init__(
        self,
        redis_client: Redis,
        capacity: int,
        window_seconds: int,
    ):
        self.redis = redis_client
        self.capacity = capacity
        self.window_seconds = window_seconds
        self.refill_rate = capacity / window_seconds

    def check(self, client_id: str) -> Tuple[bool, float, float]:
        key = f"rate_limit:{client_id}"

        current_time = time.time()

        data = self.redis.hgetall(key)

        if data:
            tokens = float(data.get(b"tokens", self.capacity))
            last_refill = float(data.get(b"last_refill", current_time))
        else:
            tokens = float(self.capacity)
            last_refill = current_time

        elapsed = current_time - last_refill

        tokens = min(
            self.capacity,
            tokens + elapsed * self.refill_rate,
        )

        if tokens >= 1:
            tokens -= 1
            allowed = True
            retry_after = 0.0
        else:
            allowed = False
            retry_after = (1 - tokens) / self.refill_rate

        self.redis.hset(
            key,
            mapping={
                "tokens": tokens,
                "last_refill": current_time,
            },
        )

        self.redis.expire(
            key,
            self.window_seconds * 2,
        )

        return allowed, tokens, retry_after