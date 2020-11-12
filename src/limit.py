# from typing import Any
# import aiothrottle
# import aiohttp
# import asyncio
# import tempfile
# import sys


# class Limiter:

#     def __init__(self, limit) -> None:
#         self.limit = limit

#     async def load_file(self, url, download_type) -> Any:
#         async with aiohttp.ClientSession() as session:
#             async with session.get(url) as response:
#                 path = f'{tempfile.gettempdir()}\\Setup{download_type}'
#                 with open(path, 'wb') as f:
#                     dl = 0
#                     full_length = response.content_length
#                     async for chunk in response.content.iter_chunked(7000):
#                         f.write(chunk)
#                         dl += len(chunk)
#                         complete = int(20 * dl / full_length)
#                         fill_c, unfill_c = '#' * \
#                             complete, ' ' * (20 - complete)
#                         sys.stdout.write(
#                             f"\r[{fill_c}{unfill_c}] ⚡ {round(dl / full_length * 100, 1)} % ⚡ {round(dl / 1000000, 1)} / {round(full_length / 1000000, 1)} MB")
#                         sys.stdout.flush()
#         return path

#     def __call__(self, url, download_type) -> Any:

#         aiothrottle.limit_rate(self.limit) #1 sec

#         loop = asyncio.get_event_loop()
#         path = loop.run_until_complete(self.load_file(url, download_type))

#         return path


from typing import Any
import aiothrottle
import aiohttp
import asyncio
import tempfile
from timeit import default_timer as timer


class Limiter:

    def __init__(self, limit) -> None:
        self.limit = limit

    async def load_file(self, url, download_type) -> Any:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                path = f'{tempfile.gettempdir()}\\Setup{download_type}'
                with open(path, 'wb') as f:
                    f.write(await response.read())

        return path

    def __call__(self, url, download_type) -> Any:
        start = timer()
        aiothrottle.limit_rate(self.limit)

        loop = asyncio.get_event_loop()
        path = loop.run_until_complete(self.load_file(url, download_type))
        end = timer()
        print(end - start)
        aiothrottle.unlimit_rate()

        return path
