from typing import List

from aiolimiter import AsyncLimiter


class ThrottlerEnsemble:
    throttlers: List[AsyncLimiter]

    def __init__(self, throttlers: List[AsyncLimiter]):
        self.throttlers = throttlers

    async def wait(self):
        for throttler in self.throttlers:
            await throttler.acquire()

    def has_capacity(self) -> bool:
        for throttler in self.throttlers:
            if not throttler.has_capacity(1):
                return False

        return True
