import asyncio
from engine import MAIndonesia


async def main():
    pengadilan = 'pa-surabaya'
    year = '2023'
    # page = 15
    mongo_client = 'mongodb://localhost:27017/'
    db_name = 'ma_v3'
    col_name = pengadilan

    for page in range(1, 10):
        print(page)
        ma_indo = MAIndonesia(pengadilan, year, str(page), mongo_client, db_name, col_name)

        get_page = await ma_indo.get_page()


if __name__ == '__main__':
    asyncio.run(main())