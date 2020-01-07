# Credit to http://markalansmith.com/2018/03/04/asyncio-rate-limit/

import asyncio
from collections import deque


class AsyncRateLimiter:
    def __init__(self, call_limit, time_bucket=1.0, check_every=0.01, loop=None):
        self.call_limit = call_limit
        self.time_bucket = time_bucket
        self.check_every = check_every
        self.loop = loop or asyncio.get_event_loop()
        self._run_times = deque()

    def _flush(self, now):
        while self._run_times:
            oldest_time = self._run_times.popleft()
            elapsed = now - oldest_time
            if elapsed < self.time_bucket:
                self._run_times.appendleft(oldest_time)
                break

    async def __aenter__(self):
        while True:
            self._flush(self.loop.time())
            if len(self._run_times) < self.call_limit:
                break
            await asyncio.sleep(self.check_every)

        self._run_times.append(self.loop.time())

    async def __aexit__(self, exc_type, exc, tb):
        pass
