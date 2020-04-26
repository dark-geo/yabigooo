import asyncio
import logging
from typing import List

import aiofiles
import aiohttp
import yarl
from aiohttp import DummyCookieJar
from fake_useragent import UserAgent

logging.basicConfig(level=logging.INFO)


class BaseCrawler:
    def __init__(self, urls, out_files):
        self.urls = urls
        self.out_files = out_files
        # Initialize class with fake user agent and choose the best one, random via real world browser usage statistic
        self.headers: dict = {}
        self._update_headers()

    def _update_headers(self):
        ua = UserAgent()
        self.headers = {
            'pragma': 'no-cache',
            'user-agent': ua.random,
        }

    async def fetch(self, client: aiohttp.ClientSession, url: str):
        # encode url as we want requests to be send as encoded strings
        url = yarl.URL(url, encoded=True)
        async with client.get(url, headers=self.headers) as resp:
            assert resp.status == 200
            return await resp.content.read()

    async def save(self, content, out_file: str):
        async with aiofiles.open(f'{out_file}', 'wb') as f:
            logging.info(f'Writing file {out_file}')
            await f.write(content)

    async def fetch_and_save(self, client: aiohttp.ClientSession, url: str, out_file: str):
        content = await self.fetch(client, url)
        if content:
            await self.save(content, out_file)

    async def fetch_and_save_all(self, urls: List[str], out_files: List[str]):
        tasks = []
        async with aiohttp.ClientSession(cookie_jar=DummyCookieJar()) as client:
            for url, out_file in zip(urls, out_files):
                tasks.append(self.fetch_and_save(client, url, out_file))
            # responses = [await f for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks))]
            await asyncio.gather(*tasks)

    def run(self):
        loop = asyncio.get_event_loop()
        tasks = [asyncio.ensure_future(self.fetch_and_save_all(self.urls, self.out_files))]
        loop.run_until_complete(asyncio.wait(tasks))
