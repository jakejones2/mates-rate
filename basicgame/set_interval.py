import asyncio
from contextlib import suppress


class setIntervalAsync:
    """
    Object of this class periodically execute a given function
    in a new asyncio task. Should not be blocking.
    """

    def __init__(self, func, progress, period=2, limit=30):
        self.func = func
        self.period = period
        self.has_started = False
        self._task = None
        self.max_broadcasts = limit
        self.current_broadcasts = 0
        self.progress = progress

    async def start(self):
        """
        Use this method to start the interval.
        """
        if not self.has_started:
            self.has_started = True
            self._task = asyncio.create_task(self._run())

    async def stop(self):
        """
        Use this method to stop the interval.
        """
        if self.has_started:
            self.has_started = False
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run(self):
        while True:
            self.current_broadcasts += 1
            if self.current_broadcasts > self.max_broadcasts:
                await self.stop()
                break
            await self.func()
            await asyncio.sleep(self.period)
