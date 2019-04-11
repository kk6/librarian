import more_itertools
import requests
from tqdm import tqdm
import aiohttp
import asyncio
from tortoise import Tortoise

from models import BookSummary


def fetch_isbn_list():
    res = requests.get("https://api.openbd.jp/v1/coverage")
    return res.json()


async def fetch_book_data(session, isbn_list, sem):
    isbn_csv = ",".join(isbn_list)
    url = f"https://api.openbd.jp/v1/get?isbn={isbn_csv}"
    async with sem:
        async with session.get(url) as res:
            return await res.json()


async def fetch_all(chunked_isbn_list, limit=5):
    sem = asyncio.Semaphore(limit)
    async with aiohttp.ClientSession() as session:
        cors = [fetch_book_data(session, isbn_list, sem) for isbn_list in chunked_isbn_list]
        responses = [await f for f in tqdm(asyncio.as_completed(cors), total=len(cors), desc="downloding")]
        return responses


async def insert(summary):
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


async def bulk_insert(responses):
    rs = more_itertools.flatten(responses)
    cors = [insert(r["summary"]) for r in rs]
    responses = [await f for f in tqdm(asyncio.as_completed(cors), total=len(cors), desc="saving")]
    return responses


async def main():
    await Tortoise.init(db_url="sqlite://db.sqlite3", modules={"models": ["models"]})
    await Tortoise.generate_schemas()
    all_isbn_list = fetch_isbn_list()

    chunked_isbn_list = more_itertools.chunked(all_isbn_list, 1000)
    responses = await fetch_all(chunked_isbn_list)
    return await bulk_insert(responses)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
