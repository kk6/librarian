from typing import Iterable

import more_itertools
import requests
from tqdm import tqdm
import aiohttp
import asyncio
from tortoise import Tortoise

from models import BookSummary


def request_isbn_list():
    res = requests.get("https://api.openbd.jp/v1/coverage")
    return res.json()


async def request_book_data(
    session: aiohttp.ClientSession, isbn_list: list, semaphore: asyncio.Semaphore
):
    isbn_csv = ",".join(isbn_list)
    url = f"https://api.openbd.jp/v1/get?isbn={isbn_csv}"
    async with semaphore:
        async with session.get(url) as resp:
            return await resp.json()


async def request_all_book_data(chunked_isbn_list: Iterable[list], limit: int = 5):
    semaphore = asyncio.Semaphore(limit)
    async with aiohttp.ClientSession() as session:
        cors = [
            request_book_data(session, isbn_list, semaphore)
            for isbn_list in chunked_isbn_list
        ]
        responses = [
            await f
            for f in tqdm(
                asyncio.as_completed(cors), total=len(cors), desc="downloding"
            )
        ]
        return responses


async def insert_book_summary(summary):
    return await BookSummary.get_or_create(
        isbn=summary["isbn"],
        title=summary["title"],
        volume=summary["volume"],
        series=summary["series"],
        author=summary["author"],
        publisher=summary["publisher"],
        pubdate=summary["pubdate"],
        cover=summary["cover"],
    )


async def bulk_insert_book_summary(responses):
    rs = more_itertools.flatten(responses)
    cors = [insert_book_summary(r["summary"]) for r in rs]
    responses = [
        await f
        for f in tqdm(asyncio.as_completed(cors), total=len(cors), desc="saving")
    ]
    return responses


async def main():
    await Tortoise.init(db_url="sqlite://db.sqlite3", modules={"models": ["models"]})
    await Tortoise.generate_schemas()
    all_isbn_list = request_isbn_list()

    chunked_isbn_list = more_itertools.chunked(all_isbn_list, 1000)
    responses = await request_all_book_data(chunked_isbn_list)
    return await bulk_insert_book_summary(responses)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
