import more_itertools
import requests
from tqdm import tqdm
import aiohttp
import asyncio


"""
aiohttp版に改良中。

参考URL

- https://qiita.com/meznat/items/c34fad95dab593f9bffa
- https://qiita.com/icoxfog417/items/07cbf5110ca82629aca0

async with tqdm

- https://postd.cc/fast-scraping-in-python-with-asyncio/

"""


def fetch_isbn_list():
    res = requests.get("https://api.openbd.jp/v1/coverage")
    return res.json()


async def fetch_book_data(session, isbn_list, sem):
    isbn_csv = ",".join(isbn_list)
    url = f"https://api.openbd.jp/v1/get?isbn={isbn_csv}"
    with await sem:
        async with session.get(url) as res:
            return await res.text()


async def fetch_all(chunked_isbn_list, limit=5):
    sem = asyncio.Semaphore(limit)
    async with aiohttp.ClientSession() as session:
        for isbn_list in chunked_isbn_list:
            data = await fetch_book_data(session, isbn_list, sem)
            print(data)


async def main():
    all_isbn_list = fetch_isbn_list()
    books_total = len(all_isbn_list)

    chunked_isbn_list = more_itertools.chunked(all_isbn_list, 1000)

    with tqdm(total=books_total) as progress_bar:
        progress_bar.set_description("Downloading book summary")
        return await fetch_all(chunked_isbn_list)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
