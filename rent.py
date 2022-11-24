from bs4 import BeautifulSoup
import scrapy
from uszipcode import SearchEngine
import cloudscraper
import logging
from sqlitedict import SqliteDict
from scrapy.extensions.postprocessing import GzipPlugin
import pathlib

logging.getLogger('scrapy.core.scraper').addFilter(
    lambda x: not x.getMessage().startswith('Scraped from'))

SCRAPER = cloudscraper.create_scraper(delay=10, browser={'custom': 'ScraperBot/1.0',})

def get_zips():
    s = SearchEngine()
    l = s.by_pattern('', returns=1000000)
    return [x.zipcode for x in list(l)]

def get_important_urls(page_contents):
    soup = BeautifulSoup(page_contents, 'lxml')
    property_links = []
    url_prefix = "https://www.rent.com"
    for a in soup.select('a[data-tid="pdp-link"]'):
        property_links.append(url_prefix+a.attrs['href'])
    page_links = []
    for a in soup.select('a[data-tag_section="pagination"]'):
        page_links.append(url_prefix+a.attrs['href'])
    return page_links, property_links

class RentSpider(scrapy.Spider):
    name = "rent"
    allowed_domains = ["rent.com"]
    TEST_ZIPS = [78758, 78602, 77450]
    start_urls = ["https://www.rent.com/zip-{z}-apartments".format(z=z) for z in get_zips()]
    page_urls = []
    handle_httpstatus_list = [403]
    property_urls = []
    custom_settings = {
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'FEEDS': {
            pathlib.Path('%(batch_id)d-items.json.gz'): {
                'format': 'json',
                'postprocessing': ['scrapy.extensions.postprocessing.GzipPlugin'],
                'gzip_compresslevel': 9,
                'batch_item_count': 100,
            },
        }
    }
    def __init__(self):
        self.scrape_keys = SqliteDict("scrape_keys.sqlite")

    def repair_response(self, response):
        if response.status==403:
            new_response = SCRAPER.get(response.url)
            response = response.replace(body=new_response.text)
        return response

    def parse_property(self, response):
        if response.url in self.scrape_keys:
            return
        response = self.repair_response(response)
        self.scrape_keys[response.url] = True
        self.scrape_keys.commit()
        yield {
            'response.body': str(response.body),
            'response.url': str(response.url),
            'response.status': str(response.status)
        }

    def parse(self, response):
        if response.url in self.scrape_keys:
            return
        response = self.repair_response(response)
        self.scrape_keys[response.url] = True
        self.scrape_keys.commit()
        pages, properties = get_important_urls(response.body)
        for page in pages:
            yield response.follow(page, self.parse)
        for property in properties:
            yield response.follow(property, self.parse_property)

    def closed(self, reason):
        self.scrape_keys.close()
