# MAIndonesia Python Class

This class provides methods to scrape and store Indonesian court verdicts (putusan) from the Mahkamah Agung (Supreme Court) website, https://putusan3.mahkamahagung.go.id/. It uses aiohttp and asyncio libraries for asynchronous requests and beautifulsoup4 for HTML parsing. The scraped data is stored in MongoDB and the corresponding PDFs are downloaded and saved in the pdf/ folder.
Class attributes

    pengadilan: The court names to be scraped. Possible values: 'pa-surabaya', 'pa-kab-malang', 'pa-cibinong', etc.
    year: The year of the verdicts to be scraped.
    page: The page number of the verdicts to be scraped.
    mongo_client: The MongoDB client URL.
    db_name: The name of the MongoDB database where the data will be stored.
    col_name: The name of the MongoDB collection where the data will be stored.

## Class methods
### __init__(self, pengadilan, year, page, mongo_client, db_name, col_name)

The class constructor initializes the logger, sets the base URL for scraping, initializes the MongoDB client and sets the database and collection names. It also sets the timezone and current datetime.
async def fetch(self, session, url)

This method asynchronously fetches the content of a given URL using the provided session object. If there is a 503 Service Unavailable response, it retries the request until it succeeds. If there is an error in the response, it logs an error message.
### async def get_page(self)

This method asynchronously gets the list of verdicts from the base URL and extracts the detail page links. It then creates tasks for scraping each detail page using the get_detail method, and runs them asynchronously using asyncio.gather(). If there is an error in the response, it logs an error message.
### async def get_detail(self, session, detail_page, semaphore)

This method asynchronously gets the details of a single verdict from the detail page URL provided. It extracts the verdict data and PDF link, and then creates tasks for downloading the PDF and storing the data in MongoDB using the download_pdf and store_to_mongo methods, respectively. It runs these tasks asynchronously using asyncio.gather(). If there is an error in the response, it logs an error message.
### async def download_pdf(self, session, data, filename, retry=3)

This method asynchronously downloads the PDF file from the given URL and saves it to the provided filename. If there is an error in the response, it logs a warning message and retries the download up to retry times. If it fails to download the PDF after retry attempts, it logs an error message.
### async def store_to_mongo(self, data)

This method asynchronously stores the given data in MongoDB using the provided collection name. If the data with the same Nomor value already exists in the collection, it logs a message indicating that it already exists. If there is an error in storing the data, it logs an error message.

## How to use

To use this class, you need to instantiate an object of the MAIndonesia class and pass the necessary parameters.

``` python

    from MAIndonesia import MAIndonesia

    pengadilan = '01'
    year = '2022'
    page = 1
    mongo_client = 'mongodb://localhost:27017/'
    db_name = 'mydb'
    col_name = 'mycollection'

    mai = MAIndonesia(pengadilan, year, page, mongo_client, db_name, col_name)

    await mai.get_page()
```

### Parameters

    pengadilan: string representing the court code, e.g., 'pa-surabaya' for the Mahkamah Agung.
    year: string representing the year of the court decisions to be fetched, e.g., '2022'.
    page: integer representing the page number of the court decisions to be fetched, e.g., 1.
    mongo_client: string representing the URL of the MongoDB client, e.g., 'mongodb://localhost:27017/'.
    db_name: string representing the name of the MongoDB database, e.g., 'mydb'.
    col_name: string representing the name of the MongoDB collection, e.g., 'mycollection'.

### Methods

    __init__(): initializes the MAIndonesia object and sets up the logger, base URL, MongoDB client, database name, and collection name.
    fetch(session, url): asynchronous method that fetches the HTML content of a URL using aiohttp.
    get_page(): asynchronous method that retrieves the court decisions from a given page and calls the get_detail() method for each decision found.
    get_detail(session, detail_page, semaphore): asynchronous method that retrieves the details of a court decision and stores them in MongoDB.
    download_pdf(session, data, filename, retry): asynchronous method that downloads a PDF file of a court decision and saves it to disk.
    store_to_mongo(data): asynchronous method that stores a court decision in MongoDB.

## Other Features
The MAIndonesia class is designed to scrape and download Indonesian court verdicts from the official website of the Supreme Court of Indonesia (Mahkamah Agung). The following are the notable features of this class:

### Logging:
The class uses Python's built-in logging module to log various events during the scraping process. It logs messages at the DEBUG and ERROR levels and writes them to a file named app.log. This feature helps in debugging and troubleshooting any issues that may arise during the scraping process.

### Asyncio:
The class uses the asyncio library to perform asynchronous web scraping. The fetch() function uses async with to create an asynchronous HTTP request and return the HTML content of the page. The get_page() function uses async with and asyncio.gather() to asynchronously scrape multiple pages at once. The get_detail() function uses async with and a semaphore to limit the number of concurrent requests made to the server. The download_pdf() and store_to_mongo() functions also use async with to create asynchronous file downloads and MongoDB write operations, respectively. Using asyncio helps improve the scraping speed and efficiency.

### OOP:
The class is designed using the principles of Object-Oriented Programming (OOP). It has a constructor (__init__()) that initializes various class variables such as the base URL, MongoDB client, and collection name. It also has methods such as fetch(), get_page(), get_detail(), download_pdf(), and store_to_mongo() that perform specific tasks related to the scraping process. Using OOP principles helps improve the code's organization and readability, making it easier to maintain and update in the future.