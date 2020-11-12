import asyncio
from typing import Any
import aiohttp
import aiothrottle


class Limiter:
    def __init__(self, limit) -> None:
        self.limit = limit
    

    async def load_file(self, url, output_path) -> Any:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                with open(output_path, 'wb') as f:
                    f.write(await response.read())


    def __call__(self, url, output_path) -> Any:
        aiothrottle.limit_rate(self.limit * 1024)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.load_file(url, output_path))

        aiothrottle.unlimit_rate()

