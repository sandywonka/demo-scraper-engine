import asyncio
import aiohttp
import os
import pymongo
import pytz
import datetime
import logging
from bs4 import BeautifulSoup as bs4

class MAIndonesia:

    def __init__(self, pengadilan, year, page, mongo_client, db_name, col_name):
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.base_url = f'https://putusan3.mahkamahagung.go.id/direktori/index/pengadilan/{pengadilan}/tahunjenis/putus/tahun/{year}/page/{page}.html'
        self.mongo_client = pymongo.MongoClient(mongo_client)
        self.db_name = self.mongo_client[db_name]
        self.col_name = self.db_name[col_name]
        self.timezone = pytz.timezone('Asia/Jakarta')
        self.now = datetime.datetime.now(self.timezone)

    async def fetch(self, session, url):
        try:
            async with session.get(url, timeout=60) as response:
                return await response.text()
        except aiohttp.ClientResponseError as e:
             if e.status == 503:
                 return await self.fetch(session, url)
             else:
                self.logger.error(f'Error fetching page {url}: {e}')
        
    async def get_page(self):
        try:
            async with aiohttp.ClientSession() as session:
                page = await self.fetch(session, self.base_url)
                soup = bs4(page, 'html.parser')
                content = soup.find('div', id='popular-post-list-sidebar')
                content_link = content.find_all('a')
                tasks = []
                semaphore = asyncio.Semaphore(4)
                for elem in content_link:
                    if 'Putusan' in elem.text:
                        task = asyncio.create_task(self.get_detail(session, elem, semaphore))
                        tasks.append(task)
                await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f'Error getting page: {e}')

    async def get_detail(self, session, detail_page, semaphore):
        try:
            async with semaphore:
                result = []
                my_dict = {}
                detail_content = await self.fetch(session, detail_page['href'])
                main_content = bs4(detail_content, 'html.parser')
                table = main_content.find('table', class_='table')
                pdf_links = main_content.find('div', class_='card-body bg-white')
                for elems in table.select('td'):
                    result.append(elems.text.strip())
                result.pop(0)
                for i in range(0, len(result), 2):
                    key = result[i]
                    value = result[i+1]
                    my_dict[key] = value
                for elems in pdf_links.find_all('a'):
                    if 'pdf' in elems.text:
                        my_dict['PDF Link'] = elems['href']
                filename = f"pdf/{my_dict['Nomor'].replace('/', '_')}.pdf"
                my_dict['PDF Location'] = filename
                my_dict['created_at'] = self.now.strftime('%Y-%m-%d %H:%M:%S %Z%z')
                my_dict['updated_at'] = ''

                task = [
                    asyncio.create_task(self.download_pdf(session, my_dict, filename)),
                    asyncio.create_task(self.store_to_mongo(my_dict))
                ]

                await asyncio.gather(*task)
        except aiohttp.ClientResponseError as e:
            self.logger.error(f'Error getting detail page {detail_page["href"]}: {e}')

    async def download_pdf(self, session, data, filename, retry=3):
        try:
            async with session.get(data['PDF Link']) as response:
                if response.status == 200:
                    if os.path.exists(filename):
                        print(f'{filename} already exists')
                    else:
                        with open(filename, 'wb') as f:
                            async for chunk in response.content.iter_chunked(1024):
                                f.write(chunk)
                        print(f'Downloaded PDF {filename}')
                else:
                    self.logger.warning(f'Error downloading PDF, response not == 200 {data["PDF Link"]}')
                    if retry > 0:
                        self.logger.warning(f'Retrying {retry} more times...')
                        await asyncio.sleep(5)
                        await self.download_pdf(session, data, filename, retry=retry-1)
        except Exception as e:
            self.logger.error(f'Error downloading PDF {data["PDF Link"]}: {e}')

    async def store_to_mongo(self, data):
        try:
            if self.col_name.find_one({'Nomor': data['Nomor']}) is None:
                self.col_name.insert_one(data)
                print(f'{data["Nomor"]} stored successfully')
            else:
                print(f'{data["Nomor"]} already exists')
        except Exception as e:
            self.logger.error(f'Error storing data to MongoDB: {e}')